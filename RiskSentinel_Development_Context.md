# Risk Sentinel 项目开发上下文

**最后更新**: 2025-12-10
**项目仓库**: https://gitlab.awx.im/awx-platform/ml-platform/risk-sentinel
**当前分支**: feature/AR-7572-build-project
**MR 链接**: https://gitlab.awx.im/awx-platform/ml-platform/risk-sentinel/-/merge_requests/1

---

## 1. 项目概述

### 1.1 系统简介

Risk Sentinel Alert System 是 Airwallex Sentinel 的核心模块之一，负责：
- 接收来自外部风险检测系统的 Metric 数据
- 通过 AI Agent 生成智能告警摘要
- 通过多渠道（Slack、Webapp、SMS）通知商户
- 支持灵活的频率控制和触发条件配置

### 1.2 核心功能

| 功能 | 描述 |
|------|------|
| 智能告警生成 | 基于外部 Metrics 通过 AI Agent 生成人类可读的告警摘要 |
| 多渠道通知 | 支持 Slack、Webapp、SMS 三种通知渠道 |
| 频率控制 | 支持商户和时间维度的频率限制配置 |
| 灵活触发条件 | 基于外部 Metrics 的可配置触发规则 |
| 告警管理 | 提供告警列表和详情页面供商户查看和管理 |

### 1.3 技术栈

- **语言**: Kotlin 1.9.23
- **框架**: Spring Boot 3.x
- **数据库**: PostgreSQL + Flyway
- **缓存**: Redis
- **消息队列**: Kafka
- **Web 服务器**: Jetty
- **构建工具**: Gradle 7.x (Kotlin DSL)
- **触发引擎**: Prometheus + Alertmanager

---

## 2. 项目结构

### 2.1 模块划分

```
risk-sentinel/
├── risk-sentinel-domain/        # 领域层（核心业务模型）
├── risk-sentinel-sdk/           # SDK 层（客户端、配置、数据模型）
├── risk-sentinel-persistence/   # 持久化层（Entity、Repository、Flyway）
└── risk-sentinel-start/         # 启动层（Controller、Service、Application）
```

### 2.2 参考项目

项目结构和代码规范参考 `risk-common-attribute-layer`：
- Entity 使用 Spring Data JDBC 注解
- Repository 继承 `CrudRepository`
- Flyway 脚本放在 `persistence` 模块

---

## 3. 数据模型

### 3.1 ER 图

```mermaid
erDiagram
    ALERT ||--o{ ALERT_DYNAMIC : "has"
    ALERT ||--o{ ALERT_RELATIONSHIP : "has"
    ALERT ||--o{ NOTIFICATION : "generates"
    ALERT ||--o{ ALERT_COMMENT : "has"
    ALERT ||--o{ ALERT_TRIGGER_LOG : "triggered_by"
    ALERT }o--|| ALERT_TEMPLATE : "uses"
    ALERT_COMMENT ||--o{ NOTIFICATION : "triggers"

    ALERT {
        uuid id PK
        string alert_type
        string original_severity
        string title
        text summary
        json suggested_action
        uuid template_id FK
        string condition_fingerprint
        json metrics_data
        json metadata
        string namespace
        string checkpoint
        string created_by
        string updated_by
        timestamp created_at
        timestamp updated_at
    }

    ALERT_DYNAMIC {
        uuid id PK
        uuid alert_id FK
        string current_severity
        string status
        int occurrence_count
        timestamp session_started_at
        timestamp session_last_active
        string session_status
        timestamp first_triggered_at
        timestamp last_triggered_at
        json escalation_history
        timestamp last_escalated_at
        timestamp resolved_at
        timestamp last_notified_at
        timestamp updated_at
    }

    ALERT_TRIGGER_LOG {
        uuid id PK
        uuid alert_id FK
        string condition_fingerprint
        string alert_name
        string alert_type
        string status
        string severity
        json metrics_data
        string namespace
        string checkpoint
        timestamp created_at
    }

    ALERT_RELATIONSHIP {
        uuid id PK
        uuid alert_id FK
        string account_id
        string account_type
        string slack_channel
        string slack_bot
        json metadata
        string namespace
        string checkpoint
        timestamp created_at
    }

    ALERT_COMMENT {
        uuid id PK
        uuid alert_id FK
        string comment_type
        text content
        json metrics_snapshot
        json metadata
        string created_by
        string namespace
        string checkpoint
        timestamp created_at
    }

    ALERT_TEMPLATE {
        uuid id PK
        string template_name
        string alert_type
        text prompt_template
        json default_config
        boolean is_active
        int version
        string namespace
        string checkpoint
        timestamp created_at
        timestamp updated_at
    }

    NOTIFICATION {
        uuid id PK
        uuid alert_id FK
        uuid comment_id FK
        string channel_type
        string status
        text content
        json metadata
        timestamp sent_at
        timestamp delivered_at
        timestamp failed_at
        text error_message
        int retry_count
        string namespace
        string checkpoint
    }

    ALERT_CONFIG {
        uuid id PK
        string account_id
        string alert_type
        boolean enabled
        json channel_preferences
        json notification_settings
        string namespace
        string checkpoint
        timestamp created_at
        timestamp updated_at
    }
```

### 3.2 表说明

| 表名 | 说明 |
|------|------|
| `alert_template` | AI Prompt 模板，用于生成告警摘要 |
| `alert` | 核心告警实体，存储 AI 生成的摘要内容 |
| `alert_dynamic` | 告警动态字段（状态、会话、升级），分离以提高写入性能 |
| `alert_relationship` | 告警与商户账户、通知渠道的关联 |
| `alert_comment` | 告警评论/事件记录（触发事件、用户备注、系统日志） |
| `alert_trigger_log` | Prometheus 触发原始日志，用于审计和分析 |
| `notification` | 通知记录，支持多渠道 |
| `alert_config` | 商户级别的告警配置和通知偏好 |

---

## 4. 开发进度

### 4.1 已完成

| 阶段 | 内容 | 完成日期 |
|------|------|----------|
| 项目骨架 | 多模块项目结构、CI/CD、Docker 配置 | 2025-11 |
| Flyway 迁移脚本 | `V1_0_0__create_tables.sql`（8 张表） | 2025-12-10 |
| Entity 类 | 8 个实体类 + 7 个枚举类 | 2025-12-10 |
| Repository 接口 | 8 个 Spring Data JDBC Repository | 2025-12-10 |

### 4.2 待开发（TDD 分步计划）

| 阶段 | 内容 | 优先级 | 状态 |
|------|------|--------|------|
| Phase 2 | Trigger Condition Engine（条件评估引擎） | P0 | 待开发 |
| Phase 4 | Alert Service 核心业务（创建、聚合、升级） | P0 | 待开发 |
| Phase 5 | Frequency Control 频控服务 | P1 | 待开发 |
| Phase 6 | AI Agent 服务（LLM 集成） | P1 | 待开发 |
| Phase 7 | Notification Service 通知服务 | P1 | 待开发 |
| Phase 8 | REST API 层 | P1 | 待开发 |
| Phase 9 | 集成与端到端测试 | P2 | 待开发 |

---

## 5. 关键设计决策

### 5.1 Trigger Engine 选择 Prometheus

**原因**：
- 多数据源支持（REST API、BigQuery、Kafka 等）
- PromQL 支持复杂条件逻辑、时间窗口聚合、异常检测
- 成熟稳定，生态完善
- 可水平扩展

**数据流**：
```
Prometheus 触发 → Alertmanager → Webhook → Sentinel Alert System
```

### 5.2 Alert 聚合策略

采用**混合聚合策略**：

1. **Session-based 聚合**：触发间隔 < 15 分钟视为同一攻击会话
2. **滑动窗口**：24 小时内相同 fingerprint 的 Alert 聚合
3. **严重级别升级**：
   - `occurrence_count >= 10` → P2
   - `occurrence_count >= 50` → P1
   - 持续时间 >= 2 小时 → P1

### 5.3 Alert 与 Alert_Dynamic 分离

将频繁更新的字段（status、occurrence_count、session_last_active 等）分离到 `alert_dynamic` 表，减少对 `alert` 主表的写入压力。

---

## 6. 文件清单

### 6.1 Flyway 迁移脚本

```
risk-sentinel-persistence/src/main/resources/db/migration/
└── V1_0_0__create_tables.sql
```

### 6.2 Entity 类

```
risk-sentinel-persistence/src/main/kotlin/com/airwallex/risk/sentinel/persistence/entity/
├── Severity.kt                 # P0, P1, P2, P3
├── AlertStatus.kt              # ACTIVE, RESOLVED, DISMISSED
├── SessionStatus.kt            # ACTIVE, EXPIRED, RESOLVED
├── CommentType.kt              # TRIGGER_EVENT, SEVERITY_ESCALATION, USER_NOTE, SYSTEM_LOG
├── ChannelType.kt              # SLACK, SMS, WEBAPP
├── NotificationStatus.kt       # PENDING, SENDING, SENT, DELIVERED, FAILED
├── TriggerStatus.kt            # FIRING, RESOLVED
├── AlertTemplateEntity.kt
├── AlertEntity.kt
├── AlertDynamicEntity.kt
├── AlertRelationshipEntity.kt
├── AlertCommentEntity.kt
├── AlertTriggerLogEntity.kt
├── NotificationEntity.kt
└── AlertConfigEntity.kt
```

### 6.3 Repository 接口

```
risk-sentinel-persistence/src/main/kotlin/com/airwallex/risk/sentinel/persistence/repo/
├── AlertTemplateRepository.kt
├── AlertRepository.kt
├── AlertDynamicRepository.kt
├── AlertRelationshipRepository.kt
├── AlertCommentRepository.kt
├── AlertTriggerLogRepository.kt
├── NotificationRepository.kt
└── AlertConfigRepository.kt
```

---

## 7. 相关文档

### 7.1 文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 系统设计文档（英文） | `/Users/boyi.wang/Projects/AwxSentinel/AlertSystemDesign_EN.md` | 完整技术设计，含架构图、流程图、API 定义 |
| 系统设计文档（中文） | `/Users/boyi.wang/Projects/AwxSentinel/AlertSystemDesign_CN.md` | 英文文档的中文翻译版本 |
| Confluence 页面 | [Airwallex Sentinel Alert Service](https://airwallex.atlassian.net/wiki/spaces/AR/pages/4594368769) | 在线协作文档，包含最新讨论 |

---

### 7.2 AlertSystemDesign_EN.md 文档摘要

**文档版本**: v1.0 (2025-11-19)
**作者**: Boyi Wang

#### 核心章节结构

| 章节 | 内容 |
|------|------|
| **1. Overview** | 系统简介、核心功能 |
| **2. System Architecture** | 整体架构图、分层说明 |
| **3. Core Workflows** | 告警生成流程、AI 摘要生成、频控、聚合策略、Prometheus 集成 |
| **4. Data Model** | ER 图、实体说明 |
| **5. API Design** | 告警接收、查询、配置、操作 API |
| **6. Notification Channel** | Slack、SMS、Webapp 配置 |
| **7. Technical Implementation** | AI Agent、频控、消息队列 |
| **8. Frontend Page Design** | 告警列表页、详情页 |
| **9. Monitoring and Logging** | 监控指标、告警规则、日志标准 |
| **10-14** | 安全、扩展性、部署、测试、发布计划 |

#### 关键架构图（Mermaid）

1. **整体架构图** - 展示外部系统、核心服务、数据层、通知渠道的关系
2. **告警生成序列图** - Metric Platform → API → Trigger Engine → AI Agent → DB → Notification
3. **AI 摘要生成流程** - 模板加载 → 上下文构建 → LLM 调用 → 响应解析
4. **频控流程** - Redis 计数器、滑动窗口、速率限制
5. **告警聚合流程** - Session-based 聚合、滑动窗口、严重级别升级
6. **Prometheus 集成架构** - Exporter → Prometheus → Alertmanager → Webhook

#### Trigger Engine 技术选型结论

| 方案 | 选择 | 理由 |
|------|------|------|
| Plan A: 复用 Rule Engine | ❌ 不推荐 | 过度工程化，只用到 5% 能力，依赖外部团队 |
| Plan B: 独立 Condition Flow | ✅ **推荐** | 简单高效，10-20x 性能提升，团队自治 |

---

### 7.3 Confluence 页面内容摘要

**页面**: [Airwallex Sentinel Alert Service](https://airwallex.atlassian.net/wiki/spaces/AR/pages/4594368769)

#### 主要内容

| 章节 | 内容 |
|------|------|
| **1. Background** | 系统简介、核心功能列表 |
| **2. Architecture** | 用户交互流程、系统架构图、告警生成流程图 |
| **3. Core Work Flow** | Trigger Engine（Prometheus）、Alert Gateway、聚合流程、AI Summary、频控 |
| **4. User Case** | Card Testing Alert、Max Ticket Size Alert、Issuing Alert |
| **5. Data Model** | ER 图、实体描述 |
| **6. API Design** | Alert Ingestion、Query、Configuration、Action API |
| **7. Notification Channel** | Slack、SMS、Webapp 配置要求 |

#### Prometheus 作为 Trigger Engine 的关键设计

**选择 Prometheus 的原因**:
- 多数据源支持（REST API、BigQuery、Kafka 等）
- PromQL 支持复杂条件逻辑（时间窗口聚合、异常检测）
- 成熟稳定，生态完善
- 可水平扩展

**PromQL 能力示例**:
```promql
# 简单阈值
block_rate > 0.3

# 多条件组合
A > 0.3 AND B > 0.5

# 时间窗口聚合
avg_over_time(metric[10m])

# 环比变化
metric / metric offset 1h

# 异常检测（3倍标准差）
(metric - avg) / stddev > 3
```

**Prometheus Rule 配置示例**:
```yaml
groups:
  - name: sentinel_alerts
    rules:
      - alert: CardTestingDetected
        expr: sentinel_block_rate > 0.2 AND sentinel_failed_auth_rate > 0.3
        for: 5m
        labels:
          alert_type: CARD_TESTING
          severity: P2
        annotations:
          summary: "Card testing attack detected"
          account_id: "{{ $labels.account_id }}"
```

**Alertmanager Webhook 数据结构**:
```kotlin
data class AlertmanagerPayload(
    val version: String,
    val groupKey: String,
    val status: String,  // "firing" | "resolved"
    val receiver: String,
    val groupLabels: Map<String, String>,
    val commonLabels: Map<String, String>,
    val commonAnnotations: Map<String, String>,
    val externalURL: String,
    val alerts: List<AlertmanagerAlert>
)

data class AlertmanagerAlert(
    val status: String,
    val labels: Map<String, String>,
    val annotations: Map<String, String>,
    val startsAt: String,
    val endsAt: String,
    val generatorURL: String,
    val fingerprint: String
)
```

#### AI Summary Prompt 模板示例

```
You are a fraud detection expert analyzing payment metrics for merchant {{merchant_name}}.

Metrics Data:
{{metrics_data}}

Historical Context:
{{historical_alerts}}

Please analyze the above metrics and provide:
1. A concise title (max 100 chars)
2. A summary of the potential fraud attack (max 300 words)
3. Severity level (P1/P2/P3)
4. Suggested immediate action

Format your response as JSON:
{
  "title": "...",
  "summary": "...",
  "severity": "...",
  "suggested_action": "..."
}
```

---

## 8. 开发规范

### 8.1 代码风格

- 参考 `risk-common-attribute-layer` 项目
- Entity 使用 `data class` + Spring Data JDBC 注解
- Repository 继承 `CrudRepository<Entity, UUID>`
- 使用 `Instant` 而非 `Date` 作为时间类型

### 8.2 Flyway 命名规范

```
V{主版本}_{次版本}_{修订版本}__{描述}.sql

示例：
V1_0_0__create_tables.sql
V1_0_1__add_column_xxx.sql
```

### 8.3 Git 提交规范

```
feat: 功能描述

详细说明...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 9. 常用命令

```bash
# 进入项目目录
cd /Users/boyi.wang/Projects/risk-sentinel

# 编译项目
./gradlew compileKotlin

# 运行测试
./gradlew test

# 构建
./gradlew build

# 本地启动（需要先启动 PostgreSQL）
./gradlew :risk-sentinel-start:bootRun
```

---

## 10. 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2025-12-10 | 创建文档；完成 Flyway 迁移脚本、Entity、Repository |
| 2025-12-10 | 补充引用文档摘要：AlertSystemDesign_EN.md、Confluence 页面内容 |
