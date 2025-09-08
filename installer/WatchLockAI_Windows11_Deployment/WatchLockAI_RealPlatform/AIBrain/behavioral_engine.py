#!/usr/bin/env python3
'''
WatchLockAI - Behavioral Baselining Engine
Advanced user and system behavior analysis with machine learning
'''

import json
import numpy as np
import sqlite3
import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

@dataclass
class BehaviorProfile:
    user_id: str
    activity_patterns: Dict[str, List[float]]
    time_patterns: Dict[str, List[int]]
    network_patterns: Dict[str, List[str]]
    process_patterns: Dict[str, List[str]]
    baseline_score: float
    last_updated: str

class AdvancedBehavioralEngine:
    '''Advanced behavioral analysis with ML-based anomaly detection'''
    
    def __init__(self, db_path: str = "behavioral_baselines.db"):
        self.db_path = db_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.user_profiles = {}
        self._init_database()
        
    def _init_database(self):
        '''Initialize behavioral baseline database'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_baselines (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                created_at TEXT,
                updated_at TEXT,
                baseline_version INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                timestamp TEXT,
                activity_type TEXT,
                activity_data TEXT,
                anomaly_score REAL,
                is_flagged BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def learn_user_behavior(self, user_id: str, activity_data: Dict[str, Any]):
        '''Learn and update user behavioral patterns'''
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = BehaviorProfile(
                user_id=user_id,
                activity_patterns={},
                time_patterns={},
                network_patterns={},
                process_patterns={},
                baseline_score=0.0,
                last_updated=datetime.datetime.now().isoformat()
            )
            
        profile = self.user_profiles[user_id]
        
        # Learn activity patterns
        activity_type = activity_data.get('type', 'unknown')
        if activity_type not in profile.activity_patterns:
            profile.activity_patterns[activity_type] = []
            
        # Extract numerical features for ML
        features = self._extract_features(activity_data)
        profile.activity_patterns[activity_type].append(features)
        
        # Learn temporal patterns
        current_hour = datetime.datetime.now().hour
        if activity_type not in profile.time_patterns:
            profile.time_patterns[activity_type] = []
        profile.time_patterns[activity_type].append(current_hour)
        
        # Learn network patterns
        if 'network' in activity_data:
            if 'network' not in profile.network_patterns:
                profile.network_patterns['network'] = []
            profile.network_patterns['network'].append(activity_data['network'])
            
        # Learn process patterns
        if 'process' in activity_data:
            if 'processes' not in profile.process_patterns:
                profile.process_patterns['processes'] = []
            profile.process_patterns['processes'].append(activity_data['process'])
        
        # Update baseline
        self._update_baseline(user_id)
        
    def _extract_features(self, activity_data: Dict[str, Any]) -> List[float]:
        '''Extract numerical features from activity data'''
        features = []
        
        # Time-based features
        now = datetime.datetime.now()
        features.extend([
            now.hour,  # Hour of day
            now.weekday(),  # Day of week
            now.day  # Day of month
        ])
        
        # Activity-specific features
        features.append(len(str(activity_data.get('command', ''))))  # Command length
        features.append(len(activity_data.get('arguments', [])))  # Number of arguments
        features.append(int(activity_data.get('elevated', False)))  # Elevated privileges
        features.append(len(activity_data.get('network_connections', [])))  # Network connections
        
        return features
        
    def _update_baseline(self, user_id: str):
        '''Update ML baseline for user'''
        profile = self.user_profiles[user_id]
        
        # Collect all features for training
        all_features = []
        for activity_type, feature_lists in profile.activity_patterns.items():
            all_features.extend(feature_lists)
            
        if len(all_features) >= 10:  # Minimum samples for training
            features_array = np.array(all_features)
            
            # Normalize features
            normalized_features = self.scaler.fit_transform(features_array)
            
            # Train isolation forest
            self.isolation_forest.fit(normalized_features)
            
            # Calculate baseline score
            scores = self.isolation_forest.decision_function(normalized_features)
            profile.baseline_score = np.mean(scores)
            
        profile.last_updated = datetime.datetime.now().isoformat()
        
    def detect_anomaly(self, user_id: str, activity_data: Dict[str, Any]) -> Tuple[float, bool]:
        '''Detect behavioral anomalies using ML'''
        if user_id not in self.user_profiles:
            return 0.8, True  # Unknown user is anomalous
            
        profile = self.user_profiles[user_id]
        
        # Extract features
        features = self._extract_features(activity_data)
        
        # Check if we have enough data for ML detection
        total_samples = sum(len(patterns) for patterns in profile.activity_patterns.values())
        if total_samples < 10:
            return self._rule_based_detection(user_id, activity_data)
            
        try:
            # Normalize features
            features_array = np.array([features])
            normalized_features = self.scaler.transform(features_array)
            
            # Get anomaly score
            anomaly_score = self.isolation_forest.decision_function(normalized_features)[0]
            is_anomaly = self.isolation_forest.predict(normalized_features)[0] == -1
            
            # Convert to 0-1 scale (higher = more anomalous)
            normalized_score = max(0, min(1, (profile.baseline_score - anomaly_score) / 2))
            
            return normalized_score, is_anomaly
            
        except Exception as e:
            logger.warning(f"ML anomaly detection failed: {e}, falling back to rule-based")
            return self._rule_based_detection(user_id, activity_data)
            
    def _rule_based_detection(self, user_id: str, activity_data: Dict[str, Any]) -> Tuple[float, bool]:
        '''Fallback rule-based anomaly detection'''
        profile = self.user_profiles[user_id]
        anomaly_score = 0.0
        
        # Check temporal anomalies
        current_hour = datetime.datetime.now().hour
        activity_type = activity_data.get('type', 'unknown')
        
        if activity_type in profile.time_patterns:
            usual_hours = profile.time_patterns[activity_type]
            if usual_hours and current_hour not in usual_hours:
                anomaly_score += 0.3
                
        # Check command/process anomalies
        if 'command' in activity_data:
            command = activity_data['command'].lower()
            suspicious_commands = [
                'powershell -enc', 'wmic process call create',
                'rundll32 javascript:', 'certutil -urlcache',
                'reg save hklm\sam', 'net user /add'
            ]
            
            for sus_cmd in suspicious_commands:
                if sus_cmd in command:
                    anomaly_score += 0.4
                    break
                    
        # Check network anomalies
        if 'network' in activity_data:
            network_data = activity_data['network']
            if isinstance(network_data, str) and any(indicator in network_data.lower() for indicator in 
                ['tor', 'proxy', 'tunnel', 'beacon']):
                anomaly_score += 0.3
                
        # Check privilege escalation
        if activity_data.get('elevated', False):
            if user_id not in ['SYSTEM', 'Administrator']:
                anomaly_score += 0.2
                
        is_anomaly = anomaly_score > 0.5
        return min(1.0, anomaly_score), is_anomaly
        
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        '''Get user behavioral profile'''
        if user_id not in self.user_profiles:
            return {"error": "User profile not found"}
            
        profile = self.user_profiles[user_id]
        return {
            "user_id": user_id,
            "baseline_score": profile.baseline_score,
            "last_updated": profile.last_updated,
            "activity_types": list(profile.activity_patterns.keys()),
            "total_activities": sum(len(patterns) for patterns in profile.activity_patterns.values()),
            "common_hours": self._get_common_hours(profile.time_patterns),
            "risk_level": self._calculate_risk_level(profile)
        }
        
    def _get_common_hours(self, time_patterns: Dict[str, List[int]]) -> List[int]:
        '''Get most common activity hours'''
        all_hours = []
        for hours_list in time_patterns.values():
            all_hours.extend(hours_list)
            
        if not all_hours:
            return []
            
        # Count frequency of each hour
        hour_counts = {}
        for hour in all_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
        # Return most common hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:6]]  # Top 6 hours
        
    def _calculate_risk_level(self, profile: BehaviorProfile) -> str:
        '''Calculate user risk level based on profile'''
        total_activities = sum(len(patterns) for patterns in profile.activity_patterns.values())
        
        if total_activities < 5:
            return "unknown"
        elif profile.baseline_score < -0.5:
            return "high_risk"
        elif profile.baseline_score < 0:
            return "medium_risk"
        else:
            return "low_risk"
