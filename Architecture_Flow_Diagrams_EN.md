# Airwallex Sentinel - Architecture & Flow Diagrams

**Version:** 1.0
**Date:** November 14, 2025
**Author:** Technical Architecture Team

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Core Components Relationship](#core-components-relationship)
3. [Real-time Fraud Detection Flow](#real-time-fraud-detection-flow)
4. [AI Analysis Processing Flow](#ai-analysis-processing-flow)
5. [Rule Deployment Flow](#rule-deployment-flow)
6. [Automation Platform Workflow](#automation-platform-workflow)
7. [Data Processing Pipeline](#data-processing-pipeline)
8. [Deployment Architecture](#deployment-architecture)
9. [User Interaction Flow](#user-interaction-flow)

---

## System Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Layer"
        UI[Merchant Dashboard]
        Mobile[Mobile App]
        Email[Email Notifications]
        SMS[SMS Notifications]
    end

    subgraph "Gateway Layer"
        LB[Load Balancer]
        Gateway[API Gateway]
        Auth[Auth Service]
    end

    subgraph "Application Service Layer"
        subgraph "Sentinel Core"
            AlertEngine[Alert Detection Engine]
            AIAnalysis[AI Analysis Module]
            RuleDeploy[Rule Deployment Engine]
            Notification[Notification Service]
        end

        subgraph "Automation Platform"
            RuleGen[Auto Rule Generation]
            ModelTrain[Model Training]
            Backtest[Backtest Service]
            Governance[Rule Governance]
        end

        RiskEngine[Risk Engine<br/>Existing System]
    end

    subgraph "Data & AI Layer"
        FeatureStore[Feature Store]
        ModelServing[Model Serving]
        MLPipeline[ML Training Pipeline]
        Analytics[Real-time Analytics]
    end

    subgraph "Storage Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        BigQuery[(BigQuery)]
        Kafka[Kafka Message Queue]
        S3[(Object Storage)]
    end

    UI --> LB
    Mobile --> LB
    LB --> Gateway
    Gateway --> Auth

    Auth --> AlertEngine
    Auth --> RuleDeploy
    Auth --> RuleGen

    AlertEngine --> AIAnalysis
    AIAnalysis --> RuleDeploy
    RuleDeploy --> RiskEngine
    RuleDeploy --> Notification

    Notification --> Email
    Notification --> SMS
    Notification --> UI

    RuleGen --> ModelServing
    ModelTrain --> MLPipeline
    Backtest --> Analytics

    AlertEngine --> Kafka
    AIAnalysis --> FeatureStore
    ModelServing --> FeatureStore

    RuleDeploy --> PostgreSQL
    AlertEngine --> Redis
    Analytics --> BigQuery
    ModelTrain --> S3

    RiskEngine -.feedback.-> AlertEngine
    Governance -.monitoring.-> RuleDeploy

    style SentinelCore fill:#e1f5ff
    style AutomationPlatform fill:#fff4e6
    style Data&AILayer fill:#f3e5f5
```

---

## Core Components Relationship

### Component Interaction & Dependencies

```mermaid
graph LR
    subgraph "Frontend Components"
        Dashboard[Dashboard UI]
        AlertPanel[Alert Panel]
        RuleManager[Rule Manager]
        Analytics_UI[Analytics Reports]
    end

    subgraph "Backend Core Services"
        API[API Service]
        AlertDetector[Alert Detector]
        AIEngine[AI Engine]
        RuleEngine[Rule Engine]
        NotificationSvc[Notification Service]
    end

    subgraph "ML Services"
        ModelRegistry[Model Registry]
        Inference[Inference Service]
        Training[Training Service]
        FeatureEng[Feature Engineering]
    end

    subgraph "Data Services"
        DataPipeline[Data Pipeline]
        CacheService[Cache Service]
        Storage[Storage Service]
        StreamProcessor[Stream Processor]
    end

    Dashboard --> API
    AlertPanel --> API
    RuleManager --> API
    Analytics_UI --> API

    API --> AlertDetector
    API --> RuleEngine
    API --> NotificationSvc

    AlertDetector --> AIEngine
    AlertDetector --> StreamProcessor

    AIEngine --> Inference
    AIEngine --> FeatureEng

    RuleEngine --> ModelRegistry

    Training --> ModelRegistry
    FeatureEng --> DataPipeline

    Inference --> CacheService
    StreamProcessor --> DataPipeline
    DataPipeline --> Storage

    style MLServices fill:#ffe0b2
    style DataServices fill:#c8e6c9
```

---

## Real-time Fraud Detection Flow

### End-to-End Detection Flow

```mermaid
sequenceDiagram
    participant Txn as Transaction Event
    participant Stream as Stream Processor<br/>(Kafka/Flink)
    participant Monitor as Metric Monitor
    participant Threshold as Threshold Checker
    participant Alert as Alert Generator
    participant AI as AI Analysis Engine
    participant Rule as Rule Recommender
    participant Notify as Notification Service
    participant Merchant as Merchant
    participant Deploy as Deployment Engine
    participant Risk as Risk Engine

    Txn->>Stream: 1. Receive transaction stream
    Stream->>Monitor: 2. Real-time feature extraction
    Monitor->>Monitor: 3. Calculate sliding window metrics
    Note over Monitor: Block rate, failure rate<br/>transaction volume, etc.

    Monitor->>Threshold: 4. Check thresholds
    alt Threshold breached
        Threshold->>Alert: 5. Trigger alert
        Alert->>AI: 6. Start AI analysis

        par Parallel analysis
            AI->>AI: Clustering analysis
        and
            AI->>AI: Pattern recognition
        and
            AI->>AI: Data integrity check
        and
            AI->>AI: Leakage analysis
        end

        AI->>Rule: 7. Generate rule recommendation
        Rule->>Notify: 8. Send notification

        par Multi-channel notification
            Notify->>Merchant: In-app push
        and
            Notify->>Merchant: Email notification
        and
            Notify->>Merchant: SMS (P1)
        end

        Merchant->>Deploy: 9. One-click/Auto deployment
        Deploy->>Risk: 10. Push rule to risk engine
        Risk->>Txn: 11. Apply rule to block
    else Normal
        Threshold->>Monitor: Continue monitoring
    end
```

---

## AI Analysis Processing Flow

### AI Analysis Module Detailed Flow

```mermaid
flowchart TD
    Start([Receive Alert]) --> LoadData[Load Transaction Data]
    LoadData --> FeatureExtract[Feature Extraction]

    FeatureExtract --> ParallelAnalysis{Parallel Analysis Tasks}

    ParallelAnalysis --> Clustering[Behavioral Clustering]
    ParallelAnalysis --> Pattern[Pattern Recognition]
    ParallelAnalysis --> Integrity[Data Integrity Check]
    ParallelAnalysis --> Leakage[Leakage Analysis]

    Clustering --> ClusterAlgo[DBSCAN/K-Means<br/>Clustering Algorithm]
    ClusterAlgo --> ClusterResult[Identify Suspicious Clusters]

    Pattern --> ClassifyModel[XGBoost<br/>Classification Model]
    ClassifyModel --> AttackType[Attack Type Classification]

    Integrity --> NLP[NLP Detection]
    Integrity --> AnomalyDet[Anomaly Detection]
    NLP --> DataQuality[Data Quality Score]
    AnomalyDet --> DataQuality

    Leakage --> QueryBypass[Query Bypassed Transactions]
    QueryBypass --> AnalyzeTraits[Analyze Common Traits]

    ClusterResult --> Aggregate[Aggregate Analysis Results]
    AttackType --> Aggregate
    DataQuality --> Aggregate
    AnalyzeTraits --> Aggregate

    Aggregate --> GenConclusion[Generate Conclusion]
    GenConclusion --> CalcConfidence[Calculate Confidence]
    CalcConfidence --> GenAction[Generate Recommended Action]

    GenAction --> CheckConfidence{Confidence > 0.9?}
    CheckConfidence -->|Yes| AutoDeploy[Mark for Auto Deployment]
    CheckConfidence -->|No| ManualReview[Mark for Manual Review]

    AutoDeploy --> Output[Output JSON Result]
    ManualReview --> Output

    Output --> End([Return Analysis Report])

    style Clustering fill:#e3f2fd
    style Pattern fill:#e8f5e9
    style Integrity fill:#fff3e0
    style Leakage fill:#fce4ec
```

---

## Rule Deployment Flow

### One-Click & Auto Deployment Flow

```mermaid
stateDiagram-v2
    [*] --> ReceiveRecommendation: AI generates recommendation

    ReceiveRecommendation --> ValidateRule: Rule validation
    ValidateRule --> CheckSyntax: Check syntax
    CheckSyntax --> CheckConflict: Check conflicts

    CheckConflict --> DeploymentMode: Determine deployment mode

    DeploymentMode --> OneClick: One-click mode
    DeploymentMode --> AutoOn: Auto mode

    OneClick --> ShadowDeploy: Shadow deployment
    AutoOn --> ShadowDeploy

    ShadowDeploy --> Monitor: Monitor performance
    Monitor --> Evaluate: Evaluate metrics

    Evaluate --> OneClickApproval: One-click mode
    Evaluate --> AutoApproval: Auto mode

    OneClickApproval --> WaitMerchant: Wait for merchant confirmation
    WaitMerchant --> MerchantApproved: Merchant approved
    WaitMerchant --> MerchantRejected: Merchant rejected

    AutoApproval --> AutoCheck: Auto check
    AutoCheck --> PerformanceGood: Good performance
    AutoCheck --> PerformancePoor: Poor performance

    MerchantApproved --> LiveDeploy: Live deployment
    PerformanceGood --> LiveDeploy

    LiveDeploy --> UpdateRiskEngine: Update risk engine
    UpdateRiskEngine --> NotifySuccess: Notify deployment success
    NotifySuccess --> ContinuousMonitor: Continuous monitoring

    MerchantRejected --> ArchiveRule: Archive rule
    PerformancePoor --> Refine: Refine rule
    Refine --> ShadowDeploy

    ContinuousMonitor --> RuleRetirement: Rule retirement process
    ArchiveRule --> [*]
    RuleRetirement --> [*]
```

---

## Automation Platform Workflow

### Auto Rule Generation Flow

```mermaid
graph TD
    subgraph "Data Preparation Phase"
        Start([Start]) --> ConfigJob[Configure Generation Job]
        ConfigJob --> SelectUseCase{Select Use Case Type}

        SelectUseCase -->|Segment Level| SegmentData[Extract Segment Data]
        SelectUseCase -->|Merchant Level| MerchantData[Extract Merchant Data]
        SelectUseCase -->|Attack Pattern| AttackData[Extract Attack Pattern Data]

        SegmentData --> PrepData[Data Cleaning & Preparation]
        MerchantData --> PrepData
        AttackData --> PrepData

        PrepData --> FeatureGen[Feature Generation]
        FeatureGen --> LabelGen[Label Generation<br/>Soft/Hard Labels]
    end

    subgraph "Algorithm Training Phase"
        LabelGen --> SelectAlgo{Select Algorithm}

        SelectAlgo -->|XGBoost| XGB[XGBoost Training]
        SelectAlgo -->|Greedy Search| Greedy[Greedy Algorithm]
        SelectAlgo -->|Exhaustive Search| Exhaustive[Exhaustive Search]

        XGB --> BuildModel[Build Model]
        Greedy --> BuildModel
        Exhaustive --> BuildModel

        BuildModel --> OptimizeObj[Optimize Objective Function]
        OptimizeObj --> GenRules[Generate Rule Candidates]
    end

    subgraph "Rule Optimization Phase"
        GenRules --> RankRules[Rank Rules]
        RankRules --> FilterRules[Filter Low-quality Rules]
        FilterRules --> RefineRules[Refine Rules]
        RefineRules --> ValidateRules[Validate Rules]
    end

    subgraph "Deployment Evaluation Phase"
        ValidateRules --> RunBacktest[Run Backtest]
        RunBacktest --> CalcMetrics[Calculate Performance Metrics]
        CalcMetrics --> CheckThreshold{Meet Threshold?}

        CheckThreshold -->|Yes| ShadowTest[Shadow Testing]
        CheckThreshold -->|No| Reject[Reject Rule]

        ShadowTest --> ABTest[A/B Testing]
        ABTest --> FinalApproval{Final Approval?}

        FinalApproval -->|Yes| Deploy[Deploy to Production]
        FinalApproval -->|No| Archive[Archive Rule]

        Deploy --> Monitor[Continuous Monitoring]
        Monitor --> End([Complete])
        Reject --> End
        Archive --> End
    end

    style DataPreparationPhase fill:#e1f5fe
    style AlgorithmTrainingPhase fill:#f3e5f5
    style RuleOptimizationPhase fill:#fff9c4
    style DeploymentEvaluationPhase fill:#c8e6c9
```

### Model Training Pipeline

```mermaid
flowchart LR
    subgraph "Data Phase"
        DC[Data Collection] --> DV[Data Validation]
        DV --> DT[Data Transformation]
    end

    subgraph "Feature Phase"
        DT --> FE[Feature Engineering]
        FE --> FS[Feature Selection]
        FS --> FStore[(Feature Store)]
    end

    subgraph "Training Phase"
        FStore --> Split[Data Split]
        Split --> Train[Model Training]
        Train --> Validate[Model Validation]
        Validate --> HyperTune[Hyperparameter Tuning]
    end

    subgraph "Evaluation Phase"
        HyperTune --> Eval[Model Evaluation]
        Eval --> Compare{Compare with<br/>Champion Model}
        Compare -->|Better| Register[Register Challenger]
        Compare -->|Worse| Discard[Discard Model]
    end

    subgraph "Deployment Phase"
        Register --> Package[Model Packaging]
        Package --> ABTestDeploy[A/B Test Deployment]
        ABTestDeploy --> MonitorAB[Monitor A/B Test]
        MonitorAB --> Promote{Promote to Champion?}
        Promote -->|Yes| ProdDeploy[Production Deployment]
        Promote -->|No| Rollback[Rollback]
        ProdDeploy --> ContinuousMonitor[Continuous Monitoring]
    end

    Discard -.feedback.-> FE
    Rollback -.feedback.-> Train

    style DataPhase fill:#e8eaf6
    style FeaturePhase fill:#f3e5f5
    style TrainingPhase fill:#e0f2f1
    style EvaluationPhase fill:#fff3e0
    style DeploymentPhase fill:#e8f5e9
```

---

## Data Processing Pipeline

### Real-time Data Flow Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        Txns[Transaction Event Stream]
        User[User Behavior Data]
        External[External Data Sources]
    end

    subgraph "Ingestion Layer"
        Txns --> KafkaTxn[Kafka Topic:<br/>transactions]
        User --> KafkaUser[Kafka Topic:<br/>user-events]
        External --> KafkaExt[Kafka Topic:<br/>external-data]
    end

    subgraph "Stream Processing Layer (Flink)"
        KafkaTxn --> FlinkJob1[Real-time Aggregation]
        KafkaUser --> FlinkJob2[User Profile Job]
        KafkaExt --> FlinkJob3[Data Enrichment Job]

        FlinkJob1 --> Window1[Sliding Window<br/>5 minutes]
        FlinkJob2 --> Window2[Session Window]
        FlinkJob3 --> Window3[Tumbling Window<br/>1 hour]
    end

    subgraph "Feature Computation"
        Window1 --> Metrics[Real-time Metric Calculation]
        Window2 --> Profile[User Profile Update]
        Window3 --> Enrichment[Data Enrichment]

        Metrics --> FeatureCache[(Redis<br/>Feature Cache)]
        Profile --> FeatureCache
        Enrichment --> FeatureCache
    end

    subgraph "Storage Layer"
        FeatureCache --> RealTime[Real-time Query]

        Metrics --> OLAP[(BigQuery<br/>OLAP)]
        Profile --> OLTP[(PostgreSQL<br/>OLTP)]
        Enrichment --> DataLake[(S3<br/>Data Lake)]
    end

    subgraph "Consumer Layer"
        RealTime --> AlertSystem[Alert System]
        RealTime --> MLInference[ML Inference]
        OLAP --> Analytics[Offline Analytics]
        OLTP --> API[API Query]
        DataLake --> Training[Model Training]
    end

    style IngestionLayer fill:#e3f2fd
    style StreamProcessingLayerFlink fill:#f3e5f5
    style FeatureComputation fill:#fff3e0
    style StorageLayer fill:#e8f5e9
```

### Batch Processing Data Flow

```mermaid
flowchart TD
    subgraph "Scheduler Layer"
        Scheduler[Airflow Scheduler]
    end

    subgraph "Data Extraction"
        Scheduler --> Extract1[Extract Transaction Data]
        Scheduler --> Extract2[Extract User Data]
        Scheduler --> Extract3[Extract Label Data]
    end

    subgraph "ETL Processing"
        Extract1 --> Transform[Spark Transform Job]
        Extract2 --> Transform
        Extract3 --> Transform

        Transform --> Clean[Data Cleaning]
        Clean --> Join[Data Joining]
        Join --> Aggregate[Data Aggregation]
    end

    subgraph "Feature Engineering"
        Aggregate --> FeatureCalc[Feature Calculation]
        FeatureCalc --> FeatureValidate[Feature Validation]
        FeatureValidate --> FeatureStore[(Feature Store)]
    end

    subgraph "Model Training"
        FeatureStore --> SampleData[Sample Data]
        SampleData --> TrainModel[Train Model]
        TrainModel --> EvalModel[Evaluate Model]
        EvalModel --> SaveModel[(Model Storage)]
    end

    subgraph "Rule Generation"
        FeatureStore --> RuleGenJob[Rule Generation Job]
        SaveModel --> RuleGenJob
        RuleGenJob --> RuleValidate[Rule Validation]
        RuleValidate --> RuleStore[(Rule Repository)]
    end

    subgraph "Quality Check"
        Transform -.quality check.-> QC[Data Quality Monitoring]
        FeatureCalc -.quality check.-> QC
        TrainModel -.quality check.-> QC
        RuleGenJob -.quality check.-> QC
    end

    QC --> Alert{Quality Issue?}
    Alert -->|Yes| NotifyTeam[Notify Team]
    Alert -->|No| Success[Job Success]
```

---

## Deployment Architecture

### Kubernetes Deployment Topology

```mermaid
graph TB
    subgraph "Ingress Layer"
        Internet([Internet])
        CDN[CDN]
        WAF[WAF Firewall]
        LB[Load Balancer<br/>ALB/NLB]
    end

    subgraph "K8s Cluster - AZ 1"
        subgraph "Namespace: sentinel-prod"
            API1[API Pod x3]
            Alert1[Alert Engine Pod x2]
            AI1[AI Engine Pod x2]
            Rule1[Rule Engine Pod x2]
        end

        subgraph "Namespace: automation"
            AutoRule1[Rule Gen Pod x2]
            Train1[Training Pod x2]
        end
    end

    subgraph "K8s Cluster - AZ 2"
        subgraph "Namespace: sentinel-prod "
            API2[API Pod x3]
            Alert2[Alert Engine Pod x2]
            AI2[AI Engine Pod x2]
            Rule2[Rule Engine Pod x2]
        end

        subgraph "Namespace: automation "
            AutoRule2[Rule Gen Pod x2]
            Train2[Training Pod x2]
        end
    end

    subgraph "K8s Cluster - AZ 3"
        subgraph "Namespace: sentinel-prod  "
            API3[API Pod x3]
            Alert3[Alert Engine Pod x2]
            AI3[AI Engine Pod x2]
            Rule3[Rule Engine Pod x2]
        end

        subgraph "Namespace: automation  "
            AutoRule3[Rule Gen Pod x2]
            Train3[Training Pod x2]
        end
    end

    subgraph "Data Layer - Multi-AZ"
        PG[(PostgreSQL<br/>Primary + 2 Replicas)]
        Redis[(Redis Cluster<br/>6 Nodes)]
        Kafka[(Kafka Cluster<br/>3 Brokers)]
    end

    subgraph "External Services"
        BigQuery[(BigQuery)]
        S3[(S3)]
        Monitoring[Prometheus/Grafana]
    end

    Internet --> CDN
    CDN --> WAF
    WAF --> LB

    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> Alert1
    API2 --> Alert2
    API3 --> Alert3

    Alert1 --> AI1
    Alert2 --> AI2
    Alert3 --> AI3

    AI1 --> Rule1
    AI2 --> Rule2
    AI3 --> Rule3

    API1 & API2 & API3 --> PG
    Alert1 & Alert2 & Alert3 --> Redis
    Alert1 & Alert2 & Alert3 --> Kafka

    Train1 & Train2 & Train3 --> BigQuery
    Train1 & Train2 & Train3 --> S3

    API1 & API2 & API3 -.metrics.-> Monitoring
    Alert1 & Alert2 & Alert3 -.metrics.-> Monitoring

    style AZ1 fill:#e3f2fd
    style AZ2 fill:#f3e5f5
    style AZ3 fill:#fff3e0
```

### Service Mesh Architecture

```mermaid
graph LR
    subgraph "Service Mesh (Istio)"
        subgraph "Control Plane"
            Pilot[Pilot<br/>Traffic Management]
            Citadel[Citadel<br/>Security Auth]
            Galley[Galley<br/>Config Management]
        end

        subgraph "Data Plane"
            subgraph "Pod A"
                App1[App Container]
                Envoy1[Envoy Sidecar]
            end

            subgraph "Pod B"
                App2[App Container]
                Envoy2[Envoy Sidecar]
            end

            subgraph "Pod C"
                App3[App Container]
                Envoy3[Envoy Sidecar]
            end
        end
    end

    Pilot -.config.-> Envoy1
    Pilot -.config.-> Envoy2
    Pilot -.config.-> Envoy3

    Citadel -.certs.-> Envoy1
    Citadel -.certs.-> Envoy2
    Citadel -.certs.-> Envoy3

    App1 --> Envoy1
    Envoy1 -->|mTLS| Envoy2
    App2 --> Envoy2
    Envoy2 -->|mTLS| Envoy3
    App3 --> Envoy3

    Envoy1 & Envoy2 & Envoy3 -.telemetry.-> Telemetry[Telemetry Collector]
    Telemetry --> Prometheus[Prometheus]
    Telemetry --> Jaeger[Jaeger Tracing]
```

---

## User Interaction Flow

### Merchant Journey Using Sentinel

```mermaid
journey
    title Merchant Journey to Defend Against Fraud Attacks
    section Monitoring Phase
      Normal transaction processing: 5: Merchant, System
      System continuous monitoring: 5: System
      Detect anomaly: 3: System
    section Alert Phase
      Receive in-app notification: 4: Merchant
      Receive email alert: 4: Merchant
      View alert details: 4: Merchant
      AI analysis report display: 5: Merchant, AI
    section Decision Phase
      Review recommended rule: 5: Merchant
      Understand impact scope: 5: Merchant
      Click one-click deploy: 5: Merchant
    section Deployment Phase
      Rule enters shadow mode: 4: System
      Monitor performance metrics: 4: Merchant, System
      Confirm rule live: 5: Merchant
      Rule takes effect blocking: 5: System
    section Feedback Phase
      Attack successfully blocked: 5: Merchant, System
      View protection report: 5: Merchant
      Submit feedback: 5: Merchant
      Return to normal business: 5: Merchant
```

### User Operation Sequence Diagram

```mermaid
sequenceDiagram
    actor Merchant as Merchant
    participant UI as Dashboard
    participant API as API Service
    participant Alert as Alert Service
    participant AI as AI Engine
    participant Deploy as Deployment Engine
    participant Risk as Risk Engine

    Note over Merchant,Risk: Scenario: Receive fraud alert and deploy rule

    Alert->>UI: 1. Push real-time alert
    UI->>Merchant: 2. Display alert notification

    Merchant->>UI: 3. Click to view details
    UI->>API: 4. GET /alerts/{id}
    API->>Alert: 5. Query alert details
    Alert->>AI: 6. Get AI analysis result
    AI-->>Alert: 7. Return analysis report
    Alert-->>API: 8. Return complete data
    API-->>UI: 9. Return JSON
    UI->>Merchant: 10. Display detailed analysis

    Note over Merchant: Merchant reviews analysis report<br/>and decides whether to deploy rule

    Merchant->>UI: 11. Click "One-Click Deploy"
    UI->>API: 12. POST /rules/deploy
    API->>Deploy: 13. Create deployment task

    par Parallel operations
        Deploy->>Deploy: 14a. Rule validation
        Deploy->>Deploy: 14b. Conflict detection
    end

    Deploy->>Risk: 15. Shadow mode deployment
    Deploy-->>UI: 16. Return deployment status
    UI->>Merchant: 17. Display "Shadow mode running"

    loop Shadow mode monitoring (5-10 minutes)
        Risk->>Deploy: 18. Report performance metrics
        Deploy->>UI: 19. Update monitoring data
        UI->>Merchant: 20. Real-time display metrics
    end

    alt Good performance
        Deploy->>Risk: 21. Go live with rule
        Risk-->>Deploy: 22. Confirm live
        Deploy->>UI: 23. Notify live success
        UI->>Merchant: 24. Display "Rule is active"

        Note over Merchant,Risk: Rule starts blocking fraud transactions

    else Poor performance
        Deploy->>UI: 21. Notify need optimization
        UI->>Merchant: 22. Show tuning suggestions
    end

    Merchant->>UI: 25. View protection effectiveness
    UI->>API: 26. GET /rules/{id}/metrics
    API-->>UI: 27. Return blocking statistics
    UI->>Merchant: 28. Display report

    Merchant->>UI: 29. Submit feedback (👍/👎)
    UI->>API: 30. POST /feedback
    API->>AI: 31. Record feedback for training
```

---

## Rule Lifecycle Management

### Complete Lifecycle from Creation to Retirement

```mermaid
stateDiagram-v2
    [*] --> Created: Rule generated

    Created --> Validated: Pass validation
    Created --> Rejected: Validation failed

    Validated --> Shadow: Shadow deployment
    Shadow --> ShadowMonitoring: Monitoring

    ShadowMonitoring --> Live: Performance meets criteria<br/>Go live
    ShadowMonitoring --> Tuning: Needs tuning
    ShadowMonitoring --> Rejected: Poor performance

    Tuning --> Shadow: Re-test

    Live --> Active: Rule activated
    Active --> Monitoring: Continuous monitoring

    Monitoring --> Active: Normal operation
    Monitoring --> Degraded: Performance degradation
    Monitoring --> Conflicted: Rule conflict

    Degraded --> Warning: Issue warning
    Warning --> Active: Recover to normal
    Warning --> Tuning: Needs optimization
    Warning --> Deprecated: Mark as deprecated

    Conflicted --> Resolution: Conflict resolution
    Resolution --> Active: Resolution complete
    Resolution --> Deprecated: Cannot resolve

    Deprecated --> RetirementNotice: Issue retirement notice
    RetirementNotice --> GracePeriod: Grace period (2 weeks)

    GracePeriod --> Retired: Auto retire
    GracePeriod --> Active: Merchant renewal

    Retired --> Archived: Archive
    Rejected --> Archived: Archive

    Archived --> [*]

    note right of Created
        Rule sources:
        - AI auto-generated
        - Manual creation
        - Template instantiation
    end note

    note right of Live
        Deployment strategy:
        - Canary release
        - Blue-green deployment
        - A/B testing
    end note

    note right of Monitoring
        Monitoring metrics:
        - Precision
        - Recall
        - False positive rate
        - Execution latency
    end note
```

---

## Security Architecture

### Multi-layer Security Protection

```mermaid
graph TB
    subgraph "Perimeter Security"
        Internet([Internet]) --> DDoS[DDoS Protection]
        DDoS --> WAF[WAF Firewall]
        WAF --> RateLimit[Rate Limiting]
    end

    subgraph "Network Security"
        RateLimit --> VPC[VPC Isolation]
        VPC --> SecurityGroup[Security Groups]
        SecurityGroup --> NetworkACL[Network ACL]
    end

    subgraph "Application Security"
        NetworkACL --> AuthN[Authentication]
        AuthN --> OAuth[OAuth 2.0]
        AuthN --> JWT[JWT Validation]
        AuthN --> MFA[Multi-factor Auth]

        OAuth --> AuthZ[Authorization]
        JWT --> AuthZ
        MFA --> AuthZ

        AuthZ --> RBAC[RBAC Access Control]
        RBAC --> API[API Services]
    end

    subgraph "Data Security"
        API --> Encryption{Encryption Layer}
        Encryption --> TLS[TLS 1.3<br/>Encryption in Transit]
        Encryption --> AES[AES-256<br/>Encryption at Rest]
        Encryption --> Tokenization[PII Tokenization]
    end

    subgraph "Service Security"
        API --> ServiceMesh[Service Mesh]
        ServiceMesh --> mTLS[mTLS Authentication]
        mTLS --> Services[Microservices]
    end

    subgraph "Audit & Compliance"
        Services --> AuditLog[Audit Logs]
        AuditLog --> SIEM[SIEM System]
        SIEM --> Compliance[Compliance Checks]
        Compliance --> PCI[PCI DSS]
        Compliance --> GDPR[GDPR]
        Compliance --> SOC2[SOC 2]
    end

    subgraph "Monitoring & Alerting"
        Services -.anomaly detection.-> IDS[Intrusion Detection]
        IDS --> SecurityAlert[Security Alerts]
        SecurityAlert --> SOC[Security Operations Center]
    end

    style PerimeterSecurity fill:#ffcdd2
    style NetworkSecurity fill:#f8bbd0
    style ApplicationSecurity fill:#e1bee7
    style DataSecurity fill:#c5cae9
    style ServiceSecurity fill:#bbdefb
    style Audit&Compliance fill:#b2dfdb
```

---

## Monitoring & Alerting System

### Observability Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        Service1[Service A]
        Service2[Service B]
        Service3[Service C]
    end

    subgraph "Data Collection"
        Service1 & Service2 & Service3 --> Metrics[Metrics Collector]
        Service1 & Service2 & Service3 --> Logs[Logs Collector]
        Service1 & Service2 & Service3 --> Traces[Traces Collector]
    end

    subgraph "Storage Layer"
        Metrics --> Prometheus[(Prometheus)]
        Logs --> Elasticsearch[(Elasticsearch)]
        Traces --> Jaeger[(Jaeger)]
    end

    subgraph "Analysis Layer"
        Prometheus --> Grafana[Grafana Dashboard]
        Elasticsearch --> Kibana[Kibana Log Analysis]
        Jaeger --> TraceUI[Trace Visualization]
    end

    subgraph "Alerting Layer"
        Grafana --> AlertManager[Alert Manager]
        Kibana --> Watcher[Elasticsearch Watcher]

        AlertManager --> PagerDuty[PagerDuty]
        AlertManager --> Slack[Slack]
        AlertManager --> Email[Email]

        Watcher --> PagerDuty
        Watcher --> Slack
    end

    subgraph "Intelligent Analysis"
        Prometheus --> AIOps[AIOps Engine]
        Elasticsearch --> AIOps
        AIOps --> AnomalyDet[Anomaly Detection]
        AnomalyDet --> RootCause[Root Cause Analysis]
        RootCause --> AutoRemediation[Auto Remediation]
    end

    style DataCollection fill:#e3f2fd
    style StorageLayer fill:#f3e5f5
    style AnalysisLayer fill:#fff3e0
    style AlertingLayer fill:#ffebee
    style IntelligentAnalysis fill:#e8f5e9
```

### Key Metrics Dashboard

```mermaid
mindmap
  root((Monitoring Metrics))
    Business Metrics
      Alert generation rate
      Rule deployment success rate
      Fraud blocked count
      False positive rate
      Merchant satisfaction
    Performance Metrics
      API latency
        p50
        p95
        p99
      Throughput
        TPS
        QPS
      Availability
        SLA
        Uptime
    System Metrics
      CPU usage
      Memory usage
      Disk I/O
      Network bandwidth
      Connection count
    ML Metrics
      Model accuracy
      Inference latency
      Feature computation time
      Model drift
      Data quality
    Data Metrics
      Database performance
        Query latency
        Connection pool usage
        Slow queries
      Cache performance
        Hit ratio
        Eviction rate
        Memory usage
      Message queue
        Queue depth
        Consumer lag
        Backlog
```

---

## Disaster Recovery & High Availability

### Failover Process

```mermaid
sequenceDiagram
    participant LB as Load Balancer
    participant Primary as Primary Service (AZ-1)
    participant Secondary as Secondary Service (AZ-2)
    participant HealthCheck as Health Check
    participant Monitor as Monitoring System
    participant Ops as Operations Team

    loop Continuous health check
        HealthCheck->>Primary: Health check
        Primary-->>HealthCheck: 200 OK
    end

    Note over Primary: Primary service failure

    HealthCheck->>Primary: Health check
    Primary--xHealthCheck: Timeout/Error

    HealthCheck->>HealthCheck: Retry 3 times
    HealthCheck->>Primary: Check again
    Primary--xHealthCheck: Continuous failure

    HealthCheck->>Monitor: Report failure
    Monitor->>Ops: Send alert

    HealthCheck->>LB: Mark primary unavailable
    LB->>LB: Update routing table

    Note over LB,Secondary: Traffic switches to secondary

    LB->>Secondary: Forward all traffic
    Secondary-->>LB: Normal response

    par Parallel operations
        Monitor->>Monitor: Record failure event
    and
        Ops->>Primary: Start failure diagnosis
    and
        Secondary->>Secondary: Handle all traffic
    end

    Ops->>Primary: Recovery complete
    Primary->>HealthCheck: Restore normal

    HealthCheck->>LB: Mark primary available
    LB->>LB: Gradually restore traffic

    Note over LB: Use canary release<br/>gradually switch traffic

    LB->>Primary: 10% traffic
    LB->>Secondary: 90% traffic

    alt Primary stable
        LB->>Primary: 50% traffic
        LB->>Secondary: 50% traffic
        LB->>Primary: 100% traffic
        Note over LB,Secondary: Fully recovered
    else Primary still unstable
        LB->>Secondary: 100% traffic
        Note over Ops: Continue troubleshooting
    end
```

---

## Cost Optimization Strategy

### Resource Usage Optimization

```mermaid
graph TD
    subgraph "Compute Resource Optimization"
        AutoScale[Auto Scaling]
        SpotInstance[Spot Instances]
        RightSize[Instance Rightsizing]

        AutoScale --> HPA[HPA Horizontal Scaling]
        AutoScale --> VPA[VPA Vertical Scaling]
        AutoScale --> CronScale[Scheduled Scaling]
    end

    subgraph "Storage Optimization"
        DataLifecycle[Data Lifecycle]
        Compression[Data Compression]
        Dedup[Data Deduplication]

        DataLifecycle --> HotData[Hot Data: SSD]
        DataLifecycle --> WarmData[Warm Data: HDD]
        DataLifecycle --> ColdData[Cold Data: Archive]
    end

    subgraph "Network Optimization"
        CDN[CDN Acceleration]
        Caching[Smart Caching]
        DataTransfer[Data Transfer Optimization]
    end

    subgraph "ML Training Optimization"
        SpotTraining[Spot Instance Training]
        Quantization[Model Quantization]
        Pruning[Model Pruning]
        DistilledModel[Model Distillation]
    end

    subgraph "Monitoring & Optimization"
        CostMonitor[Cost Monitoring]
        CostAlert[Cost Alerts]
        CostReport[Cost Reports]

        CostMonitor --> Analyze[Cost Analysis]
        Analyze --> Optimize[Optimization Recommendations]
    end

    HPA & VPA & CronScale --> Analyze
    HotData & WarmData & ColdData --> Analyze
    SpotInstance --> Analyze
    SpotTraining --> Analyze

    Optimize --> Actions[Execute Optimization]

    style ComputeResourceOptimization fill:#e3f2fd
    style StorageOptimization fill:#f3e5f5
    style NetworkOptimization fill:#fff3e0
    style MLTrainingOptimization fill:#e8f5e9
    style Monitoring&Optimization fill:#fce4ec
```

---

## Summary

This document provides complete architecture and process visualization for the Airwallex Sentinel project, including:

- ✅ **System Architecture**: High-level architecture and component relationships
- ✅ **Business Flows**: Real-time detection, AI analysis, rule deployment
- ✅ **Technical Flows**: Data processing, model training, automation platform
- ✅ **Deployment Architecture**: Kubernetes, multi-AZ, service mesh
- ✅ **User Experience**: Merchant journey and interaction flows
- ✅ **Security & Compliance**: Multi-layer security protection system
- ✅ **Operations**: Monitoring, disaster recovery, cost optimization

These diagrams help the team better understand the system design, facilitate cross-team collaboration, and serve as reference documentation for development and operations.

---

**Document Maintenance:** Please update relevant diagrams when architecture changes
**Viewing Recommendation:** Use a Markdown reader that supports Mermaid to view this document
