# Airwallex Sentinel Technical Design Document

**Version:** 1.0
**Date:** November 14, 2025
**Status:** Under Design Review

---

## 1. Requirements / Objectives

### 1.1 Product Vision

Airwallex Sentinel is an AI-powered fraud attack prevention product that automatically analyzes risk alerts, immediately tests and deploys strategies to prevent attacks, and provides incident reports with recommended next steps to protect merchants' accounts from future attacks.

**Tagline:** "Life is too short to worry about fraud attacks... read a book, enjoy the view... Airwallex Sentinel has got you covered."

### 1.2 Core Objectives

#### Business Objectives
- **Reduce Merchant Fraud Loss:** Through faster, more precise fraud mitigation, target 30%-50% reduction in financial impact from card testing and other attacks
- **Improve Operational Efficiency:** Automate alert analysis and response workflow for merchants and internal Risk Operations team, target 60% reduction in manual effort
- **Enhance Merchant Experience:** Provide peace of mind and simple, powerful tools to manage risk without requiring specialized fraud knowledge
- **Establish Market Leadership:** Position Airwallex as a first-to-market innovator in AI-powered, autonomous fraud prevention

#### Technical Objectives
- **Real-time Detection:** Alert detection latency < 1 second, AI analysis time < 5 seconds
- **High Availability:** System availability > 99.9%, support multi-AZ deployment
- **Scalability:** Support millions of transactions per day, peak TPS reaching 50,000
- **Automation Rate:** 80% of attack scenarios support auto-deployment rules

### 1.3 Supported Attack Types

| Attack Category | Detection Method | Priority |
|----------------|------------------|----------|
| **Card Testing** | Monitor high volumes of small, failed transactions from a single source, detect sequential card number patterns | P1 |
| **Velocity Attacks** | Track transaction frequency and volume in real-time, alert on sudden surges | P1 |
| **Account Takeover** | Use behavioral biometrics and anomaly detection to flag suspicious logins | P2 |
| **Chargeback Fraud** | Analyze chargeback data to identify recurring patterns | P2 |

### 1.4 Core User Stories

1. **As a merchant**, I want to be notified in the app of a potential fraud attack so that I can take immediate action
2. **As a merchant**, I want to see a simple, easy-to-understand summary of the fraud attack, including the type of attack and its impact
3. **As a merchant**, I want a one-click button to deploy the recommended fraud rule so that I can instantly stop the attack
4. **As a merchant**, I want the system to auto-deploy fraud rules and instantly stop the attack, providing me with an incident summary
5. **As a risk operations personnel**, I want the system to automatically generate and optimize rules, reducing manual rule writing work

### 1.5 Success Metrics

- **Merchant Adoption Rate:** % of active merchants with Sentinel enabled > 60%
- **False Positive Rate Reduction:** Compared to manual process, reduce by > 30%
- **Mitigation Time:** Average time from alert generation to rule deployment < 5 minutes
- **Fraud Loss Reduction:** Chargeback rate and fraud loss for merchants using Sentinel reduced by 30%-50%
- **Operational Efficiency:** Human effort in rule writing and maintenance reduced by 60%

---

## 2. Page Functionality

### 2.1 Frontend Page Structure

```mermaid
graph TB
    subgraph "Sentinel Dashboard"
        Dashboard[Main Dashboard]

        subgraph "Alert Center"
            AlertList[Alert List]
            AlertDetail[Alert Detail Page]
            AlertAnalysis[AI Analysis Report]
        end

        subgraph "Rule Management"
            RuleList[Rule List]
            RuleCreate[Create Rule]
            RuleDetail[Rule Detail]
            RulePerformance[Rule Performance]
        end

        subgraph "Protection Reports"
            Overview[Protection Overview]
            AttackHistory[Attack History]
            BlockStats[Block Statistics]
            TrendAnalysis[Trend Analysis]
        end

        subgraph "Settings"
            Notification[Notification Settings]
            AutoConfig[Automation Config]
            Threshold[Threshold Config]
        end
    end

    Dashboard --> AlertList
    Dashboard --> RuleList
    Dashboard --> Overview
    Dashboard --> Notification

    AlertList --> AlertDetail
    AlertDetail --> AlertAnalysis
    AlertDetail --> RuleCreate

    RuleList --> RuleDetail
    RuleDetail --> RulePerformance

    Overview --> AttackHistory
    Overview --> BlockStats
    Overview --> TrendAnalysis

    Notification --> AutoConfig
    AutoConfig --> Threshold

    style Dashboard fill:#e3f2fd
    style AlertCenter fill:#fff3e0
    style RuleManagement fill:#e8f5e9
    style ProtectionReports fill:#f3e5f5
    style Settings fill:#fce4ec
```

### 2.2 Core Page Functionality Details

```mermaid
graph TB
    subgraph Dashboard["📊 Main Dashboard"]
        D1["🚨 Real-time Alert Count
      P1 Alerts | P2 Alerts | P3 Alerts"]
        D2["🛡️ Today's Block Statistics"]
        D3["📋 Active Rules Count"]
        D4["⚡ Quick Action Shortcuts"]
    end

    subgraph Alert["⚠️ Alert Detail Page"]
        A1["📌 Alert Basic Info 
• Priority
• Created Time
• Status"]
        A2["🤖 AI Analysis Results
• Attack Type Identification
• Confidence Score
• Impact Analysis
• Recommended Action"]
        A3["🚀 One-Click Deploy Button"]
        A4["💬 Feedback Buttons
👍 Helpful | 👎 Not Helpful"]
    end

    subgraph Rules["🔧 Rule Management Page"]
        R1["📝 Rule List
• Filters: Status/Type/Time
• Sort Options
• Bulk Actions"]
        R2["📄 Rule Detail
• Rule Conditions
• Execution Actions"]
        R3["📈 Performance Metrics
• Precision
• Recall
• False Positive Rate"]
        R4["🧪 Test Results<br/>• Shadow Test Result<br/>• Back Test Result"]
        R5["📜 Deployment History"]
    end

    subgraph Reports["📊 Protection Reports"]
        P1["📉 Attack Trend Chart"]
        P2["✅ Block Effectiveness Stats"]
        P3["💰 Loss Avoidance Amount"]
        P4["🏆 Rule Contribution Ranking"]
        P5["📥 Export Reports"]
    end

    style Dashboard fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    style Alert fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000
    style Rules fill:#e8f5e9,stroke:#388e3c,stroke-width:3px,color:#000
    style Reports fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000

    style D1 fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000
    style D2 fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000
    style D3 fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000
    style D4 fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000

    style A1 fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000
    style A2 fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000
    style A3 fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000
    style A4 fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000

    style R1 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style R2 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style R3 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style R4 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style R5 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000

    style P1 fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style P2 fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style P3 fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style P4 fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style P5 fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
```

### 2.3 Key User Interface Flow

```mermaid
flowchart TD
    Start([Merchant Login]) --> Dashboard[View Main Dashboard]

    Dashboard --> CheckAlert{New Alert?}

    CheckAlert -->|Yes| ViewAlert[Click to View Alert]
    CheckAlert -->|No| ViewReports[View Protection Reports]

    ViewAlert --> ReadAnalysis[Read AI Analysis]
    ReadAnalysis --> DecideAction{Decide to Act?}

    DecideAction -->|Yes| ClickDeploy[Click One-Click Deploy]
    DecideAction -->|No| Dismiss[Dismiss Alert]

    ClickDeploy --> ConfirmModal[Confirm Deployment Modal]
    ConfirmModal --> ReviewImpact[Review Impact Scope]
    ReviewImpact --> Confirm{Confirm Deploy?}

    Confirm -->|Yes| AutoBacktest[AI Auto-Run Backtest]
    Confirm -->|No| Cancel[Cancel]

    AutoBacktest --> BacktestResult{Backtest Result<br/>Performance Met?}

    BacktestResult -->|Yes| DeployRule[Deploy Rule]
    BacktestResult -->|No| ShowWarning[Show Backtest Warning]

    ShowWarning --> MerchantDecide{Merchant Decision}
    MerchantDecide -->|Continue Deploy| DeployRule
    MerchantDecide -->|Cancel| Cancel

    DeployRule --> ShadowMode[Rule Enters Shadow Mode]
    ShadowMode --> MonitorShadow[Monitor Shadow Performance]
    MonitorShadow --> CheckPerf{Good Performance?}

    CheckPerf -->|Yes| GoLive[Rule Goes Live]
    CheckPerf -->|No| Tune[Tune Rule]

    GoLive --> ShowSuccess[Show Success Message]
    ShowSuccess --> ViewProtection[View Protection Effectiveness]

    Tune --> ShadowMode

    ViewProtection --> SubmitFeedback[Submit Feedback]
    SubmitFeedback --> End([Complete])

    Dismiss --> End
    Cancel --> End
    ViewReports --> End

    style AutoBacktest fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style BacktestResult fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style ShowWarning fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Start fill:#c8e6c9
    style End fill:#ffcdd2
    style ClickDeploy fill:#fff59d
    style GoLive fill:#a5d6a7
```

---

## 3. Business Flow

### 3.1 Core Business Flow Overview

```mermaid
graph TB
    subgraph "Real-time Monitoring"
        A1[Transaction Stream Monitoring]
        A2[Metric Calculation]
        A3[Threshold Check]
    end

    subgraph "Alert Generation"
        B1[Trigger Alert]
        B2[Data Collection]
        B3[Alert Classification]
    end

    subgraph "AI Analysis"
        C1[Feature Extraction]
        C2[Pattern Recognition]
        C3[Attack Classification]
        C4[Rule Recommendation]
    end

    subgraph "Merchant Decision"
        D1[Notify Merchant]
        D2[Show Analysis]
        D3[Wait for Action]
    end

    subgraph "Rule Deployment"
        E1[Validate Rule]
        E1a[Auto Backtest]
        E2[Shadow Deploy]
        E3[Performance Eval]
        E4[Live Deploy]
    end

    subgraph "Continuous Optimization"
        F1[Collect Feedback]
        F2[Performance Monitor]
        F3[Rule Optimization]
        F4[Model Training]
    end

    A1 --> A2 --> A3
    A3 -->|Threshold Breached| B1
    B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3 --> C4
    C4 --> D1 --> D2 --> D3
    D3 -->|One-Click Deploy| E1
    D3 -->|Auto Deploy| E1
    E1 --> E1a --> E2 --> E3 --> E4
    E4 --> F1
    D2 --> F1
    F1 --> F2 --> F3 --> F4
    F4 -.Model Update.-> C2

    style Real-timeMonitoring fill:#e3f2fd
    style AlertGeneration fill:#fff3e0
    style AIAnalysis fill:#f3e5f5
    style MerchantDecision fill:#e8f5e9
    style RuleDeployment fill:#ffe0b2
    style ContinuousOptimization fill:#d1c4e9
```

### 3.2 One-Click Deployment Flow Detailed Design

```mermaid
sequenceDiagram
    autonumber
    actor Merchant as Merchant
    participant UI as Frontend UI
    participant API as API Gateway
    participant Alert as Alert Service
    participant AI as AI Engine
    participant Deploy as Deployment Engine
    participant Shadow as Shadow Environment
    participant Risk as Risk Engine
    participant Notify as Notification Service

    Note over Merchant,Notify: Scenario: Merchant receives alert and executes one-click deployment

    Alert->>UI: Push new alert
    UI->>Merchant: Display notification badge

    Merchant->>UI: Click to view alert
    UI->>API: GET /api/v1/alerts/{id}
    API->>Alert: Query alert
    Alert->>AI: Get AI analysis result
    AI-->>Alert: Return analysis report
    Alert-->>API: Return complete data
    API-->>UI: Return JSON
    UI->>Merchant: Show alert detail and AI analysis

    Note over Merchant: Merchant reviews<br/>AI recommended rule

    Merchant->>UI: Click "One-Click Deploy"
    UI->>Merchant: Show confirmation dialog
    Merchant->>UI: Confirm deployment

    UI->>API: POST /api/v1/rules/deploy
    API->>Deploy: Create deployment task

    par Parallel Validation
        Deploy->>Deploy: Syntax validation
    and
        Deploy->>Deploy: Conflict detection
    and
        Deploy->>Deploy: Impact assessment
    end

    Deploy->>Shadow: Deploy to shadow environment
    Deploy->>UI: Return deployment ID
    UI->>Merchant: Display "Shadow mode running"

    loop Update every 30 seconds (5-10 minutes duration)
        Shadow->>Deploy: Report performance metrics
        Deploy->>API: Push update
        API->>UI: WebSocket push
        UI->>Merchant: Update monitoring charts
    end

    Deploy->>Deploy: Evaluate shadow performance

    alt Performance meets criteria
        Deploy->>Risk: Go live with rule
        Risk-->>Deploy: Confirm live
        Deploy->>Notify: Send success notification
        Notify->>Merchant: Email/SMS/In-app notification
        Deploy->>UI: Push live success
        UI->>Merchant: Show celebration animation + "Read a Book" view
    else Poor performance
        Deploy->>Notify: Send optimization suggestion
        Notify->>Merchant: Notify needs adjustment
        Deploy->>UI: Push optimization suggestion
        UI->>Merchant: Show tuning suggestions
    end

    Merchant->>UI: View rule detail
    UI->>API: GET /api/v1/rules/{id}/metrics
    API-->>UI: Return real-time metrics
    UI->>Merchant: Show block statistics

    Merchant->>UI: Submit feedback (👍)
    UI->>API: POST /api/v1/feedback
    API->>AI: Record positive feedback
    AI->>AI: Update training dataset
```

### 3.3 Auto-Deployment Flow (Auto-On Mode)

```mermaid
flowchart TD
    Start([Fraud Attack Detected]) --> CollectData[Collect Transaction Data]
    CollectData --> AIAnalysis[AI Analysis Engine]

    AIAnalysis --> ExtractFeatures[Feature Extraction]
    ExtractFeatures --> RunModels[Run ML Models]

    RunModels --> ClassifyAttack[Attack Type Classification]
    ClassifyAttack --> CalcConfidence[Calculate Confidence]

    CalcConfidence --> CheckConfidence{Confidence >= 0.9<br/>AND<br/>Known Attack Pattern?}

    CheckConfidence -->|Yes| AutoMode[Enter Auto Mode]
    CheckConfidence -->|No| ManualMode[Enter Manual Mode]

    AutoMode --> GenRule[Generate Rule]
    GenRule --> ValidateRule[Validate Rule]
    ValidateRule --> CheckConflict{Rule Conflict?}

    CheckConflict -->|Yes| ResolveConflict[Resolve Conflict]
    CheckConflict -->|No| ShadowDeploy[Shadow Deploy]

    ResolveConflict --> ShadowDeploy

    ShadowDeploy --> MonitorShadow[Monitor 5 minutes]
    MonitorShadow --> EvalMetrics[Evaluate Metrics]

    EvalMetrics --> CheckMetrics{Precision > 95%<br/>AND<br/>FPR < 1%?}

    CheckMetrics -->|Yes| AutoLive[Auto Go Live]
    CheckMetrics -->|No| NeedTuning{Can Tune?}

    NeedTuning -->|Yes| TuneRule[Auto Tuning]
    NeedTuning -->|No| EscalateHuman[Escalate to Human]

    TuneRule --> ShadowDeploy

    AutoLive --> UpdateRiskEngine[Update Risk Engine]
    UpdateRiskEngine --> NotifyMerchant[Notify Merchant]
    NotifyMerchant --> StartBlocking[Start Blocking]

    StartBlocking --> MonitorLive[Continuous Monitoring]
    MonitorLive --> CollectFeedback[Collect Feedback]
    CollectFeedback --> End([Complete])

    ManualMode --> NotifyForReview[Notify Merchant for Review]
    NotifyForReview --> End

    EscalateHuman --> NotifyOps[Notify Operations Team]
    NotifyOps --> End

    style AutoMode fill:#a5d6a7
    style AutoLive fill:#66bb6a
    style ManualMode fill:#fff59d
    style EscalateHuman fill:#ffab91
```

### 3.4 Auto Rule Generation and Optimization Flow

```mermaid
stateDiagram-v2
    [*] --> DataCollection: Trigger condition met

    DataCollection --> FeatureEngineering: Data preparation complete
    note right of DataCollection
        Trigger conditions:
        - Scheduled task (daily)
        - Performance degradation
        - New attack pattern
    end note

    FeatureEngineering --> AlgorithmSelection: Features ready

    AlgorithmSelection --> XGBoost: Classification task
    AlgorithmSelection --> Greedy: Optimization task
    AlgorithmSelection --> Clustering: Clustering task

    XGBoost --> RuleGeneration
    Greedy --> RuleGeneration
    Clustering --> RuleGeneration

    RuleGeneration --> Validation: Rule candidates

    Validation --> SyntaxCheck: Start validation
    SyntaxCheck --> ConflictCheck: Syntax passed
    ConflictCheck --> PerformanceTest: No conflicts

    PerformanceTest --> BacktestEval: Run backtest
    BacktestEval --> MetricsCheck: Calculate metrics

    MetricsCheck --> Approved: Metrics met
    MetricsCheck --> Rejected: Metrics not met
    MetricsCheck --> NeedsTuning: Close to target

    NeedsTuning --> Optimization: Auto tuning
    Optimization --> BacktestEval: Re-test

    Approved --> ShadowDeployment: Approve deployment
    ShadowDeployment --> ShadowMonitoring: Shadow running

    ShadowMonitoring --> LiveDeployment: Good performance
    ShadowMonitoring --> Optimization: Needs tuning

    LiveDeployment --> ProductionMonitoring: Go live
    ProductionMonitoring --> Active: Stable operation

    Active --> PerformanceDegradation: Performance degrades
    Active --> RuleRetirement: Rule expires

    PerformanceDegradation --> Optimization: Try to optimize

    RuleRetirement --> Deprecated: Mark as deprecated
    Deprecated --> [*]

    Rejected --> [*]

    note left of Approved
        Criteria met:
        - Precision > 90%
        - Recall > 80%
        - FPR < 2%
    end note
```

---

## 4. Technical Architecture

### 4.1 Overall Technical Architecture

```mermaid
C4Context
    title Airwallex Sentinel System Architecture (C4 - Level 1)

    Person(merchant, "Merchant", "Uses Sentinel<br/>to defend fraud")
    Person(ops, "Risk Operations", "Manages rules and<br/>monitors system")

    System_Boundary(sentinel, "Airwallex Sentinel") {
        System(webapp, "Sentinel Web App", "React frontend<br/>Merchant dashboard")
        System(api, "API Gateway", "FastAPI<br/>Unified interface")
        System(core, "Sentinel Core", "Fraud detection<br/>AI analysis<br/>Rule deployment")
        System(automation, "Automation Platform", "Rule generation<br/>Model training<br/>Rule governance")
    }

    System_Ext(riskengine, "Risk Engine", "Existing system<br/>Rule execution")
    System_Ext(kafka, "Kafka", "Transaction event stream")
    System_Ext(bigquery, "BigQuery", "Data warehouse")

    Rel(merchant, webapp, "Uses", "HTTPS")
    Rel(ops, webapp, "Uses", "HTTPS")

    Rel(webapp, api, "Calls", "REST/WebSocket")
    Rel(api, core, "Calls", "gRPC")
    Rel(api, automation, "Calls", "gRPC")

    Rel(core, riskengine, "Syncs rules", "gRPC")
    Rel(core, kafka, "Consumes events", "Kafka Protocol")

    Rel(automation, bigquery, "Queries data", "SQL")
    Rel(automation, riskengine, "Updates rules", "gRPC")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 4.2 Core Service Architecture

```mermaid
flowchart TB
    subgraph FrontendLayer["Frontend Layer"]
        direction LR
        WebApp["Web Application<br/>&lt;br&gt;React + TypeScript"]
        Mobile["Mobile App<br/>&lt;br&gt;React Native"]
        SentinelCore["Sentinel Core"]
        DataWarehouse["Data & AI Layer"]
    end

    subgraph GatewayLayer["Gateway Layer"]
        direction LR
        CDN["CDN / CloudFlare"]
        LoadBalancer["Load Balancer<br/>&lt;br&gt;Layer 4"]
        APIGateway["API Gateway<br/>&lt;br&gt;Kong / APISIX"]
    end

    subgraph AppServiceLayer["Application Service Layer"]
        direction LR

        subgraph BaseServices["Base Services"]
            AuthSvc["Auth Service<br/>&lt;br&gt;Go"]
            ConfigSvc["Config Service<br/>&lt;br&gt;Go"]
        end
    end

    subgraph SentinelCoreLayer["Sentinel Core Services"]
        direction LR

        subgraph CoreServices["Core Services"]
            AlertSvc["Alert Service<br/>&lt;br&gt;Go"]
            PredictSvc["Predict Service<br/>&lt;br&gt;Python/Fast<br/>API"]
            AISvc["AI Analysis Service<br/>&lt;br&gt;Python/Fast<br/>API"]
        end
    end

    subgraph AutomationLayer["Automation Platform Services"]
        direction LR
        RuleGenSvc["Rule Generation Service<br/>&lt;br&gt;Python"]
        ModelSvc["Model Service<br/>&lt;br&gt;Python"]
        BacktestSvc["Backtest Service<br/>&lt;br&gt;Python/Sp<br/>ark"]
        GovernSvc["Governance Service<br/>&lt;br&gt;Pytho<br/>n"]
    end

    subgraph ExternalLayer["External Systems"]
        direction LR
        RiskEngine["Risk Engine"]
        MailSvc["Mail Service"]
        SmsSvc["SMS Service"]
    end

    subgraph DataAILayer["Data & AI Layer"]
        direction LR
        StreamProc["Stream Processing<br/>&lt;br&gt;Flin<br/>k"]
        BatchProc["Batch Processing<br/>&lt;br&gt;Spa<br/>rk"]
        ModelServing["Model Serving<br/>&lt;br&gt;TF<br/>Serving"]
        FeatureStore["Feature Store<br/>&lt;br&gt;Feast"]
    end

    subgraph StorageLayer["Data Storage Layer"]
        direction LR
        PostgreSQL["PostgreSQL<br/>&lt;br&gt;OLTP"]
        Redis["Redis<br/>&lt;br&gt;Cac<br/>he"]
        Kafka["Kafka&lt;br&gt;&lt;br&gt;Message<br/>Queue"]
        BigQuery["BigQuery&lt;br&gt;<br/>&lt;br&gt;OLAP"]
        S3["S3&lt;br&gt;Object<br/>Storage"]
    end

    FrontendLayer --> GatewayLayer

    CDN --> LoadBalancer
    LoadBalancer --> APIGateway

    APIGateway --> AuthSvc
    APIGateway --> ConfigSvc

    AuthSvc -.Auth.-> AlertSvc
    AuthSvc -.Auth.-> PredictSvc
    ConfigSvc -.Config.-> AlertSvc
    ConfigSvc -.Config.-> PredictSvc

    APIGateway --> AlertSvc
    APIGateway --> PredictSvc
    APIGateway --> AISvc

    AlertSvc --> RuleGenSvc
    PredictSvc --> RuleGenSvc
    AISvc --> RuleGenSvc

    AlertSvc --> ModelSvc
    PredictSvc --> ModelSvc
    AISvc --> ModelSvc

    RuleGenSvc --> BacktestSvc
    ModelSvc --> BacktestSvc

    CoreServices --> RiskEngine
    CoreServices --> MailSvc
    CoreServices --> SmsSvc

    AutomationLayer --> StreamProc
    AutomationLayer --> BatchProc
    AutomationLayer --> ModelServing
    AutomationLayer --> FeatureStore

    SentinelCoreLayer --> PostgreSQL
    SentinelCoreLayer --> Redis
    SentinelCoreLayer --> Kafka

    DataAILayer --> BigQuery
    DataAILayer --> S3
    DataAILayer --> FeatureStore

    StreamProc --> Kafka
    BatchProc --> BigQuery
    ModelServing --> FeatureStore

    style FrontendLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style GatewayLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style AppServiceLayer fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    style BaseServices fill:#fff59d,stroke:#f9a825,stroke-width:1px
    style SentinelCoreLayer fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style CoreServices fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style AutomationLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style ExternalLayer fill:#efebe9,stroke:#5d4037,stroke-width:2px
    style DataAILayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    style StorageLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

### 4.3 Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Data Sources"
        TxnStream[Transaction Event Stream]
        UserEvents[User Behavior Events]
        ExtData[External Data]
    end

    subgraph "Real-time Layer"
        Kafka[Kafka<br/>Message Queue]
        Flink[Flink<br/>Stream Processing]
        Redis[Redis<br/>Real-time Cache]
    end

    subgraph "Offline Layer"
        BQ[BigQuery<br/>Data Warehouse]
        Spark[Spark<br/>Batch Processing]
        S3[S3<br/>Data Lake]
    end

    subgraph "Feature Layer"
        FeatureCalc[Feature Calculation]
        FeatureStore[Feature Store<br/>Feast]
    end

    subgraph "Application Layer"
        AlertEngine[Alert Engine]
        AIEngine[AI Engine]
        RuleEngine[Rule Engine]
        Training[Model Training]
    end

    TxnStream --> Kafka
    UserEvents --> Kafka
    ExtData --> Kafka

    Kafka --> Flink
    Flink --> FeatureCalc
    Flink --> Redis

    Kafka --> BQ
    BQ --> Spark
    Spark --> FeatureCalc
    Spark --> S3

    FeatureCalc --> FeatureStore

    FeatureStore --> AlertEngine
    FeatureStore --> AIEngine
    FeatureStore --> Training

    Redis --> AlertEngine
    Redis --> AIEngine

    BQ --> Training
    S3 --> Training

    style Real-timeLayer fill:#e3f2fd
    style OfflineLayer fill:#fff3e0
    style FeatureLayer fill:#f3e5f5
    style ApplicationLayer fill:#e8f5e9
```

### 4.4 Deployment Architecture

```mermaid
graph TB
    subgraph "Region 1 - Primary"
        subgraph "K8s Cluster 1"
            NS1_1[Namespace: sentinel-prod<br/>API Pods x3<br/>Alert Pods x2<br/>AI Pods x2]
            NS1_2[Namespace: automation<br/>RuleGen Pods x2<br/>Training Pods x2]
        end

        subgraph "Database Cluster 1"
            PG1[PostgreSQL Primary]
            Redis1[Redis Master x3]
        end
    end

    subgraph "Region 2 - Secondary"
        subgraph "K8s Cluster 2"
            NS2_1[Namespace: sentinel-prod<br/>API Pods x3<br/>Alert Pods x2<br/>AI Pods x2]
            NS2_2[Namespace: automation<br/>RuleGen Pods x2<br/>Training Pods x2]
        end

        subgraph "Database Cluster 2"
            PG2[PostgreSQL Replica]
            Redis2[Redis Replica x3]
        end
    end

    subgraph "Shared Services Layer"
        ALB[Application Load Balancer]
        Kafka_Cluster[Kafka Cluster<br/>3 Brokers]
        BQ[BigQuery]
        S3[S3 / GCS]
    end

    Internet([Internet]) --> ALB

    ALB --> NS1_1
    ALB --> NS2_1

    NS1_1 --> PG1
    NS1_1 --> Redis1
    NS1_1 --> Kafka_Cluster

    NS2_1 --> PG2
    NS2_1 --> Redis2
    NS2_1 --> Kafka_Cluster

    NS1_2 --> BQ
    NS1_2 --> S3
    NS2_2 --> BQ
    NS2_2 --> S3

    PG1 -.replication.-> PG2
    Redis1 -.replication.-> Redis2

    style Region1-Primary fill:#e3f2fd
    style Region2-Secondary fill:#fff3e0
    style SharedServicesLayer fill:#f3e5f5
```

---

## 5. Module Division

### 5.1 Module Overview

```mermaid
graph TB
    subgraph "Frontend Modules"
        FE1[Dashboard Module]
        FE2[Alert Module]
        FE3[Rule Module]
        FE4[Report Module]
        FE5[Settings Module]
    end

    subgraph "Backend Core Modules"
        BE1[API Gateway Module]
        BE2[Auth & Authorization Module]
        BE3[Alert Detection Module]
        BE4[AI Analysis Module]
        BE5[Rule Deployment Module]
        BE6[Notification Module]
    end

    subgraph "Automation Modules"
        AUTO1[Rule Generation Module]
        AUTO2[Model Training Module]
        AUTO3[Backtest Module]
        AUTO4[Rule Governance Module]
        AUTO5[Monitoring & Optimization Module]
    end

    subgraph "Data Modules"
        DATA1[Feature Engineering Module]
        DATA2[Stream Processing Module]
        DATA3[Batch Processing Module]
        DATA4[Data Storage Module]
    end

    subgraph "Infrastructure Modules"
        INFRA1[Config Center]
        INFRA2[Service Discovery]
        INFRA3[Monitoring & Alerting]
        INFRA4[Log Collection]
    end

    FE1 & FE2 & FE3 & FE4 & FE5 --> BE1
    BE1 --> BE2
    BE2 --> BE3 & BE5
    BE3 --> BE4
    BE4 --> BE5
    BE5 --> BE6

    BE3 & BE4 --> DATA2
    AUTO1 & AUTO2 & AUTO3 --> DATA3
    DATA2 & DATA3 --> DATA1
    DATA1 --> DATA4

    BE3 & BE4 & BE5 --> INFRA1
    BE1 & BE3 & BE4 & BE5 --> INFRA2
    BE1 & BE3 & BE4 & BE5 --> INFRA3
    BE1 & BE3 & BE4 & BE5 --> INFRA4

    style FrontendModules fill:#e3f2fd
    style BackendCoreModules fill:#fff3e0
    style AutomationModules fill:#f3e5f5
    style DataModules fill:#e8f5e9
    style InfrastructureModules fill:#fce4ec
```

### 5.2 Core Module Detailed Division

```mermaid
mindmap
  root((Sentinel Modules))
    Frontend Modules
      Dashboard Module
        Real-time data display
        Chart components
        Quick actions
      Alert Module
        Alert list
        Alert details
        AI analysis display
        One-click deploy UI
      Rule Module
        Rule list
        Rule details
        Performance monitoring
        Configuration management
      Report Module
        Attack history
        Block statistics
        Trend analysis
        Report export
      Settings Module
        Notification config
        Automation settings
        Threshold management

    Backend Core Modules
      API Gateway Module
        Route management
        Protocol conversion
        Traffic control
        API aggregation

      Alert Detection Module
        Metric Monitor
          Real-time metric calculation
          Sliding window stats
        Threshold Checker
          Dynamic threshold
          Multi-dimensional check
        Alert Generator
          Alert classification
          Priority determination
          Data collection

      AI Analysis Module
        Feature Extractor
          Real-time features
          Historical features
        Model Inference Engine
          Classification models
          Clustering models
          Anomaly detection
        Rule Recommender
          Rule generation
          Confidence calculation
          Impact assessment

      Rule Deployment Module
        Rule Validator
          Syntax check
          Conflict detection
        Shadow Deployer
          Traffic splitting
          Performance monitoring
        Live Manager
          Canary release
          Auto rollback

      Notification Module
        Message routing
        Template engine
        Multi-channel delivery
        Delivery status tracking

    Automation Modules
      Rule Generation Module
        Data preparer
        Algorithm selector
        Rule trainer
        Rule optimizer

      Model Training Module
        Feature engineering
        Model training
        Model evaluation
        Model registry

      Backtest Module
        Historical data loading
        Rule simulation
        Performance calculation
        Report generation

      Rule Governance Module
        Performance monitoring
        Auto retirement
        Conflict management
        Version control

      Monitoring & Optimization Module
        Metrics collection
        Anomaly detection
        Auto tuning
        Report generation

    Data Modules
      Feature Engineering Module
        Feature calculation
        Feature storage
        Feature serving

      Stream Processing Module
        Event consumption
        Real-time aggregation
        Window computation

      Batch Processing Module
        Data extraction
        Data transformation
        Data loading

      Data Storage Module
        OLTP storage
        OLAP storage
        Cache management
        Object storage
```

### 5.3 Module Dependency Relationships

```mermaid
graph LR
    subgraph "Layer 1: Foundation Layer"
        L1_1[Config Center]
        L1_2[Service Discovery]
        L1_3[Auth Service]
    end

    subgraph "Layer 2: Data Layer"
        L2_1[Data Storage]
        L2_2[Cache Service]
        L2_3[Message Queue]
    end

    subgraph "Layer 3: Data Processing Layer"
        L3_1[Stream Processing]
        L3_2[Batch Processing]
        L3_3[Feature Engineering]
    end

    subgraph "Layer 4: Core Business Layer"
        L4_1[Alert Detection]
        L4_2[AI Analysis]
        L4_3[Rule Deployment]
        L4_4[Notification Service]
    end

    subgraph "Layer 5: Automation Layer"
        L5_1[Rule Generation]
        L5_2[Model Training]
        L5_3[Rule Governance]
    end

    subgraph "Layer 6: Interface Layer"
        L6_1[API Gateway]
    end

    subgraph "Layer 7: Presentation Layer"
        L7_1[Web Frontend]
    end

    L1_1 & L1_2 & L1_3 --> L2_1 & L2_2 & L2_3
    L2_1 & L2_2 & L2_3 --> L3_1 & L3_2 & L3_3
    L3_1 & L3_2 & L3_3 --> L4_1 & L4_2 & L4_3 & L4_4
    L4_1 & L4_2 & L4_3 --> L5_1 & L5_2 & L5_3
    L4_1 & L4_2 & L4_3 & L4_4 & L5_1 & L5_2 & L5_3 --> L6_1
    L6_1 --> L7_1

    style Layer1:FoundationLayer fill:#fce4ec
    style Layer2:DataLayer fill:#e8f5e9
    style Layer3:DataProcessingLayer fill:#fff3e0
    style Layer4:CoreBusinessLayer fill:#e3f2fd
    style Layer5:AutomationLayer fill:#f3e5f5
    style Layer6:InterfaceLayer fill:#d1c4e9
    style Layer7:PresentationLayer fill:#c8e6c9
```

---

## 6. Module Interaction & Flow

### 6.1 Real-time Alert Detection Flow (Module Interaction)

```mermaid
sequenceDiagram
    participant Kafka as Kafka<br/>Message Queue
    participant Stream as Stream Processing Module<br/>Flink
    participant Monitor as Metric Monitor<br/>Alert Detection Module
    participant Threshold as Threshold Checker<br/>Alert Detection Module
    participant Generator as Alert Generator<br/>Alert Detection Module
    participant Feature as Feature Extractor<br/>AI Analysis Module
    participant Model as Model Inference Engine<br/>AI Analysis Module
    participant Recommender as Rule Recommender<br/>AI Analysis Module
    participant Notifier as Notification Module
    participant DB as PostgreSQL
    participant Cache as Redis

    Kafka->>Stream: 1. Receive transaction event stream
    Stream->>Stream: 2. Window aggregation
    Stream->>Monitor: 3. Calculate real-time metrics

    Monitor->>Cache: 4. Cache metric data
    Monitor->>Threshold: 5. Send metrics

    Threshold->>Threshold: 6. Check threshold

    alt Threshold breached
        Threshold->>Generator: 7. Trigger alert generation
        Generator->>DB: 8. Query historical data
        DB-->>Generator: 9. Return historical data

        Generator->>Generator: 10. Classify alert (P1/P2/P3)
        Generator->>DB: 11. Save alert

        Generator->>Feature: 12. Request AI analysis
        Feature->>DB: 13. Load transaction details
        DB-->>Feature: 14. Return transaction data

        Feature->>Feature: 15. Extract features
        Feature->>Model: 16. Call model inference

        par Parallel Inference
            Model->>Model: Attack classification
        and
            Model->>Model: Clustering analysis
        and
            Model->>Model: Anomaly detection
        end

        Model->>Recommender: 17. Inference results
        Recommender->>Recommender: 18. Generate rule recommendation
        Recommender->>Recommender: 19. Calculate confidence

        Recommender->>DB: 20. Save analysis results
        Recommender->>Generator: 21. Return analysis report

        Generator->>Notifier: 22. Send notification request

        par Multi-channel Notification
            Notifier->>Notifier: In-app push
        and
            Notifier->>Notifier: Email notification
        and
            Notifier->>Notifier: SMS notification (P1)
        end

        Notifier->>DB: 23. Record notification status
    else Normal
        Threshold->>Monitor: Continue monitoring
    end
```

### 6.2 Rule Deployment Flow (Module Interaction)

```mermaid
sequenceDiagram
    participant UI as Web Frontend
    participant Gateway as API Gateway
    participant Auth as Auth Module
    participant RuleAPI as Rule Deployment Module<br/>API Layer
    participant Validator as Rule Validator
    participant Shadow as Shadow Deployer
    participant Monitor as Performance Monitor
    participant LiveDeploy as Live Manager
    participant RiskEngine as Risk Engine
    participant Notifier as Notification Module
    participant DB as PostgreSQL
    participant Cache as Redis

    UI->>Gateway: 1. POST /rules/deploy
    Gateway->>Auth: 2. Verify Token
    Auth-->>Gateway: 3. Token valid

    Gateway->>RuleAPI: 4. Forward request
    RuleAPI->>DB: 5. Query rule definition
    DB-->>RuleAPI: 6. Return rule

    RuleAPI->>Validator: 7. Validate rule

    par Parallel Validation
        Validator->>Validator: Syntax check
    and
        Validator->>DB: Query existing rules
        DB-->>Validator: Return rule list
        Validator->>Validator: Conflict detection
    and
        Validator->>Validator: Impact assessment
    end

    Validator-->>RuleAPI: 8. Validation passed

    RuleAPI->>Shadow: 9. Deploy to shadow environment
    Shadow->>RiskEngine: 10. Push shadow rule
    RiskEngine-->>Shadow: 11. Confirm deployment

    Shadow->>Cache: 12. Cache shadow status
    Shadow->>DB: 13. Record deployment

    Shadow-->>UI: 14. Return deployment ID (WebSocket)

    loop Monitor 5-10 minutes
        RiskEngine->>Monitor: 15. Report performance metrics
        Monitor->>Monitor: 16. Calculate metrics
        Monitor->>Cache: 17. Update cache
        Monitor-->>UI: 18. Push metrics (WebSocket)
    end

    Monitor->>Monitor: 19. Evaluate performance

    alt Performance meets criteria
        Monitor->>LiveDeploy: 20. Request go live
        LiveDeploy->>RiskEngine: 21. Go live with rule
        RiskEngine-->>LiveDeploy: 22. Confirm live

        LiveDeploy->>DB: 23. Update status to LIVE
        LiveDeploy->>Cache: 24. Update cache

        LiveDeploy->>Notifier: 25. Send success notification
        Notifier-->>UI: 26. Push success message

    else Poor performance
        Monitor->>Notifier: 20. Send optimization suggestion
        Notifier-->>UI: 21. Push optimization suggestion
    end
```

### 6.3 Auto Rule Generation Flow (Module Interaction)

```mermaid
flowchart TD
    Start([Scheduled Task Trigger<br/>or Manual Trigger]) --> Scheduler[Scheduler<br/>Airflow]

    Scheduler --> DataPrep[Data Preparer<br/>Rule Generation Module]

    DataPrep --> QueryBQ[Query BigQuery]
    QueryBQ --> ExtractData[Extract Training Data]
    ExtractData --> LabelData[Label Data]

    LabelData --> FeatureEng[Feature Engineering Module]
    FeatureEng --> CalcFeatures[Calculate Features]
    CalcFeatures --> SaveFeatures[Save to Feature Store]

    SaveFeatures --> AlgoSelect[Algorithm Selector<br/>Rule Generation Module]
    AlgoSelect --> ChooseAlgo{Choose Algorithm}

    ChooseAlgo -->|Classification Task| XGBoost[XGBoost Training]
    ChooseAlgo -->|Optimization Task| Greedy[Greedy Search]
    ChooseAlgo -->|Clustering Task| Clustering[Clustering Algorithm]

    XGBoost --> RuleGen[Rule Trainer]
    Greedy --> RuleGen
    Clustering --> RuleGen

    RuleGen --> GenCandidates[Generate Rule Candidates]
    GenCandidates --> RuleOpt[Rule Optimizer]

    RuleOpt --> RankRules[Rank Rules]
    RankRules --> FilterRules[Filter Low-quality Rules]
    FilterRules --> SaveRules[Save to Database]

    SaveRules --> BacktestMod[Backtest Module]
    BacktestMod --> LoadHistory[Load Historical Data]
    LoadHistory --> SimulateRule[Simulate Rule Execution]
    SimulateRule --> CalcMetrics[Calculate Performance Metrics]

    CalcMetrics --> CheckQuality{Quality Check}

    CheckQuality -->|Pass| Approved[Mark as Approved]
    CheckQuality -->|Fail| Rejected[Mark as Rejected]
    CheckQuality -->|Needs Tuning| NeedTune[Auto Tuning]

    NeedTune --> RuleOpt

    Approved --> NotifyOps[Notify Operations Team]
    NotifyOps --> ManualReview[Manual Review]

    ManualReview --> ShadowDeploy[Shadow Deploy]
    ShadowDeploy --> End([Complete])

    Rejected --> LogResult[Log Result]
    LogResult --> End

    style DataPrep fill:#e3f2fd
    style FeatureEng fill:#fff3e0
    style RuleGen fill:#f3e5f5
    style BacktestMod fill:#e8f5e9
```

### 6.4 Model Training and Update Flow (Module Interaction)

```mermaid
sequenceDiagram
    participant Scheduler as Airflow<br/>Scheduler
    participant DataMod as Batch Processing Module<br/>Spark
    participant FeatureMod as Feature Engineering Module
    participant TrainMod as Model Training Module
    participant EvalMod as Model Evaluator
    participant Registry as Model Registry
    participant Serving as Model Serving
    participant AIMod as AI Analysis Module
    participant DB as PostgreSQL
    participant BQ as BigQuery
    participant S3 as S3 Object Storage

    Note over Scheduler: Triggered daily at 2:00 AM

    Scheduler->>DataMod: 1. Start data preparation task
    DataMod->>BQ: 2. Query last 30 days transaction data
    BQ-->>DataMod: 3. Return data

    DataMod->>DataMod: 4. Data cleaning and transformation
    DataMod->>S3: 5. Save to data lake

    DataMod->>FeatureMod: 6. Trigger feature calculation
    FeatureMod->>S3: 7. Read raw data
    FeatureMod->>FeatureMod: 8. Feature engineering
    FeatureMod->>DB: 9. Save feature definitions
    FeatureMod->>S3: 10. Save feature data

    FeatureMod->>TrainMod: 11. Trigger model training
    TrainMod->>S3: 12. Load feature data
    TrainMod->>TrainMod: 13. Data split

    loop Hyperparameter Tuning
        TrainMod->>TrainMod: 14. Train model
        TrainMod->>EvalMod: 15. Evaluate model
        EvalMod->>EvalMod: 16. Calculate metrics
        EvalMod-->>TrainMod: 17. Return evaluation results
    end

    TrainMod->>EvalMod: 18. Best model evaluation
    EvalMod->>DB: 19. Query champion model performance
    DB-->>EvalMod: 20. Return champion model metrics

    EvalMod->>EvalMod: 21. Compare performance

    alt New model better
        EvalMod->>Registry: 22. Register challenger model
        Registry->>S3: 23. Save model file
        Registry->>DB: 24. Save model metadata

        Registry->>Serving: 25. Deploy to A/B test
        Serving->>Serving: 26. Load model

        Note over Serving,AIMod: A/B test for 7 days

        loop Daily check
            Serving->>DB: 27. Record inference results
            Registry->>DB: 28. Query A/B test metrics
            DB-->>Registry: 29. Return metrics
        end

        alt Challenger wins
            Registry->>Serving: 30. Promote to champion model
            Serving->>AIMod: 31. Update production model
            Registry->>DB: 32. Update model status
            Registry->>Scheduler: 33. Send success notification
        else Champion remains
            Registry->>Serving: 30. Rollback challenger
            Registry->>DB: 31. Mark as failed
        end

    else New model not better than champion
        EvalMod->>DB: 22. Record training failure
        EvalMod->>Scheduler: 23. Send failure notification
    end
```

### 6.5 Complete End-to-End Flow Integration

```mermaid
graph TB
    subgraph "Phase 1: Real-time Monitoring"
        S1_1[Transaction Stream Ingestion]
        S1_2[Real-time Metric Calculation]
        S1_3[Threshold Check]
        S1_4[Alert Trigger]
    end

    subgraph "Phase 2: Intelligent Analysis"
        S2_1[Data Collection]
        S2_2[Feature Extraction]
        S2_3[AI Model Inference]
        S2_4[Attack Classification]
        S2_5[Rule Recommendation]
    end

    subgraph "Phase 3: Merchant Decision"
        S3_1[Multi-channel Notification]
        S3_2[Display Analysis Report]
        S3_3[Merchant Action]
    end

    subgraph "Phase 4: Rule Deployment"
        S4_1[Rule Validation]
        S4_2[Shadow Deploy]
        S4_3[Performance Monitoring]
        S4_4[Auto Go Live]
    end

    subgraph "Phase 5: Effect Monitoring"
        S5_1[Block Statistics]
        S5_2[Performance Tracking]
        S5_3[Feedback Collection]
    end

    subgraph "Phase 6: Continuous Optimization"
        S6_1[Data Labeling]
        S6_2[Model Retraining]
        S6_3[Rule Optimization]
        S6_4[System Iteration]
    end

    S1_1 --> S1_2 --> S1_3 --> S1_4
    S1_4 --> S2_1 --> S2_2 --> S2_3 --> S2_4 --> S2_5
    S2_5 --> S3_1 --> S3_2 --> S3_3
    S3_3 --> S4_1 --> S4_2 --> S4_3 --> S4_4
    S4_4 --> S5_1 --> S5_2 --> S5_3
    S5_3 --> S6_1 --> S6_2 --> S6_3 --> S6_4

    S6_4 -.Feedback Loop.-> S2_3
    S5_2 -.Performance Degradation.-> S6_3

    style Phase1:Real-timeMonitoring fill:#e3f2fd
    style Phase2:IntelligentAnalysis fill:#fff3e0
    style Phase3:MerchantDecision fill:#e8f5e9
    style Phase4:RuleDeployment fill:#f3e5f5
    style Phase5:EffectMonitoring fill:#ffe0b2
    style Phase6:ContinuousOptimization fill:#d1c4e9
```

---

## Appendix

### A. Technology Stack Summary

| Layer | Technology Selection | Description |
|-------|---------------------|-------------|
| **Frontend** | React 18 + TypeScript + Material-UI | Modern UI framework |
| **API Gateway** | Kong / APISIX | High-performance API gateway |
| **Backend Services** | Python (FastAPI) + Go | Python for AI/ML, Go for high-performance services |
| **Real-time Processing** | Apache Kafka + Flink | Stream processing platform |
| **Batch Processing** | Apache Spark + Airflow | Big data processing |
| **ML Framework** | XGBoost, scikit-learn, TensorFlow | Machine learning |
| **Model Serving** | TensorFlow Serving / Seldon | Model inference |
| **Feature Store** | Feast | Feature management |
| **OLTP** | PostgreSQL 15+ | Transactional database |
| **OLAP** | Google BigQuery | Analytical database |
| **Cache** | Redis Cluster | Distributed cache |
| **Object Storage** | AWS S3 / GCS | File storage |
| **Container Orchestration** | Kubernetes | Container management |
| **Monitoring** | Prometheus + Grafana | Monitoring and alerting |
| **Logging** | ELK Stack | Log analysis |
| **Tracing** | Jaeger | Distributed tracing |

### B. Key Metrics Definition

| Metric | Definition | Target |
|--------|-----------|--------|
| **Alert Detection Latency** | Time from transaction to alert generation | < 1 second |
| **AI Analysis Time** | Time required for AI analysis completion | < 5 seconds |
| **Rule Deployment Time** | Time from click deploy to rule active | < 30 seconds |
| **System Availability** | System uptime percentage | > 99.9% |
| **Precision** | True Positives / (True Positives + False Positives) | > 95% |
| **Recall** | True Positives / (True Positives + False Negatives) | > 85% |
| **False Positive Rate** | False Positives / (False Positives + True Negatives) | < 1% |

### C. Implementation Plan

| Phase | Timeline | Main Deliverables |
|-------|----------|-------------------|
| **Phase 1 - MVP** | 2025 Q4 | Basic alert detection + One-click deploy + Card testing detection |
| **Phase 2 - Automation** | 2026 Q1 | Auto rule generation + Auto retirement + Backtest functionality |
| **Phase 3 - Advanced Features** | 2026 Q2 | Auto-On mode + Multi-attack vectors + Advanced analytics |
| **Phase 4 - Optimization & Scale** | 2026 Q3 | Multi-region deployment + Strategy automation + AI feature generation |

---

**Document Status:** Pending Review
**Created Date:** 2025-11-14
**Last Updated:** 2025-11-14
**Maintainer:** Technical Architecture Team
