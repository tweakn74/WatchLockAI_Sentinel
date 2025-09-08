# WatchLockAI Sentinel Anomaly Detection Data Path

This diagram illustrates the anomaly detection pipeline, from raw event data through feature extraction to threat scoring and response actions.

```mermaid
graph TD
    %% Raw Event Input
    A[Raw System Events] --> B[Event Normalization]
    A1[File System Events] --> B
    A2[Network Events] --> B
    A3[Process Events] --> B
    A4[Registry Events] --> B

    %% Event Processing
    B --> C[Event Filtering]
    C --> D{Event Relevance?}
    D -->|Relevant| E[Feature Extraction]
    D -->|Irrelevant| F[Discard Event]

    %% Feature Engineering
    E --> G[Statistical Features]
    E --> H[Behavioral Features]
    E --> I[Temporal Features]
    E --> J[Contextual Features]

    %% Statistical Analysis
    G --> K[Frequency Analysis]
    G --> L[Distribution Analysis]
    G --> M[Baseline Comparison]

    %% Behavioral Pattern Analysis
    H --> N[Process Behavior]
    H --> O[Network Patterns]
    H --> P[File Access Patterns]
    H --> Q[User Activity Patterns]

    %% Temporal Pattern Analysis
    I --> R[Time Series Analysis]
    I --> S[Sequence Detection]
    I --> T[Periodicity Analysis]

    %% Contextual Analysis
    J --> U[Environment Context]
    J --> V[User Context]
    J --> W[System State Context]

    %% Anomaly Detection Engines
    K --> X[Anomaly Detector]
    L --> X
    M --> X
    N --> X
    O --> X
    P --> X
    Q --> X
    R --> X
    S --> X
    T --> X
    U --> X
    V --> X
    W --> X

    %% Detection Algorithms
    X --> Y[Statistical Outlier Detection]
    X --> Z[Threshold-Based Detection]
    X --> AA[Machine Learning Scoring]
    X --> BB[Rule-Based Detection]

    %% Scoring and Ranking
    Y --> CC[Anomaly Score Calculation]
    Z --> CC
    AA --> CC
    BB --> CC

    CC --> DD[Score Normalization]
    DD --> EE[Risk Assessment]

    %% Threshold Evaluation
    EE --> FF{Score > Threshold?}
    FF -->|Yes| GG[Alert Generation]
    FF -->|No| HH[Log for Analysis]

    %% Alert Processing
    GG --> II[Alert Prioritization]
    II --> JJ[Alert Correlation]
    JJ --> KK[Response Action Selection]

    %% Response Actions
    KK --> LL[Quarantine Action]
    KK --> MM[Notification Action]
    KK --> NN[Logging Action]
    KK --> OO[Monitoring Enhancement]

    %% Quarantine Flow
    LL --> PP[Quarantine Assessment]
    PP --> QQ{Safe to Quarantine?}
    QQ -->|Yes| RR[Move to Quarantine]
    QQ -->|No| SS[Enhanced Monitoring]

    %% Learning and Adaptation
    CC --> TT[Model Training Data]
    EE --> TT
    GG --> UU[Feedback Collection]
    UU --> VV[Model Retraining]
    VV --> AA

    %% Configuration Control
    WW[Anomaly Config] --> XX[Detection Thresholds]
    WW --> YY[Feature Weights]
    WW --> ZZ[Model Parameters]

    XX --> FF
    YY --> CC
    ZZ --> AA

    %% Performance Monitoring
    CC --> AAA[Detection Metrics]
    GG --> BBB[Alert Metrics]
    LL --> CCC[Response Metrics]

    AAA --> DDD[Performance Dashboard]
    BBB --> DDD
    CCC --> DDD

    %% Styling
    classDef input fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef processing fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef detection fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef response fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef storage fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef config fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class A,A1,A2,A3,A4,B,C,D,E,F input
    class G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W processing
    class X,Y,Z,AA,BB,CC,DD,EE,FF detection
    class GG,II,JJ,KK,LL,MM,NN,OO,PP,QQ,RR,SS response
    class HH,TT,UU,VV,AAA,BBB,CCC,DDD storage
    class WW,XX,YY,ZZ config
```

## Feature Extraction Pipeline

### Statistical Features
- **Frequency Analysis**: Event occurrence rates and patterns
- **Distribution Analysis**: Statistical distribution of event parameters
- **Baseline Comparison**: Deviation from established normal behavior

### Behavioral Features
- **Process Behavior**: Process creation patterns, parent-child relationships
- **Network Patterns**: Connection patterns, data transfer anomalies
- **File Access Patterns**: File system access patterns and permissions
- **User Activity Patterns**: User session and activity correlations

### Temporal Features
- **Time Series Analysis**: Trend detection and seasonal patterns
- **Sequence Detection**: Event sequence anomalies and outliers
- **Periodicity Analysis**: Detection of unusual timing patterns

### Contextual Features
- **Environment Context**: System state and configuration context
- **User Context**: User profile and historical behavior context
- **System State Context**: Current system load and resource utilization

## Detection Algorithms

### Statistical Outlier Detection
- **Z-Score Analysis**: Standard deviation-based outlier detection
- **Isolation Forest**: Unsupervised anomaly detection algorithm
- **Local Outlier Factor**: Density-based outlier detection

### Threshold-Based Detection
- **Static Thresholds**: Predefined limits for critical metrics
- **Dynamic Thresholds**: Adaptive limits based on historical data
- **Composite Thresholds**: Multi-dimensional threshold evaluation

### Machine Learning Scoring
- **Supervised Learning**: Trained models for known threat patterns
- **Unsupervised Learning**: Clustering and density estimation
- **Ensemble Methods**: Combined scoring from multiple algorithms

### Rule-Based Detection
- **Pattern Matching**: Signature-based threat detection
- **State Machines**: Complex behavioral pattern detection
- **Expert Rules**: Domain-specific detection rules

## Scoring and Risk Assessment

### Score Calculation
1. **Feature Normalization**: Scale features to comparable ranges
2. **Weight Application**: Apply configured feature importance weights
3. **Algorithm Combination**: Combine scores from multiple detection methods
4. **Score Normalization**: Normalize final score to 0-100 range

### Risk Classification
- **Low Risk (0-30)**: Normal behavior, log for analysis
- **Medium Risk (31-70)**: Suspicious behavior, enhanced monitoring
- **High Risk (71-90)**: Likely threat, generate alert
- **Critical Risk (91-100)**: Immediate threat, automatic response

## Response Actions

### Quarantine Actions
- **File Quarantine**: Move suspicious files to isolated storage
- **Process Termination**: Stop potentially malicious processes
- **Network Isolation**: Block suspicious network connections
- **User Account Lockout**: Temporarily disable compromised accounts

### Notification Actions
- **Real-time Alerts**: Immediate notification to administrators
- **Email Notifications**: Detailed alert information via email
- **System Tray Notifications**: Desktop notifications for local users
- **API Webhooks**: Integration with external alerting systems

### Monitoring Enhancement
- **Increased Sampling**: Higher frequency monitoring of affected areas
- **Additional Metrics**: Expanded data collection for investigation
- **Enhanced Logging**: Detailed logging of related activities
- **Forensic Collection**: Automated evidence collection

## Configuration and Tuning

### Detection Thresholds
- **Global Thresholds**: System-wide anomaly detection sensitivity
- **Per-Category Thresholds**: Specific thresholds for different event types
- **Dynamic Adjustment**: Automatic threshold tuning based on false positive rates

### Feature Configuration
- **Feature Selection**: Enable/disable specific feature categories
- **Weight Assignment**: Relative importance of different features
- **Normalization Parameters**: Feature scaling and transformation settings

### Model Parameters
- **Algorithm Selection**: Choose detection algorithms and ensemble methods
- **Training Parameters**: Model training configuration and hyperparameters
- **Update Frequency**: Model retraining and parameter update schedules

## Performance Monitoring

### Detection Metrics
- **True Positive Rate**: Correctly identified anomalies
- **False Positive Rate**: Incorrectly flagged normal behavior
- **Detection Latency**: Time from event to anomaly detection
- **Throughput**: Events processed per second

### Alert Metrics
- **Alert Volume**: Number of alerts generated per time period
- **Alert Accuracy**: Percentage of actionable alerts
- **Response Time**: Time from alert to response action
- **Resolution Time**: Time to investigate and resolve alerts

### System Performance
- **Resource Utilization**: CPU, memory, and storage usage
- **Processing Latency**: End-to-end processing time
- **Scalability Metrics**: Performance under varying load
- **Availability Metrics**: System uptime and reliability
