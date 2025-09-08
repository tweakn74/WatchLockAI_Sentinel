"""Behavioral Analysis Engine implementing adaptive threat detection.

This module provides behavioral analysis capabilities including baseline learning
from historical data and live anomaly detection with ML-based scoring.
"""

from __future__ import annotations

import json
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from app_core.schemas import DetectionAlert, EventType, SentinelEvent
from detection.ml_scoring import get_ml_scorer

if TYPE_CHECKING:
    from app_core.bus import EventBus
    from app_core.schemas import BaseEvent

# Lazy import for optional ML dependencies
def _get_sklearn_models() -> tuple[type | None, type | None, type | None]:
    """Lazy import scikit-learn models to avoid import-time dependencies."""
    try:
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.svm import OneClassSVM
        return IsolationForest, OneClassSVM, np
    except ImportError:
        logger.warning("scikit-learn not available, using heuristic-based detection")
        return None, None, None


class BehavioralBaseline:
    """Behavioral baseline for a specific entity (host, process, user)."""
    
    def __init__(self, entity_id: str, entity_type: str) -> None:
        """Initialize behavioral baseline.
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (host, process, user, etc.)
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.created_at = datetime.now(timezone.utc)
        self.last_updated = self.created_at
        
        # Event frequency baselines
        self.event_rates: dict[str, list[float]] = defaultdict(list)
        self.hourly_patterns: dict[str, list[int]] = defaultdict(lambda: [0] * 24)
        
        # Process behavior baselines
        self.process_patterns: dict[str, dict[str, Any]] = {}
        self.network_patterns: dict[str, Any] = {
            "connection_rates": [],
            "port_usage": defaultdict(int),
            "destination_ips": set(),
            "dns_queries": defaultdict(int)
        }
        
        # File system baselines
        self.file_patterns: dict[str, Any] = {
            "creation_rates": [],
            "modification_rates": [],
            "deletion_rates": [],
            "extensions_accessed": defaultdict(int),
            "directories_accessed": defaultdict(int)
        }
        
        # Resource usage baselines
        self.resource_patterns: dict[str, list[float]] = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_io": [],
            "network_io": []
        }

    def update_from_event(self, event: BaseEvent) -> None:
        """Update baseline from a historical event.
        
        Args:
            event: Event to incorporate into baseline
        """
        self.last_updated = datetime.now(timezone.utc)
        
        # Parse timestamp from ISO string
        try:
            event_timestamp = datetime.fromisoformat(event.ts.replace('Z', '+00:00'))
            event_hour = event_timestamp.hour
        except (ValueError, AttributeError):
            event_hour = 12  # Default fallback
        
        # Update event rate patterns based on event type
        event_type_str = self._get_event_type_string(event)
        self.hourly_patterns[event_type_str][event_hour] += 1
        
        # Update specific patterns based on event type
        if hasattr(event, 'event_type'):
            if str(event.event_type) in ['started', 'exited']:
                self._update_process_baseline(event)
            elif str(event.event_type) in ['connection', 'listen', 'close']:
                self._update_network_baseline(event)
            elif str(event.event_type) in ['created', 'modified', 'deleted']:
                self._update_file_baseline(event)

    def _get_event_type_string(self, event: BaseEvent) -> str:
        """Get event type as string for classification."""
        if hasattr(event, 'event_type'):
            if hasattr(event.event_type, 'value'):
                return event.event_type.value
            return str(event.event_type)
        return event.__class__.__name__.lower()

    def _update_process_baseline(self, event: BaseEvent) -> None:
        """Update process-related baseline patterns."""
        # Check if this is a ProcessEvent with the expected attributes
        if hasattr(event, 'proc_name') and event.proc_name:
            process_name = event.proc_name
            if process_name not in self.process_patterns:
                self.process_patterns[process_name] = {
                    'execution_count': 0,
                    'parent_processes': defaultdict(int),
                    'command_lines': defaultdict(int),
                    'working_directories': defaultdict(int)
                }
            
            pattern = self.process_patterns[process_name]
            pattern['execution_count'] += 1
            
            # ProcessEvent may have additional fields
            if hasattr(event, 'parent_pid') and event.parent_pid:
                pattern['parent_processes'][str(event.parent_pid)] += 1
            if hasattr(event, 'command_line') and event.command_line:
                pattern['command_lines'][event.command_line] += 1

    def _update_network_baseline(self, event: BaseEvent) -> None:
        """Update network-related baseline patterns."""
        if hasattr(event, 'remote_ip') and event.remote_ip:
            self.network_patterns['destination_ips'].add(event.remote_ip)
        if hasattr(event, 'remote_port') and event.remote_port:
            self.network_patterns['port_usage'][event.remote_port] += 1

    def _update_file_baseline(self, event: BaseEvent) -> None:
        """Update file system baseline patterns."""
        if hasattr(event, 'path') and event.path:
            file_path = event.path
            # Extract file extension and directory
            path_obj = Path(file_path)
            if path_obj.suffix:
                self.file_patterns['extensions_accessed'][path_obj.suffix.lower()] += 1
            self.file_patterns['directories_accessed'][str(path_obj.parent)] += 1

    def _update_resource_baseline(self, event: BaseEvent) -> None:
        """Update resource usage baseline patterns."""
        # HealthMetric events would have different structure
        # This is a placeholder for health/resource monitoring events
        # In practice, you'd check for specific HealthMetric attributes
        pass

    def get_statistics(self) -> dict[str, Any]:
        """Get baseline statistics for anomaly detection."""
        stats = {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'last_updated': self.last_updated.isoformat(),
            'event_patterns': {},
            'process_stats': {},
            'network_stats': {},
            'file_stats': {},
            'resource_stats': {}
        }
        
        # Event pattern statistics
        for event_type, hourly_counts in self.hourly_patterns.items():
            stats['event_patterns'][event_type] = {
                'total_events': sum(hourly_counts),
                'avg_hourly': statistics.mean(hourly_counts) if hourly_counts else 0,
                'peak_hour': hourly_counts.index(max(hourly_counts)) if hourly_counts else 0,
                'std_dev': statistics.stdev(hourly_counts) if len(hourly_counts) > 1 else 0
            }
        
        # Process statistics
        stats['process_stats'] = {
            'unique_processes': len(self.process_patterns),
            'most_common_processes': sorted(
                [(name, data['execution_count']) for name, data in self.process_patterns.items()],
                key=lambda x: x[1], reverse=True
            )[:10]
        }
        
        # Network statistics  
        stats['network_stats'] = {
            'unique_destinations': len(self.network_patterns['destination_ips']),
            'unique_ports': len(self.network_patterns['port_usage']),
            'top_ports': sorted(
                self.network_patterns['port_usage'].items(),
                key=lambda x: x[1], reverse=True
            )[:10]
        }
        
        # File statistics
        stats['file_stats'] = {
            'unique_extensions': len(self.file_patterns['extensions_accessed']),
            'unique_directories': len(self.file_patterns['directories_accessed']),
            'top_extensions': sorted(
                self.file_patterns['extensions_accessed'].items(),
                key=lambda x: x[1], reverse=True
            )[:10]
        }
        
        # Resource statistics
        for metric, values in self.resource_patterns.items():
            if values:
                stats['resource_stats'][metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats


class BehavioralEngine:
    """Behavioral analysis engine for adaptive threat detection."""
    
    def __init__(self, logs_dir: str = "logs/events") -> None:
        """Initialize behavioral engine.
        
        Args:
            logs_dir: Directory containing historical event logs
        """
        self.logs_dir = Path(logs_dir)
        self.baselines: dict[str, BehavioralBaseline] = {}
        self.ml_models: dict[str, Any] = {}
        self.recent_detections: list[dict[str, Any]] = []
        self.event_bus: EventBus | None = None
        
        # Configuration
        self.baseline_learning_enabled = True
        self.max_baseline_age_days = 30
        self.anomaly_threshold = 0.05  # 5th percentile for outlier detection
        self.max_recent_detections = 100
        
        self._initialize_ml_models()
        logger.info("BehavioralEngine initialized")

    def start(self) -> None:
        """Start the behavioral engine."""
        try:
            if self.baseline_learning_enabled:
                self._load_historical_baselines()
            logger.info("BehavioralEngine started successfully")
        except Exception as e:
            logger.error(f"Failed to start BehavioralEngine: {e}")
            raise

    def stop(self) -> None:
        """Stop the behavioral engine."""
        logger.info("BehavioralEngine stopped")

    def set_event_bus(self, event_bus: EventBus) -> None:
        """Set event bus for live event processing.
        
        Args:
            event_bus: Event bus instance
        """
        self.event_bus = event_bus
        # Subscribe to events for live analysis
        if hasattr(event_bus, 'subscribe'):
            event_bus.subscribe(EventType.PROCESS_CREATED, self._analyze_live_event)
            event_bus.subscribe(EventType.NETWORK_CONNECTION, self._analyze_live_event)
            event_bus.subscribe(EventType.FILE_CREATED, self._analyze_live_event)
            event_bus.subscribe(EventType.FILE_MODIFIED, self._analyze_live_event)
            event_bus.subscribe(EventType.FILE_DELETED, self._analyze_live_event)
            event_bus.subscribe(EventType.HEALTH_CHECK, self._analyze_live_event)

    def _initialize_ml_models(self) -> None:
        """Initialize ML models for anomaly detection."""
        IsolationForest, OneClassSVM, np = _get_sklearn_models()
        
        if IsolationForest is None or OneClassSVM is None:
            logger.info("Scikit-learn not available, using heuristic-based detection")
            return
            
        try:
            # Initialize Isolation Forest for general anomaly detection
            self.ml_models['isolation_forest'] = IsolationForest(
                contamination=self.anomaly_threshold,
                random_state=42,
                n_estimators=100
            )
            
            # Initialize One-Class SVM for behavior modeling
            self.ml_models['one_class_svm'] = OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=self.anomaly_threshold
            )
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize ML models: {e}")
            self.ml_models = {}

    def _load_historical_baselines(self) -> None:
        """Load historical event data to build behavioral baselines."""
        logger.info("Loading historical baselines from event logs...")
        
        events_processed = 0
        baselines_created = 0
        
        try:
            # Find all JSONL files in logs directory
            for log_file in self.logs_dir.glob("*.jsonl"):
                try:
                    with open(log_file, encoding='utf-8') as f:
                        for line in f:
                            try:
                                event_data = json.loads(line.strip())
                                event = self._parse_event_data(event_data)
                                if event:
                                    self._update_baselines_from_event(event)
                                    events_processed += 1
                            except (json.JSONDecodeError, KeyError, ValueError) as e:
                                logger.debug(f"Skipped invalid event in {log_file}: {e}")
                                continue
                                
                except Exception as e:
                    logger.warning(f"Error processing log file {log_file}: {e}")
                    continue
            
            # Train ML models on baseline data
            self._train_ml_models()
            
            baselines_created = len(self.baselines)
            logger.info(f"Loaded {events_processed} events, created {baselines_created} baselines")
            
        except Exception as e:
            logger.error(f"Error loading historical baselines: {e}")

    def _parse_event_data(self, event_data: dict[str, Any]) -> BaseEvent | None:
        """Parse event data from JSONL format."""
        try:
            # This is a simplified parser - create a basic BaseEvent
            from app_core.schemas import BaseEvent
            
            # Create minimal event for baseline building
            event = BaseEvent(
                host_id=event_data.get('host_id', 'unknown'),
                sentinel_version=event_data.get('sentinel_version', '1.0.0'),
                ts=event_data.get('ts', datetime.now(timezone.utc).isoformat())
            )
            
            return event
            
        except Exception as e:
            logger.debug(f"Failed to parse event data: {e}")
            return None

    def _update_baselines_from_event(self, event: BaseEvent) -> None:
        """Update baselines from a historical event."""
        try:
            # Determine entity ID based on event source and details
            entity_id = self._get_entity_id(event)
            entity_type = self._get_entity_type(event)
            
            # Get or create baseline
            baseline_key = f"{entity_type}:{entity_id}"
            if baseline_key not in self.baselines:
                self.baselines[baseline_key] = BehavioralBaseline(entity_id, entity_type)
            
            # Update baseline with event
            self.baselines[baseline_key].update_from_event(event)
            
        except Exception as e:
            logger.debug(f"Error updating baseline from event: {e}")

    def _get_entity_id(self, event: BaseEvent) -> str:
        """Extract entity ID from event."""
        # Priority: host_id -> source -> 'default'
        if hasattr(event, 'host_id') and event.host_id:
            return event.host_id
        return 'default'

    def _get_entity_type(self, event: BaseEvent) -> str:
        """Extract entity type from event."""
        if hasattr(event, 'host_id') and event.host_id:
            return 'host'
        return 'system'

    def _train_ml_models(self) -> None:
        """Train ML models on baseline data."""
        IsolationForest, OneClassSVM, np = _get_sklearn_models()
        
        if IsolationForest is None or OneClassSVM is None or np is None or not self.baselines:
            return
            
        try:
            # Prepare training data from baselines
            features = []
            for baseline in self.baselines.values():
                feature_vector = self._extract_features_from_baseline(baseline)
                if feature_vector and len(feature_vector) > 0:
                    features.append(feature_vector)
            
            if len(features) < 10:  # Need minimum samples for training
                logger.info("Insufficient baseline data for ML model training")
                return
                
            features_array = np.array(features)
            
            # Train Isolation Forest
            if 'isolation_forest' in self.ml_models:
                self.ml_models['isolation_forest'].fit(features_array)
                logger.info(f"Trained Isolation Forest on {len(features)} baseline samples")
            
            # Train One-Class SVM  
            if 'one_class_svm' in self.ml_models:
                self.ml_models['one_class_svm'].fit(features_array)
                logger.info(f"Trained One-Class SVM on {len(features)} baseline samples")
                
        except Exception as e:
            logger.warning(f"Failed to train ML models: {e}")

    def _extract_features_from_baseline(self, baseline: BehavioralBaseline) -> list[float]:
        """Extract numerical features from baseline for ML training."""
        features = []
        
        try:
            stats = baseline.get_statistics()
            
            # Event pattern features
            for _event_type, pattern_stats in stats['event_patterns'].items():
                features.extend([
                    pattern_stats.get('total_events', 0),
                    pattern_stats.get('avg_hourly', 0),
                    pattern_stats.get('std_dev', 0)
                ])
            
            # Pad or truncate to fixed size (30 features)
            while len(features) < 30:
                features.append(0.0)
            features = features[:30]
            
            return features
            
        except Exception as e:
            logger.debug(f"Error extracting features from baseline: {e}")
            return []

    def _analyze_live_event(self, event: SentinelEvent) -> None:
        """Analyze live event for anomalies."""
        try:
            # Update baselines with new event
            self._update_baselines_from_event(event)
            
            # Perform anomaly detection
            anomaly_score = self._calculate_anomaly_score(event)
            
            if anomaly_score > 0.7:  # High anomaly threshold
                alert = self._create_behavioral_alert(event, anomaly_score)
                self._add_recent_detection(alert)
                
                # Emit alert through event bus if available
                if self.event_bus and hasattr(self.event_bus, 'emit'):
                    self.event_bus.emit('detection_alert', alert)
                    
        except Exception as e:
            logger.error(f"Error analyzing live event: {e}")

    def _calculate_anomaly_score(self, event: SentinelEvent) -> float:
        """Calculate anomaly score for an event."""
        try:
            # Try ML-based scoring first
            IsolationForest, OneClassSVM, np = _get_sklearn_models()
            if IsolationForest is not None and self.ml_models:
                ml_score = self._ml_anomaly_score(event)
                if ml_score is not None:
                    return ml_score
            
            # Fallback to heuristic scoring
            return self._heuristic_anomaly_score(event)
            
        except Exception as e:
            logger.debug(f"Error calculating anomaly score: {e}")
            return 0.0

    def _ml_anomaly_score(self, event: SentinelEvent) -> float | None:
        """Calculate ML-based anomaly score."""
        try:
            IsolationForest, OneClassSVM, np = _get_sklearn_models()
            if np is None:
                return None
                
            entity_id = self._get_entity_id(event)
            entity_type = self._get_entity_type(event)
            baseline_key = f"{entity_type}:{entity_id}"
            
            if baseline_key not in self.baselines:
                return None
                
            baseline = self.baselines[baseline_key]
            features = self._extract_features_from_baseline(baseline)
            
            if not features or 'isolation_forest' not in self.ml_models:
                return None
                
            # Get anomaly score from Isolation Forest
            feature_array = np.array([features])
            scores = self.ml_models['isolation_forest'].decision_function(feature_array)
            
            # Convert to 0-1 range (higher = more anomalous)
            normalized_score = max(0, min(1, (0.5 - scores[0]) * 2))
            return normalized_score
            
        except Exception as e:
            logger.debug(f"ML anomaly scoring failed: {e}")
            return None

    def _heuristic_anomaly_score(self, event: SentinelEvent) -> float:
        """Calculate heuristic-based anomaly score."""
        score = 0.0
        
        try:
            entity_id = self._get_entity_id(event)
            entity_type = self._get_entity_type(event)
            baseline_key = f"{entity_type}:{entity_id}"
            
            if baseline_key not in self.baselines:
                # No baseline = moderate anomaly
                return 0.5
                
            baseline = self.baselines[baseline_key]
            current_hour = datetime.now(timezone.utc).hour
            
            # Check event frequency anomalies
            event_type_str = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
            if event_type_str in baseline.hourly_patterns:
                hourly_pattern = baseline.hourly_patterns[event_type_str]
                avg_for_hour = hourly_pattern[current_hour]
                overall_avg = statistics.mean(hourly_pattern) if hourly_pattern else 0
                
                if overall_avg > 0:
                    deviation = abs(avg_for_hour - overall_avg) / overall_avg
                    score += min(0.3, deviation)  # Up to 30% score contribution
            
            # Check process anomalies
            if event.event_type == EventType.PROCESS_CREATED and hasattr(event, 'details'):
                process_name = event.details.get('process_name', '') if event.details else ''
                if process_name and process_name not in baseline.process_patterns:
                    score += 0.4  # New process = significant anomaly
            
            # Check network anomalies
            if event.event_type == EventType.NETWORK_CONNECTION and hasattr(event, 'details'):
                if event.details:
                    dest_ip = event.details.get('destination_ip', '')
                    if dest_ip and dest_ip not in baseline.network_patterns['destination_ips']:
                        score += 0.3  # New destination = moderate anomaly
                        
                    dest_port = event.details.get('destination_port', 0)
                    if dest_port and dest_port not in baseline.network_patterns['port_usage']:
                        score += 0.2  # New port = minor anomaly
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            logger.debug(f"Heuristic scoring failed: {e}")
            return 0.0

    def _create_behavioral_alert(self, event: SentinelEvent, anomaly_score: float) -> DetectionAlert:
        """Create behavioral detection alert."""
        # Get baseline context
        entity_id = self._get_entity_id(event)
        entity_type = self._get_entity_type(event)
        baseline_key = f"{entity_type}:{entity_id}"
        
        baseline_info = "No baseline available"
        if baseline_key in self.baselines:
            baseline_stats = self.baselines[baseline_key].get_statistics()
            baseline_info = f"Entity has {baseline_stats['event_patterns']} event patterns"
        
        # Use ML scorer for additional context
        ml_scorer = get_ml_scorer()
        ml_score = None
        if ml_scorer.is_available() and hasattr(event, 'details'):
            signal = self._event_to_signal(event)
            ml_result = ml_scorer.score_behavior(signal)
            if ml_result:
                ml_score, ml_rationale = ml_result
        
        # Create detection alert
        alert = DetectionAlert(
            alert_id=f"behavioral_{int(time.time())}_{hash(str(event.event_id)) % 10000}",
            title=f"Behavioral Anomaly Detected ({entity_type})",
            description=f"Unusual behavior detected for {entity_type} '{entity_id}' with anomaly score {anomaly_score:.3f}",
            severity="warning" if anomaly_score < 0.8 else "critical",
            confidence=anomaly_score,
            timestamp=datetime.now(timezone.utc),
            source="BehavioralEngine",
            alert_type="behavioral_anomaly",
            related_events=[event.event_id] if hasattr(event, 'event_id') else [],
            metadata={
                "anomaly_score": anomaly_score,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "baseline_info": baseline_info,
                "ml_score": ml_score,
                "detection_method": "behavioral_analysis",
                "event_type": str(event.event_type)
            }
        )
        
        return alert

    def _event_to_signal(self, event: SentinelEvent) -> dict[str, Any]:
        """Convert event to signal dictionary for ML scoring."""
        signal = {
            "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp),
            "event_type": str(event.event_type),
            "source": event.source if hasattr(event, 'source') else 'unknown'
        }
        
        # Add event details if available
        if hasattr(event, 'details') and event.details:
            signal.update(event.details)
            
        return signal

    def _add_recent_detection(self, alert: DetectionAlert) -> None:
        """Add detection to recent detections list."""
        detection_dict = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity,
            "confidence": alert.confidence,
            "timestamp": alert.timestamp.isoformat(),
            "source": alert.source,
            "metadata": alert.metadata or {}
        }
        
        self.recent_detections.insert(0, detection_dict)  # Add to front
        
        # Keep only max_recent_detections
        if len(self.recent_detections) > self.max_recent_detections:
            self.recent_detections = self.recent_detections[:self.max_recent_detections]

    def get_recent_detections(self, limit: int = 50, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Get recent behavioral detections.
        
        Args:
            limit: Maximum number of detections to return
            filters: Optional filters to apply
            
        Returns:
            List of recent detection dictionaries
        """
        try:
            detections = self.recent_detections.copy()
            
            # Apply filters if provided
            if filters:
                if 'severity' in filters and filters['severity']:
                    detections = [d for d in detections if d.get('severity') == filters['severity']]
                if 'entity_type' in filters and filters['entity_type']:
                    detections = [d for d in detections if d.get('metadata', {}).get('entity_type') == filters['entity_type']]
            
            # Apply limit
            return detections[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent detections: {e}")
            return []

    def get_baseline_summary(self) -> dict[str, Any]:
        """Get summary of current baselines."""
        try:
            return {
                "total_baselines": len(self.baselines),
                "baseline_types": {
                    entity_type: sum(1 for key in self.baselines.keys() if key.startswith(f"{entity_type}:"))
                    for entity_type in ['host', 'process', 'system']
                },
                "oldest_baseline": min(
                    (baseline.created_at for baseline in self.baselines.values()),
                    default=datetime.now(timezone.utc)
                ).isoformat(),
                "newest_baseline": max(
                    (baseline.last_updated for baseline in self.baselines.values()),
                    default=datetime.now(timezone.utc)
                ).isoformat(),
                "ml_models_available": bool(self.ml_models) and _get_sklearn_models()[0] is not None,
                "recent_detections_count": len(self.recent_detections)
            }
        except Exception as e:
            logger.error(f"Error getting baseline summary: {e}")
            return {}


# Global instance (lazy initialization)
_behavioral_engine: BehavioralEngine | None = None


def get_behavioral_engine() -> BehavioralEngine:
    """Get global behavioral engine instance.
    
    Returns:
        Global BehavioralEngine instance.
    """
    global _behavioral_engine
    if _behavioral_engine is None:
        _behavioral_engine = BehavioralEngine()
    return _behavioral_engine
