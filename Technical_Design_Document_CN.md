# Airwallex Sentinel - 技术设计文档

**版本：** 1.0
**日期：** 2025年11月14日
**作者：** 技术架构团队

---

## 目录

1. [执行摘要](#执行摘要)
2. [系统架构概览](#系统架构概览)
3. [核心组件](#核心组件)
4. [数据流和处理管道](#数据流和处理管道)
5. [API 设计](#api-设计)
6. [技术栈](#技术栈)
7. [部署架构](#部署架构)
8. [安全与合规](#安全与合规)
9. [可扩展性和性能](#可扩展性和性能)
10. [监控和可观测性](#监控和可观测性)
11. [实施路线图](#实施路线图)

---

## 执行摘要

本文档概述了 **Airwallex Sentinel** 的技术设计，这是一个 AI 驱动的欺诈预防平台，结合了实时欺诈检测、自动规则生成和智能风险缓解策略。系统集成了两个主要组件：

1. **Sentinel 核心**：面向客户的欺诈预防产品，提供一键和自动缓解功能
2. **自动化平台**：用于模型训练、规则生成和系统优化的后端基础设施

### 关键设计原则

- **实时处理**：欺诈检测和规则执行的亚秒级延迟
- **AI 优先架构**：ML 模型是决策的核心
- **可扩展性**：每天处理数百万笔交易
- **自动化**：通过智能自动化最小化人工干预
- **灵活性**：支持多种欺诈攻击向量和缓解策略

---

## 系统架构概览

### 高层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        商户门户层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  仪表板 UI   │  │  通知系统    │  │   规则管理界面       │  │
│  │              │  │ (SMS/Email)  │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API 网关与 BFF 层                             │
│         身份验证 │ 速率限制 │ 负载均衡                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Sentinel   │    │    自动化平台    │    │   风险引擎     │
│   核心服务   │◄──►│                  │◄──►│   (现有)       │
│              │    │                  │    │                │
└──────────────┘    └──────────────────┘    └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       数据与 ML 平台                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  特征库  │  │  模型服务│  │ 训练管道 │  │  实时分析     │  │
│  │          │  │          │  │          │  │               │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      存储与数据层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │PostgreSQL│  │  Redis   │  │BigQuery  │  │  时序数据库   │  │
│  │  (OLTP)  │  │  缓存    │  │  (OLAP)  │  │   (指标)      │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. Sentinel 核心服务

#### 1.1 警报检测引擎

**目的**：实时监控交易模式以检测潜在的欺诈攻击

**关键组件**：
- **指标监控器**：持续跟踪关键指标（拦截率、授权失败率、交易量）
- **阈值管理器**：可配置的 P1/P2 警报阈值
- **警报生成器**：创建带有元数据的结构化警报

**实现**：
```python
class AlertDetectionEngine:
    def __init__(self):
        self.metric_monitor = MetricMonitor()
        self.threshold_manager = ThresholdManager()
        self.alert_generator = AlertGenerator()

    async def process_transaction_stream(self, transactions):
        metrics = await self.metric_monitor.calculate_metrics(transactions)
        if self.threshold_manager.is_threshold_breached(metrics):
            alert = await self.alert_generator.create_alert(metrics)
            await self.publish_alert(alert)
```

**技术**：
- Apache Kafka 用于交易流处理
- Apache Flink 用于实时指标计算
- Redis 用于滑动窗口计算

---

#### 1.2 AI 分析模块 (Sentinel Agent)

**目的**：使用 ML 模型分析警报以分类攻击类型并推荐操作

**关键能力**：
- **行为分析**：按可疑属性对交易进行聚类
- **模式识别**：识别欺诈类型（卡测试、速率攻击等）
- **数据完整性检查**：检测交易数据中的异常
- **泄漏分析**：查找绕过规则但在发卡行失败的交易

**ML 管道**：
```
交易数据 → 特征工程 → 模型推理 →
结构化分析 (JSON) → 推荐操作
```

**使用的模型**：
- XGBoost 用于分类
- DBSCAN/K-Means 用于聚类
- Isolation Forest 用于异常检测
- NLP 模型用于电子邮件/域名分析

**输出格式**：
```json
{
  "alert_id": "ALT-20251114-001",
  "conclusion": "检测到卡测试攻击",
  "attack_category": "card_testing",
  "confidence_score": 0.95,
  "suggested_action": {
    "type": "block_rule",
    "conditions": ["bin=456789", "ip_country=CN"],
    "action": "BLOCK",
    "urgency": "high"
  },
  "impact_analysis": {
    "affected_transactions": 1250,
    "estimated_loss": 45000,
    "time_window": "last_30_minutes"
  }
}
```

---

#### 1.3 规则部署引擎

**目的**：将 AI 推荐转换为可执行规则并部署它们

**架构**：
```
AI 推荐 → 规则转换器 → 规则验证器 →
影子部署 → 性能监控 → 上线部署
```

**部署模式**：
- **一键模式**：商户在部署前批准
- **自动开启模式**：对高置信度攻击自动部署

**规则转换逻辑**：
```python
class RuleDeploymentEngine:
    async def deploy_rule(self, suggestion, mode='one_click'):
        # 将 AI 建议转换为规则格式
        rule = self.rule_translator.translate(suggestion)

        # 验证规则语法和冲突
        await self.rule_validator.validate(rule)

        # 首先部署到影子模式
        shadow_id = await self.deploy_to_shadow(rule)

        if mode == 'auto_on' and suggestion['confidence_score'] > 0.9:
            # 影子验证后自动部署
            await self.auto_deploy_to_live(shadow_id)
        else:
            # 等待商户批准
            await self.wait_for_approval(shadow_id)
```

---

#### 1.4 通知服务

**目的**：向商户提供多渠道警报传递

**渠道**：
- 应用内通知
- 电子邮件警报
- 短信（用于 P1 警报）
- Webhook 回调

**优先级处理**：
- P1 警报：通过所有渠道立即传递
- P2 警报：应用内 + 电子邮件
- P3 警报：仅应用内

**实现**：
- 消息队列（RabbitMQ/AWS SQS）用于可靠传递
- 模板引擎用于可自定义通知
- 指数退避的重试机制

---

### 2. 自动化平台

#### 2.1 模型训练管道

**目的**：通过自动化训练持续改进模型

**工作流**：
```
数据收集 → 特征工程 → 模型训练 →
模型验证 → 模型注册 → A/B 测试 → 部署
```

**组件**：
- **数据准备服务**：统一的训练数据管道
- **特征存储**：集中式特征仓库
- **模型注册表**：ML 模型的版本控制
- **实验跟踪器**：MLflow 用于跟踪实验

**刷新节奏**：
- 常规刷新：每日增量学习
- 按需刷新：由性能下降触发
- 智能刷新：由显著模式变化触发

---

#### 2.2 规则自动生成服务

**目的**：使用 ML 自动创建规则

**用例**：
1. **细分级别规则**：区域、行业特定
2. **商户级别规则**：单个商户的自定义规则
3. **攻击模式规则**：已知攻击模式的规则

**算法选择**：
```python
class RuleAutoGenerator:
    def __init__(self):
        self.algorithms = {
            'xgboost': XGBoostRuleGenerator(),
            'greedy': GreedySearchGenerator(),
            'exhaustive': ExhaustiveSearchGenerator()
        }

    def generate_rules(self, data, use_case):
        algorithm = self.select_algorithm(use_case)
        rules = algorithm.generate(data)
        return self.optimize_rules(rules)
```

---

#### 2.3 规则治理服务

**目的**：管理规则生命周期（监控、退役、优化）

**功能**：
- **自动退役**：删除表现不佳的规则
- **自动优化**：优化规则参数
- **冲突检测**：识别规则冲突
- **性能跟踪**：监控规则有效性

**规则退役工作流**：
```
每周性能审查 → 标记低性能规则 →
通知规则所有者 → 宽限期（2周）→ 自动退役
```

---

#### 2.4 回测服务

**目的**：在历史数据上模拟规则性能

**能力**：
- 历史数据重放
- 规则性能模拟
- 影响分析
- A/B 测试模拟

**实现**：
```python
class BacktestingService:
    async def run_backtest(self, rule, start_date, end_date):
        transactions = await self.get_historical_data(start_date, end_date)
        results = await self.simulate_rule(rule, transactions)
        return {
            'precision': results.precision,
            'recall': results.recall,
            'false_positive_rate': results.fpr,
            'estimated_loss_reduction': results.loss_reduction
        }
```

---

### 3. 风险引擎集成

**目的**：与现有风险引擎对接以执行规则

**集成点**：
- 规则同步（离线 → 在线）
- 交易评分
- 操作执行（BLOCK、CHALLENGE、ALLOW）
- 性能反馈

---

## 数据流和处理管道

### 实时欺诈检测流程

```
1. 交易事件
   ↓
2. 特征提取（实时）
   ↓
3. 指标计算（滑动窗口）
   ↓
4. 阈值检查
   ↓
5. 警报生成（如果阈值被突破）
   ↓
6. AI 分析
   ↓
7. 规则推荐
   ↓
8. 通知传递
   ↓
9. 商户操作 / 自动部署
   ↓
10. 规则执行
   ↓
11. 性能监控
```

### 批处理流程

```
1. 每日数据收集
   ↓
2. 特征工程
   ↓
3. 模型训练 / 规则生成
   ↓
4. 模型验证
   ↓
5. 影子部署
   ↓
6. A/B 测试
   ↓
7. 生产部署
```

---

## API 设计

### 1. Sentinel 核心 API

#### 获取警报
```http
GET /api/v1/sentinel/alerts
Authorization: Bearer {token}

查询参数:
- status: pending|acknowledged|resolved
- priority: P1|P2|P3
- start_date: ISO8601
- end_date: ISO8601
- limit: int (默认: 50)
- offset: int (默认: 0)

响应:
{
  "alerts": [
    {
      "id": "ALT-20251114-001",
      "category": "card_testing",
      "priority": "P1",
      "created_at": "2025-11-14T10:30:00Z",
      "status": "pending",
      "summary": {
        "conclusion": "检测到卡测试攻击",
        "confidence": 0.95,
        "affected_transactions": 1250,
        "estimated_loss": 45000
      },
      "suggested_action": {
        "type": "block_rule",
        "conditions": ["bin=456789"],
        "urgency": "high"
      }
    }
  ],
  "total": 150,
  "has_more": true
}
```

#### 部署规则（一键）
```http
POST /api/v1/sentinel/rules/deploy
Authorization: Bearer {token}
Content-Type: application/json

请求:
{
  "alert_id": "ALT-20251114-001",
  "deployment_mode": "shadow|live",
  "confirmation": true
}

响应:
{
  "rule_id": "RULE-20251114-001",
  "status": "deploying",
  "estimated_completion": "2025-11-14T10:35:00Z"
}
```

#### 提交反馈
```http
POST /api/v1/sentinel/alerts/{alert_id}/feedback
Authorization: Bearer {token}
Content-Type: application/json

请求:
{
  "helpful": true,
  "comment": "准确的检测，规则运作良好"
}

响应:
{
  "success": true,
  "message": "反馈已记录"
}
```

---

### 2. 自动化平台 API

#### 生成规则
```http
POST /api/v1/automation/rules/generate
Authorization: Bearer {token}
Content-Type: application/json

请求:
{
  "use_case": "segment|merchant|attack_pattern",
  "algorithm": "xgboost|greedy|exhaustive",
  "data_config": {
    "start_date": "2025-10-01",
    "end_date": "2025-11-14",
    "segment": "region:APAC,industry:ecommerce"
  },
  "optimization_target": "precision|recall|f1"
}

响应:
{
  "job_id": "JOB-20251114-001",
  "status": "queued",
  "estimated_completion": "2025-11-14T12:00:00Z"
}
```

#### 运行回测
```http
POST /api/v1/automation/backtest
Authorization: Bearer {token}
Content-Type: application/json

请求:
{
  "rule_definition": {
    "conditions": ["bin=456789", "amount<100"],
    "action": "BLOCK"
  },
  "test_period": {
    "start_date": "2025-10-01",
    "end_date": "2025-11-01"
  }
}

响应:
{
  "backtest_id": "BT-20251114-001",
  "results": {
    "transactions_evaluated": 1000000,
    "true_positives": 1200,
    "false_positives": 50,
    "precision": 0.96,
    "recall": 0.85,
    "estimated_loss_reduction": 120000
  }
}
```

---

## 技术栈

### 后端服务
- **语言**：Python 3.11+（FastAPI/Django）、Go（用于高性能服务）
- **API 框架**：FastAPI、gRPC 用于内部服务
- **任务队列**：Celery 配合 Redis/RabbitMQ
- **缓存**：Redis 集群
- **消息代理**：Apache Kafka

### 数据与 ML 平台
- **ML 框架**：scikit-learn、XGBoost、TensorFlow
- **特征存储**：Feast 或自定义解决方案
- **模型服务**：TensorFlow Serving、Seldon Core
- **实验跟踪**：MLflow
- **数据处理**：Apache Spark、Apache Flink
- **工作流编排**：Apache Airflow

### 存储
- **OLTP 数据库**：PostgreSQL 15+（带分区）
- **OLAP 数据库**：Google BigQuery
- **时序数据库**：InfluxDB 或 TimescaleDB
- **对象存储**：AWS S3 或 GCS
- **缓存**：Redis 集群

### 前端
- **框架**：React 18+ 配合 TypeScript
- **状态管理**：Redux Toolkit 或 Zustand
- **UI 库**：Material-UI 或 Ant Design
- **图表**：Recharts 或 D3.js
- **实时更新**：WebSocket 或 Server-Sent Events

### DevOps 与基础设施
- **容器化**：Docker
- **编排**：Kubernetes
- **CI/CD**：GitHub Actions、ArgoCD
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack（Elasticsearch、Logstash、Kibana）
- **追踪**：Jaeger 或 Zipkin
- **云提供商**：AWS 或 GCP

---

## 部署架构

### 生产环境

```
┌────────────────────────────────────────────────────────────┐
│                        CDN 层                               │
│                  (CloudFront/CloudFlare)                    │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   负载均衡器 (ALB/NLB)                      │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│  API 网关    │    │   Web 服务器     │    │  WebSocket     │
│  集群        │    │    (React)       │    │   服务         │
│ (3+ 节点)    │    │  (3+ 节点)       │    │  (2+ 节点)     │
└──────────────┘    └──────────────────┘    └────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│            Kubernetes 集群 (多可用区)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Sentinel   │  │   自动化     │  │  ML 推理服务     │ │
│  │    服务      │  │    平台      │  │                  │ │
│  │ (Deployment) │  │(StatefulSet) │  │  (Deployment)    │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   数据层 (多可用区)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  PostgreSQL  │  │  Redis       │  │  Kafka           │ │
│  │  主库 + 副本 │  │  集群        │  │  集群            │ │
│  │              │  │ (6 节点)     │  │ (3 代理)         │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 高可用配置

- **多可用区部署**：服务部署在 3 个可用区
- **自动扩展**：基于 CPU/内存/自定义指标的水平 Pod 自动扩展
- **数据库**：主-副本设置，具有自动故障转移
- **缓存**：Redis 集群配合哨兵实现自动故障转移
- **消息队列**：Kafka 集群，复制因子为 3

---

## 安全与合规

### 身份验证与授权
- **商户身份验证**：OAuth 2.0 / JWT 令牌
- **服务间通信**：mTLS，具有证书轮换
- **API 密钥**：用于 webhook 回调
- **基于角色的访问控制 (RBAC)**：细粒度权限

### 数据安全
- **静态加密**：所有数据库使用 AES-256
- **传输加密**：所有通信使用 TLS 1.3
- **PII 保护**：敏感卡数据令牌化
- **数据保留**：每种数据类型的可配置保留策略

### 合规性
- **PCI DSS**：卡数据处理的一级合规
- **GDPR**：删除权、数据可移植性
- **SOC 2**：Type II 认证
- **审计日志**：所有操作记录，具有防篡改存储

### 速率限制
- API 速率限制：每个商户每分钟 1000 次请求
- 影子部署速率：最多 10% 的流量
- 警报生成速率限制：防止警报风暴

---

## 可扩展性和性能

### 性能目标

| 指标 | 目标 | 当前能力 |
|------|------|----------|
| 警报检测延迟 | < 1 秒 | 亚秒级 |
| AI 分析时间 | < 5 秒 | 2-3 秒 |
| 规则部署时间 | < 30 秒 | 15-20 秒 |
| 仪表板加载时间 | < 2 秒 | 1.5 秒 |
| API 响应时间 (p95) | < 500ms | 200-300ms |
| 交易处理 | 10,000 TPS | 可扩展至 50,000 TPS |

### 扩展策略

#### 水平扩展
- **API 服务**：基于请求率自动扩展
- **ML 推理**：专用 GPU 实例，具有自动扩展
- **Kafka 消费者**：基于分区的扩展

#### 垂直扩展
- **数据库**：在高峰负载时使用更大的实例类型
- **缓存**：为热数据增加内存

#### 数据分区
- **基于时间的分区**：交易数据按月分区
- **基于商户的分区**：将大型商户分布在分片上
- **地理分区**：区域数据隔离

---

## 监控和可观测性

### 指标收集

#### 业务指标
- 警报生成率
- 误报率
- 规则部署成功率
- 商户参与率
- 欺诈损失减少

#### 技术指标
- API 延迟（p50、p95、p99）
- 按端点的错误率
- ML 模型推理时间
- 数据库查询性能
- 缓存命中率
- 队列深度

### 警报规则

```yaml
alerts:
  - name: 高警报失败率
    condition: alert_failure_rate > 5%
    severity: critical
    notification: PagerDuty

  - name: ML推理慢
    condition: ml_inference_time_p95 > 10s
    severity: warning
    notification: Slack

  - name: 数据库连接池耗尽
    condition: db_connection_usage > 90%
    severity: critical
    notification: PagerDuty
```

### 仪表板

1. **Sentinel 概览仪表板**
   - 按优先级的活动警报
   - 规则部署状态
   - 商户参与指标
   - 防止的欺诈损失

2. **系统健康仪表板**
   - 服务可用性
   - API 性能
   - 资源利用率
   - 错误率

3. **ML 性能仪表板**
   - 模型准确性指标
   - 推理延迟
   - 模型漂移检测
   - 训练作业状态

---

## 实施路线图

### 第一阶段：MVP（2025 Q4）

**目标：**
- 推出具有基本欺诈检测功能的 Sentinel 核心
- 实现一键规则部署
- 支持卡测试和速率攻击检测

**交付物：**
- [ ] 警报检测引擎
- [ ] AI 分析模块（基础）
- [ ] 规则部署引擎
- [ ] 商户仪表板
- [ ] 通知服务
- [ ] 与现有风险引擎集成

**时间线：** 3 个月

---

### 第二阶段：自动化平台（2026 Q1）

**目标：**
- 推出规则自动生成
- 实现自动退役
- 添加回测功能

**交付物：**
- [ ] 规则自动生成服务
- [ ] 规则治理服务
- [ ] 回测服务
- [ ] 模型训练管道
- [ ] 特征存储

**时间线：** 3 个月

---

### 第三阶段：高级功能（2026 Q2）

**目标：**
- 自动开启缓解模式
- 高级 ML 模型
- 多攻击向量支持

**交付物：**
- [ ] 自动开启部署
- [ ] 账户接管检测
- [ ] 拒付欺诈检测
- [ ] 高级分析仪表板
- [ ] 商户 API 用于自定义集成

**时间线：** 3 个月

---

### 第四阶段：优化与扩展（2026 Q3）

**目标：**
- 优化规模
- 全球扩展
- 高级自动化

**交付物：**
- [ ] 多区域部署
- [ ] 策略自动化（模型 + 规则握手）
- [ ] AI 驱动的特征生成
- [ ] 自我修复规则
- [ ] 高级报告

**时间线：** 3 个月

---

## 附录

### A. 术语表

- **P1/P2/P3 警报**：欺诈警报的优先级级别
- **影子模式**：在实时流量上测试规则而不影响交易
- **软标签**：用于训练数据的概率标签
- **冠军/挑战者**：模型/规则的 A/B 测试模式
- **BIN**：银行识别号码（卡号的前 6 位数字）

### B. 参考文献

- Airwallex Sentinel PRD
- PA 欺诈解决方案自动化全景
- 风险引擎 2.0 架构
- ML 平台设计文档

### C. 待解决问题

1. 如何处理 Sentinel 和现有风险引擎规则之间的规则冲突？
2. 如果 AI 分析服务宕机，回退策略是什么？
3. 如何大规模处理商户特定的自定义？
4. 原始交易数据的数据保留策略是什么？

---

**文档状态：** 审查草案
**下次审查日期：** 2025年11月30日
**批准人：** 产品、工程、ML 团队负责人
