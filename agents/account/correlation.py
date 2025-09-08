#!/usr/bin/env python3
'''
WatchLockAI Identity Correlation Engine
Correlate user identities across multiple systems and contexts
'''

import os
import json
import time
import sqlite3
import datetime
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class Identity:
    primary_id: str
    username: str
    full_name: str
    email: str
    domain: str
    sid: str
    aliases: List[str]
    linked_accounts: List[str]
    confidence_score: float
    last_seen: str
    
class IdentityCorrelationEngine:
    '''Correlate and track user identities across systems'''
    
    def __init__(self):
        self.identity_database = "identity_correlation.db"
        self.identities = {}
        self._init_database()
        
    def _init_database(self):
        '''Initialize identity correlation database'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            # Identities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identities (
                    primary_id TEXT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    email TEXT,
                    domain TEXT,
                    sid TEXT,
                    aliases TEXT,
                    linked_accounts TEXT,
                    confidence_score REAL,
                    last_seen TEXT,
                    created_time TEXT,
                    updated_time TEXT
                )
            ''')
            
            # Identity events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identity_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    identity_id TEXT,
                    event_type TEXT,
                    source_system TEXT,
                    details TEXT,
                    correlation_confidence REAL
                )
            ''')
            
            # Identity relationships
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identity_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identity1_id TEXT,
                    identity2_id TEXT,
                    relationship_type TEXT,
                    confidence_score REAL,
                    evidence TEXT,
                    created_time TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Identity correlation database initialized")
            
        except Exception as e:
            logger.error(f"Identity database initialization failed: {e}")
            
    def correlate_identity(self, username: str, additional_info: Dict[str, Any]) -> str:
        '''Correlate and identify user across systems'''
        try:
            # Generate primary identity ID
            primary_id = self._generate_identity_id(username, additional_info)
            
            # Check for existing identity
            existing_identity = self._find_existing_identity(username, additional_info)
            
            if existing_identity:
                # Update existing identity
                self._update_identity(existing_identity, additional_info)
                return existing_identity.primary_id
            else:
                # Create new identity
                identity = self._create_identity(primary_id, username, additional_info)
                return identity.primary_id
                
        except Exception as e:
            logger.error(f"Identity correlation failed: {e}")
            return f"unknown_{username}"
            
    def _generate_identity_id(self, username: str, info: Dict[str, Any]) -> str:
        '''Generate unique identity ID'''
        try:
            # Create deterministic ID based on key attributes
            key_attributes = [
                username.lower(),
                info.get('sid', ''),
                info.get('email', '').lower(),
                info.get('domain', '').lower()
            ]
            
            combined = '|'.join(filter(None, key_attributes))
            hash_obj = hashlib.sha256(combined.encode())
            return f"id_{hash_obj.hexdigest()[:16]}"
            
        except Exception:
            return f"id_{username}_{int(time.time())}"
            
    def _find_existing_identity(self, username: str, info: Dict[str, Any]) -> Optional[Identity]:
        '''Find existing identity by various correlation methods'''
        try:
            # Method 1: Exact username match
            identity = self._find_by_username(username)
            if identity:
                return identity
                
            # Method 2: SID match
            sid = info.get('sid')
            if sid:
                identity = self._find_by_sid(sid)
                if identity:
                    return identity
                    
            # Method 3: Email match
            email = info.get('email')
            if email:
                identity = self._find_by_email(email)
                if identity:
                    return identity
                    
            # Method 4: Full name match
            full_name = info.get('full_name')
            if full_name:
                identity = self._find_by_full_name(full_name)
                if identity:
                    return identity
                    
            return None
            
        except Exception as e:
            logger.error(f"Identity search failed: {e}")
            return None
            
    def _find_by_username(self, username: str) -> Optional[Identity]:
        '''Find identity by username'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM identities WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_identity(row)
                
            conn.close()
            return None
            
        except Exception:
            return None
            
    def _find_by_sid(self, sid: str) -> Optional[Identity]:
        '''Find identity by Windows SID'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM identities WHERE sid = ?', (sid,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_identity(row)
                
            conn.close()
            return None
            
        except Exception:
            return None
            
    def _find_by_email(self, email: str) -> Optional[Identity]:
        '''Find identity by email address'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM identities WHERE email = ?', (email.lower(),))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_identity(row)
                
            conn.close()
            return None
            
        except Exception:
            return None
            
    def _find_by_full_name(self, full_name: str) -> Optional[Identity]:
        '''Find identity by full name'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM identities WHERE full_name = ?', (full_name,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_identity(row)
                
            conn.close()
            return None
            
        except Exception:
            return None
            
    def _row_to_identity(self, row) -> Identity:
        '''Convert database row to Identity object'''
        return Identity(
            primary_id=row[0],
            username=row[1],
            full_name=row[2],
            email=row[3],
            domain=row[4],
            sid=row[5],
            aliases=json.loads(row[6]) if row[6] else [],
            linked_accounts=json.loads(row[7]) if row[7] else [],
            confidence_score=row[8],
            last_seen=row[9]
        )
        
    def _create_identity(self, primary_id: str, username: str, info: Dict[str, Any]) -> Identity:
        '''Create new identity'''
        try:
            identity = Identity(
                primary_id=primary_id,
                username=username,
                full_name=info.get('full_name', ''),
                email=info.get('email', ''),
                domain=info.get('domain', ''),
                sid=info.get('sid', ''),
                aliases=[],
                linked_accounts=[],
                confidence_score=1.0,
                last_seen=datetime.datetime.now().isoformat()
            )
            
            self._save_identity(identity)
            self.identities[primary_id] = identity
            
            return identity
            
        except Exception as e:
            logger.error(f"Identity creation failed: {e}")
            return Identity(primary_id, username, '', '', '', '', [], [], 0.0, '')
            
    def _update_identity(self, identity: Identity, info: Dict[str, Any]):
        '''Update existing identity with new information'''
        try:
            # Update fields if new information available
            if info.get('full_name') and not identity.full_name:
                identity.full_name = info['full_name']
                
            if info.get('email') and not identity.email:
                identity.email = info['email']
                
            if info.get('domain') and not identity.domain:
                identity.domain = info['domain']
                
            if info.get('sid') and not identity.sid:
                identity.sid = info['sid']
                
            identity.last_seen = datetime.datetime.now().isoformat()
            
            self._save_identity(identity)
            self.identities[identity.primary_id] = identity
            
        except Exception as e:
            logger.error(f"Identity update failed: {e}")
            
    def _save_identity(self, identity: Identity):
        '''Save identity to database'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO identities 
                (primary_id, username, full_name, email, domain, sid,
                 aliases, linked_accounts, confidence_score, last_seen,
                 created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                identity.primary_id,
                identity.username,
                identity.full_name,
                identity.email,
                identity.domain,
                identity.sid,
                json.dumps(identity.aliases),
                json.dumps(identity.linked_accounts),
                identity.confidence_score,
                identity.last_seen,
                datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Identity save failed: {e}")
            
    def get_identity_relationships(self, primary_id: str) -> List[Dict[str, Any]]:
        '''Get relationships for an identity'''
        try:
            conn = sqlite3.connect(self.identity_database)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM identity_relationships 
                WHERE identity1_id = ? OR identity2_id = ?
            ''', (primary_id, primary_id))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append({
                    'relationship_id': row[0],
                    'identity1_id': row[1],
                    'identity2_id': row[2],
                    'relationship_type': row[3],
                    'confidence_score': row[4],
                    'evidence': json.loads(row[5]) if row[5] else {},
                    'created_time': row[6]
                })
                
            conn.close()
            return relationships
            
        except Exception as e:
            logger.error(f"Failed to get relationships: {e}")
            return []

def main():
    '''Test identity correlation'''
    print("🔗 WatchLockAI Identity Correlation Engine")
    print("Correlating user identities across systems")
    
    engine = IdentityCorrelationEngine()
    
    # Test identity correlation
    test_users = [
        {"username": "jdoe", "full_name": "John Doe", "email": "john.doe@company.com", "sid": "S-1-5-21-123456789-1"},
        {"username": "john.doe", "full_name": "John Doe", "email": "john.doe@company.com", "sid": "S-1-5-21-123456789-1"},
        {"username": "administrator", "full_name": "Built-in Administrator", "sid": "S-1-5-21-123456789-500"}
    ]
    
    for user in test_users:
        identity_id = engine.correlate_identity(user["username"], user)
        print(f"   User '{user['username']}' → Identity ID: {identity_id}")
    
    print("✅ Identity correlation test completed")

if __name__ == "__main__":
    main()
