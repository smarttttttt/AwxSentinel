# Airwallex Sentinel - Technical Design Document

**Version:** 1.0
**Date:** November 14, 2025
**Author:** Technical Architecture Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Core Components](#core-components)
4. [Data Flow and Processing Pipeline](#data-flow-and-processing-pipeline)
5. [API Design](#api-design)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Security and Compliance](#security-and-compliance)
9. [Scalability and Performance](#scalability-and-performance)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

This document outlines the technical design for **Airwallex Sentinel**, an AI-powered fraud prevention platform that combines real-time fraud detection, automated rule generation, and intelligent risk mitigation strategies. The system integrates two major components:

1. **Sentinel Core**: Customer-facing fraud prevention product with one-click and auto-on mitigation
2. **Automation Platform**: Backend infrastructure for model training, rule generation, and system optimization

### Key Design Principles

- **Real-time Processing**: Sub-second latency for fraud detection and rule execution
- **AI-First Architecture**: ML models at the core of decision-making
- **Scalability**: Handle millions of transactions per day
- **Automation**: Minimize manual intervention through intelligent automation
- **Flexibility**: Support multiple fraud attack vectors and mitigation strategies

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Merchant Portal Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Dashboard   │  │ Notifications │  │  Rule Management     │  │
│  │    UI        │  │   (SMS/Email) │  │      Interface       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway & BFF Layer                     │
│         Authentication │ Rate Limiting │ Load Balancing          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Sentinel   │    │   Automation     │    │  Risk Engine   │
│     Core     │◄──►│    Platform      │◄──►│   (Existing)   │
│   Services   │    │                  │    │                │
└──────────────┘    └──────────────────┘    └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data & ML Platform                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Feature │  │  Model   │  │  Training│  │  Real-time    │  │
│  │   Store  │  │  Serving │  │ Pipeline │  │  Analytics    │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage & Data Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │PostgreSQL│  │  Redis   │  │BigQuery  │  │  Time-series  │  │
│  │  (OLTP)  │  │  Cache   │  │  (OLAP)  │  │  DB (Metrics) │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Sentinel Core Services

#### 1.1 Alert Detection Engine

**Purpose**: Real-time monitoring of transaction patterns to detect potential fraud attacks

**Key Components**:
- **Metric Monitor**: Continuously tracks key metrics (block rate, auth failure rate, transaction volume)
- **Threshold Manager**: Configurable P1/P2 alert thresholds
- **Alert Generator**: Creates structured alerts with metadata

**Implementation**:
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

**Technology**:
- Apache Kafka for transaction stream processing
- Apache Flink for real-time metric computation
- Redis for sliding window calculations

---

#### 1.2 AI Analysis Module (Sentinel Agent)

**Purpose**: Analyze alerts using ML models to classify attack types and recommend actions

**Key Capabilities**:
- **Behavioral Analysis**: Clustering transactions by suspicious attributes
- **Pattern Recognition**: Identify fraud typologies (Card Testing, Velocity, etc.)
- **Data Integrity Check**: Detect anomalies in transaction data
- **Leakage Analysis**: Find transactions that bypassed rules but failed at issuer

**ML Pipeline**:
```
Transaction Data → Feature Engineering → Model Inference →
Structured Analysis (JSON) → Recommended Action
```

**Models Used**:
- XGBoost for classification
- DBSCAN/K-Means for clustering
- Isolation Forest for anomaly detection
- NLP models for email/domain analysis

**Output Format**:
```json
{
  "alert_id": "ALT-20251114-001",
  "conclusion": "Card Testing Attack Detected",
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

#### 1.3 Rule Deployment Engine

**Purpose**: Translate AI recommendations into executable rules and deploy them

**Architecture**:
```
AI Recommendation → Rule Translator → Rule Validator →
Shadow Deployment → Performance Monitor → Live Deployment
```

**Deployment Modes**:
- **One-Click Mode**: Merchant approves before deployment
- **Auto-On Mode**: Automatic deployment for high-confidence attacks

**Rule Translation Logic**:
```python
class RuleDeploymentEngine:
    async def deploy_rule(self, suggestion, mode='one_click'):
        # Translate AI suggestion to rule format
        rule = self.rule_translator.translate(suggestion)

        # Validate rule syntax and conflicts
        await self.rule_validator.validate(rule)

        # Deploy to shadow mode first
        shadow_id = await self.deploy_to_shadow(rule)

        if mode == 'auto_on' and suggestion['confidence_score'] > 0.9:
            # Auto-deploy after shadow validation
            await self.auto_deploy_to_live(shadow_id)
        else:
            # Wait for merchant approval
            await self.wait_for_approval(shadow_id)
```

---

#### 1.4 Notification Service

**Purpose**: Multi-channel alert delivery to merchants

**Channels**:
- In-app notifications
- Email alerts
- SMS (for P1 alerts)
- Webhook callbacks

**Priority Handling**:
- P1 alerts: Immediate delivery across all channels
- P2 alerts: In-app + email
- P3 alerts: In-app only

**Implementation**:
- Message queue (RabbitMQ/AWS SQS) for reliable delivery
- Template engine for customizable notifications
- Retry mechanism with exponential backoff

---

### 2. Automation Platform

#### 2.1 Model Training Pipeline

**Purpose**: Continuous model improvement through automated training

**Workflow**:
```
Data Collection → Feature Engineering → Model Training →
Model Validation → Model Registration → A/B Testing → Deployment
```

**Components**:
- **Data Preparation Service**: Unified training data pipeline
- **Feature Store**: Centralized feature repository
- **Model Registry**: Version control for ML models
- **Experiment Tracker**: MLflow for tracking experiments

**Refresh Cadence**:
- Routine refresh: Daily incremental learning
- On-demand refresh: Triggered by performance degradation
- Smart refresh: Triggered by significant pattern changes

---

#### 2.2 Rule Auto-Generation Service

**Purpose**: Automated rule creation using ML

**Use Cases**:
1. **Segment-level rules**: Regional, industry-specific
2. **Merchant-level rules**: Custom rules for individual merchants
3. **Attack-pattern rules**: Rules for known attack patterns

**Algorithm Selection**:
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

#### 2.3 Rule Governance Service

**Purpose**: Manage rule lifecycle (monitoring, retirement, refinement)

**Features**:
- **Auto-retirement**: Remove underperforming rules
- **Auto-refinement**: Optimize rule parameters
- **Conflict detection**: Identify rule conflicts
- **Performance tracking**: Monitor rule effectiveness

**Rule Retirement Workflow**:
```
Weekly Performance Review → Flag Low-performing Rules →
Notify Rule Owner → Grace Period (2 weeks) → Auto-retire
```

---

#### 2.4 Backtesting Service

**Purpose**: Simulate rule performance on historical data

**Capabilities**:
- Historical data replay
- Rule performance simulation
- Impact analysis
- A/B test simulation

**Implementation**:
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

### 3. Risk Engine Integration

**Purpose**: Interface with existing risk engine for rule execution

**Integration Points**:
- Rule synchronization (offline → online)
- Transaction scoring
- Action execution (BLOCK, CHALLENGE, ALLOW)
- Performance feedback

---

## Data Flow and Processing Pipeline

### Real-time Fraud Detection Flow

```
1. Transaction Event
   ↓
2. Feature Extraction (Real-time)
   ↓
3. Metric Calculation (Sliding Windows)
   ↓
4. Threshold Check
   ↓
5. Alert Generation (if threshold breached)
   ↓
6. AI Analysis
   ↓
7. Rule Recommendation
   ↓
8. Notification Delivery
   ↓
9. Merchant Action / Auto-deployment
   ↓
10. Rule Execution
   ↓
11. Performance Monitoring
```

### Batch Processing Flow

```
1. Daily Data Collection
   ↓
2. Feature Engineering
   ↓
3. Model Training / Rule Generation
   ↓
4. Model Validation
   ↓
5. Shadow Deployment
   ↓
6. A/B Testing
   ↓
7. Production Deployment
```

---

## API Design

### 1. Sentinel Core APIs

#### Get Alerts
```http
GET /api/v1/sentinel/alerts
Authorization: Bearer {token}

Query Parameters:
- status: pending|acknowledged|resolved
- priority: P1|P2|P3
- start_date: ISO8601
- end_date: ISO8601
- limit: int (default: 50)
- offset: int (default: 0)

Response:
{
  "alerts": [
    {
      "id": "ALT-20251114-001",
      "category": "card_testing",
      "priority": "P1",
      "created_at": "2025-11-14T10:30:00Z",
      "status": "pending",
      "summary": {
        "conclusion": "Card Testing Attack Detected",
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

#### Deploy Rule (One-Click)
```http
POST /api/v1/sentinel/rules/deploy
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "alert_id": "ALT-20251114-001",
  "deployment_mode": "shadow|live",
  "confirmation": true
}

Response:
{
  "rule_id": "RULE-20251114-001",
  "status": "deploying",
  "estimated_completion": "2025-11-14T10:35:00Z"
}
```

#### Submit Feedback
```http
POST /api/v1/sentinel/alerts/{alert_id}/feedback
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "helpful": true,
  "comment": "Accurate detection, rule worked well"
}

Response:
{
  "success": true,
  "message": "Feedback recorded"
}
```

---

### 2. Automation Platform APIs

#### Generate Rules
```http
POST /api/v1/automation/rules/generate
Authorization: Bearer {token}
Content-Type: application/json

Request:
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

Response:
{
  "job_id": "JOB-20251114-001",
  "status": "queued",
  "estimated_completion": "2025-11-14T12:00:00Z"
}
```

#### Run Backtest
```http
POST /api/v1/automation/backtest
Authorization: Bearer {token}
Content-Type: application/json

Request:
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

Response:
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

## Technology Stack

### Backend Services
- **Language**: Python 3.11+ (FastAPI/Django), Go (for high-performance services)
- **API Framework**: FastAPI, gRPC for internal services
- **Task Queue**: Celery with Redis/RabbitMQ
- **Caching**: Redis Cluster
- **Message Broker**: Apache Kafka

### Data & ML Platform
- **ML Framework**: scikit-learn, XGBoost, TensorFlow
- **Feature Store**: Feast or custom solution
- **Model Serving**: TensorFlow Serving, Seldon Core
- **Experiment Tracking**: MLflow
- **Data Processing**: Apache Spark, Apache Flink
- **Workflow Orchestration**: Apache Airflow

### Storage
- **OLTP Database**: PostgreSQL 15+ (with partitioning)
- **OLAP Database**: Google BigQuery
- **Time-series DB**: InfluxDB or TimescaleDB
- **Object Storage**: AWS S3 or GCS
- **Cache**: Redis Cluster

### Frontend
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit or Zustand
- **UI Library**: Material-UI or Ant Design
- **Charting**: Recharts or D3.js
- **Real-time Updates**: WebSocket or Server-Sent Events

### DevOps & Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions, ArgoCD
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger or Zipkin
- **Cloud Provider**: AWS or GCP

---

## Deployment Architecture

### Production Environment

```
┌────────────────────────────────────────────────────────────┐
│                        CDN Layer                            │
│                     (CloudFront/CloudFlare)                 │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   Load Balancer (ALB/NLB)                   │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│  API Gateway │    │   Web Servers    │    │  WebSocket     │
│  Cluster     │    │    (React)       │    │   Service      │
│ (3+ nodes)   │    │  (3+ nodes)      │    │  (2+ nodes)    │
└──────────────┘    └──────────────────┘    └────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Multi-AZ)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Sentinel   │  │  Automation  │  │  ML Inference    │ │
│  │   Services   │  │   Platform   │  │    Services      │ │
│  │ (Deployment) │  │ (StatefulSet)│  │  (Deployment)    │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    Data Layer (Multi-AZ)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  PostgreSQL  │  │  Redis       │  │  Kafka           │ │
│  │   Primary    │  │  Cluster     │  │  Cluster         │ │
│  │  + Replicas  │  │ (6 nodes)    │  │ (3 brokers)      │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### High Availability Configuration

- **Multi-AZ Deployment**: Services deployed across 3 availability zones
- **Auto-scaling**: Horizontal pod autoscaling based on CPU/memory/custom metrics
- **Database**: Primary-replica setup with automatic failover
- **Cache**: Redis cluster with sentinel for automatic failover
- **Message Queue**: Kafka cluster with replication factor 3

---

## Security and Compliance

### Authentication & Authorization
- **Merchant Authentication**: OAuth 2.0 / JWT tokens
- **Service-to-Service**: mTLS with certificate rotation
- **API Keys**: For webhook callbacks
- **Role-Based Access Control (RBAC)**: Fine-grained permissions

### Data Security
- **Encryption at Rest**: AES-256 for all databases
- **Encryption in Transit**: TLS 1.3 for all communications
- **PII Protection**: Tokenization of sensitive card data
- **Data Retention**: Configurable retention policies per data type

### Compliance
- **PCI DSS**: Level 1 compliance for card data handling
- **GDPR**: Right to erasure, data portability
- **SOC 2**: Type II certification
- **Audit Logging**: All actions logged with tamper-proof storage

### Rate Limiting
- API rate limits: 1000 requests/minute per merchant
- Shadow deployment rate: Max 10% of traffic
- Alert generation rate limit: Prevent alert storms

---

## Scalability and Performance

### Performance Targets

| Metric | Target | Current Capability |
|--------|--------|-------------------|
| Alert Detection Latency | < 1 second | Sub-second |
| AI Analysis Time | < 5 seconds | 2-3 seconds |
| Rule Deployment Time | < 30 seconds | 15-20 seconds |
| Dashboard Load Time | < 2 seconds | 1.5 seconds |
| API Response Time (p95) | < 500ms | 200-300ms |
| Transaction Processing | 10,000 TPS | Scalable to 50,000 TPS |

### Scaling Strategies

#### Horizontal Scaling
- **API Services**: Auto-scale based on request rate
- **ML Inference**: Dedicated GPU instances with auto-scaling
- **Kafka Consumers**: Partition-based scaling

#### Vertical Scaling
- **Database**: Use larger instance types for peak loads
- **Cache**: Increase memory for hot data

#### Data Partitioning
- **Time-based Partitioning**: Transaction data partitioned by month
- **Merchant-based Partitioning**: Distribute large merchants across shards
- **Geographic Partitioning**: Regional data isolation

---

## Monitoring and Observability

### Metrics Collection

#### Business Metrics
- Alert generation rate
- False positive rate
- Rule deployment success rate
- Merchant engagement rate
- Fraud loss reduction

#### Technical Metrics
- API latency (p50, p95, p99)
- Error rates by endpoint
- ML model inference time
- Database query performance
- Cache hit ratio
- Queue depth

### Alerting Rules

```yaml
alerts:
  - name: HighAlertFailureRate
    condition: alert_failure_rate > 5%
    severity: critical
    notification: PagerDuty

  - name: SlowMLInference
    condition: ml_inference_time_p95 > 10s
    severity: warning
    notification: Slack

  - name: DatabaseConnectionPoolExhausted
    condition: db_connection_usage > 90%
    severity: critical
    notification: PagerDuty
```

### Dashboards

1. **Sentinel Overview Dashboard**
   - Active alerts by priority
   - Rule deployment status
   - Merchant engagement metrics
   - Fraud loss prevented

2. **System Health Dashboard**
   - Service availability
   - API performance
   - Resource utilization
   - Error rates

3. **ML Performance Dashboard**
   - Model accuracy metrics
   - Inference latency
   - Model drift detection
   - Training job status

---

## Implementation Roadmap

### Phase 1: MVP (Q4 2025)

**Goals:**
- Launch Sentinel Core with basic fraud detection
- Implement one-click rule deployment
- Support card testing and velocity attack detection

**Deliverables:**
- [ ] Alert Detection Engine
- [ ] AI Analysis Module (basic)
- [ ] Rule Deployment Engine
- [ ] Merchant Dashboard
- [ ] Notification Service
- [ ] Integration with existing Risk Engine

**Timeline:** 3 months

---

### Phase 2: Automation Platform (Q1 2026)

**Goals:**
- Launch rule auto-generation
- Implement auto-retirement
- Add backtesting capabilities

**Deliverables:**
- [ ] Rule Auto-Generation Service
- [ ] Rule Governance Service
- [ ] Backtesting Service
- [ ] Model Training Pipeline
- [ ] Feature Store

**Timeline:** 3 months

---

### Phase 3: Advanced Features (Q2 2026)

**Goals:**
- Auto-On mitigation mode
- Advanced ML models
- Multi-attack vector support

**Deliverables:**
- [ ] Auto-On Deployment
- [ ] Account Takeover Detection
- [ ] Chargeback Fraud Detection
- [ ] Advanced Analytics Dashboard
- [ ] Merchant API for custom integrations

**Timeline:** 3 months

---

### Phase 4: Optimization & Scale (Q3 2026)

**Goals:**
- Optimize for scale
- Global expansion
- Advanced automation

**Deliverables:**
- [ ] Multi-region deployment
- [ ] Strategy automation (model + rule handshake)
- [ ] AI-powered feature generation
- [ ] Self-healing rules
- [ ] Advanced reporting

**Timeline:** 3 months

---

## Appendix

### A. Glossary

- **P1/P2/P3 Alerts**: Priority levels for fraud alerts
- **Shadow Mode**: Testing rules on live traffic without affecting transactions
- **Soft Label**: Probabilistic labels for training data
- **Champion/Challenger**: A/B testing pattern for models/rules
- **BIN**: Bank Identification Number (first 6 digits of card)

### B. References

- Airwallex Sentinel PRD
- PA Fraud Solution Automation Landscape
- Risk Engine 2.0 Architecture
- ML Platform Design Docs

### C. Open Questions

1. How to handle rule conflicts between Sentinel and existing risk engine rules?
2. What's the fallback strategy if AI analysis service is down?
3. How to handle merchant-specific customizations at scale?
4. What's the data retention policy for raw transaction data?

---

**Document Status:** Draft for Review
**Next Review Date:** November 30, 2025
**Approvers:** Product, Engineering, ML Team Leads
