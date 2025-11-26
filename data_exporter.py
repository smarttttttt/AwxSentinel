"""
Universal Data Exporter for Prometheus
通用数据导出器 - 将多种数据源的指标暴露给 Prometheus 拉取

功能:
- 支持多种数据源: REST API、BigQuery、MySQL/PostgreSQL、GCS/S3
- 配置驱动: 通过 YAML 配置文件管理数据源
- 自动过期: 定期清理不再更新的指标数据
- 并行采集: 每个数据源独立线程，互不影响

使用方式:
    python data_exporter.py --config exporter-config.yaml

Prometheus 拉取:
    GET http://localhost:8000/metrics

Author: Boyi Wang
Date: 2025-11-26
"""

import os
import sys
import time
import json
import yaml
import logging
import argparse
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

# Prometheus 客户端库
from prometheus_client import start_http_server, Gauge, Counter, REGISTRY
from prometheus_client.core import GaugeMetricFamily

# ============================================================================
# 日志配置
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('data_exporter')


# ============================================================================
# Collector 基类
# ============================================================================
class BaseCollector(ABC):
    """
    数据采集器基类
    所有具体的采集器都需要继承此类并实现 collect() 方法
    """

    def __init__(self, config: dict):
        """
        初始化采集器

        Args:
            config: 数据源配置字典，包含 name、type、endpoint 等信息
        """
        self.config = config
        self.name = config['name']
        self.logger = logging.getLogger(f'collector.{self.name}')

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        采集数据的抽象方法，子类必须实现

        Returns:
            List[Dict]: 采集到的数据列表，每个元素是一个包含指标值和标签的字典
            示例: [
                {'account_id': 'acc_123', 'block_rate': 0.45, 'region': 'HK'},
                {'account_id': 'acc_456', 'block_rate': 0.32, 'region': 'US'},
            ]
        """
        pass


# ============================================================================
# REST API Collector
# ============================================================================
class RestApiCollector(BaseCollector):
    """
    REST API 数据采集器
    通过 HTTP 请求从 API 端点获取指标数据
    """

    def __init__(self, config: dict):
        super().__init__(config)
        # 延迟导入，避免不需要时报错
        import requests
        self.requests = requests

    def collect(self) -> List[Dict[str, Any]]:
        """
        从 REST API 采集数据

        配置示例:
            endpoint: https://metric-platform.awx.im/api/v1/metrics
            auth:
                type: bearer_token
                token_env: METRIC_PLATFORM_TOKEN
        """
        headers = self._build_headers()

        try:
            response = self.requests.get(
                self.config['endpoint'],
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()

            # 支持不同的响应格式
            data = response.json()

            # 如果响应有 data 字段，取 data；否则直接使用响应
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, list):
                return data
            else:
                self.logger.warning(f"Unexpected response format: {type(data)}")
                return []

        except self.requests.RequestException as e:
            self.logger.error(f"Failed to fetch from API: {e}")
            raise

    def _build_headers(self) -> dict:
        """构建 HTTP 请求头，处理认证信息"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        auth = self.config.get('auth', {})
        auth_type = auth.get('type')

        if auth_type == 'bearer_token':
            # 从环境变量获取 token
            token_env = auth.get('token_env', 'API_TOKEN')
            token = os.environ.get(token_env)
            if token:
                headers['Authorization'] = f'Bearer {token}'
            else:
                self.logger.warning(f"Token env var '{token_env}' not set")

        elif auth_type == 'api_key':
            # API Key 认证
            key_env = auth.get('key_env', 'API_KEY')
            key_header = auth.get('header_name', 'X-API-Key')
            api_key = os.environ.get(key_env)
            if api_key:
                headers[key_header] = api_key

        elif auth_type == 'basic':
            # Basic 认证
            import base64
            username = os.environ.get(auth.get('username_env', 'API_USERNAME'), '')
            password = os.environ.get(auth.get('password_env', 'API_PASSWORD'), '')
            credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'

        return headers


# ============================================================================
# BigQuery Collector
# ============================================================================
class BigQueryCollector(BaseCollector):
    """
    BigQuery 数据采集器
    执行 SQL 查询从 BigQuery 获取指标数据
    """

    def __init__(self, config: dict):
        super().__init__(config)
        # 延迟导入 BigQuery 客户端
        from google.cloud import bigquery
        self.client = bigquery.Client(project=config.get('project'))

    def collect(self) -> List[Dict[str, Any]]:
        """
        从 BigQuery 执行查询并返回结果

        配置示例:
            project: risk-prod-xxx
            query: |
                SELECT account_id, block_rate, failed_auth_rate
                FROM `risk-prod.ads_pafraud.daily_merchant_stats`
                WHERE date = CURRENT_DATE()
        """
        query = self.config['query']

        try:
            # 执行查询
            query_job = self.client.query(query)
            results = query_job.result()

            # 转换为字典列表
            data = [dict(row) for row in results]
            self.logger.info(f"Fetched {len(data)} rows from BigQuery")
            return data

        except Exception as e:
            self.logger.error(f"BigQuery query failed: {e}")
            raise


# ============================================================================
# Database Collector (MySQL/PostgreSQL)
# ============================================================================
class DatabaseCollector(BaseCollector):
    """
    数据库采集器
    支持 MySQL 和 PostgreSQL
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.conn_config = config['connection']
        self.driver = self.conn_config.get('driver', 'mysql')

    def collect(self) -> List[Dict[str, Any]]:
        """
        从数据库执行查询并返回结果

        配置示例:
            connection:
                driver: mysql  # 或 postgresql
                host_env: MYSQL_HOST
                port: 3306
                database: risk_db
                username_env: MYSQL_USER
                password_env: MYSQL_PASSWORD
            query: SELECT account_id, alert_threshold FROM merchant_config
        """
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(self.config['query'])

            # 获取列名
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # 转换为字典列表
            data = [dict(zip(columns, row)) for row in rows]
            self.logger.info(f"Fetched {len(data)} rows from database")
            return data

        finally:
            conn.close()

    def _get_connection(self):
        """获取数据库连接"""
        host = os.environ.get(self.conn_config.get('host_env', 'DB_HOST'), 'localhost')
        port = self.conn_config.get('port', 3306)
        database = self.conn_config.get('database', '')
        username = os.environ.get(self.conn_config.get('username_env', 'DB_USER'), '')
        password = os.environ.get(self.conn_config.get('password_env', 'DB_PASSWORD'), '')

        if self.driver == 'mysql':
            import pymysql
            return pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
        elif self.driver == 'postgresql':
            import psycopg2
            return psycopg2.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                dbname=database
            )
        else:
            raise ValueError(f"Unsupported database driver: {self.driver}")


# ============================================================================
# GCS Collector
# ============================================================================
class GcsCollector(BaseCollector):
    """
    Google Cloud Storage 文件采集器
    从 GCS 读取 JSON/CSV 文件获取指标数据
    """

    def __init__(self, config: dict):
        super().__init__(config)
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(config['bucket'])

    def collect(self) -> List[Dict[str, Any]]:
        """
        从 GCS 读取文件并解析

        配置示例:
            bucket: awx-ml-platform-prod
            path_pattern: "metrics/hourly/{date}/report.json"
            format: json
        """
        # 替换路径模板变量
        path = self.config['path_pattern'].format(
            date=datetime.now().strftime('%Y-%m-%d'),
            hour=datetime.now().strftime('%H')
        )

        try:
            blob = self.bucket.blob(path)
            content = blob.download_as_text()

            file_format = self.config.get('format', 'json')

            if file_format == 'json':
                data = json.loads(content)
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                return data if isinstance(data, list) else [data]

            elif file_format == 'csv':
                import csv
                import io
                reader = csv.DictReader(io.StringIO(content))
                return list(reader)

            else:
                raise ValueError(f"Unsupported file format: {file_format}")

        except Exception as e:
            self.logger.error(f"Failed to read from GCS: {e}")
            raise


# ============================================================================
# Collector Factory
# ============================================================================
class CollectorFactory:
    """
    采集器工厂类
    根据配置中的 type 字段创建对应的采集器实例
    """

    # 注册所有支持的采集器类型
    COLLECTORS = {
        'rest_api': RestApiCollector,
        'bigquery': BigQueryCollector,
        'database': DatabaseCollector,
        'gcs_file': GcsCollector,
    }

    @classmethod
    def create(cls, config: dict) -> BaseCollector:
        """
        根据配置创建采集器实例

        Args:
            config: 数据源配置

        Returns:
            BaseCollector: 对应类型的采集器实例
        """
        collector_type = config.get('type')

        if collector_type not in cls.COLLECTORS:
            raise ValueError(
                f"Unknown collector type: {collector_type}. "
                f"Supported types: {list(cls.COLLECTORS.keys())}"
            )

        return cls.COLLECTORS[collector_type](config)

    @classmethod
    def register(cls, type_name: str, collector_class: type):
        """
        注册新的采集器类型（扩展用）

        Args:
            type_name: 类型名称
            collector_class: 采集器类
        """
        cls.COLLECTORS[type_name] = collector_class


# ============================================================================
# 带 TTL 的指标管理器
# ============================================================================
class MetricsManager:
    """
    指标管理器
    负责管理 Prometheus 指标，支持数据过期清理
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        初始化指标管理器

        Args:
            ttl_seconds: 指标数据过期时间（秒），默认 5 分钟
        """
        self.gauges: Dict[str, Gauge] = {}
        self.timestamps: Dict[str, Dict[tuple, float]] = {}  # {metric_name: {label_key: timestamp}}
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
        self.logger = logging.getLogger('metrics_manager')

    def register_gauge(self, name: str, description: str, labels: List[str]) -> Gauge:
        """
        注册一个新的 Gauge 指标

        Args:
            name: 指标名称
            description: 指标描述
            labels: 标签列表

        Returns:
            Gauge: Prometheus Gauge 对象
        """
        if name not in self.gauges:
            self.gauges[name] = Gauge(name, description, labels)
            self.timestamps[name] = {}
            self.logger.info(f"Registered gauge: {name} with labels {labels}")
        return self.gauges[name]

    def set_value(self, metric_name: str, labels: Dict[str, str], value: float):
        """
        设置指标值并更新时间戳

        Args:
            metric_name: 指标名称
            labels: 标签字典
            value: 指标值
        """
        if metric_name not in self.gauges:
            self.logger.warning(f"Gauge '{metric_name}' not registered")
            return

        gauge = self.gauges[metric_name]
        label_key = tuple(sorted(labels.items()))

        with self.lock:
            # 更新值和时间戳
            gauge.labels(**labels).set(value)
            self.timestamps[metric_name][label_key] = time.time()

    def clear_metric(self, metric_name: str):
        """
        清空指定指标的所有标签组合（用于每次采集前清理）

        Args:
            metric_name: 指标名称
        """
        if metric_name not in self.gauges:
            return

        gauge = self.gauges[metric_name]

        with self.lock:
            # 清空 Gauge 内部存储
            gauge._metrics.clear()
            self.timestamps[metric_name].clear()

    def cleanup_expired(self):
        """
        清理所有过期的指标数据
        遍历所有指标，删除超过 TTL 的标签组合
        """
        now = time.time()
        total_cleaned = 0

        with self.lock:
            for metric_name, gauge in self.gauges.items():
                timestamps = self.timestamps.get(metric_name, {})
                expired_keys = [
                    key for key, ts in timestamps.items()
                    if now - ts > self.ttl
                ]

                for key in expired_keys:
                    try:
                        # 获取标签值列表（按 Gauge 定义的顺序）
                        labels_dict = dict(key)
                        label_values = [labels_dict.get(l, '') for l in gauge._labelnames]
                        gauge.remove(*label_values)
                        del timestamps[key]
                        total_cleaned += 1
                    except Exception as e:
                        self.logger.error(f"Failed to remove expired metric: {e}")

        if total_cleaned > 0:
            self.logger.info(f"Cleaned up {total_cleaned} expired metric(s)")


# ============================================================================
# Universal Exporter 主类
# ============================================================================
class UniversalExporter:
    """
    通用数据导出器
    主类，负责协调数据采集、指标更新和 HTTP 服务
    """

    def __init__(self, config_path: str):
        """
        初始化导出器

        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger('exporter')

        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.logger.info(f"Loaded configuration from {config_path}")

        # 初始化指标管理器
        ttl = self.config.get('exporter', {}).get('metrics_ttl_seconds', 300)
        self.metrics_manager = MetricsManager(ttl_seconds=ttl)

        # 初始化指标
        self._init_metrics()

        # Exporter 自身的监控指标
        self.scrape_success = Counter(
            'exporter_scrape_success_total',
            'Total number of successful scrapes',
            ['source']
        )
        self.scrape_errors = Counter(
            'exporter_scrape_errors_total',
            'Total number of scrape errors',
            ['source']
        )
        self.scrape_duration = Gauge(
            'exporter_scrape_duration_seconds',
            'Duration of last scrape in seconds',
            ['source']
        )
        self.last_scrape_time = Gauge(
            'exporter_last_scrape_timestamp',
            'Timestamp of last successful scrape',
            ['source']
        )

    def _init_metrics(self):
        """
        根据配置初始化所有 Prometheus 指标
        """
        for source in self.config.get('data_sources', []):
            if not source.get('enabled', True):
                continue

            for metric_config in source.get('metrics', []):
                name = metric_config['prometheus_name']
                labels = metric_config.get('labels', [])
                description = metric_config.get('description', f"Metric from {source['name']}")

                self.metrics_manager.register_gauge(name, description, labels)

    def _update_metrics(self, source: dict, clear_before_update: bool = True):
        """
        更新指定数据源的指标

        Args:
            source: 数据源配置
            clear_before_update: 是否在更新前清空旧数据
        """
        source_name = source['name']
        start_time = time.time()

        try:
            # 创建采集器并获取数据
            collector = CollectorFactory.create(source)
            data = collector.collect()

            if not data:
                self.logger.warning(f"[{source_name}] No data returned, keeping previous values")
                return

            # 清空旧数据（可选）
            if clear_before_update:
                for metric_config in source.get('metrics', []):
                    self.metrics_manager.clear_metric(metric_config['prometheus_name'])

            # 更新指标值
            updated_count = 0
            for item in data:
                for metric_config in source.get('metrics', []):
                    metric_name = metric_config['prometheus_name']
                    source_field = metric_config['source_field']
                    label_names = metric_config.get('labels', [])

                    # 提取标签值
                    labels = {
                        label: str(item.get(label, 'unknown'))
                        for label in label_names
                    }

                    # 提取指标值
                    value = item.get(source_field)
                    if value is not None:
                        try:
                            value = float(value)
                            self.metrics_manager.set_value(metric_name, labels, value)
                            updated_count += 1
                        except (ValueError, TypeError) as e:
                            self.logger.warning(
                                f"[{source_name}] Invalid value for {source_field}: {value}"
                            )

            # 更新监控指标
            duration = time.time() - start_time
            self.scrape_success.labels(source=source_name).inc()
            self.scrape_duration.labels(source=source_name).set(duration)
            self.last_scrape_time.labels(source=source_name).set(time.time())

            self.logger.info(
                f"[{source_name}] Updated {updated_count} metrics in {duration:.2f}s"
            )

        except Exception as e:
            self.scrape_errors.labels(source=source_name).inc()
            self.logger.error(f"[{source_name}] Scrape failed: {e}")

    def _run_source_loop(self, source: dict):
        """
        运行单个数据源的采集循环（在独立线程中）

        Args:
            source: 数据源配置
        """
        source_name = source['name']
        interval = self._parse_interval(source.get('interval', '60s'))

        self.logger.info(f"[{source_name}] Starting collector loop (interval: {interval}s)")

        # 立即执行一次
        self._update_metrics(source)

        # 循环采集
        while True:
            time.sleep(interval)
            self._update_metrics(source)

    def _run_cleanup_loop(self):
        """
        运行过期数据清理循环
        """
        cleanup_interval = self.config.get('exporter', {}).get('cleanup_interval_seconds', 60)

        self.logger.info(f"Starting cleanup loop (interval: {cleanup_interval}s)")

        while True:
            time.sleep(cleanup_interval)
            self.metrics_manager.cleanup_expired()

    def _parse_interval(self, interval_str: str) -> int:
        """
        解析时间间隔字符串

        Args:
            interval_str: 时间字符串，如 "30s", "5m", "1h"

        Returns:
            int: 秒数
        """
        if isinstance(interval_str, int):
            return interval_str

        interval_str = str(interval_str).strip().lower()

        if interval_str.endswith('s'):
            return int(interval_str[:-1])
        elif interval_str.endswith('m'):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith('h'):
            return int(interval_str[:-1]) * 3600
        else:
            return int(interval_str)

    def start(self):
        """
        启动 Exporter 服务

        流程:
        1. 启动 HTTP Server 暴露 /metrics 端点
        2. 为每个数据源启动独立的采集线程
        3. 启动过期数据清理线程
        4. 主线程保持运行
        """
        port = self.config.get('exporter', {}).get('port', 8000)

        # 启动 Prometheus HTTP Server
        start_http_server(port)
        self.logger.info(f"Exporter started on http://0.0.0.0:{port}/metrics")

        # 为每个启用的数据源启动采集线程
        for source in self.config.get('data_sources', []):
            if not source.get('enabled', True):
                self.logger.info(f"[{source['name']}] Skipped (disabled)")
                continue

            thread = threading.Thread(
                target=self._run_source_loop,
                args=(source,),
                daemon=True,
                name=f"collector-{source['name']}"
            )
            thread.start()
            self.logger.info(f"[{source['name']}] Collector thread started")

        # 启动清理线程
        cleanup_thread = threading.Thread(
            target=self._run_cleanup_loop,
            daemon=True,
            name="cleanup"
        )
        cleanup_thread.start()

        # 主线程保持运行
        self.logger.info("Exporter is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            sys.exit(0)


# ============================================================================
# 命令行入口
# ============================================================================
def main():
    """
    命令行入口函数
    """
    parser = argparse.ArgumentParser(
        description='Universal Data Exporter for Prometheus'
    )
    parser.add_argument(
        '--config', '-c',
        default='exporter-config.yaml',
        help='Path to configuration file (default: exporter-config.yaml)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=None,
        help='Override port from config file'
    )

    args = parser.parse_args()

    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        logger.info("Creating example configuration file...")
        create_example_config(args.config)
        logger.info(f"Example config created at {args.config}. Please edit and restart.")
        sys.exit(1)

    # 启动 Exporter
    exporter = UniversalExporter(args.config)

    # 如果命令行指定了端口，覆盖配置
    if args.port:
        exporter.config.setdefault('exporter', {})['port'] = args.port

    exporter.start()


def create_example_config(path: str):
    """
    创建示例配置文件

    Args:
        path: 配置文件路径
    """
    example_config = """# Universal Exporter Configuration
# 通用数据导出器配置文件

exporter:
  port: 8000                      # HTTP 服务端口
  log_level: INFO                 # 日志级别
  metrics_ttl_seconds: 300        # 指标数据过期时间（秒）
  cleanup_interval_seconds: 60    # 过期数据清理间隔（秒）

data_sources:
  # ============ REST API 示例 ============
  - name: metric_platform_fraud
    type: rest_api
    enabled: true
    endpoint: https://metric-platform.example.com/api/v1/metrics/fraud
    auth:
      type: bearer_token
      token_env: METRIC_PLATFORM_TOKEN    # 从环境变量读取 Token
    timeout: 30
    interval: 30s                          # 采集间隔
    metrics:
      - source_field: block_rate           # API 响应中的字段名
        prometheus_name: sentinel_block_rate
        description: "Transaction block rate"
        type: gauge
        labels: [account_id, merchant_name, region]
      - source_field: failed_auth_rate
        prometheus_name: sentinel_failed_auth_rate
        description: "Failed authorization rate"
        type: gauge
        labels: [account_id, merchant_name]

  # ============ BigQuery 示例 ============
  - name: bigquery_daily_stats
    type: bigquery
    enabled: false                         # 设为 true 启用
    project: your-gcp-project-id
    query: |
      SELECT
        account_id,
        merchant_name,
        block_rate,
        failed_auth_rate,
        total_transactions
      FROM `your-project.dataset.daily_merchant_stats`
      WHERE date = CURRENT_DATE()
    interval: 5m
    metrics:
      - source_field: block_rate
        prometheus_name: sentinel_daily_block_rate
        description: "Daily block rate from BigQuery"
        type: gauge
        labels: [account_id, merchant_name]

  # ============ MySQL 示例 ============
  - name: mysql_merchant_config
    type: database
    enabled: false                         # 设为 true 启用
    connection:
      driver: mysql                        # 或 postgresql
      host_env: MYSQL_HOST
      port: 3306
      database: risk_db
      username_env: MYSQL_USER
      password_env: MYSQL_PASSWORD
    query: |
      SELECT
        account_id,
        alert_threshold,
        is_high_risk
      FROM merchant_risk_config
      WHERE updated_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    interval: 5m
    metrics:
      - source_field: alert_threshold
        prometheus_name: sentinel_merchant_threshold
        description: "Merchant alert threshold"
        type: gauge
        labels: [account_id]

  # ============ GCS 文件示例 ============
  - name: gcs_hourly_report
    type: gcs_file
    enabled: false                         # 设为 true 启用
    bucket: your-bucket-name
    path_pattern: "metrics/hourly/{date}/report.json"
    format: json
    interval: 1h
    metrics:
      - source_field: hourly_block_rate
        prometheus_name: sentinel_hourly_block_rate
        description: "Hourly block rate from GCS"
        type: gauge
        labels: [account_id, region]
"""

    with open(path, 'w', encoding='utf-8') as f:
        f.write(example_config)


# ============================================================================
# 程序入口
# ============================================================================
if __name__ == '__main__':
    main()
