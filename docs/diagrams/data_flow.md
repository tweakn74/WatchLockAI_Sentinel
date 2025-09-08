# WatchLockAI Sentinel Data Flow Architecture

This diagram illustrates the primary data flow through the WatchLockAI Sentinel system, from data ingestion through the event bus to metrics output.

```mermaid
graph TD
    %% External Data Sources
    A[System Events] --> B[Data Collectors]
    A1[File System Monitor] --> B
    A2[Network Monitor] --> B
    A3[Process Monitor] --> B
    A4[Registry Monitor] --> B
    A5[Health Monitor] --> B

    %% Data Collection Layer
    B --> C[Event Bus]
    B1[fs_monitor.py] --> C
    B2[net_monitor.py] --> C
    B3[proc_monitor.py] --> C
    B4[reg_monitor.py] --> C
    B5[health_monitor.py] --> C

    %% Event Bus (Core Message Broker)
    C --> D[Detection Engine]
    C --> E[Anomaly Detection]
    C --> F[Metrics Collection]
    C --> G[Quarantine System]

    %% Detection & Analysis Layer
    D --> H[Rules Engine]
    D --> I[Behavioral Engine]
    D --> J[ML Scoring]
    D --> K[Attack Matrix]

    %% Anomaly Detection Pipeline
    E --> L[Feature Extraction]
    E --> M[Statistical Analysis]
    E --> N[Threshold Monitoring]

    %% Data Storage & Processing
    H --> O[Data Directory]
    I --> O
    J --> O
    L --> O
    M --> O

    %% Quarantine Flow
    G --> P[Quarantine Directory]
    G --> Q[Backup & Restore]

    %% Metrics & Reporting
    F --> R[Health Metrics]
    F --> S[Performance Metrics]
    F --> T[Security Metrics]

    %% API Layer
    R --> U[Web API]
    S --> U
    T --> U
    O --> U

    %% Output Interfaces
    U --> V[Admin Console]
    U --> W[System Tray UI]
    U --> X[Export Endpoints]
    U --> Y[Stream Endpoints]

    %% Configuration & Control
    Z[Configuration] --> B
    Z --> C
    Z --> D
    Z --> E
    Z --> F
    Z --> G

    %% Styling
    classDef collector fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef engine fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef storage fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef ui fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class A,A1,A2,A3,A4,A5,B,B1,B2,B3,B4,B5 collector
    class C,D,E,F,G,H,I,J,K,L,M,N engine
    class O,P,Q storage
    class R,S,T,U,X,Y api
    class V,W ui
```

## Key Components

### Data Collection Layer
- **fs_monitor.py**: File system monitoring and change detection
- **net_monitor.py**: Network activity and connection monitoring  
- **proc_monitor.py**: Process lifecycle and behavior monitoring
- **reg_monitor.py**: Windows registry change monitoring
- **health_monitor.py**: System health and performance monitoring

### Event Bus (app_core/bus.py)
Central message broker that routes events between components with:
- Asynchronous event processing
- Event filtering and transformation
- Component isolation and fault tolerance
- Metrics collection and monitoring

### Detection Engines
- **Rules Engine**: Pattern-based threat detection
- **Behavioral Engine**: Anomaly detection based on system behavior
- **ML Scoring**: Machine learning-based threat scoring
- **Attack Matrix**: MITRE ATT&CK framework mapping

### Data Storage
- **Data Directory**: Structured storage for events and analysis
- **Quarantine Directory**: Isolated storage for suspicious items
- **Backup & Restore**: Data recovery and historical analysis

### API & UI Layer
- **Web API**: RESTful interface for all system functions
- **Admin Console**: Web-based management interface
- **System Tray UI**: Desktop notification and control
- **Export/Stream**: Data export and real-time streaming

## Data Flow Patterns

1. **Ingestion**: Collectors monitor system activities and generate events
2. **Routing**: Event bus distributes events to appropriate processing engines
3. **Analysis**: Detection engines analyze events for threats and anomalies
4. **Storage**: Processed data stored in structured directories
5. **Response**: Actions taken based on analysis (quarantine, alerts, etc.)
6. **Reporting**: Metrics and status exposed via API endpoints
7. **Interface**: Users interact through web console or tray application

## Configuration Control

The system uses environment variables and configuration files to control:
- Data collection sensitivity and scope
- Detection engine thresholds and rules
- Storage policies and retention
- API security and access control
- UI features and presentation
