#!/usr/bin/env python3
"""WatchLockAI Sentinel Python SDK Client.

Comprehensive Python client library for WatchLockAI Sentinel API with:
- Full API endpoint coverage (41+ routes)
- Authentication and session management
- Error handling and retry logic
- Rate limiting awareness
- Streaming support (SSE)
- Comprehensive logging
- Type hints and documentation

Usage:
    from sentinel_sdk import SentinelClient
    
    client = SentinelClient(base_url="http://localhost:8080")
    health = client.get_health()
    print(f"Service status: {health['ok']}")
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator
from urllib.parse import urljoin, urlencode
import warnings

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests library not available - HTTP functionality disabled")

try:
    import sseclient
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    warnings.warn("sseclient-py not available - streaming functionality disabled")


class SentinelAPIError(Exception):
    """Base exception for Sentinel API errors."""
    def __init__(self, message: str, response: Optional[requests.Response] = None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response else None


class SentinelAuthError(SentinelAPIError):
    """Authentication-related API errors."""
    pass


class SentinelRateLimitError(SentinelAPIError):
    """Rate limiting API errors."""
    pass


class SentinelClient:
    """WatchLockAI Sentinel API Client.
    
    Provides comprehensive access to all Sentinel API endpoints with
    authentication, error handling, and rate limiting support.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        admin_token: Optional[str] = None,
        session_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        user_agent: str = "SentinelSDK/1.0",
        verify_ssl: bool = True,
        debug: bool = False
    ):
        """Initialize Sentinel API client.
        
        Args:
            base_url: Base URL of Sentinel API server
            admin_token: Admin token for privileged operations
            session_key: Session key for cookie-based authentication
            username: Username for login-based authentication
            password: Password for login-based authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            backoff_factor: Backoff factor for retry delays
            user_agent: User-Agent header for requests
            verify_ssl: Whether to verify SSL certificates
            debug: Enable debug logging
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for SentinelClient")
            
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token
        self.session_key = session_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.user_agent = user_agent
        self.verify_ssl = verify_ssl
        self.debug = debug
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        
        # Setup HTTP session with retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Session state
        self.authenticated = False
        self.session_cookies = {}
        
        # Auto-authenticate if credentials provided
        if username and password:
            self.login(username, password)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        require_auth: bool = False,
        require_admin: bool = False
    ) -> requests.Response:
        """Make authenticated API request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            require_auth: Whether authentication is required
            require_admin: Whether admin authentication is required
            
        Returns:
            Response object
            
        Raises:
            SentinelAuthError: Authentication required but not provided
            SentinelRateLimitError: Rate limit exceeded
            SentinelAPIError: Other API errors
        """
        url = urljoin(self.base_url, endpoint)
        request_headers = self.session.headers.copy()
        
        # Add custom headers
        if headers:
            request_headers.update(headers)
        
        # Add admin authentication if required
        if require_admin:
            if not self.admin_token:
                raise SentinelAuthError("Admin token required for this operation")
            request_headers['X-Admin-Token'] = self.admin_token
        
        # Add session authentication if available
        if require_auth and self.session_cookies:
            # Session cookies handled by session object
            pass
        elif require_auth and not self.authenticated:
            raise SentinelAuthError("Authentication required for this operation")
        
        # Log request if debug enabled
        if self.debug:
            self.logger.debug(f"{method} {url} - params: {params}, json: {json_data}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                cookies=self.session_cookies
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise SentinelRateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    response
                )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise SentinelAuthError("Authentication failed", response)
            
            if response.status_code == 403:
                raise SentinelAuthError("Insufficient permissions", response)
            
            # Handle other errors
            if not response.ok:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_detail = response.json().get('detail', response.text)
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise SentinelAPIError(error_msg, response)
            
            # Update session cookies if present
            if response.cookies:
                self.session_cookies.update(response.cookies)
            
            return response
            
        except requests.exceptions.Timeout:
            raise SentinelAPIError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise SentinelAPIError(f"Connection error to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise SentinelAPIError(f"Request failed: {str(e)}")
    
    def _get_json(self, *args, **kwargs) -> Dict[str, Any]:
        """Make GET request and return JSON response."""
        response = self._make_request('GET', *args, **kwargs)
        return response.json()
    
    def _post_json(self, *args, **kwargs) -> Dict[str, Any]:
        """Make POST request and return JSON response."""
        response = self._make_request('POST', *args, **kwargs)
        return response.json()
    
    # Authentication Methods
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response data
        """
        response = self._post_json(
            '/api/auth/login',
            json_data={'username': username, 'password': password}
        )
        self.authenticated = True
        self.username = username
        return response
    
    def logout(self) -> Dict[str, Any]:
        """Logout current session.
        
        Returns:
            Logout response data
        """
        response = self._post_json('/api/auth/logout', require_auth=True)
        self.authenticated = False
        self.session_cookies = {}
        return response
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user information.
        
        Returns:
            User information
        """
        return self._get_json('/api/auth/me', require_auth=True)
    
    # Health and Status Methods
    
    def get_health(self) -> Dict[str, Any]:
        """Get basic health status.
        
        Returns:
            Health status information
        """
        return self._get_json('/health')
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed service status.
        
        Returns:
            Detailed status information
        """
        return self._get_json('/api/status')
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics (requires HEALTH_ENDPOINT_ENABLED=1).
        
        Returns:
            Health metrics data
        """
        return self._get_json('/api/metrics/health', require_auth=True)
    
    def get_event_bus_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics (requires METRICS_DEBUG_ENABLED=1).
        
        Returns:
            Event bus metrics data
        """
        return self._get_json('/api/metrics/event_bus', require_auth=True)
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get comprehensive metrics snapshot.
        
        Returns:
            Metrics snapshot data
        """
        return self._get_json('/api/metrics/snapshot', require_auth=True)
    
    # Detection and Alert Methods
    
    def get_alerts(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get alerts with optional pagination.
        
        Args:
            limit: Maximum number of alerts to return
            offset: Number of alerts to skip
            
        Returns:
            Alerts data
        """
        params = {'limit': limit, 'offset': offset}
        return self._get_json('/api/alerts', params=params)
    
    def get_detections(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get detections with optional pagination.
        
        Args:
            limit: Maximum number of detections to return
            offset: Number of detections to skip
            
        Returns:
            Detections data
        """
        params = {'limit': limit, 'offset': offset}
        return self._get_json('/api/detections', params=params)
    
    def get_anomaly_score(self) -> Dict[str, Any]:
        """Get current anomaly score.
        
        Returns:
            Anomaly score data
        """
        return self._get_json('/api/anomaly/score')
    
    # Policy Management Methods
    
    def get_policies(self) -> Dict[str, Any]:
        """Get all policies.
        
        Returns:
            Policies data
        """
        return self._get_json('/api/policies')
    
    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new policy.
        
        Args:
            policy_data: Policy configuration
            
        Returns:
            Created policy data
        """
        return self._post_json('/api/policies', json_data=policy_data)
    
    # Action Control Methods
    
    def pause_service(self) -> Dict[str, Any]:
        """Pause the service.
        
        Returns:
            Pause response
        """
        return self._post_json('/api/actions/pause')
    
    def resume_service(self) -> Dict[str, Any]:
        """Resume the service.
        
        Returns:
            Resume response
        """
        return self._post_json('/api/actions/resume')
    
    # Threat Intelligence Methods
    
    def search_threat_intel(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search threat intelligence database.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Threat intelligence search results
        """
        params = {'q': query, 'limit': limit}
        return self._get_json('/api/ti/search', params=params)
    
    # MITRE ATT&CK Methods
    
    def get_mitre_coverage(self) -> Dict[str, Any]:
        """Get MITRE ATT&CK framework coverage.
        
        Returns:
            MITRE coverage data
        """
        return self._get_json('/api/mitre/coverage')
    
    # Streaming Methods
    
    def get_stream_health(self) -> Dict[str, Any]:
        """Get streaming health status.
        
        Returns:
            Stream health data
        """
        return self._get_json('/api/stream/health')
    
    def stream_events(self, require_auth: bool = False) -> Iterator[Dict[str, Any]]:
        """Stream events via Server-Sent Events.
        
        Args:
            require_auth: Whether authentication is required
            
        Yields:
            Event data dictionaries
            
        Raises:
            ImportError: If sseclient-py not available
        """
        if not SSE_AVAILABLE:
            raise ImportError("sseclient-py required for streaming functionality")
        
        headers = {}
        if require_auth and self.admin_token:
            headers['X-Admin-Token'] = self.admin_token
        
        url = urljoin(self.base_url, '/api/stream')
        client = sseclient.SSEClient(url, headers=headers)
        
        for event in client.events():
            if event.data:
                try:
                    yield json.loads(event.data)
                except json.JSONDecodeError:
                    yield {'raw_data': event.data, 'event_type': event.event}
    
    # Export Methods
    
    def export_telemetry(self, format: str = 'json') -> Dict[str, Any]:
        """Export telemetry data.
        
        Args:
            format: Export format (json, csv, etc.)
            
        Returns:
            Export response
        """
        params = {'format': format}
        return self._get_json('/api/export/telemetry', params=params)
    
    # Admin Methods (require admin authentication)
    
    def get_admin_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema (admin only).
        
        Returns:
            Configuration schema
        """
        return self._get_json('/api/admin/config/schema', require_admin=True)
    
    def reload_config(self, debounce_ms: int = 750) -> Dict[str, Any]:
        """Reload configuration (admin only).
        
        Args:
            debounce_ms: Debounce delay in milliseconds
            
        Returns:
            Reload response
        """
        params = {'debounce_ms': debounce_ms}
        return self._post_json('/api/admin/config/reload', params=params, require_admin=True)
    
    def train_anomaly_model(self) -> Dict[str, Any]:
        """Train anomaly detection model (admin only).
        
        Returns:
            Training response
        """
        return self._post_json('/api/admin/anomaly/train', require_admin=True)
    
    def quarantine_file(self, file_path: str) -> Dict[str, Any]:
        """Quarantine a file (admin only).
        
        Args:
            file_path: Path to file to quarantine
            
        Returns:
            Quarantine response
        """
        return self._post_json(
            '/api/admin/quarantine',
            json_data={'file_path': file_path},
            require_admin=True
        )
    
    def restore_quarantined_file(self, quarantine_id: str) -> Dict[str, Any]:
        """Restore quarantined file (admin only).
        
        Args:
            quarantine_id: Quarantine identifier
            
        Returns:
            Restore response
        """
        return self._post_json(
            '/api/admin/quarantine/restore',
            json_data={'quarantine_id': quarantine_id},
            require_admin=True
        )
    
    def get_plugins(self) -> Dict[str, Any]:
        """Get available plugins (admin only).
        
        Returns:
            Plugins list
        """
        return self._get_json('/api/admin/plugins', require_admin=True)
    
    def execute_plugin(self, plugin_name: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a plugin (admin only).
        
        Args:
            plugin_name: Name of plugin to execute
            args: Plugin arguments
            
        Returns:
            Plugin execution response
        """
        json_data = {'plugin_name': plugin_name}
        if args:
            json_data['args'] = args
        return self._post_json('/api/admin/plugins/execute', json_data=json_data, require_admin=True)
    
    def backup_system(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create system backup (admin only).
        
        Args:
            backup_name: Optional backup name
            
        Returns:
            Backup response
        """
        json_data = {}
        if backup_name:
            json_data['backup_name'] = backup_name
        return self._post_json('/api/admin/backup', json_data=json_data, require_admin=True)
    
    def restore_system(self, backup_id: str) -> Dict[str, Any]:
        """Restore system from backup (admin only).
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Restore response
        """
        return self._post_json(
            '/api/admin/restore',
            json_data={'backup_id': backup_id},
            require_admin=True
        )
    
    def get_preflight_status(self) -> Dict[str, Any]:
        """Get preflight check status (admin only).
        
        Returns:
            Preflight status
        """
        return self._get_json('/api/admin/preflight', require_admin=True)
    
    def preview_secret_rotation(self) -> Dict[str, Any]:
        """Preview secret rotation changes (admin only).
        
        Returns:
            Rotation preview
        """
        return self._post_json('/api/admin/rotate/preview', require_admin=True)
    
    def execute_secret_rotation(self) -> Dict[str, Any]:
        """Execute secret rotation (admin only).
        
        Returns:
            Rotation response
        """
        return self._post_json('/api/admin/rotate/execute', require_admin=True)
    
    def get_chaos_status(self) -> Dict[str, Any]:
        """Get chaos engineering status (admin only).
        
        Returns:
            Chaos status
        """
        return self._get_json('/api/admin/chaos/status', require_admin=True)
    
    def inject_chaos(self, chaos_type: str, duration_seconds: int = 60) -> Dict[str, Any]:
        """Inject chaos for testing (admin only).
        
        Args:
            chaos_type: Type of chaos to inject
            duration_seconds: Duration in seconds
            
        Returns:
            Chaos injection response
        """
        return self._post_json(
            '/api/admin/chaos/inject',
            json_data={'type': chaos_type, 'duration_seconds': duration_seconds},
            require_admin=True
        )
    
    def get_retention_stats(self) -> Dict[str, Any]:
        """Get data retention statistics (admin only).
        
        Returns:
            Retention statistics
        """
        return self._get_json('/api/admin/retention/stats', require_admin=True)
    
    def run_retention_cleanup(self) -> Dict[str, Any]:
        """Run data retention cleanup (admin only).
        
        Returns:
            Cleanup response
        """
        return self._post_json('/api/admin/retention/run', require_admin=True)
    
    def run_quick_performance_probe(self) -> Dict[str, Any]:
        """Run quick performance probe (admin only).
        
        Returns:
            Performance probe results
        """
        return self._get_json('/api/admin/perf/quick', require_admin=True)
    
    def run_detailed_performance_probe(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Run detailed performance probe (admin only).
        
        Args:
            duration_seconds: Probe duration in seconds
            
        Returns:
            Performance probe results
        """
        return self._post_json(
            '/api/admin/perf/probe',
            json_data={'duration_seconds': duration_seconds},
            require_admin=True
        )
    
    # Utility Methods
    
    def ping(self) -> bool:
        """Simple connectivity test.
        
        Returns:
            True if server is reachable
        """
        try:
            response = self._make_request('GET', '/health')
            return response.ok
        except:
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information.
        
        Returns:
            Server information including health, status, and metrics
        """
        info = {}
        
        try:
            info['health'] = self.get_health()
        except Exception as e:
            info['health_error'] = str(e)
        
        try:
            info['status'] = self.get_status()
        except Exception as e:
            info['status_error'] = str(e)
        
        try:
            info['metrics_snapshot'] = self.get_metrics_snapshot()
        except Exception as e:
            info['metrics_error'] = str(e)
        
        return info
    
    def validate_connection(self) -> Dict[str, Any]:
        """Validate connection and available endpoints.
        
        Returns:
            Connection validation results
        """
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'base_url': self.base_url,
            'connectivity': False,
            'authentication': False,
            'admin_access': False,
            'available_endpoints': [],
            'errors': []
        }
        
        # Test basic connectivity
        try:
            health = self.get_health()
            results['connectivity'] = True
            results['available_endpoints'].append('/health')
        except Exception as e:
            results['errors'].append(f"Connectivity test failed: {str(e)}")
        
        # Test authentication if credentials available
        if self.authenticated or (self.username and self.password):
            try:
                self.get_current_user()
                results['authentication'] = True
                results['available_endpoints'].append('/api/auth/me')
            except Exception as e:
                results['errors'].append(f"Authentication test failed: {str(e)}")
        
        # Test admin access if token available
        if self.admin_token:
            try:
                self.get_admin_config_schema()
                results['admin_access'] = True
                results['available_endpoints'].append('/api/admin/config/schema')
            except Exception as e:
                results['errors'].append(f"Admin access test failed: {str(e)}")
        
        return results


# Convenience functions for quick usage

def create_client(**kwargs) -> SentinelClient:
    """Create a new Sentinel client with the given parameters.
    
    Returns:
        Configured SentinelClient instance
    """
    return SentinelClient(**kwargs)


def quick_health_check(base_url: str = "http://localhost:8080") -> Dict[str, Any]:
    """Perform a quick health check.
    
    Args:
        base_url: Sentinel server URL
        
    Returns:
        Health check results
    """
    client = SentinelClient(base_url=base_url)
    return client.get_health()


def quick_status_check(base_url: str = "http://localhost:8080") -> Dict[str, Any]:
    """Perform a quick status check.
    
    Args:
        base_url: Sentinel server URL
        
    Returns:
        Status check results
    """
    client = SentinelClient(base_url=base_url)
    return client.get_server_info()


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sentinel_sdk.py <base_url> [admin_token]")
        print("Example: python sentinel_sdk.py http://localhost:8080")
        sys.exit(1)
    
    base_url = sys.argv[1]
    admin_token = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        client = SentinelClient(base_url=base_url, admin_token=admin_token, debug=True)
        
        print("=== Connection Validation ===")
        validation = client.validate_connection()
        print(json.dumps(validation, indent=2))
        
        print("\n=== Server Information ===")
        server_info = client.get_server_info()
        print(json.dumps(server_info, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
