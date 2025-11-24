# Airwallex Sentinel - Alert系统技术设计文档

**作者：** Boyi Wang
**日期：** 2025年11月19日
**版本：** 1.0

---

## 1. 概述

### 1.1 文档目的
本文档描述Airwallex Sentinel系统中Alert（警报）模块的技术设计，包括系统架构、数据流程、实体模型和API接口定义。

### 1.2 系统简介
Alert系统是Sentinel的核心模块之一，负责接收外部风险检测系统的指标数据（Metrics），通过AI Agent生成智能化的警报摘要，并通过多种渠道（Slack、Webapp、SMS）通知商户。系统支持灵活的频率控制和触发条件配置。

### 1.3 核心功能
- **智能警报生成**：基于外部Metrics通过AI Agent生成人类可读的警报摘要
- **多渠道通知**：支持Slack、Webapp、SMS三种通知渠道
- **频率控制**：支持商户维度和时间维度的频率限制配置
- **灵活触发条件**：基于外部Metrics的可配置触发规则
- **警报管理**：提供Alert List和Alert Detail页面供商户查看和管理

---

## 2. 系统架构

### 2.1 整体架构图

```mermaid
graph TB
    subgraph "外部系统"
        MS[Metric Platform<br/>指标监控平台]
        RS[Risk Engine<br/>风险引擎]
    end

    subgraph "Alert核心系统"
        subgraph "接入层"
            API[Alert API Gateway<br/>API网关]
        end

        subgraph "业务逻辑层"
            TC[Trigger Condition Engine<br/>触发条件引擎]
            FC[Frequency Control Service<br/>频率控制服务]
            AG[AI Agent Service<br/>AI代理服务]
            AS[Alert Service<br/>警报服务]
            NS[Notification Service<br/>通知服务]
        end

        subgraph "数据层"
            PG[(PostgreSQL<br/>主数据库)]
            REDIS[(Redis<br/>缓存/频控)]
            MQ[Message Queue<br/>消息队列]
        end
    end

    subgraph "通知渠道"
        SLACK[Slack API]
        SMS[SMS Gateway]
        WEB[Webapp Notification]
    end

    subgraph "AI服务"
        LLM[LLM Service<br/>Claude/GPT]
    end

    MS -->|发送Metrics| API
    RS -->|发送风险事件| API

    API -->|验证并路由| TC
    TC -->|检查触发条件| FC
    FC -->|通过频控| AS
    AS -->|请求生成摘要| AG
    AG -->|调用AI| LLM
    LLM -->|返回摘要| AG
    AG -->|返回警报内容| AS
    AS -->|保存警报| PG
    AS -->|发送通知任务| MQ
    MQ -->|消费任务| NS

    NS -->|发送消息| SLACK
    NS -->|发送短信| SMS
    NS -->|推送通知| WEB

    FC -.->|读写频控数据| REDIS
    AS -.->|缓存查询| REDIS

    style API fill:#e1f5ff
    style TC fill:#fff4e1
    style FC fill:#fff4e1
    style AG fill:#f0e1ff
    style AS fill:#fff4e1
    style NS fill:#e1ffe1
    style LLM fill:#ffe1e1
```

### 2.2 架构说明

#### 2.2.1 接入层
- **Alert API Gateway**：统一的API入口，负责请求验证、路由和限流

#### 2.2.2 业务逻辑层
- **Trigger Condition Engine**：评估外部Metrics是否满足警报触发条件
- **Frequency Control Service**：基于商户和时间维度的频率控制
- **AI Agent Service**：调用LLM生成警报摘要，管理Prompt模板
- **Alert Service**：核心警报业务逻辑，管理警报生命周期
- **Notification Service**：多渠道通知发送服务

#### 2.2.3 数据层
- **PostgreSQL**：存储警报、配置、历史记录等持久化数据
- **Redis**：缓存热数据，存储频率控制计数器
- **Message Queue (Kafka/RabbitMQ)**：异步处理通知任务

---

## 3. 核心流程

### 3.1 警报生成与通知流程

```mermaid
sequenceDiagram
    participant MP as Metric Platform
    participant API as Alert API
    participant TCE as Trigger Condition<br/>Engine
    participant FCS as Frequency Control<br/>Service
    participant AS as Alert Service
    participant AGS as AI Agent Service
    participant LLM as LLM Service
    participant DB as Database
    participant MQ as Message Queue
    participant NS as Notification Service
    participant CH as Channels<br/>(Slack/SMS/Web)

    MP->>API: POST /api/v1/alerts/metrics<br/>{merchantId, metrics, metadata}
    API->>API: 验证请求
    API->>TCE: 评估触发条件

    alt 不满足触发条件
        TCE->>API: 返回：不触发
        API->>MP: 200 OK (no alert)
    else 满足触发条件
        TCE->>FCS: 检查频率限制

        alt 超过频率限制
            FCS->>API: 返回：频率限制
            API->>MP: 429 Too Many Requests
        else 通过频率检查
            FCS->>FCS: 更新频控计数器
            FCS->>AS: 创建警报请求

            AS->>AGS: 请求生成AI摘要<br/>{metrics, promptTemplate}
            AGS->>AGS: 加载Prompt模板
            AGS->>LLM: 调用LLM API<br/>{prompt, metrics}
            LLM->>AGS: 返回AI生成摘要
            AGS->>AS: 返回警报内容

            AS->>DB: 保存警报记录
            DB->>AS: 返回alertId

            AS->>MQ: 发布通知任务<br/>{alertId, channels}
            AS->>API: 返回alertId
            API->>MP: 201 Created<br/>{alertId}

            MQ->>NS: 消费通知任务

            par 并行发送多渠道通知
                NS->>CH: 发送Slack通知
                NS->>CH: 发送SMS通知
                NS->>CH: 发送Webapp通知
            end

            NS->>DB: 更新通知状态
        end
    end
```

### 3.2 AI摘要生成流程

```mermaid
flowchart TD
    Start([接收Metrics数据]) --> LoadTemplate[加载Prompt模板]
    LoadTemplate --> BuildContext[构建上下文数据<br/>- 商户信息<br/>- 历史警报<br/>- Metrics数据]
    BuildContext --> RenderPrompt[渲染Prompt]
    RenderPrompt --> CallLLM[调用LLM API]

    CallLLM --> CheckResponse{响应成功?}
    CheckResponse -->|否| Retry{重试次数<3?}
    Retry -->|是| CallLLM
    Retry -->|否| UseFallback[使用默认摘要模板]

    CheckResponse -->|是| ParseResponse[解析AI响应]
    ParseResponse --> ValidateFormat{格式验证}
    ValidateFormat -->|失败| UseFallback
    ValidateFormat -->|成功| ExtractFields[提取字段<br/>- title<br/>- summary<br/>- severity<br/>- suggestedAction]

    UseFallback --> FormatOutput
    ExtractFields --> FormatOutput[格式化输出]
    FormatOutput --> CacheResult[缓存结果]
    CacheResult --> End([返回警报内容])

    style Start fill:#e1f5ff
    style End fill:#e1ffe1
    style CallLLM fill:#f0e1ff
    style UseFallback fill:#ffe1e1
```

### 3.3 频率控制流程

```mermaid
flowchart TD
    Start([收到警报请求]) --> GetConfig[获取频控配置<br/>商户级别配置<br/>全局配置]
    GetConfig --> BuildKey[构建频控Key<br/>格式: merchant:id:alert:type:window]

    BuildKey --> CheckRedis{Redis中存在计数器?}
    CheckRedis -->|否| InitCounter[初始化计数器<br/>count=0, ttl=窗口时长]
    CheckRedis -->|是| GetCount[获取当前计数]

    InitCounter --> IncrementCounter[递增计数器]
    GetCount --> CompareLimit{count >= 限制数量?}

    CompareLimit -->|是| CalcRetry[计算重试时间]
    CalcRetry --> LogBlock[记录频控日志]
    LogBlock --> ReturnBlock([返回: 拒绝<br/>Retry-After: X秒])

    CompareLimit -->|否| IncrementCounter
    IncrementCounter --> UpdateMeta[更新元数据<br/>lastAlertTime<br/>alertCount]
    UpdateMeta --> ReturnPass([返回: 通过])

    style Start fill:#e1f5ff
    style ReturnBlock fill:#ffe1e1
    style ReturnPass fill:#e1ffe1
```

### 3.4 用户侧交互流程

```mermaid
flowchart TD
    Start([攻击发生]) --> SystemDetect[系统检测到异常指标]
    SystemDetect --> AlertGen[系统生成警报]

    AlertGen --> Notify{用户接收通知}

    Notify -->|Slack| SlackMsg[Slack消息<br/>包含摘要和链接]
    Notify -->|SMS| SMSMsg[短信通知<br/>简短摘要+链接]
    Notify -->|Webapp| WebMsg[Web应用推送<br/>实时通知]

    SlackMsg --> UserSee[用户看到通知]
    SMSMsg --> UserSee
    WebMsg --> UserSee

    UserSee --> Decision1{用户选择}

    Decision1 -->|点击通知| OpenDetail[打开Alert详情页]
    Decision1 -->|稍后查看| GoToList[进入Alert列表页]
    Decision1 -->|忽略通知| End1([暂不处理])

    GoToList --> FilterSort[筛选和排序<br/>- 按类型筛选<br/>- 按严重程度<br/>- 按时间范围]
    FilterSort --> SelectAlert[选择特定警报]
    SelectAlert --> OpenDetail

    OpenDetail --> ViewDetails[查看详细信息<br/>- AI生成摘要<br/>- 攻击指标数据<br/>- 建议操作]

    ViewDetails --> Decision2{用户决策}

    Decision2 -->|同意建议| DeployRule[一键部署规则]
    Decision2 -->|需要更多信息| ViewMetrics[查看原始数据]
    Decision2 -->|误报| DismissAlert[忽略警报]
    Decision2 -->|自定义方案| ManualAction[手动创建规则]

    ViewMetrics --> Decision3{重新评估}
    Decision3 -->|确认攻击| DeployRule
    Decision3 -->|误报| DismissAlert

    DeployRule --> ConfirmModal[确认模态框<br/>显示规则影响]
    ConfirmModal --> Decision4{确认?}

    Decision4 -->|是| RuleDeployed[规则部署成功]
    Decision4 -->|否| ViewDetails

    RuleDeployed --> MarkResolved[自动标记为已解决]
    ManualAction --> MarkResolved

    MarkResolved --> ViewSuccess[查看成功反馈<br/>- 规则详情<br/>- 预计影响<br/>- 后续建议]

    ViewSuccess --> Decision5{继续操作?}
    Decision5 -->|查看其他警报| GoToList
    Decision5 -->|完成| Enjoy["读本书，享受美景"<br/>系统继续监控]

    DismissAlert --> AddReason[添加忽略原因<br/>- 误报<br/>- 正常业务<br/>- 其他]
    AddReason --> FeedbackSubmit[提交反馈<br/>帮助AI学习]
    FeedbackSubmit --> GoToList

    Enjoy --> MonitorContinue[系统持续监控]
    MonitorContinue --> NewAlert{检测到新攻击?}
    NewAlert -->|是| AlertGen
    NewAlert -->|否| MonitorContinue

    style Start fill:#ffe1e1
    style UserSee fill:#e1f5ff
    style DeployRule fill:#f0e1ff
    style RuleDeployed fill:#e1ffe1
    style MarkResolved fill:#e1ffe1
    style Enjoy fill:#e1ffe1
    style DismissAlert fill:#fff4e1
```

### 3.5 触发条件评估流程

```mermaid
flowchart TD
    Start([接收Metrics数据]) --> ExtractInfo[提取信息<br/>merchantId, alertType, metrics]
    ExtractInfo --> LoadConfig[加载触发条件配置<br/>从数据库获取]

    LoadConfig --> CheckConfigExists{配置存在且启用?}
    CheckConfigExists -->|否| NoTrigger1([返回: 不触发])
    CheckConfigExists -->|是| SortByPriority[按priority排序条件]

    SortByPriority --> InitEval[初始化评估结果列表]
    InitEval --> LoopConditions[遍历每个条件]

    LoopConditions --> GetCondition[获取条件<br/>metric_name, operator, threshold]
    GetCondition --> FindMetric[查找对应的Metric数据]

    FindMetric --> MetricFound{找到指标?}
    MetricFound -->|否| RecordNotMet[记录: 条件不满足<br/>原因: 指标缺失]
    MetricFound -->|是| EvalOperator[评估操作符<br/>支持: >, >=, <, <=, ==, !=]

    EvalOperator -->|满足| RecordMet[记录: 条件满足<br/>actual_value, threshold]
    EvalOperator -->|不满足| RecordNotMet

    RecordMet --> NextCondition{还有更多条件?}
    RecordNotMet --> NextCondition

    NextCondition -->|是| LoopConditions
    NextCondition -->|否| ApplyLogic[应用组合逻辑]

    ApplyLogic --> LogicType{逻辑类型?}

    LogicType -->|AND| CheckAND{所有条件都满足?}
    LogicType -->|OR| CheckOR{任一条件满足?}

    CheckAND -->|是| TriggerAlert[触发警报]
    CheckAND -->|否| NoTrigger2[不触发]

    CheckOR -->|是| TriggerAlert
    CheckOR -->|否| NoTrigger2

    TriggerAlert --> LogResult[记录评估日志<br/>条件详情、指标值]
    NoTrigger2 --> LogResult

    LogResult --> FinalDecision{最终决定?}
    FinalDecision -->|触发| ReturnTrigger([返回: 触发<br/>传递到频率控制])
    FinalDecision -->|不触发| ReturnNoTrigger([返回: 不触发<br/>附带评估详情])

    style Start fill:#e1f5ff
    style TriggerAlert fill:#e1ffe1
    style ReturnTrigger fill:#e1ffe1
    style NoTrigger2 fill:#ffe1e1
    style NoTrigger1 fill:#fff4e1
    style ReturnNoTrigger fill:#fff4e1
    style RecordMet fill:#d4edda
    style RecordNotMet fill:#f8d7da
```

### 3.6 Alert聚合流程

Alert系统采用**混合聚合策略**，结合会话式聚合、滑动窗口和严重程度递进，以更智能地处理欺诈攻击告警。

#### 3.6.1 聚合策略说明

**1. 会话式聚合（Session-based Aggregation）**
- **核心思想**：基于攻击活跃度动态判断是否属于同一次攻击
- **策略**：如果两次触发间隔 < session_timeout_minutes（默认15分钟）→ 认为是同一次攻击会话
- **优点**：更符合真实攻击场景（攻击通常是突发式的），自动区分多轮攻击

**2. 滑动窗口（Sliding Window）**
- **核心思想**：在固定时长内（如24小时）查找相同fingerprint的Alert
- **作用**：作为兜底机制，避免创建过多Alert
- **优点**：避免固定窗口的边界问题，提供更平滑的聚合效果

**3. 严重程度递进（Severity Escalation）**
- **核心思想**：同一攻击持续时间越长/次数越多，自动提升严重程度
- **策略**：
  - 触发次数达到10次 → 提升至P2
  - 触发次数达到50次 → 提升至P1
  - 持续时间超过2小时 → 提升至P1
- **优点**：自动识别严重攻击，提升响应优先级

#### 3.6.2 Alert聚合逻辑流程

```mermaid
flowchart TD
    Start([触发条件满足]) --> CalcFingerprint[计算Condition Fingerprint<br/>MD5哈希算法]
    CalcFingerprint --> CheckSession{检查活跃会话<br/>session_status=ACTIVE?<br/>last_active within timeout?}

    CheckSession -->|是| UpdateSession[更新会话<br/>session_last_active=now]
    CheckSession -->|否| ExpireOldSession[过期旧会话<br/>session_status=EXPIRED]

    ExpireOldSession --> CheckWindow{检查滑动窗口<br/>24h内有相同fingerprint?}

    CheckWindow -->|是| CreateNewSession[创建新会话<br/>关联到现有Alert]
    CheckWindow -->|否| CreateNewAlert[创建新Alert<br/>初始化所有字段]

    UpdateSession --> IncrementCount[递增occurrence_count<br/>更新last_triggered_at]
    CreateNewSession --> IncrementCount
    CreateNewAlert --> SetInitialValues[设置初始值<br/>occurrence_count=1<br/>original_severity]

    SetInitialValues --> CreateComment[创建Alert Comment<br/>type=TRIGGER_EVENT<br/>保存metrics_snapshot]
    IncrementCount --> CreateComment

    CreateComment --> CheckEscalation{需要提升严重程度?<br/>检查escalation规则}

    CheckEscalation -->|是| EscalateSeverity[提升current_severity<br/>记录escalation_history]
    CheckEscalation -->|否| DecideNotify{是否需要通知?}

    EscalateSeverity --> LogEscalation[记录提升事件]
    LogEscalation --> ForceNotify[标记:需要通知<br/>原因:严重程度提升]

    DecideNotify -->|是| NeedNotify[标记:需要通知]
    DecideNotify -->|否| NoNotify[标记:不通知<br/>原因:聚合中]

    ForceNotify --> SaveAlert[保存Alert到数据库]
    NeedNotify --> SaveAlert
    NoNotify --> SaveAlert

    SaveAlert --> End([流程结束<br/>输出:通知标记])

    style Start fill:#e1f5ff
    style CreateNewAlert fill:#fff4e1
    style UpdateSession fill:#fff4e1
    style EscalateSeverity fill:#ffe1e1
    style ForceNotify fill:#e1ffe1
    style NeedNotify fill:#e1ffe1
    style NoNotify fill:#fff4e1
    style End fill:#e8e8e8
```

#### 3.6.3 通知发送与频控流程

```mermaid
flowchart TD
    Start([接收Alert<br/>带通知标记]) --> CheckMark{需要发送通知?}

    CheckMark -->|否| Skip[跳过通知<br/>记录日志]
    CheckMark -->|是| CheckReason{通知原因?}

    CheckReason -->|严重程度提升| ForceNotify[强制通知模式]
    CheckReason -->|常规触发| EvalStrategy[评估通知策略]

    EvalStrategy --> StrategyType{通知策略类型?}

    StrategyType -->|首次触发| CheckFirst{是首次触发?<br/>occurrence_count==1}
    StrategyType -->|阈值触发| CheckThreshold{达到通知阈值?}
    StrategyType -->|间隔触发| CheckInterval{超过时间间隔?}

    CheckFirst -->|是| ShouldNotify[通过策略检查]
    CheckFirst -->|否| StrategySkip[策略拦截<br/>不发送通知]

    CheckThreshold -->|是| ShouldNotify
    CheckThreshold -->|否| StrategySkip

    CheckInterval -->|是| ShouldNotify
    CheckInterval -->|否| StrategySkip

    ForceNotify --> CreateTask[创建通知任务<br/>优先级:HIGH]
    ShouldNotify --> CreateTask

    CreateTask --> FreqControl[频率控制检查<br/>Redis计数器]
    FreqControl --> FreqCheck{通过频控?}

    FreqCheck -->|是| SendNotif[发送多渠道通知<br/>Slack/SMS/Webapp]
    FreqCheck -->|否| FreqSkip[频控拦截<br/>记录Retry-After]

    SendNotif --> UpdateStatus[更新通知状态<br/>last_notified_at]

    Skip --> End([结束])
    StrategySkip --> LogStrategy[记录策略拦截]
    LogStrategy --> End
    FreqSkip --> LogFreq[记录频控拦截]
    LogFreq --> End
    UpdateStatus --> End

    style Start fill:#e1f5ff
    style ForceNotify fill:#ffe1e1
    style ShouldNotify fill:#e1ffe1
    style SendNotif fill:#e1ffe1
    style StrategySkip fill:#fff4e1
    style FreqSkip fill:#fff4e1
    style End fill:#e8e8e8
```

#### 3.6.4 严重程度递进规则

系统会根据以下规则自动提升Alert的严重程度：

| 触发条件 | 提升至 | 说明 |
|---------|-------|------|
| occurrence_count >= 10 | P2 | 中等强度攻击 |
| occurrence_count >= 50 | P1 | 高强度攻击 |
| 持续时长 >= 2小时 | P1 | 持续性攻击 |
| 持续时长 >= 6小时 | P0 | 严重持续攻击 |

**Escalation History示例**：
```json
{
  "escalations": [
    {
      "from_severity": "P3",
      "to_severity": "P2",
      "reason": "occurrence_count_threshold",
      "occurrence_count": 10,
      "escalated_at": "2025-11-19T10:45:00Z"
    },
    {
      "from_severity": "P2",
      "to_severity": "P1",
      "reason": "occurrence_count_threshold",
      "occurrence_count": 50,
      "escalated_at": "2025-11-19T11:30:00Z"
    }
  ]
}
```

#### 3.6.5 会话管理

**会话状态流转**：
```
ACTIVE → EXPIRED → (可能重新激活为ACTIVE)
ACTIVE → RESOLVED (用户手动解决)
```

**会话超时配置**：
- 默认超时时间：15分钟
- 可按Alert类型配置不同的超时时间
- 例如：卡测试攻击建议15分钟，速率攻击建议30分钟

**会话重新激活**：
- 如果EXPIRED的会话在滑动窗口内再次被触发，可以创建新会话关联到同一Alert
- 这样可以追踪间歇性攻击模式

---

## 4. 数据模型

### 4.1 实体关系图 (ERD)

```mermaid
erDiagram
    MERCHANT ||--o{ ALERT : "receives"
    MERCHANT ||--o{ ALERT_CONFIG : "configures"
    MERCHANT ||--o{ FREQUENCY_CONTROL_CONFIG : "has"

    ALERT ||--o{ NOTIFICATION : "generates"
    ALERT ||--|{ ALERT_METRIC : "contains"
    ALERT }o--|| ALERT_TEMPLATE : "uses"

    NOTIFICATION }o--|| NOTIFICATION_CHANNEL : "sends_via"

    ALERT_CONFIG ||--o{ TRIGGER_CONDITION : "defines"

    MERCHANT {
        uuid id PK
        string merchant_code UK
        string name
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    ALERT {
        uuid id PK
        uuid merchant_id FK
        string alert_type
        string original_severity
        string current_severity
        string title
        text summary
        json suggested_action
        uuid template_id FK
        string status
        string condition_fingerprint
        int occurrence_count
        timestamp session_started_at
        timestamp session_last_active
        int session_timeout_minutes
        string session_status
        int aggregation_window_hours
        timestamp first_triggered_at
        timestamp last_triggered_at
        json escalation_history
        timestamp last_escalated_at
        timestamp resolved_at
        varchar namespace
        varchar checkpoint
        timestamp created_at
        timestamp updated_at
    }

    ALERT_METRIC {
        uuid id PK
        uuid alert_id FK
        string metric_name
        string metric_type
        decimal metric_value
        decimal threshold_value
        json metadata
        timestamp recorded_at
    }

    ALERT_TEMPLATE {
        uuid id PK
        string template_name
        string alert_type
        text prompt_template
        json default_config
        boolean is_active
        int version
        timestamp created_at
        timestamp updated_at
    }

    NOTIFICATION {
        uuid id PK
        uuid alert_id FK
        uuid channel_id FK
        string status
        text content
        json metadata
        timestamp sent_at
        timestamp delivered_at
        timestamp failed_at
        text error_message
        int retry_count
    }

    NOTIFICATION_CHANNEL {
        uuid id PK
        string channel_type
        string channel_name
        json config
        boolean is_active
    }

    ALERT_CONFIG {
        uuid id PK
        uuid merchant_id FK
        string alert_type
        boolean enabled
        json channel_preferences
        json notification_settings
        timestamp created_at
        timestamp updated_at
    }

    TRIGGER_CONDITION {
        uuid id PK
        uuid config_id FK
        string metric_name
        string operator
        decimal threshold
        string time_window
        int priority
        boolean is_active
    }

    FREQUENCY_CONTROL_CONFIG {
        uuid id PK
        uuid merchant_id FK
        string alert_type
        int max_alerts_per_hour
        int max_alerts_per_day
        int min_interval_minutes
        boolean enabled
        timestamp created_at
        timestamp updated_at
    }
```

### 4.2 核心实体说明

#### 4.2.1 Alert (警报)
存储警报的核心信息，包括AI生成的摘要内容和聚合管理字段。

**关键字段**：
- `alert_type`: 警报类型（CARD_TESTING, VELOCITY_ATTACK等）
- `original_severity`: 初始严重程度（P0, P1, P2, P3）
- `current_severity`: 当前严重程度（可能被自动提升）
- `summary`: AI生成的警报摘要
- `suggested_action`: AI建议的操作（JSON格式）
- `status`: 警报状态（ACTIVE, RESOLVED, DISMISSED）

**聚合相关字段**：
- `condition_fingerprint`: 条件指纹（MD5哈希），用于识别相同触发条件的Alert
- `occurrence_count`: 触发次数计数器
- `session_started_at`: 会话开始时间
- `session_last_active`: 会话最后活跃时间
- `session_timeout_minutes`: 会话超时时长（分钟）
- `session_status`: 会话状态（ACTIVE, EXPIRED, RESOLVED）
- `aggregation_window_hours`: 聚合窗口时长（小时）
- `first_triggered_at`: 首次触发时间
- `last_triggered_at`: 最后触发时间

**严重程度递进字段**：
- `escalation_history`: 严重程度提升历史记录（JSON格式）
- `last_escalated_at`: 最后一次提升时间

**通用字段**：
- `namespace`: 命名空间，用于多租户隔离
- `checkpoint`: 检查点标记，用于数据同步和恢复

#### 4.2.2 Alert Metric (警报指标)
记录触发警报的具体指标数据，支持多个指标。

#### 4.2.3 Alert Template (警报模板)
定义不同类型警报的Prompt模板，用于生成AI摘要。

**Prompt模板示例**：
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

#### 4.2.4 Frequency Control Config (频率控制配置)
定义商户维度和时间维度的频率限制规则。

**配置示例**：
- 每小时最多5条警报
- 每天最多20条警报
- 相同类型警报最小间隔15分钟

#### 4.2.5 Trigger Condition (触发条件)
定义基于Metrics的触发规则，支持多条件组合。

**条件示例**：
- `block_rate > 0.3` AND `time_window = 10min`
- `failed_auth_count > 100` AND `time_window = 5min`

---

## 5. API设计

### 5.1 警报接收API

#### 5.1.1 接收外部Metrics并创建警报

**端点**: `POST /api/v1/alerts/metrics`

**请求头**:
```
Content-Type: application/json
X-API-Key: {api_key}
X-Request-ID: {unique_request_id}
```

**请求体**:
```json
{
  "merchant_id": "uuid",
  "alert_type": "CARD_TESTING",
  "metrics": [
    {
      "metric_name": "block_rate",
      "metric_value": 0.45,
      "threshold": 0.30,
      "time_window": "10min",
      "metadata": {
        "total_transactions": 1000,
        "blocked_transactions": 450
      }
    },
    {
      "metric_name": "failed_auth_rate",
      "metric_value": 0.67,
      "threshold": 0.50,
      "time_window": "10min"
    }
  ],
  "event_metadata": {
    "source_system": "metric-platform",
    "detected_at": "2025-11-19T10:30:00Z",
    "region": "AP"
  }
}
```

**响应 (成功 - 201 Created)**:
```json
{
  "alert_id": "uuid",
  "status": "created",
  "triggered_at": "2025-11-19T10:30:05Z",
  "message": "Alert created and notifications queued"
}
```

**响应 (频率限制 - 429 Too Many Requests)**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Alert frequency limit exceeded for merchant",
  "retry_after_seconds": 1800,
  "limit_details": {
    "max_per_hour": 5,
    "current_count": 5,
    "window_reset_at": "2025-11-19T11:00:00Z"
  }
}
```

**响应 (条件不满足 - 200 OK)**:
```json
{
  "status": "no_alert",
  "message": "Metrics do not meet trigger conditions",
  "evaluated_conditions": [
    {
      "condition": "block_rate > 0.3",
      "met": true
    },
    {
      "condition": "failed_auth_rate > 0.5",
      "met": true
    }
  ]
}
```

---

### 5.2 警报查询API

#### 5.2.1 获取警报列表

**端点**: `GET /api/v1/alerts`

**查询参数**:
```
merchant_id: uuid (required)
alert_type: string (optional) - CARD_TESTING|VELOCITY_ATTACK|ACCOUNT_TAKEOVER
severity: string (optional) - P1|P2|P3
status: string (optional) - ACTIVE|RESOLVED|DISMISSED
from_date: datetime (optional)
to_date: datetime (optional)
page: int (default: 1)
page_size: int (default: 20, max: 100)
sort_by: string (default: triggered_at)
sort_order: string (default: desc)
```

**响应 (200 OK)**:
```json
{
  "data": [
    {
      "alert_id": "uuid",
      "merchant_id": "uuid",
      "alert_type": "CARD_TESTING",
      "severity": "P1",
      "title": "Suspected Card Testing Attack Detected",
      "summary": "We detected a significant spike in failed authorization attempts...",
      "status": "ACTIVE",
      "triggered_at": "2025-11-19T10:30:05Z",
      "metrics_summary": {
        "block_rate": 0.45,
        "failed_transactions": 450
      },
      "notification_channels": ["slack", "sms", "webapp"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 156,
    "total_pages": 8
  }
}
```

#### 5.2.2 获取警报详情

**端点**: `GET /api/v1/alerts/{alert_id}`

**路径参数**:
- `alert_id`: uuid (required)

**响应 (200 OK)**:
```json
{
  "alert_id": "uuid",
  "merchant_id": "uuid",
  "merchant_name": "Example Merchant Ltd",
  "alert_type": "CARD_TESTING",
  "severity": "P1",
  "title": "Suspected Card Testing Attack Detected",
  "summary": "We detected a significant spike in failed authorization attempts originating from multiple IP addresses in the past 10 minutes. The block rate increased from 5% to 45%, indicating a potential automated card testing attack...",
  "suggested_action": "Deploy the recommended rule to block transactions from suspicious IP ranges and enable additional verification for new cards.",
  "status": "ACTIVE",
  "triggered_at": "2025-11-19T10:30:05Z",
  "resolved_at": null,
  "metrics": [
    {
      "metric_name": "block_rate",
      "metric_value": 0.45,
      "threshold": 0.30,
      "time_window": "10min",
      "metadata": {
        "total_transactions": 1000,
        "blocked_transactions": 450,
        "comparison_to_baseline": "+40%"
      }
    },
    {
      "metric_name": "failed_auth_rate",
      "metric_value": 0.67,
      "threshold": 0.50,
      "time_window": "10min"
    }
  ],
  "raw_metrics": {
    "source_system": "metric-platform",
    "detected_at": "2025-11-19T10:30:00Z",
    "region": "AP",
    "detailed_breakdown": {...}
  },
  "notifications": [
    {
      "channel": "slack",
      "status": "delivered",
      "sent_at": "2025-11-19T10:30:06Z",
      "delivered_at": "2025-11-19T10:30:07Z"
    },
    {
      "channel": "sms",
      "status": "delivered",
      "sent_at": "2025-11-19T10:30:06Z",
      "delivered_at": "2025-11-19T10:30:08Z"
    },
    {
      "channel": "webapp",
      "status": "delivered",
      "sent_at": "2025-11-19T10:30:06Z",
      "delivered_at": "2025-11-19T10:30:06Z"
    }
  ],
  "actions_taken": [
    {
      "action_type": "rule_deployed",
      "action_time": "2025-11-19T10:35:00Z",
      "performed_by": "user_uuid",
      "details": {
        "rule_id": "rule_uuid",
        "rule_name": "Block suspicious IP ranges"
      }
    }
  ]
}
```

---

### 5.3 警报配置API

#### 5.3.1 获取警报配置

**端点**: `GET /api/v1/alerts/config`

**查询参数**:
```
merchant_id: uuid (required)
```

**响应 (200 OK)**:
```json
{
  "merchant_id": "uuid",
  "alert_configs": [
    {
      "alert_type": "CARD_TESTING",
      "enabled": true,
      "channels": {
        "slack": {
          "enabled": true,
          "webhook_url": "https://hooks.slack.com/..."
        },
        "sms": {
          "enabled": true,
          "phone_numbers": ["+1234567890"]
        },
        "webapp": {
          "enabled": true
        }
      },
      "trigger_conditions": [
        {
          "metric_name": "block_rate",
          "operator": ">",
          "threshold": 0.30,
          "time_window": "10min"
        }
      ],
      "frequency_control": {
        "max_alerts_per_hour": 5,
        "max_alerts_per_day": 20,
        "min_interval_minutes": 15
      }
    }
  ]
}
```

#### 5.3.2 更新警报配置

**端点**: `PUT /api/v1/alerts/config`

**请求体**:
```json
{
  "merchant_id": "uuid",
  "alert_type": "CARD_TESTING",
  "enabled": true,
  "channels": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/..."
    },
    "sms": {
      "enabled": false
    },
    "webapp": {
      "enabled": true
    }
  },
  "trigger_conditions": [
    {
      "metric_name": "block_rate",
      "operator": ">",
      "threshold": 0.35,
      "time_window": "10min"
    }
  ],
  "frequency_control": {
    "max_alerts_per_hour": 3,
    "max_alerts_per_day": 15,
    "min_interval_minutes": 20
  }
}
```

**响应 (200 OK)**:
```json
{
  "config_id": "uuid",
  "message": "Alert configuration updated successfully",
  "updated_at": "2025-11-19T11:00:00Z"
}
```

---

### 5.4 警报操作API

#### 5.4.1 标记警报为已解决

**端点**: `POST /api/v1/alerts/{alert_id}/resolve`

**请求体**:
```json
{
  "resolution_note": "Deployed blocking rule, attack mitigated",
  "resolved_by": "user_uuid"
}
```

**响应 (200 OK)**:
```json
{
  "alert_id": "uuid",
  "status": "RESOLVED",
  "resolved_at": "2025-11-19T11:30:00Z",
  "message": "Alert marked as resolved"
}
```

#### 5.4.2 忽略警报

**端点**: `POST /api/v1/alerts/{alert_id}/dismiss`

**请求体**:
```json
{
  "dismiss_reason": "False positive - normal traffic pattern",
  "dismissed_by": "user_uuid"
}
```

**响应 (200 OK)**:
```json
{
  "alert_id": "uuid",
  "status": "DISMISSED",
  "dismissed_at": "2025-11-19T11:30:00Z"
}
```

#### 5.4.3 重新发送通知

**端点**: `POST /api/v1/alerts/{alert_id}/resend-notification`

**请求体**:
```json
{
  "channels": ["slack", "sms"]
}
```

**响应 (200 OK)**:
```json
{
  "alert_id": "uuid",
  "message": "Notifications queued for resending",
  "queued_channels": ["slack", "sms"]
}
```

---

## 6. 通知渠道配置

### 6.1 Slack通知

**配置要求**:
- Webhook URL
- Channel名称
- 消息格式模板

**消息格式示例**:
```json
{
  "text": "🚨 Fraud Alert: Card Testing Attack Detected",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚨 Suspected Card Testing Attack"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Severity:*\nP1 - Critical"
        },
        {
          "type": "mrkdwn",
          "text": "*Merchant:*\nExample Merchant Ltd"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Summary:*\nWe detected a significant spike in failed authorization attempts..."
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View Details"
          },
          "url": "https://portal.airwallex.com/alerts/{alert_id}"
        }
      ]
    }
  ]
}
```

### 6.2 SMS通知

**配置要求**:
- 电话号码列表
- SMS网关配置
- 字符限制（建议160字符以内）

**消息格式示例**:
```
Airwallex Alert [P1]: Card testing attack detected. Block rate: 45%. View: https://awx.link/a/{short_id}
```

### 6.3 Webapp通知

**配置要求**:
- WebSocket连接或SSE
- 浏览器Push API支持

**通知Payload**:
```json
{
  "notification_id": "uuid",
  "type": "fraud_alert",
  "severity": "P1",
  "title": "Card Testing Attack Detected",
  "body": "We detected suspicious activity on your account",
  "alert_id": "uuid",
  "timestamp": "2025-11-19T10:30:05Z",
  "actions": [
    {
      "label": "View Details",
      "action": "navigate",
      "url": "/alerts/{alert_id}"
    },
    {
      "label": "Dismiss",
      "action": "dismiss"
    }
  ]
}
```

---

## 7. 技术实现细节

### 7.1 AI Agent集成

#### 7.1.1 LLM选择
- **主要选择**: Claude 3.5 Sonnet (高质量分析)
- **备选方案**: GPT-4 (故障转移)
- **快速模式**: Claude 3 Haiku (低延迟场景)

#### 7.1.2 Prompt工程
**模板变量**:
- `{{merchant_name}}`: 商户名称
- `{{merchant_code}}`: 商户代码
- `{{metrics_data}}`: 格式化的指标数据
- `{{historical_alerts}}`: 历史警报上下文
- `{{time_window}}`: 时间窗口
- `{{baseline_metrics}}`: 基线指标对比

**响应解析**:
- 结构化JSON输出
- Schema验证
- 错误处理和重试机制

#### 7.1.3 性能优化
- 异步调用LLM API
- 响应缓存（相似Metrics）
- 批量处理（低优先级警报）
- 超时控制（5秒）

### 7.2 频率控制实现

#### 7.2.1 Redis数据结构
```
# 滑动窗口计数器
Key: freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:hour:{timestamp_hour}
Value: count
TTL: 3600 seconds

Key: freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:day:{timestamp_day}
Value: count
TTL: 86400 seconds

# 最小间隔控制
Key: freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:last
Value: timestamp
TTL: min_interval_minutes * 60
```

#### 7.2.2 算法实现
```python
def check_frequency_limit(merchant_id, alert_type, config):
    now = datetime.now()

    # 检查最小间隔
    last_alert_key = f"freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:last"
    last_alert_time = redis.get(last_alert_key)
    if last_alert_time:
        elapsed = (now - last_alert_time).seconds
        if elapsed < config.min_interval_minutes * 60:
            return False, f"Too soon, wait {config.min_interval_minutes * 60 - elapsed}s"

    # 检查小时限制
    hour_key = f"freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:hour:{now.hour}"
    hour_count = redis.get(hour_key) or 0
    if hour_count >= config.max_alerts_per_hour:
        return False, "Hourly limit exceeded"

    # 检查每日限制
    day_key = f"freq_ctrl:merchant:{merchant_id}:alert:{alert_type}:day:{now.date()}"
    day_count = redis.get(day_key) or 0
    if day_count >= config.max_alerts_per_day:
        return False, "Daily limit exceeded"

    # 更新计数器
    redis.incr(hour_key)
    redis.expire(hour_key, 3600)
    redis.incr(day_key)
    redis.expire(day_key, 86400)
    redis.set(last_alert_key, now.timestamp(), ex=config.min_interval_minutes * 60)

    return True, "Passed"
```

### 7.3 消息队列设计

#### 7.3.1 主题设计
```
Topic: sentinel.alerts.notifications
Partitions: 10 (按merchant_id分区)
Replication: 3
Retention: 7 days
```

#### 7.3.2 消息格式
```json
{
  "message_id": "uuid",
  "alert_id": "uuid",
  "merchant_id": "uuid",
  "channels": ["slack", "sms", "webapp"],
  "priority": "high",
  "content": {
    "title": "...",
    "summary": "...",
    "alert_url": "..."
  },
  "created_at": "2025-11-19T10:30:05Z",
  "retry_count": 0,
  "max_retries": 3
}
```

---

## 8. 前端页面设计

### 8.1 Alert List页面

#### 8.1.1 功能需求
- 列表展示所有警报
- 筛选（类型、严重程度、状态、时间范围）
- 排序（时间、严重程度）
- 分页
- 批量操作（标记已读、忽略）

#### 8.1.2 UI组件
```
Alert List Component
├── Header
│   ├── Title: "Fraud Alerts"
│   ├── Summary Stats (Total, Active, Resolved)
│   └── Filter Bar
├── Alert Cards
│   ├── Alert Type Badge
│   ├── Severity Indicator (P1/P2/P3)
│   ├── Title
│   ├── Timestamp
│   ├── Status Badge
│   └── Quick Actions (View, Dismiss)
└── Pagination
```

#### 8.1.3 接口调用
```javascript
// 获取警报列表
GET /api/v1/alerts?merchant_id={id}&page=1&page_size=20&status=ACTIVE

// 响应数据绑定到UI
{
  data: [
    {
      alert_id: "...",
      severity: "P1",
      title: "Card Testing Attack",
      triggered_at: "2025-11-19T10:30:05Z",
      status: "ACTIVE"
    }
  ]
}
```

### 8.2 Alert Detail页面

#### 8.2.1 功能需求
- 完整警报信息展示
- AI生成的摘要和建议
- Metrics详细数据
- 通知发送状态
- 操作历史记录
- 快速操作按钮（部署规则、标记解决、忽略）

#### 8.2.2 UI布局
```
Alert Detail Page
├── Header
│   ├── Back Button
│   ├── Alert Title
│   ├── Severity Badge
│   └── Status Badge
├── Summary Section
│   ├── AI Generated Summary
│   ├── Suggested Action (highlighted)
│   └── Timestamp
├── Metrics Section
│   ├── Metric Cards (with charts)
│   │   ├── Block Rate: 45% (threshold: 30%)
│   │   └── Failed Auth Rate: 67% (threshold: 50%)
│   └── Raw Data Link
├── Notifications Section
│   ├── Channel Status (Slack ✓, SMS ✓, Webapp ✓)
│   └── Delivery Timeline
├── Actions Section
│   ├── Deploy Rule Button (primary)
│   ├── Mark Resolved Button
│   ├── Dismiss Button
│   └── Resend Notification
└── History Section
    └── Timeline of Actions Taken
```

#### 8.2.3 接口调用
```javascript
// 获取警报详情
GET /api/v1/alerts/{alert_id}

// 标记为已解决
POST /api/v1/alerts/{alert_id}/resolve
Body: { resolution_note: "...", resolved_by: "..." }

// 忽略警报
POST /api/v1/alerts/{alert_id}/dismiss
Body: { dismiss_reason: "...", dismissed_by: "..." }
```

---

## 9. 监控与日志

### 9.1 关键指标

#### 9.1.1 业务指标
- 警报触发率（按类型、商户）
- AI摘要生成成功率
- 通知发送成功率（按渠道）
- 频率控制拦截率
- 警报响应时间（从触发到首次操作）

#### 9.1.2 技术指标
- API响应时间（P50, P95, P99）
- LLM调用延迟和成功率
- 消息队列积压
- Redis缓存命中率
- 数据库查询性能

### 9.2 告警规则
```yaml
- name: alert_generation_failure
  condition: alert_generation_error_rate > 5%
  duration: 5m
  severity: critical

- name: notification_delivery_failure
  condition: notification_failure_rate > 10%
  duration: 5m
  severity: high

- name: llm_api_slow
  condition: llm_api_p95_latency > 5s
  duration: 3m
  severity: warning

- name: frequency_control_high_rejection
  condition: frequency_control_rejection_rate > 30%
  duration: 10m
  severity: warning
```

### 9.3 日志规范

#### 9.3.1 结构化日志格式
```json
{
  "timestamp": "2025-11-19T10:30:05.123Z",
  "level": "INFO",
  "service": "alert-service",
  "trace_id": "uuid",
  "merchant_id": "uuid",
  "alert_id": "uuid",
  "event": "alert_created",
  "message": "Alert created successfully",
  "metadata": {
    "alert_type": "CARD_TESTING",
    "severity": "P1",
    "processing_time_ms": 234
  }
}
```

#### 9.3.2 关键日志事件
- `alert_received`: 接收到外部Metrics
- `trigger_condition_evaluated`: 触发条件评估
- `frequency_check_passed/rejected`: 频率控制结果
- `ai_summary_requested`: AI摘要生成请求
- `ai_summary_generated`: AI摘要生成成功
- `alert_created`: 警报创建
- `notification_sent`: 通知发送
- `alert_resolved`: 警报解决

---

## 10. 安全考虑

### 10.1 API安全
- API Key认证
- Rate Limiting（基于IP和API Key）
- 请求签名验证
- HTTPS强制

### 10.2 数据安全
- 敏感数据加密存储（电话号码、Webhook URL）
- PII数据脱敏（日志中）
- 访问控制（商户只能访问自己的警报）
- 审计日志（所有操作记录）

### 10.3 通知安全
- Webhook URL验证
- SMS发送限流（防滥用）
- Slack OAuth Token加密存储

---

## 11. 扩展性设计

### 11.1 水平扩展
- 无状态服务设计
- 负载均衡
- 数据库读写分离
- 消息队列分区

### 11.2 未来扩展点
- 支持更多通知渠道（Email, MS Teams, Webhook）
- 多语言AI摘要
- 自定义Prompt模板（商户级别）
- 机器学习优化触发条件
- 警报聚合和关联分析

---

## 12. 部署架构

### 12.1 生产环境

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[AWS ALB]
    end

    subgraph "Application Tier"
        API1[Alert API<br/>Instance 1]
        API2[Alert API<br/>Instance 2]
        API3[Alert API<br/>Instance 3]
    end

    subgraph "Background Workers"
        W1[Notification Worker 1]
        W2[Notification Worker 2]
        W3[AI Agent Worker 1]
    end

    subgraph "Data Tier"
        PG_M[(PostgreSQL<br/>Master)]
        PG_R1[(PostgreSQL<br/>Read Replica 1)]
        PG_R2[(PostgreSQL<br/>Read Replica 2)]

        REDIS_M[(Redis<br/>Master)]
        REDIS_R1[(Redis<br/>Replica 1)]
        REDIS_R2[(Redis<br/>Replica 2)]
    end

    subgraph "Message Queue"
        KAFKA[Kafka Cluster<br/>3 Brokers]
    end

    subgraph "External Services"
        LLM[LLM API<br/>Claude/GPT]
        SLACK[Slack API]
        SMS_GW[SMS Gateway]
    end

    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> PG_M
    API2 --> PG_M
    API3 --> PG_M

    API1 --> PG_R1
    API2 --> PG_R2
    API3 --> PG_R1

    API1 --> REDIS_M
    API2 --> REDIS_M
    API3 --> REDIS_M

    API1 --> KAFKA
    API2 --> KAFKA
    API3 --> KAFKA

    KAFKA --> W1
    KAFKA --> W2
    KAFKA --> W3

    W3 --> LLM
    W1 --> SLACK
    W2 --> SMS_GW

    PG_M --> PG_R1
    PG_M --> PG_R2
    REDIS_M --> REDIS_R1
    REDIS_M --> REDIS_R2

    style LB fill:#e1f5ff
    style API1 fill:#fff4e1
    style API2 fill:#fff4e1
    style API3 fill:#fff4e1
    style W1 fill:#e1ffe1
    style W2 fill:#e1ffe1
    style W3 fill:#f0e1ff
```

### 12.2 资源配置建议

#### 12.2.1 API服务
- **实例规格**: 4 vCPU, 8GB RAM
- **实例数量**: 3-5个（根据负载自动扩展）
- **自动扩展**: CPU > 70% 或 请求队列 > 100

#### 12.2.2 Worker服务
- **Notification Worker**: 2 vCPU, 4GB RAM × 2
- **AI Agent Worker**: 2 vCPU, 4GB RAM × 1-3（根据LLM调用量）

#### 12.2.3 数据库
- **PostgreSQL**: db.r6g.xlarge (4 vCPU, 32GB RAM)
- **Redis**: cache.r6g.large (2 vCPU, 13GB RAM)

#### 12.2.4 消息队列
- **Kafka**: 3 brokers × (4 vCPU, 16GB RAM, 500GB SSD)

---

## 13. 测试策略

### 13.1 单元测试
- 触发条件评估逻辑
- 频率控制算法
- AI响应解析
- 数据验证

### 13.2 集成测试
- API端到端流程
- 消息队列集成
- 数据库操作
- 外部服务Mock

### 13.3 性能测试
- 负载测试（1000 req/s）
- 压力测试（峰值处理能力）
- AI生成延迟测试
- 数据库查询优化

### 13.4 灾难恢复测试
- 数据库故障转移
- Redis故障恢复
- 消息队列重试机制
- LLM服务降级

---

## 14. 发布计划

### 14.1 Phase 1 - MVP (Week 1-4)
- 基础Alert接收和存储
- 简单的触发条件引擎
- AI摘要生成（Claude集成）
- Webapp通知渠道
- Alert List和Detail页面

### 14.2 Phase 2 - 频率控制与多渠道 (Week 5-6)
- 完整频率控制实现
- Slack通知集成
- SMS通知集成
- 配置管理API

### 14.3 Phase 3 - 优化与扩展 (Week 7-8)
- 性能优化
- 监控和告警完善
- 批量操作支持
- 高级筛选和搜索

---

## 15. 附录

### 15.1 术语表
- **Metric**: 指标，从外部系统获取的量化数据
- **Alert**: 警报，基于Metrics触发的通知
- **Trigger Condition**: 触发条件，定义何时生成警报的规则
- **Frequency Control**: 频率控制，限制警报发送频率的机制
- **AI Agent**: AI代理，使用LLM生成警报摘要的服务

### 15.2 参考文档
- Airwallex Sentinel PRD
- Metric Platform API文档
- Claude API文档
- Slack API文档

---

**文档版本历史**:
- v1.0 (2025-11-19): 初始版本
