# PA Fraud Solution Automation Landscape

## Project Objective

**Vision:** Enable innovative, scalable and automated risk decisions and strategies

- Full decision layer automation relying on smart and rapid model refresh based on incremental learnings supported by reliable and scalable solutions and infrastructure
- Innovative products and risk engine features with collaboration
- Improve operation efficiency and expand merchant support coverage with scalabilities

**Thinking:** Integrate AI in PA automation to make process more streamlined

---

## Automation Coverage

### Model and Infra

- Infra and pipeline support auto and smart model refresh, update and replacement
- Infra to support rule generation offline to shadow/live online and real time monitoring

### Solution Automation

#### Auto Strategy Refresh
- Reliable and flexible strategy refresh - cutoff optimization with handshake with model refresh, dominant to high portfolio loss catch, auto designed high level segmentation
- Simple strategy rules update from offline and online cutoff update

#### Automation Tools Targeting Fraud Attack Mitigation
- Auto-solution with supervised loss reduction at segment level like regional, industry, flows etc.
- Auto-solution with unsupervised loss reduction (cluster or self-supervised using Poisson distribution etc.)
- Auto-solution on merchant level with pre-defined rule sets or new use case from supervised auto-solution tool

#### Automation Tools Targeting Rule Governance and Risk Engine Eco System
- Rule historical data backtesting automation - save a lot of manual effort
- Rule auto-retirement
- Rule auto-refinement tool from monthly report and new logic generation
- Streamlined model retirement / replacement pipeline for rules

#### Business Enablement Use Case (Potentially)
- Quickly adjust scores or create new low risk solutions when support flash sale, hot event on both seasonal & market level and merchant level

---

## OKR Impact

- **Significant fraud loss reduction** → Target at least 30%-50% loss reduction
- **Low false decline rate on risk engine eco-system** → Target at least 30% false decline reduction to <1%
- **Reduce operation effort** - rule writing and maintenance → Target at least 60% human efforts reduction
- **Shorten response time for merchant escalation** → Target at least 60% response time and for some repeated attack, target 80% response time

---

## Rapid Model Refresh

### High Level Workflow

Need further discussion with MLE about rapid refresh pipeline as ground strategy solutions and continuous learning to improve model performance (algorithm and features)

---

## Strategy Rapid Refresh

### Steps

1. **Data preparation (Joint data pull):** Feature bank, model list and key metrics, labels, champion and challenge models
2. **Define strategy segmentation** (based on business needs, risk engine flows)
3. **Define algorithm target** (precision, recall, action etc.)
4. **Select algorithm**
5. **Build objective function** (add weight or adjust based on segments/data qualities)
6. **Generate score cutoff and feature combination**
7. **Update in offline table and template**
8. **Translate to online rules**
9. **Push rules in Shadow with evaluation and auto-monitoring** - compare champion rule sets vs. challenge rule sets
10. **Meet shadow results and auto-live, auto-retire poor performing one**
11. **Visualization and summarize in report**
12. **Monitoring dashboard**

### Strategy Segmentation

- Designed based on risk engine 2.0 profiles
- Exclusive from distinguished flows due to business nature like Sub-MIT, bank transfer, POS, AFT, general card processing, etc.
- Meet commercial and industry appetite like Young sellers, Platform sellers, digital (high profit) sellers and non-digital sellers (OTA, livestreaming etc.)
- Meet buyer behavior and trust nature to reduce frictions: consistency of assets, trust behaviors
- Risk action selection based on precision

### Algorithms Selection

XGboost, Greedy, Intelligent Exhaustive Search, MaxDifferentiated Tree etc.

---

## Infra Capabilities

### Refresh Rhythm

- Routine model (incremental learnings) & strategy refresh
- On-demand strategy refresh
- Smart triggering model & strategy refresh

### Automation Toolkits

- Capability to send offline score & segment pair to online
- Efficient BQ operation toolkits
- Rule translation
- Rule on-off backtest, auto-shadow, auto-live per performance
- Rule sets comparisons
- Tech check to live adjudicate / retirement
- Automatic adjudication or retirement based on simulated results (i.e. auto compare champion model to decide if approve challenge model)
- Multiple segment level and feature selection supported
- Users can config start point (enforce feature like model or industry etc.)
- Various features: running windows, historical evaluation etc.

---

## Automation Tools for Surgical Solutions

### Current Challenge and Opportunities

#### Starting Point (Alerting Portal)

Need a general alerting portal powered with AI to manage all kinds of alerting / rule setting reminder requests / records.

- Segment fraud early detection (i.e. regional, industry or cluster etc.)
- Merchant level fraud early detection (i.e. certain threshold)
- Rule level abnormality detection
- Adhoc alerting or monitoring needs

#### Rule Auto-Generation (pending: how to use AI on this)

- Use case for segment level and portfolio optimization
- Use case for merchant level new fraud pattern
- Use case for repeatedly happened merchant level fraud trend
- Use AI to explain rule configuration internal use - role/profile/inconsistency/...

### Automation Toolkits

#### Use Case 1 & 2:

- Python package
- Visualized portal with stages, configurable settings on different use cases
- Enriched algorithms and algo selection
- Offline to online rule logic translation
- Auto shadow evaluation and one-click live/release process
- Post-release benefits monitoring

#### Use Case 3:

- Existing rulesets with most frequently happened rules (patterns)
- Easy backtesting or leverage async shadow results from rulesets
- Simulate performance (precision, recall) on merchant level for existing rulesets
- If one merchant's performance meet threshold, set flag to apply rules on merchant's traffic automatically with default expiration days

### Infra Capabilities

- AI alerts (need a separate Alerting portal to generate different alerting logics in records)
- Easy backtesting
- Rule offline to online translation and auto-release
- Visualization and real time abnormality alerting
- Externalization of automation tools
- Auto flag setting offline to online on merchant level

---

## Automation Tools for Rule Management

### High Level Workflow

#### Use Cases:

1. Rule historical data backtesting automation - save a lot of manual effort (merchant level rule expansion use case)
2. Rule auto-retirement
3. Rule auto-refinement tool from monthly report and new logic generation
4. Streamlined model retirement / replacement pipeline for rules

### Automation Toolkit

- Soft label in dataset
- Rule auto-retirement with rounds of notice to owner based on weekly/monthly report
- Rule auto fine-tuning pipeline based on control group and soft label → different data preparation and target setting similar to fraud mitigation algorithm
- Model score recommender for model retirement (MLE existing tool phase I)
- Model score mass replacement with offline to online push
- Rule governance portal (performance, rule owners, tag, profile, layers, reasons of keep rules though low performance)

### Infra Capabilities (Pending)

- Risk engine 2.0 design
- Rule auto retirement based on monitoring
- Model score mass replacement
- Rule governance portal and functions

---

## Early Fraud Detection

### Methodology

- Supervised leveraging soft label (safe or risky, confidence level, urgency level, decision level)
- Unsupervised leveraging graph and clustering based on linking, abnormal volume surge, multi-alert signals
- Identify past attacks and remove impacted statistics to ensure alert accuracy
- Visualization in report / dashboard and pattern summary

---

## Path to Full Automation Landscape

### Phase I

- **Urgency** - Achieve strategy solution automation to save manual efforts on rule generation due to high frequency of this use case
- **Urgency** - Achieve merchant level solution (use case 2) automation to save manual efforts on rule generation due to high frequency of this use case. Select common rule sets for use case 3
- **2026Q1** - Rule monitoring and auto-retirement (pending SOP)
- **2026Q2** - Rule auto-refinement

### Phase II

- **2026Q2** - Merchant level pre-define rulesets automation with easy backtesting feature
- **2026Q2** - Model score auto-replacement
- **2026Q3** - Strategy automation

### Phase III

- **Long term** - Model + strategy handshake automation

---

## Sub-project List (WIP)

### Brainstorming (What AI Can Do)

- AI visualization (Web portal)
- AI rule recommendation (Risk webapp externalization)

### Project Details

| Sub-project | Ownership | Priority | Effort - Timeline | Benefits | Memo |
|-------------|-----------|----------|-------------------|----------|------|
| **Rule auto-generator v1** - XGBoost based | @Zhaoyu Zuo | High | L - 2025Q4 | Save effort | First version in Python package. Ideal version should be on a Web portal |
| **Unified solution training data preparation** | @Zhaoyu Zuo | High | M - 2025Q4 | | |
| **Rule auto-generator v2** - merchant level fine-tune | @Zhaoyu Zuo @Wanqiu Zheng | High | | | Data preparation pipeline. Threshold for merchant rules. Fraud label- combine soft label or cross sampling. Algorithm finetune |
| **Rule auto training portal** | | | | | |
| **Rule AI recommendation externalization on Risk Webapp** | @Mark Song | | | | Integrate with AI - better visualization through AI features |
| **Rule Offline to Online translation** | @Mark Song | | M | | |
| **Strategy segment rule score cutoff selection** | @Zhaoyu Zuo | | M | | |
| **Strategy segment rule offline to online flexible mapping** | @Mark Song | | M-L | | |
| **Rule auto-shadow from offline logic** | @Mark Song | | L | | Through offline rule translation, can easily push to live in shadow mode |
| **Rule auto-retirement report** | @Jazreel Tho @Wanqiu Zheng | | M | | Strategy rule threshold, notification, exemption. Merchant rule (soft label) threshold, notification and exemption |
| **Rule auto-retirement function backend** | @Mark Song | | M | | |
| **Easy backtesting** | @Mark Song @Yusup Aixirefu | | L | | Currently we can't easily backtesting logic from a shadow rule or action rule on other merchants or segments @Zhaoyu Zuo can you describe more details? |
| **Merchant level pre-defined rule sets** | @Wanqiu Zheng @Zhaoyu Zuo | | M-L | | Through solution auto-training tool, generate merchant level common rule sets. Leverage easy backtesting function to simulate on other merchants |
| **Auto-flag setting** | @Wanqiu Zheng @Mark Song | | | | |
| **Merchant level pre-define rulesets auto expansion** | @Wanqiu Zheng | | | | Alert on merchant level (ready). Easy backtesting from existing rules (logic only). Apply flag mapping to rules. Live existing rule for other merchants with similar attack |
| **AI feature generation from alert leads** | @Yusup Aixirefu @Jason Miao | | L - end of year for exploration | | Exploration especially when no solution from XGboost and need manual solution to explore new features |
| **Wave-Catcher AI alerting** | @Jazreel Tho | | L | | Try some alerting methodologies combining soft label |

---

## Appendix

### Automation Tools for Model Retirement (Pilot from MLE tool)

#### Pain Points

- Increasing needs to simplify the ecosystem
- Extensive human efforts to retire models in rules
- Lack of auto-impact analysis
- Lack of E2E SOP to connect dots

#### Solution

- A standardized and efficient efficiency process with automation capabilities and cross-functional collaboration
- Leverage AI to further simplify the process under manual audit

#### Goal

- Save human efforts
- Accelerate retirement cycle
- Simplify the system
- Externalization - easy usage for merchant to replace models with AI
