#!/usr/bin/env python3
'''
WatchLockAI - Agentic AI Brain Core
Autonomous threat detection and response AI with MITRE ATT&CK awareness
'''

import asyncio
import json
import logging
import datetime
import hashlib
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class EnumJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WatchLockAI-Brain - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_brain.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class MitrePhase(Enum):
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

@dataclass
class SecurityEvent:
    timestamp: str
    event_type: str
    source: str
    details: Dict[str, Any]
    threat_level: ThreatLevel
    mitre_phase: Optional[MitrePhase] = None
    confidence: float = 0.0
    
@dataclass
class ThreatAnalysis:
    event_id: str
    threat_detected: bool
    threat_level: ThreatLevel
    mitre_tactics: List[str]
    kill_chain_stage: str
    confidence_score: float
    narrative: str
    recommended_actions: List[str]
    artifacts: List[str]

class BehavioralBaseline:
    '''Tracks normal user and system behavior patterns'''
    
    def __init__(self):
        self.user_patterns = {}
        self.system_patterns = {}
        self.time_patterns = {}
        
    def learn_pattern(self, user: str, activity: str, context: Dict):
        '''Learn normal behavioral patterns'''
        if user not in self.user_patterns:
            self.user_patterns[user] = {}
            
        if activity not in self.user_patterns[user]:
            self.user_patterns[user][activity] = []
            
        # Add temporal context
        hour = datetime.datetime.now().hour
        day_of_week = datetime.datetime.now().weekday()
        
        pattern = {
            'context': context,
            'hour': hour,
            'day_of_week': day_of_week,
            'frequency': 1
        }
        
        self.user_patterns[user][activity].append(pattern)
        
    def is_anomalous(self, user: str, activity: str, context: Dict) -> float:
        '''Detect behavioral anomalies, return anomaly score 0-1'''
        if user not in self.user_patterns:
            return 0.8  # Unknown user is suspicious
            
        if activity not in self.user_patterns[user]:
            return 0.6  # New activity for known user
            
        # Check against learned patterns
        current_hour = datetime.datetime.now().hour
        current_day = datetime.datetime.now().weekday()
        
        patterns = self.user_patterns[user][activity]
        time_matches = [p for p in patterns if abs(p['hour'] - current_hour) <= 2]
        
        if not time_matches:
            return 0.7  # Activity at unusual time
            
        return 0.1  # Normal pattern

class MitreAttackEngine:
    '''MITRE ATT&CK framework integration for threat classification'''
    
    def __init__(self):
        self.mitre_patterns = self._load_mitre_patterns()
        
    def _load_mitre_patterns(self) -> Dict:
        '''Load MITRE ATT&CK patterns and indicators'''
        return {
            "T1059": {  # Command and Scripting Interpreter
                "name": "Command and Scripting Interpreter",
                "phase": MitrePhase.EXECUTION,
                "indicators": ["powershell.exe", "cmd.exe", "wscript.exe", "encoded_command"],
                "severity": "medium"
            },
            "T1055": {  # Process Injection
                "name": "Process Injection",
                "phase": MitrePhase.DEFENSE_EVASION,
                "indicators": ["process_hollowing", "dll_injection", "reflective_loading"],
                "severity": "high"
            },
            "T1003": {  # OS Credential Dumping
                "name": "OS Credential Dumping",
                "phase": MitrePhase.CREDENTIAL_ACCESS,
                "indicators": ["lsass.exe", "sam_access", "mimikatz", "credential_dump"],
                "severity": "critical"
            },
            "T1082": {  # System Information Discovery
                "name": "System Information Discovery",
                "phase": MitrePhase.DISCOVERY,
                "indicators": ["systeminfo", "whoami", "net_user", "environment_enum"],
                "severity": "low"
            }
        }
        
    def analyze_for_mitre(self, event: SecurityEvent) -> List[str]:
        '''Analyze event against MITRE ATT&CK patterns'''
        detected_techniques = []
        
        event_text = json.dumps(event.details).lower()
        
        for technique_id, technique in self.mitre_patterns.items():
            for indicator in technique['indicators']:
                if indicator.lower() in event_text:
                    detected_techniques.append(f"{technique_id}: {technique['name']}")
                    
        return detected_techniques

class AntiPentesterLogic:
    '''Detects red team and penetration testing activities'''
    
    def __init__(self):
        self.pentest_indicators = [
            "nmap", "metasploit", "cobalt_strike", "beacon",
            "bloodhound", "sharphound", "mimikatz", "rubeus",
            "certutil", "bitsadmin", "living_off_land",
            "powershell_empire", "covenant", "sliver"
        ]
        
        self.simulation_patterns = [
            "atomic_red_team", "caldera", "purple_team",
            "attack_simulation", "red_team_exercise"
        ]
        
    def detect_pentest_activity(self, event: SecurityEvent) -> bool:
        '''Detect if event indicates penetration testing'''
        event_text = json.dumps(event.details).lower()
        
        # Check for known pentest tools
        for indicator in self.pentest_indicators:
            if indicator in event_text:
                logger.warning(f"Penetration testing activity detected: {indicator}")
                return True
                
        # Check for simulation frameworks
        for pattern in self.simulation_patterns:
            if pattern in event_text:
                logger.info(f"Security simulation detected: {pattern}")
                return True
                
        return False

class AgenticAIBrain:
    '''Core agentic AI brain for WatchLockAI'''
    
    def __init__(self):
        self.baseline = BehavioralBaseline()
        self.mitre_engine = MitreAttackEngine()
        self.anti_pentest = AntiPentesterLogic()
        self.memory_db = self._init_memory_db()
        self.threat_analysis_cache = {}
        
        # Fog-of-war memory layers
        self.active_memory = {}  # Current session
        self.short_term_memory = {}  # Last 24 hours
        self.long_term_memory = {}  # Historical patterns
        
        logger.info("WatchLockAI Agentic AI Brain initialized")
        
    def _init_memory_db(self):
        '''Initialize SQLite database for persistent memory'''
        conn = sqlite3.connect('watchlockai_memory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                event_type TEXT,
                source TEXT,
                details TEXT,
                threat_level TEXT,
                mitre_phase TEXT,
                confidence REAL,
                analysis TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_patterns (
                id INTEGER PRIMARY KEY,
                user TEXT,
                activity TEXT,
                pattern_data TEXT,
                learned_at TEXT
            )
        ''')
        
        conn.commit()
        return conn
        
    def analyze_threat(self, event: SecurityEvent) -> ThreatAnalysis:
        '''Comprehensive threat analysis using agentic AI'''
        logger.info(f"Analyzing threat event: {event.event_type}")
        
        # Check for penetration testing first
        is_pentest = self.anti_pentest.detect_pentest_activity(event)
        if is_pentest:
            logger.warning("Penetration testing activity flagged - adjusting response")
        
        # Behavioral anomaly detection
        user = event.details.get('user', 'unknown')
        activity = event.event_type
        anomaly_score = self.baseline.is_anomalous(user, activity, event.details)
        
        # MITRE ATT&CK analysis
        mitre_techniques = self.mitre_engine.analyze_for_mitre(event)
        
        # Determine threat level
        threat_level = self._calculate_threat_level(event, anomaly_score, mitre_techniques, is_pentest)
        
        # Generate narrative
        narrative = self._generate_threat_narrative(event, anomaly_score, mitre_techniques, is_pentest)
        
        # Recommend actions
        actions = self._recommend_actions(threat_level, mitre_techniques, is_pentest)
        
        # Create analysis
        analysis = ThreatAnalysis(
            event_id=f"evt_{int(time.time())}",
            threat_detected=threat_level != ThreatLevel.LOW,
            threat_level=threat_level,
            mitre_tactics=mitre_techniques,
            kill_chain_stage=self._determine_kill_chain_stage(mitre_techniques),
            confidence_score=1.0 - anomaly_score,
            narrative=narrative,
            recommended_actions=actions,
            artifacts=self._extract_artifacts(event)
        )
        
        # Store in memory
        self._store_analysis(event, analysis)
        
        return analysis
        
    def _calculate_threat_level(self, event: SecurityEvent, anomaly_score: float, 
                              mitre_techniques: List[str], is_pentest: bool) -> ThreatLevel:
        '''Calculate overall threat level'''
        if is_pentest:
            return ThreatLevel.LOW  # Reduce threat level for pentest activities
            
        # High-risk MITRE techniques
        critical_techniques = ["T1003", "T1055", "T1078"]  # Credential dumping, injection, valid accounts
        
        if any(tech.split(":")[0] in critical_techniques for tech in mitre_techniques):
            return ThreatLevel.CRITICAL
            
        if anomaly_score > 0.7:
            return ThreatLevel.HIGH
        elif anomaly_score > 0.5 or mitre_techniques:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
            
    def _generate_threat_narrative(self, event: SecurityEvent, anomaly_score: float,
                                 mitre_techniques: List[str], is_pentest: bool) -> str:
        '''Generate human-readable threat narrative'''
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if is_pentest:
            return f"[{timestamp}] Penetration testing activity detected. Event: {event.event_type}. " \
                   f"This appears to be authorized security testing rather than a genuine threat."
        
        narrative = f"[{timestamp}] Security event detected: {event.event_type} from {event.source}. "
        
        if anomaly_score > 0.6:
            narrative += f"Behavioral anomaly detected (score: {anomaly_score:.2f}). "
            
        if mitre_techniques:
            narrative += f"MITRE ATT&CK techniques identified: {', '.join(mitre_techniques[:3])}. "
            
        narrative += f"Threat assessment: {event.threat_level.value.upper()}."
        
        return narrative
        
    def _recommend_actions(self, threat_level: ThreatLevel, mitre_techniques: List[str], 
                          is_pentest: bool) -> List[str]:
        '''Recommend response actions based on threat analysis'''
        if is_pentest:
            return [
                "Monitor activity - appears to be authorized testing",
                "Log activity for security team review",
                "Continue normal operations"
            ]
            
        actions = []
        
        if threat_level == ThreatLevel.CRITICAL:
            actions.extend([
                "IMMEDIATE: Isolate affected host from network",
                "IMMEDIATE: Terminate suspicious processes",
                "IMMEDIATE: Notify security team",
                "Preserve forensic evidence",
                "Begin incident response procedures"
            ])
        elif threat_level == ThreatLevel.HIGH:
            actions.extend([
                "Increase monitoring on affected system",
                "Collect additional forensic data",
                "Notify security team",
                "Consider host isolation if threat escalates"
            ])
        elif threat_level == ThreatLevel.MEDIUM:
            actions.extend([
                "Continue monitoring",
                "Log event for analysis",
                "Check for related activities"
            ])
        else:
            actions.append("Log event for baseline learning")
            
        return actions
        
    def _determine_kill_chain_stage(self, mitre_techniques: List[str]) -> str:
        '''Map MITRE techniques to kill chain stages'''
        if not mitre_techniques:
            return "Unknown"
            
        # Simple mapping - in real implementation would be more sophisticated
        technique_id = mitre_techniques[0].split(":")[0] if mitre_techniques else ""
        
        kill_chain_mapping = {
            "T1566": "Delivery",      # Phishing
            "T1059": "Exploitation",  # Command execution
            "T1055": "Installation",  # Process injection
            "T1003": "Actions",       # Credential dumping
            "T1082": "Reconnaissance" # System discovery
        }
        
        return kill_chain_mapping.get(technique_id, "Unknown")
        
    def _extract_artifacts(self, event: SecurityEvent) -> List[str]:
        '''Extract relevant forensic artifacts'''
        artifacts = []
        
        details = event.details
        if 'process_name' in details:
            artifacts.append(f"Process: {details['process_name']}")
        if 'file_path' in details:
            artifacts.append(f"File: {details['file_path']}")
        if 'network_connection' in details:
            artifacts.append(f"Network: {details['network_connection']}")
        if 'registry_key' in details:
            artifacts.append(f"Registry: {details['registry_key']}")
            
        return artifacts
        
    def _store_analysis(self, event: SecurityEvent, analysis: ThreatAnalysis):
        '''Store analysis in persistent memory'''
        cursor = self.memory_db.cursor()
        cursor.execute('''
            INSERT INTO threat_events 
            (timestamp, event_type, source, details, threat_level, mitre_phase, confidence, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.event_type,
            event.source,
            json.dumps(event.details),
            event.threat_level.value,
            event.mitre_phase.value if event.mitre_phase else None,
            analysis.confidence_score,
            json.dumps(asdict(analysis), cls=EnumJSONEncoder)
        ))
        self.memory_db.commit()
        
    def learn_from_feedback(self, event_id: str, was_threat: bool, feedback: str):
        '''Learn from analyst feedback to improve accuracy'''
        logger.info(f"Learning from feedback for event {event_id}: was_threat={was_threat}")
        # In full implementation, would update ML models and baselines
        
    def get_system_status(self) -> Dict[str, Any]:
        '''Get current AI brain status'''
        cursor = self.memory_db.cursor()
        cursor.execute('SELECT COUNT(*) FROM threat_events WHERE date(timestamp) = date("now")')
        today_events = cursor.fetchone()[0]
        
        return {
            "status": "operational",
            "uptime": f"{time.time() - self.start_time:.0f} seconds" if hasattr(self, 'start_time') else "unknown",
            "events_analyzed_today": today_events,
            "active_memory_size": len(self.active_memory),
            "last_analysis": datetime.datetime.now().isoformat()
        }
        
    def start(self):
        '''Start the AI brain service'''
        self.start_time = time.time()
        logger.info("WatchLockAI Agentic AI Brain started and ready for threat analysis")

class AIBrainHTTPHandler(BaseHTTPRequestHandler):
    '''HTTP server for AI Brain API'''
    
    def __init__(self, *args, brain=None, **kwargs):
        self.brain = brain
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        '''Handle GET requests'''
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/status':
            self._send_json_response(self.brain.get_system_status())
        elif path == '/health':
            self._send_json_response({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})
        else:
            self._send_error(404, "Endpoint not found")
            
    def do_POST(self):
        '''Handle POST requests'''
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/analyze':
                # Convert string threat_level to enum
                if 'threat_level' in data and isinstance(data['threat_level'], str):
                    try:
                        data['threat_level'] = ThreatLevel(data['threat_level'])
                    except ValueError:
                        data['threat_level'] = ThreatLevel.LOW
                
                # Convert string mitre_phase to enum if present
                if 'mitre_phase' in data and isinstance(data['mitre_phase'], str):
                    try:
                        data['mitre_phase'] = MitrePhase(data['mitre_phase'])
                    except ValueError:
                        data['mitre_phase'] = None
                
                event = SecurityEvent(**data)
                analysis = self.brain.analyze_threat(event)
                
                # Convert analysis to dict manually to handle enums
                analysis_dict = {
                    'event_id': analysis.event_id,
                    'threat_detected': analysis.threat_detected,
                    'threat_level': analysis.threat_level.value if hasattr(analysis.threat_level, 'value') else str(analysis.threat_level),
                    'mitre_tactics': analysis.mitre_tactics,
                    'kill_chain_stage': analysis.kill_chain_stage,
                    'confidence_score': analysis.confidence_score,
                    'narrative': analysis.narrative,
                    'recommended_actions': analysis.recommended_actions,
                    'artifacts': analysis.artifacts
                }
                
                self._send_json_response(analysis_dict)
            elif path == '/feedback':
                self.brain.learn_from_feedback(
                    data['event_id'], 
                    data['was_threat'], 
                    data.get('feedback', '')
                )
                self._send_json_response({"status": "feedback_received"})
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self._send_error(500, str(e))
            
    def _send_json_response(self, data):
        '''Send JSON response'''
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, cls=EnumJSONEncoder).encode())
        
    def _send_error(self, code, message):
        '''Send error response'''
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"error": message, "code": code}
        self.wfile.write(json.dumps(error_response).encode())
        
    def log_message(self, format, *args):
        '''Override to use our logger'''
        logger.info(f"HTTP: {format % args}")

def create_handler(brain):
    '''Create HTTP handler with brain instance'''
    def handler(*args, **kwargs):
        return AIBrainHTTPHandler(*args, brain=brain, **kwargs)
    return handler

def main():
    '''Main entry point for WatchLockAI AI Brain'''
    print("🧠 Starting WatchLockAI Agentic AI Brain...")
    
    # Initialize AI Brain
    brain = AgenticAIBrain()
    brain.start()
    
    # Start HTTP server
    port = 9999
    handler = create_handler(brain)
    httpd = HTTPServer(('localhost', port), handler)
    
    print(f"✅ WatchLockAI AI Brain running on http://localhost:{port}")
    print("📡 Endpoints:")
    print("   GET  /status  - Get AI brain status")
    print("   GET  /health  - Health check")
    print("   POST /analyze - Analyze security event")
    print("   POST /feedback - Provide learning feedback")
    print()
    print("🔍 Ready for threat analysis...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WatchLockAI AI Brain...")
        httpd.shutdown()
        brain.memory_db.close()

if __name__ == "__main__":
    main()
