#!/usr/bin/env python3
'''
WatchLockAI Browser Monitor
Monitor browser activities and detect malicious web interactions
'''

import os
import json
import sqlite3
import threading
import time
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Any
import requests

logger = logging.getLogger(__name__)

class BrowserMonitor:
    '''Monitor browser activities for security threats'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.browser_paths = self._get_browser_paths()
        self.known_urls = set()
        self.malicious_domains = [
            'malware.com', 'phishing.net', 'suspicious.org',
            'virus.info', 'trojan.biz', 'malicious.site'
        ]
        
    def _get_browser_paths(self) -> Dict[str, str]:
        '''Get browser database paths'''
        user_profile = os.environ.get('USERPROFILE', '')
        
        paths = {}
        
        # Chrome
        chrome_path = Path(user_profile) / "AppData/Local/Google/Chrome/User Data/Default/History"
        if chrome_path.exists():
            paths['chrome'] = str(chrome_path)
            
        # Firefox (find profile)
        firefox_profiles = Path(user_profile) / "AppData/Roaming/Mozilla/Firefox/Profiles"
        if firefox_profiles.exists():
            for profile_dir in firefox_profiles.iterdir():
                if profile_dir.is_dir():
                    places_db = profile_dir / "places.sqlite"
                    if places_db.exists():
                        paths['firefox'] = str(places_db)
                        break
                        
        # Edge
        edge_path = Path(user_profile) / "AppData/Local/Microsoft/Edge/User Data/Default/History"
        if edge_path.exists():
            paths['edge'] = str(edge_path)
            
        return paths
        
    def start_monitoring(self):
        '''Start browser monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_browsers)
        thread.daemon = True
        thread.start()
        logger.info(f"Browser monitoring started for: {list(self.browser_paths.keys())}")
        
    def _monitor_browsers(self):
        '''Monitor browser activities'''
        while self.running:
            try:
                for browser, db_path in self.browser_paths.items():
                    self._check_browser_history(browser, db_path)
                    
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Browser monitoring error: {e}")
                time.sleep(60)
                
    def _check_browser_history(self, browser: str, db_path: str):
        '''Check browser history for new entries'''
        try:
            # Copy database to avoid locking issues
            temp_db = f"{db_path}.temp"
            import shutil
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query recent URLs
            if browser in ['chrome', 'edge']:
                cursor.execute('''
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls 
                    WHERE last_visit_time > ?
                    ORDER BY last_visit_time DESC
                    LIMIT 100
                ''', (self._get_recent_timestamp(),))
            elif browser == 'firefox':
                cursor.execute('''
                    SELECT url, title, visit_count, last_visit_date
                    FROM moz_places 
                    WHERE last_visit_date > ?
                    ORDER BY last_visit_date DESC
                    LIMIT 100
                ''', (self._get_recent_timestamp_firefox(),))
                
            results = cursor.fetchall()
            conn.close()
            
            # Clean up temp file
            os.remove(temp_db)
            
            # Analyze URLs
            for row in results:
                url = row[0]
                if url not in self.known_urls:
                    self.known_urls.add(url)
                    self._analyze_url(browser, row)
                    
        except Exception as e:
            logger.debug(f"Error checking {browser} history: {e}")
            
    def _get_recent_timestamp(self) -> int:
        '''Get timestamp for recent activity (Chrome/Edge format)'''
        # Chrome uses microseconds since Windows epoch (1601)
        recent_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        windows_epoch = datetime.datetime(1601, 1, 1)
        delta = recent_time - windows_epoch
        return int(delta.total_seconds() * 1000000)
        
    def _get_recent_timestamp_firefox(self) -> int:
        '''Get timestamp for recent activity (Firefox format)'''
        # Firefox uses microseconds since Unix epoch
        recent_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        unix_epoch = datetime.datetime(1970, 1, 1)
        delta = recent_time - unix_epoch
        return int(delta.total_seconds() * 1000000)
        
    def _analyze_url(self, browser: str, url_data: tuple):
        '''Analyze URL for suspicious characteristics'''
        try:
            url, title, visit_count, last_visit = url_data
            
            is_suspicious = False
            reasons = []
            
            # Check for malicious domains
            for domain in self.malicious_domains:
                if domain in url:
                    is_suspicious = True
                    reasons.append(f"Known malicious domain: {domain}")
                    break
                    
            # Check for suspicious URL patterns
            suspicious_patterns = [
                'download.php', 'exploit.html', 'malware.exe',
                'phishing', 'suspicious', 'virus', 'trojan'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in url.lower():
                    is_suspicious = True
                    reasons.append(f"Suspicious URL pattern: {pattern}")
                    break
                    
            # Check for suspicious file downloads
            if any(ext in url.lower() for ext in ['.exe', '.scr', '.bat', '.vbs', '.ps1']):
                is_suspicious = True
                reasons.append("Potentially dangerous file download")
                
            # Check for base64 encoded URLs
            if 'base64' in url or len(url) > 500:
                is_suspicious = True
                reasons.append("Suspicious URL encoding or length")
                
            if is_suspicious:
                self._report_browser_event(browser, url, title, reasons)
                
        except Exception as e:
            logger.error(f"Error analyzing URL: {e}")
            
    def _report_browser_event(self, browser: str, url: str, title: str, reasons: List[str]):
        '''Report suspicious browser event'''
        try:
            event_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "browser_suspicious_activity",
                "source": f"BrowserMonitor_{browser}",
                "details": {
                    "browser": browser,
                    "url": url[:200],  # Truncate long URLs
                    "page_title": title[:100] if title else "Unknown",
                    "reasons": reasons
                },
                "threat_level": "medium"
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"Suspicious browser activity: {url}")
                    
        except Exception as e:
            logger.error(f"Failed to report browser event: {e}")

def main():
    '''Test browser monitoring'''
    print("🌐 WatchLockAI Browser Monitor")
    print("Monitoring browser activities for security threats")
    
    monitor = BrowserMonitor()
    monitor.start_monitoring()
    
    print("✅ Browser monitoring started")
    print("🔍 Monitoring browsers:", list(monitor.browser_paths.keys()))
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping browser monitor...")
        monitor.running = False

if __name__ == "__main__":
    main()
