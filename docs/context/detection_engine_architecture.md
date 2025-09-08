# Detection Engine Architecture - WatchLockAI Sentinel

## Overview

The WatchLockAI Sentinel detection system implements a multi-layered approach combining rule-based detection, behavioral analysis, machine learning scoring, and threat intelligence enrichment. The system is designed for real-time threat detection with configurable response actions.

## Core Components

### Rules Engine (`detection/rules_engine.py`)

The primary detection engine that processes events through multiple detection rules:

#### Built-in Detection Rules

**RansomwareBurstDetector**
- Detects rapid file creation/modification patterns
- Monitors file entropy levels (>7.5 indicates encryption)
- Tracks burst windows and file count thresholds
- Triggers on suspicious file extension patterns

**AutostartPersistenceDetector**
- Monitors registry autostart locations
- Detects persistence mechanism installation
- Tracks common persistence techniques (Run keys, services, etc.)

**SuspiciousParentChildDetector**
- Analyzes process spawning relationships
- Detects unusual parent-child process combinations
- Identifies process injection and hollowing attempts

**EgressAnomalyDetector**
- Monitors outbound network connections
- Detects unusual data transfer patterns
- Identifies potential data exfiltration

**HealthDegradationDetector**
- Monitors system performance metrics
- Detects resource exhaustion attacks
- Identifies system stability issues

#### Event Processing Flow
```python
async def _handle_file_event(self, event: FileEvent) -> None:
    # Check ransomware burst rule
    alert = self.ransomware_detector.check_file_event(event)
    if alert:
        await self.event_bus.publish(alert)
        
    # Check health degradation rule
    alert = self.health_detector.check_file_event(event)
    if alert:
        await self.event_bus.publish(alert)
```

### MITRE ATT&CK Integration (`detection/attack_matrix.py`)

Implements MITRE ATT&CK framework mapping with configurable rule profiles:

#### Rule Structure
```python
class Rule:
    id: str              # Unique rule identifier
    name: str            # Human-readable name
    tactic: str          # MITRE tactic (e.g., "persistence")
    technique: str       # MITRE technique (e.g., "T1547")
    event: str           # Event type to monitor
    threshold: int       # Trigger threshold
    window_s: int        # Time window in seconds
    severity: str        # Alert severity level
    response: str        # Automated response action
    stage: str           # Optional attack stage
    group_by: str        # Grouping field for counting
    where: str           # Optional filter condition
```

#### Rule Profiles
- **endpoint_basic**: Core endpoint detection rules
- **endpoint_advanced**: Extended detection with behavioral analysis
- **server_focused**: Server-specific threat patterns
- **custom**: User-defined rule sets

#### Event Processing
```python
def process_event(self, event_type: str, event_data: Dict[str, Any]) -> List[Rule]:
    matched_rules = []
    for rule in self.rules:
        if rule.event != event_type:
            continue
            
        # Apply where clause filtering
        if rule.where and not self._evaluate_where_clause(rule.where, event_data):
            continue
            
        # Check threshold
        count = self.counters[rule.id].increment(event_data[rule.group_by])
        if count >= rule.threshold:
            matched_rules.append(rule)
    
    return matched_rules
```

### Behavioral Analysis Engine (`detection/behavioral_engine.py`)

Implements adaptive threat detection through baseline learning and anomaly detection:

#### Baseline Learning
- Learns normal system behavior from historical events
- Builds statistical models for file, process, and network activity
- Adapts baselines over time with configurable learning rates

#### Anomaly Detection
- Compares live events against learned baselines
- Calculates anomaly scores using statistical methods
- Triggers alerts when anomaly scores exceed thresholds

#### ML Integration
```python
def _analyze_live_event(self, event: SentinelEvent) -> None:
    # Update baselines with new event
    self._update_baselines_from_event(event)
    
    # Perform anomaly detection
    anomaly_score = self._calculate_anomaly_score(event)
    
    if anomaly_score > 0.7:  # High anomaly threshold
        alert = self._create_behavioral_alert(event, anomaly_score)
        self._add_recent_detection(alert)
```

### Machine Learning Scoring (`detection/ml_scoring.py`)

Provides ML-based threat scoring with pluggable model support:

#### Model Support
- **Scikit-learn**: Standard ML models with `predict_proba` interface
- **Custom Models**: Models with custom `score` methods
- **Lazy Loading**: Models loaded on-demand to reduce startup time

#### Scoring Interface
```python
def score_behavior(self, signal: dict[str, Any]) -> tuple[float, str] | None:
    """Score behavior signal using loaded ML model.
    
    Returns:
        Tuple of (score, rationale) where score is 0.0-1.0 confidence,
        or None if no model is available.
    """
    if not self.model_loaded:
        return None
        
    features = self._extract_features(signal)
    probabilities = self.model.predict_proba([features])[0]
    
    if len(probabilities) >= 2:
        malicious_score = probabilities[1]
        rationale = f"ML model confidence: {malicious_score:.3f}"
        return float(malicious_score), rationale
```

### Threat Intelligence Database (`detection/threat_intel_db.py`)

RAG-powered threat intelligence with knowledge base integration:

#### Knowledge Search
```python
def search(self, query: str, k: int = 10) -> list[dict[str, Any]]:
    """Search threat intelligence knowledge base."""
    hits = self.loader.query_knowledge(query, limit=k)
    
    results = []
    for hit in hits:
        result = {
            "content": hit.content,
            "source": hit.filename,
            "section": hit.section,
            "confidence": hit.confidence,
            "framework": self._identify_framework(hit.filename),
        }
        results.append(result)
    
    return results
```

#### Alert Enrichment
```python
def enrich_alert(self, alert: DetectionAlert) -> DetectionAlert:
    """Enrich alert with threat intelligence context."""
    search_queries = self._build_search_queries(alert)
    
    threat_intel = []
    for query in search_queries:
        results = self.search(query, k=3)
        threat_intel.extend(results)
    
    # Add threat intelligence to alert metadata
    enriched_alert = alert.model_copy()
    enriched_alert.entities["threat_intel"] = threat_intel[:5]
    
    return enriched_alert
```

### Knowledge Loader (`detection/knowledge/loader.py`)

RAG knowledge system with hybrid search capabilities:

#### Search Modes
- **FTS (Full-Text Search)**: SQLite FTS for fast text matching
- **Embeddings**: Vector similarity search using sentence transformers
- **Hybrid**: Automatic fallback from embeddings to FTS

#### Index Management
```python
def rebuild_index(self) -> dict[str, Any]:
    """Rebuild knowledge index from all pack files."""
    stats = {"files_processed": 0, "chunks_indexed": 0, "errors": []}
    
    with sqlite3.connect(self.db_path) as conn:
        # Clear existing data
        conn.execute("DELETE FROM knowledge_content")
        conn.execute("DELETE FROM knowledge_fts")
        
        # Process all files in packs directory
        for file_path in self.packs_dir.rglob("*"):
            if file_path.suffix in [".md", ".yaml", ".yml", ".txt"]:
                self._index_file(file_path, conn, stats)
        
        conn.commit()
    
    return stats
```

#### Query Interface
```python
def query_knowledge(self, query: str, limit: int = 10) -> list[KnowledgeHit]:
    """Query knowledge base with automatic fallback."""
    if self.mode == "embeddings" and self.embeddings_model:
        try:
            return self._query_embeddings(query, limit)
        except Exception:
            return self._query_fts(query, limit)
    else:
        return self._query_fts(query, limit)
```

## Rule DSL Support (`detection/rule_dsl.py`)

Advanced rule definition language for complex detection patterns:

### Expression Engine
- Boolean logic operators (AND, OR, NOT)
- Comparison operators (==, !=, <, >, <=, >=)
- String matching (contains, startswith, endswith, regex)
- Arithmetic operations (+, -, *, /, %)

### Sequence Detection
```python
class SequenceRule:
    """Multi-step attack sequence detection."""
    name: str
    steps: List[SequenceStep]
    max_time_window: int
    
class SequenceStep:
    """Individual step in attack sequence."""
    event_type: str
    conditions: Dict[str, Any]
    parameter_bindings: Dict[str, str]
```

### Example Rule Definition
```yaml
- name: "Credential Dumping Sequence"
  steps:
    - event_type: "ProcessEvent"
      conditions:
        exe: "lsass.exe"
      bindings:
        target_pid: "pid"
    - event_type: "FileEvent"
      conditions:
        path: "contains:dump"
        proc_pid: "$target_pid"
  max_time_window: 300
```

## Detection Workflow

### Event Processing Pipeline
1. **Event Reception**: Events received from collectors via event bus
2. **Rule Evaluation**: Events processed through active detection rules
3. **Behavioral Analysis**: Events analyzed for anomalous patterns
4. **ML Scoring**: Suspicious events scored using ML models
5. **Threat Intel Enrichment**: Alerts enriched with knowledge base context
6. **Alert Generation**: DetectionAlert events published to event bus

### Alert Lifecycle
```python
# 1. Rule triggers detection
alert = DetectionAlert(
    severity=AlertSeverity.HIGH,
    category=AlertCategory.RANSOMWARE,
    tag="file-entropy-burst",
    entities={"file_count": 50, "avg_entropy": 7.8},
    confidence=0.95,
    rationale="High entropy file creation burst detected",
    provenance=ProvenanceInfo(file="rules_engine.py", section="ransomware")
)

# 2. Threat intel enrichment
enriched_alert = threat_intel_db.enrich_alert(alert)

# 3. ML scoring (optional)
if ml_scorer.model_loaded:
    score, rationale = ml_scorer.score_behavior(alert.entities)
    if score:
        enriched_alert.confidence = max(enriched_alert.confidence, score)

# 4. Alert publication
await event_bus.publish(enriched_alert)
```

## Configuration and Tuning

### Detection Sensitivity
- Rule thresholds and time windows
- Anomaly detection sensitivity levels
- ML model confidence thresholds
- Baseline learning parameters

### Performance Optimization
- Event processing batch sizes
- Knowledge base query limits
- ML model lazy loading
- Cache configuration for frequent queries

### Rule Management
- Dynamic rule loading from YAML files
- Rule profile selection (basic, advanced, custom)
- Runtime rule enable/disable
- Rule performance monitoring

## Integration Points

### Event Bus Integration
- Subscribes to all event types from collectors
- Publishes DetectionAlert events for response systems
- Maintains event processing metrics

### Response System Integration
- Alerts trigger automated response actions
- Operational mode affects response behavior
- User consent required for destructive actions

### Web API Integration
- Real-time detection streaming via SSE
- Detection history and statistics
- Rule management and configuration
- MITRE ATT&CK coverage reporting

## Security and Privacy

### Data Handling
- Event data sanitization and validation
- Sensitive information redaction
- Configurable data retention policies
- Secure knowledge base storage

### Model Security
- ML model integrity verification
- Secure model loading and execution
- Protection against adversarial inputs
- Model performance monitoring

### Threat Intelligence
- Knowledge base access controls
- Source attribution and provenance
- Content validation and sanitization
- Privacy-preserving search methods
