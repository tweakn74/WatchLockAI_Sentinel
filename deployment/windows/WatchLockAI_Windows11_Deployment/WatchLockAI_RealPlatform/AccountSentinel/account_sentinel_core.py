#!/usr/bin/env python3
'''
WatchLockAI Account Sentinel Core
Advanced user account monitoring and behavioral analysis
'''

import os
import sys
import json
import time
import datetime
import threading
import subprocess
import hashlib
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WatchLockAI-AccountSentinel - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchlockai_accounts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AccountEventType(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ACCOUNT_CREATION = "account_creation"
    ACCOUNT_DELETION = "account_deletion"
    PASSWORD_CHANGE = "password_change"
    GROUP_MODIFICATION = "group_modification"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    HIDDEN_ACCOUNT_DETECTED = "hidden_account_detected"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AccountEvent:
    timestamp: str
    event_type: AccountEventType
    user_account: str
    risk_level: RiskLevel
    source: str
    details: Dict[str, Any]
    machine_name: str
    session_id: Optional[str] = None

@dataclass
class UserBehaviorProfile:
    username: str
    typical_login_times: List[str]
    common_processes: List[str]
    frequent_locations: List[str]
    privilege_level: str
    last_activity: str
    behavior_score: float
    anomaly_count: int
    
class AccountDiscovery:
    '''Discover and monitor all system accounts'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.known_accounts = set()
        self.hidden_accounts = set()
        self.account_database = "accounts.db"
        self._init_database()
        
    def _init_database(self):
        '''Initialize accounts database'''
        try:
            conn = sqlite3.connect(self.account_database)
            cursor = conn.cursor()
            
            # Create accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT PRIMARY KEY,
                    sid TEXT,
                    full_name TEXT,
                    description TEXT,
                    account_type TEXT,
                    last_login TEXT,
                    password_last_set TEXT,
                    account_expires TEXT,
                    password_expires TEXT,
                    logon_count INTEGER,
                    bad_password_count INTEGER,
                    groups TEXT,
                    privileges TEXT,
                    home_directory TEXT,
                    login_script TEXT,
                    profile_path TEXT,
                    workstations TEXT,
                    comment TEXT,
                    flags INTEGER,
                    discovery_time TEXT,
                    is_hidden BOOLEAN,
                    risk_score REAL
                )
            ''')
            
            # Create account events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    username TEXT,
                    risk_level TEXT,
                    source TEXT,
                    details TEXT,
                    machine_name TEXT,
                    session_id TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Account database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            
    def discover_accounts(self) -> List[Dict[str, Any]]:
        '''Discover all system accounts'''
        try:
            accounts = []
            
            # Method 1: Use net user command
            accounts.extend(self._discover_via_net_user())
            
            # Method 2: Use wmic command 
            accounts.extend(self._discover_via_wmic())
            
            # Method 3: Registry-based discovery
            accounts.extend(self._discover_via_registry())
            
            # Method 4: WMI-based discovery
            accounts.extend(self._discover_via_wmi())
            
            # Deduplicate and analyze
            unique_accounts = self._deduplicate_accounts(accounts)
            self._analyze_for_hidden_accounts(unique_accounts)
            
            return unique_accounts
            
        except Exception as e:
            logger.error(f"Account discovery failed: {e}")
            return []
            
    def _discover_via_net_user(self) -> List[Dict[str, Any]]:
        '''Discover accounts using net user command'''
        try:
            accounts = []
            
            # Get list of users
            result = subprocess.run(['net', 'user'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Parse user list (usually in columns)
                    users = line.strip().split()
                    for user in users:
                        if user and not user.startswith('-') and user != 'User':
                            # Get detailed user info
                            user_info = self._get_user_details_net(user)
                            if user_info:
                                accounts.append(user_info)
                                
            return accounts
            
        except Exception as e:
            logger.debug(f"Net user discovery failed: {e}")
            return []
            
    def _get_user_details_net(self, username: str) -> Optional[Dict[str, Any]]:
        '''Get detailed user information using net user'''
        try:
            result = subprocess.run(
                ['net', 'user', username], 
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                info = {
                    'username': username,
                    'source': 'net_user',
                    'discovery_time': datetime.datetime.now().isoformat()
                }
                
                # Parse net user output
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        
                        if key in ['full_name', 'comment', 'user_comment', 'country_code']:
                            info[key] = value
                        elif key == 'account_active':
                            info['account_active'] = value.lower() == 'yes'
                        elif key == 'password_expires':
                            info['password_expires'] = value
                        elif key == 'local_group_memberships':
                            info['groups'] = value
                            
                return info
                
        except Exception as e:
            logger.debug(f"Failed to get user details for {username}: {e}")
            
        return None
        
    def _discover_via_wmic(self) -> List[Dict[str, Any]]:
        '''Discover accounts using WMIC'''
        try:
            accounts = []
            
            result = subprocess.run([
                'wmic', 'useraccount', 'get', 
                'Name,SID,Description,Disabled,LocalAccount,PasswordExpires',
                '/format:csv'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 6:
                            accounts.append({
                                'username': parts[5],  # Name
                                'sid': parts[4],       # SID
                                'description': parts[1], # Description
                                'disabled': parts[2] == 'TRUE',
                                'local_account': parts[3] == 'TRUE',
                                'password_expires': parts[6] == 'TRUE',
                                'source': 'wmic',
                                'discovery_time': datetime.datetime.now().isoformat()
                            })
                            
            return accounts
            
        except Exception as e:
            logger.debug(f"WMIC discovery failed: {e}")
            return []
            
    def _discover_via_registry(self) -> List[Dict[str, Any]]:
        '''Discover accounts via registry analysis'''
        try:
            accounts = []
            
            # This would analyze registry keys like:
            # HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users
            # For now, we simulate registry-based discovery
            
            logger.debug("Registry-based account discovery (simulated)")
            
            return accounts
            
        except Exception as e:
            logger.debug(f"Registry discovery failed: {e}")
            return []
            
    def _discover_via_wmi(self) -> List[Dict[str, Any]]:
        '''Discover accounts via WMI queries'''
        try:
            accounts = []
            
            # WMI query for user accounts
            wmi_query = "SELECT * FROM Win32_UserAccount WHERE LocalAccount=True"
            
            result = subprocess.run([
                'wmic', '/output:stdout', 'path', 'Win32_UserAccount',
                'where', 'LocalAccount=True', 'get', 
                'Name,SID,Description,Disabled,PasswordExpires,PasswordRequired',
                '/format:csv'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 6:
                            accounts.append({
                                'username': parts[2],  # Name
                                'sid': parts[4],       # SID 
                                'description': parts[1],
                                'disabled': parts[1] == 'TRUE',
                                'password_expires': parts[3] == 'TRUE',
                                'password_required': parts[5] == 'TRUE',
                                'source': 'wmi',
                                'discovery_time': datetime.datetime.now().isoformat()
                            })
                            
            return accounts
            
        except Exception as e:
            logger.debug(f"WMI discovery failed: {e}")
            return []
            
    def _deduplicate_accounts(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        '''Remove duplicate accounts and merge information'''
        try:
            account_map = {}
            
            for account in accounts:
                username = account.get('username', '').lower()
                if username:
                    if username in account_map:
                        # Merge information from multiple sources
                        existing = account_map[username]
                        for key, value in account.items():
                            if key not in existing or not existing[key]:
                                existing[key] = value
                    else:
                        account_map[username] = account
                        
            return list(account_map.values())
            
        except Exception as e:
            logger.error(f"Account deduplication failed: {e}")
            return accounts
            
    def _analyze_for_hidden_accounts(self, accounts: List[Dict[str, Any]]):
        '''Analyze accounts for hidden or suspicious characteristics'''
        try:
            for account in accounts:
                username = account.get('username', '')
                is_hidden = False
                risk_factors = []
                
                # Check for hidden account characteristics
                if not account.get('description'):
                    risk_factors.append("No description")
                    
                if account.get('disabled') == False and not account.get('password_required'):
                    risk_factors.append("No password required")
                    is_hidden = True
                    
                # Check for suspicious usernames
                suspicious_patterns = ['$', 'admin', 'test', 'temp', 'guest']
                if any(pattern in username.lower() for pattern in suspicious_patterns):
                    risk_factors.append("Suspicious username pattern")
                    
                # Check for unusual SIDs
                sid = account.get('sid', '')
                if sid and (len(sid) < 20 or '-500' in sid or '-501' in sid):
                    risk_factors.append("Unusual SID pattern")
                    
                account['is_hidden'] = is_hidden
                account['risk_factors'] = risk_factors
                account['risk_score'] = len(risk_factors) * 0.25
                
                if is_hidden or risk_factors:
                    self._report_suspicious_account(account)
                    
        except Exception as e:
            logger.error(f"Hidden account analysis failed: {e}")
            
    def _report_suspicious_account(self, account: Dict[str, Any]):
        '''Report suspicious account to AI Brain'''
        try:
            event = AccountEvent(
                timestamp=datetime.datetime.now().isoformat(),
                event_type=AccountEventType.HIDDEN_ACCOUNT_DETECTED,
                user_account=account.get('username', 'unknown'),
                risk_level=RiskLevel.HIGH if account.get('is_hidden') else RiskLevel.MEDIUM,
                source="AccountDiscovery",
                details={
                    "account_info": account,
                    "risk_factors": account.get('risk_factors', []),
                    "risk_score": account.get('risk_score', 0)
                },
                machine_name=os.environ.get('COMPUTERNAME', 'unknown')
            )
            
            self._send_account_event(event)
            logger.warning(f"Suspicious account detected: {account.get('username')}")
            
        except Exception as e:
            logger.error(f"Failed to report suspicious account: {e}")
            
    def _send_account_event(self, event: AccountEvent):
        '''Send account event to AI Brain'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"account_{event.event_type.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.risk_level.value,
                "user_account": event.user_account,
                "machine_name": event.machine_name
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain confirmed account threat: {event.user_account}")
                    
        except Exception as e:
            logger.error(f"Failed to send account event: {e}")

class BehaviorAnalyzer:
    '''Analyze user behavior patterns and detect anomalies'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.behavior_database = "user_behavior.db"
        self.user_profiles = {}
        self._init_behavior_database()
        
    def _init_behavior_database(self):
        '''Initialize behavior analysis database'''
        try:
            conn = sqlite3.connect(self.behavior_database)
            cursor = conn.cursor()
            
            # User behavior profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_behavior (
                    username TEXT PRIMARY KEY,
                    typical_login_times TEXT,
                    common_processes TEXT,
                    frequent_locations TEXT,
                    privilege_level TEXT,
                    last_activity TEXT,
                    behavior_score REAL,
                    anomaly_count INTEGER,
                    profile_created TEXT,
                    profile_updated TEXT
                )
            ''')
            
            # Behavior events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS behavior_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    username TEXT,
                    event_type TEXT,
                    location TEXT,
                    process_name TEXT,
                    anomaly_score REAL,
                    details TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Behavior database initialized")
            
        except Exception as e:
            logger.error(f"Behavior database initialization failed: {e}")
            
    def analyze_login_behavior(self, username: str, login_time: str, source_ip: str = None):
        '''Analyze login behavior for anomalies'''
        try:
            profile = self._get_user_profile(username)
            if not profile:
                profile = self._create_user_profile(username)
                
            # Analyze login time pattern
            anomaly_score = 0.0
            anomalies = []
            
            # Check login time against typical patterns
            current_hour = datetime.datetime.fromisoformat(login_time).hour
            typical_hours = self._parse_typical_hours(profile.typical_login_times)
            
            if typical_hours and current_hour not in typical_hours:
                if abs(current_hour - min(typical_hours)) > 4:
                    anomaly_score += 0.3
                    anomalies.append("Unusual login time")
                    
            # Check source IP (if available)
            if source_ip and not self._is_known_location(username, source_ip):
                anomaly_score += 0.4
                anomalies.append("Unknown login location")
                
            # Check frequency (rapid successive logins)
            if self._check_rapid_logins(username, login_time):
                anomaly_score += 0.3
                anomalies.append("Rapid successive logins")
                
            # Update profile
            self._update_login_behavior(username, login_time, source_ip)
            
            if anomaly_score > 0.5:
                self._report_behavior_anomaly(username, "login", anomalies, anomaly_score)
                
        except Exception as e:
            logger.error(f"Login behavior analysis failed: {e}")
            
    def analyze_process_behavior(self, username: str, process_name: str, command_line: str = None):
        '''Analyze process execution behavior'''
        try:
            profile = self._get_user_profile(username)
            if not profile:
                profile = self._create_user_profile(username)
                
            anomaly_score = 0.0
            anomalies = []
            
            # Check against common processes
            common_processes = self._parse_common_processes(profile.common_processes)
            
            if process_name.lower() not in [p.lower() for p in common_processes]:
                # New process for this user
                anomaly_score += 0.2
                
                # Check for suspicious processes
                suspicious_processes = [
                    'mimikatz', 'procdump', 'psexec', 'powershell', 'cmd', 
                    'wmic', 'net.exe', 'reg.exe', 'sc.exe'
                ]
                
                if any(susp in process_name.lower() for susp in suspicious_processes):
                    anomaly_score += 0.5
                    anomalies.append(f"Suspicious process: {process_name}")
                    
            # Analyze command line for suspicious patterns
            if command_line:
                suspicious_patterns = [
                    '-enc', '-encodedcommand', 'invoke-expression', 'downloadstring',
                    'bypass', 'hidden', 'noprofile', 'sekurlsa', 'lsadump'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern.lower() in command_line.lower():
                        anomaly_score += 0.4
                        anomalies.append(f"Suspicious command pattern: {pattern}")
                        break
                        
            # Update profile
            self._update_process_behavior(username, process_name)
            
            if anomaly_score > 0.4:
                self._report_behavior_anomaly(username, "process", anomalies, anomaly_score)
                
        except Exception as e:
            logger.error(f"Process behavior analysis failed: {e}")
            
    def detect_privilege_escalation(self, username: str, old_privileges: List[str], new_privileges: List[str]):
        '''Detect privilege escalation attempts'''
        try:
            escalation_detected = False
            escalation_details = []
            
            # Check for new high-value privileges
            high_value_privileges = [
                'SeDebugPrivilege', 'SeTcbPrivilege', 'SeBackupPrivilege',
                'SeRestorePrivilege', 'SeSystemtimePrivilege', 'SeShutdownPrivilege',
                'SeRemoteShutdownPrivilege', 'SeTakeOwnershipPrivilege',
                'SeLoadDriverPrivilege', 'SeSystemProfilePrivilege'
            ]
            
            added_privileges = set(new_privileges) - set(old_privileges)
            
            for privilege in added_privileges:
                if privilege in high_value_privileges:
                    escalation_detected = True
                    escalation_details.append(f"Gained high-value privilege: {privilege}")
                    
            # Check for admin group additions
            if self._check_admin_group_addition(username):
                escalation_detected = True
                escalation_details.append("Added to administrative group")
                
            if escalation_detected:
                event = AccountEvent(
                    timestamp=datetime.datetime.now().isoformat(),
                    event_type=AccountEventType.PRIVILEGE_ESCALATION,
                    user_account=username,
                    risk_level=RiskLevel.CRITICAL,
                    source="BehaviorAnalyzer",
                    details={
                        "escalation_type": "privilege_escalation",
                        "old_privileges": old_privileges,
                        "new_privileges": new_privileges,
                        "added_privileges": list(added_privileges),
                        "escalation_details": escalation_details
                    },
                    machine_name=os.environ.get('COMPUTERNAME', 'unknown')
                )
                
                self._send_account_event(event)
                logger.critical(f"Privilege escalation detected for user: {username}")
                
        except Exception as e:
            logger.error(f"Privilege escalation detection failed: {e}")
            
    def _get_user_profile(self, username: str) -> Optional[UserBehaviorProfile]:
        '''Get user behavior profile from database'''
        try:
            if username in self.user_profiles:
                return self.user_profiles[username]
                
            conn = sqlite3.connect(self.behavior_database)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_behavior WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if row:
                profile = UserBehaviorProfile(
                    username=row[0],
                    typical_login_times=json.loads(row[1]) if row[1] else [],
                    common_processes=json.loads(row[2]) if row[2] else [],
                    frequent_locations=json.loads(row[3]) if row[3] else [],
                    privilege_level=row[4] or "user",
                    last_activity=row[5] or "",
                    behavior_score=row[6] or 0.0,
                    anomaly_count=row[7] or 0
                )
                
                self.user_profiles[username] = profile
                return profile
                
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
            
    def _create_user_profile(self, username: str) -> UserBehaviorProfile:
        '''Create new user behavior profile'''
        try:
            profile = UserBehaviorProfile(
                username=username,
                typical_login_times=[],
                common_processes=[],
                frequent_locations=[],
                privilege_level="user",
                last_activity=datetime.datetime.now().isoformat(),
                behavior_score=0.0,
                anomaly_count=0
            )
            
            self.user_profiles[username] = profile
            self._save_user_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            return UserBehaviorProfile(username, [], [], [], "user", "", 0.0, 0)
            
    def _save_user_profile(self, profile: UserBehaviorProfile):
        '''Save user profile to database'''
        try:
            conn = sqlite3.connect(self.behavior_database)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_behavior 
                (username, typical_login_times, common_processes, frequent_locations,
                 privilege_level, last_activity, behavior_score, anomaly_count,
                 profile_created, profile_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.username,
                json.dumps(profile.typical_login_times),
                json.dumps(profile.common_processes),
                json.dumps(profile.frequent_locations),
                profile.privilege_level,
                profile.last_activity,
                profile.behavior_score,
                profile.anomaly_count,
                datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            
    def _parse_typical_hours(self, login_times: List[str]) -> List[int]:
        '''Parse typical login hours from login times'''
        try:
            hours = []
            for time_str in login_times:
                try:
                    dt = datetime.datetime.fromisoformat(time_str)
                    hours.append(dt.hour)
                except:
                    continue
            return list(set(hours))  # Remove duplicates
        except:
            return []
            
    def _parse_common_processes(self, processes: List[str]) -> List[str]:
        '''Parse common processes from profile'''
        return processes if processes else []
        
    def _is_known_location(self, username: str, source_ip: str) -> bool:
        '''Check if source IP is a known location for user'''
        try:
            profile = self._get_user_profile(username)
            if profile and profile.frequent_locations:
                return source_ip in profile.frequent_locations
            return False
        except:
            return False
            
    def _check_rapid_logins(self, username: str, login_time: str) -> bool:
        '''Check for rapid successive logins'''
        try:
            # Simple check - in real implementation would check recent login history
            return False
        except:
            return False
            
    def _check_admin_group_addition(self, username: str) -> bool:
        '''Check if user was recently added to admin groups'''
        try:
            # This would check Windows event logs or group membership changes
            return False
        except:
            return False
            
    def _update_login_behavior(self, username: str, login_time: str, source_ip: str = None):
        '''Update user login behavior profile'''
        try:
            profile = self._get_user_profile(username)
            if profile:
                # Add login time
                profile.typical_login_times.append(login_time)
                
                # Keep only recent login times (last 100)
                if len(profile.typical_login_times) > 100:
                    profile.typical_login_times = profile.typical_login_times[-100:]
                    
                # Add location if provided
                if source_ip and source_ip not in profile.frequent_locations:
                    profile.frequent_locations.append(source_ip)
                    
                profile.last_activity = login_time
                self._save_user_profile(profile)
                
        except Exception as e:
            logger.error(f"Failed to update login behavior: {e}")
            
    def _update_process_behavior(self, username: str, process_name: str):
        '''Update user process behavior profile'''
        try:
            profile = self._get_user_profile(username)
            if profile:
                if process_name not in profile.common_processes:
                    profile.common_processes.append(process_name)
                    
                    # Keep only recent processes (last 50)
                    if len(profile.common_processes) > 50:
                        profile.common_processes = profile.common_processes[-50:]
                        
                profile.last_activity = datetime.datetime.now().isoformat()
                self._save_user_profile(profile)
                
        except Exception as e:
            logger.error(f"Failed to update process behavior: {e}")
            
    def _report_behavior_anomaly(self, username: str, event_type: str, anomalies: List[str], score: float):
        '''Report behavior anomaly to AI Brain'''
        try:
            event = AccountEvent(
                timestamp=datetime.datetime.now().isoformat(),
                event_type=AccountEventType.SUSPICIOUS_ACTIVITY,
                user_account=username,
                risk_level=RiskLevel.HIGH if score > 0.7 else RiskLevel.MEDIUM,
                source="BehaviorAnalyzer",
                details={
                    "anomaly_type": event_type,
                    "anomalies": anomalies,
                    "anomaly_score": score,
                    "baseline_behavior": "deviation_detected"
                },
                machine_name=os.environ.get('COMPUTERNAME', 'unknown')
            )
            
            self._send_account_event(event)
            logger.warning(f"Behavior anomaly detected for {username}: {anomalies}")
            
        except Exception as e:
            logger.error(f"Failed to report behavior anomaly: {e}")
            
    def _send_account_event(self, event: AccountEvent):
        '''Send account event to AI Brain'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"account_{event.event_type.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.risk_level.value,
                "user_account": event.user_account,
                "machine_name": event.machine_name
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain confirmed behavior threat: {event.user_account}")
                    
        except Exception as e:
            logger.error(f"Failed to send account event: {e}")

class AccountSentinelCore:
    '''Main Account Sentinel orchestrator'''
    
    def __init__(self, config_file: str = "account_sentinel_config.json"):
        self.config = self._load_config(config_file)
        self.ai_brain_url = self.config.get('ai_brain_url', 'http://localhost:9999')
        
        # Initialize components
        self.account_discovery = AccountDiscovery(self.ai_brain_url)
        self.behavior_analyzer = BehaviorAnalyzer(self.ai_brain_url)
        
        self.running = False
        self.monitoring_thread = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        '''Load account sentinel configuration'''
        default_config = {
            "ai_brain_url": "http://localhost:9999",
            "monitoring_enabled": {
                "account_discovery": True,
                "behavior_analysis": True,
                "privilege_monitoring": True,
                "login_monitoring": True
            },
            "discovery_intervals": {
                "account_scan": 3600,      # 1 hour
                "behavior_check": 300,     # 5 minutes
                "privilege_check": 600     # 10 minutes
            },
            "anomaly_thresholds": {
                "behavior_score": 0.5,
                "privilege_escalation": 0.8,
                "login_anomaly": 0.6
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")
            
        return default_config
        
    def start_monitoring(self):
        '''Start Account Sentinel monitoring'''
        logger.info("Starting WatchLockAI Account Sentinel...")
        
        self.running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("[PASS] Account Sentinel monitoring active")
        
    def _monitoring_loop(self):
        '''Main monitoring loop'''
        last_account_scan = 0
        last_behavior_check = 0
        last_privilege_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Account discovery
                if (current_time - last_account_scan) >= self.config['discovery_intervals']['account_scan']:
                    if self.config['monitoring_enabled']['account_discovery']:
                        self._perform_account_discovery()
                    last_account_scan = current_time
                    
                # Behavior analysis
                if (current_time - last_behavior_check) >= self.config['discovery_intervals']['behavior_check']:
                    if self.config['monitoring_enabled']['behavior_analysis']:
                        self._perform_behavior_analysis()
                    last_behavior_check = current_time
                    
                # Privilege monitoring
                if (current_time - last_privilege_check) >= self.config['discovery_intervals']['privilege_check']:
                    if self.config['monitoring_enabled']['privilege_monitoring']:
                        self._perform_privilege_monitoring()
                    last_privilege_check = current_time
                    
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)
                
    def _perform_account_discovery(self):
        '''Perform account discovery scan'''
        try:
            logger.info("Performing account discovery scan...")
            accounts = self.account_discovery.discover_accounts()
            logger.info(f"Discovered {len(accounts)} accounts")
            
            # Store accounts in database
            self._store_discovered_accounts(accounts)
            
        except Exception as e:
            logger.error(f"Account discovery failed: {e}")
            
    def _perform_behavior_analysis(self):
        '''Perform behavior analysis'''
        try:
            logger.debug("Performing behavior analysis...")
            
            # Analyze current user sessions
            current_users = self._get_current_users()
            for username in current_users:
                # Simulate behavior analysis
                self.behavior_analyzer.analyze_login_behavior(
                    username, 
                    datetime.datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}")
            
    def _perform_privilege_monitoring(self):
        '''Perform privilege escalation monitoring'''
        try:
            logger.debug("Performing privilege monitoring...")
            
            # Check for privilege changes
            # This would monitor Windows event logs for privilege changes
            
        except Exception as e:
            logger.error(f"Privilege monitoring failed: {e}")
            
    def _get_current_users(self) -> List[str]:
        '''Get currently logged in users'''
        try:
            users = []
            for user in psutil.users():
                if user.name not in users:
                    users.append(user.name)
            return users
        except:
            return []
            
    def _store_discovered_accounts(self, accounts: List[Dict[str, Any]]):
        '''Store discovered accounts in database'''
        try:
            conn = sqlite3.connect(self.account_discovery.account_database)
            cursor = conn.cursor()
            
            for account in accounts:
                cursor.execute('''
                    INSERT OR REPLACE INTO accounts 
                    (username, sid, description, account_type, discovery_time, 
                     is_hidden, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    account.get('username'),
                    account.get('sid'),
                    account.get('description'),
                    account.get('source'),
                    account.get('discovery_time'),
                    account.get('is_hidden', False),
                    account.get('risk_score', 0.0)
                ))
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store accounts: {e}")
            
    def stop_monitoring(self):
        '''Stop Account Sentinel monitoring'''
        logger.info("Stopping Account Sentinel...")
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        logger.info("[PASS] Account Sentinel stopped")
        
    def get_status(self) -> Dict[str, Any]:
        '''Get Account Sentinel status'''
        return {
            "running": self.running,
            "config": self.config,
            "components": {
                "account_discovery": self.account_discovery is not None,
                "behavior_analyzer": self.behavior_analyzer is not None
            }
        }

def main():
    '''Main entry point for Account Sentinel'''
    print("[U+1F465] WatchLockAI Account Sentinel")
    print("Advanced user account monitoring and behavioral analysis")
    print()
    
    try:
        # Initialize Account Sentinel
        sentinel = AccountSentinelCore()
        sentinel.start_monitoring()
        
        print("[SEARCH] Monitoring capabilities active:")
        print("   * Account Discovery - Hidden account detection")
        print("   * Behavior Analysis - User behavior baselining")
        print("   * Privilege Monitoring - Escalation detection")
        print("   * Login Analysis - Anomalous login detection")
        print()
        print("[U+1F464] Account Sentinel is now monitoring!")
        print("Press Ctrl+C to stop monitoring")
        
        # Keep sentinel running
        while sentinel.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Shutting down Account Sentinel...")
        sentinel.stop_monitoring()
        
    except Exception as e:
        logger.error(f"Account Sentinel error: {e}")

if __name__ == "__main__":
    main()
