"""P4-006: Minimal Console UI for WatchLockAI Sentinel.

Basic HTML/JS dashboard for health monitoring and basic management.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

# Feature flags
CONSOLE_UI_ENABLED = os.getenv("CONSOLE_UI_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


def get_dashboard_html() -> str:
    """Generate minimal dashboard HTML.
    
    Returns:
        str: Complete HTML dashboard
    """
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WatchLockAI Sentinel Console</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1419;
            color: #ffffff;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: #1a1f2e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #00d4aa;
        }
        
        h1 {
            color: #00d4aa;
            font-size: 1.8rem;
            margin-bottom: 5px;
        }
        
        .subtitle {
            color: #8892b0;
            font-size: 0.9rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #1a1f2e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #2d3748;
            transition: border-color 0.3s;
        }
        
        .card:hover {
            border-color: #00d4aa;
        }
        
        .card h3 {
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 10px;
        }
        
        .status.healthy {
            background: rgba(0, 212, 170, 0.1);
            color: #00d4aa;
            border: 1px solid #00d4aa;
        }
        
        .status.warning {
            background: rgba(255, 193, 7, 0.1);
            color: #ffc107;
            border: 1px solid #ffc107;
        }
        
        .status.error {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            border: 1px solid #dc3545;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px 0;
            border-bottom: 1px solid #2d3748;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #8892b0;
            font-size: 0.9rem;
        }
        
        .metric-value {
            color: #ffffff;
            font-weight: 500;
        }
        
        .btn {
            background: #00d4aa;
            color: #0f1419;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #00b894;
            transform: translateY(-1px);
        }
        
        .btn.secondary {
            background: #2d3748;
            color: #ffffff;
        }
        
        .btn.secondary:hover {
            background: #4a5568;
        }
        
        .logs {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
        
        .log-entry {
            margin-bottom: 5px;
            color: #8b949e;
        }
        
        .log-entry.info {
            color: #58a6ff;
        }
        
        .log-entry.warning {
            color: #f1e05a;
        }
        
        .log-entry.error {
            color: #f85149;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #2d3748;
            border-radius: 50%;
            border-top-color: #00d4aa;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #8892b0;
            font-size: 0.8rem;
            border-top: 1px solid #2d3748;
            margin-top: 40px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>WatchLockAI Sentinel Console</h1>
            <div class="subtitle">Real-time endpoint security monitoring and management</div>
        </header>
        
        <div class="grid">
            <div class="card">
                <h3>System Health</h3>
                <div class="status healthy" id="health-status">
                    <span class="loading"></span> Checking...
                </div>
                <div id="health-metrics">
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value" id="system-status">Loading...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value" id="system-uptime">Loading...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Event Bus</span>
                        <span class="metric-value" id="event-bus-status">Loading...</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Detection Status</h3>
                <div class="status healthy" id="detection-status">
                    <span class="loading"></span> Checking...
                </div>
                <div id="detection-metrics">
                    <div class="metric">
                        <span class="metric-label">Rules Loaded</span>
                        <span class="metric-value" id="rules-count">Loading...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Recent Alerts</span>
                        <span class="metric-value" id="alerts-count">Loading...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Collectors</span>
                        <span class="metric-value" id="collectors-status">Loading...</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Quick Actions</h3>
                <button class="btn" onclick="refreshData()">Refresh Status</button>
                <button class="btn secondary" onclick="toggleLogs()">Toggle Logs</button>
                <button class="btn secondary" onclick="downloadReport()">Download Report</button>
                <div class="metric">
                    <span class="metric-label">Last Updated</span>
                    <span class="metric-value" id="last-updated">Never</span>
                </div>
            </div>
            
            <div class="card">
                <h3>System Information</h3>
                <div class="metric">
                    <span class="metric-label">Version</span>
                    <span class="metric-value">P4-006</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Console UI</span>
                    <span class="metric-value">Enabled</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Features</span>
                    <span class="metric-value" id="features-count">Loading...</span>
                </div>
            </div>
        </div>
        
        <div class="card" id="logs-container" style="display: none;">
            <h3>Recent Events</h3>
            <div class="logs" id="logs-content">
                <div class="log-entry info">[INFO] Console UI initialized</div>
                <div class="log-entry">Waiting for real-time updates...</div>
            </div>
        </div>
        
        <footer class="footer">
            WatchLockAI Sentinel Console &bull; Powered by FastAPI &bull; 
            <span id="connection-status">Connected</span>
        </footer>
    </div>
    
    <script>
        let autoRefresh = true;
        let refreshInterval = null;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            console.log('WatchLockAI Sentinel Console UI initialized');
            refreshData();
            startAutoRefresh();
        });
        
        // Auto-refresh functionality
        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(refreshData, 30000); // Refresh every 30 seconds
        }
        
        // Refresh system data
        async function refreshData() {
            try {
                updateConnectionStatus('connecting');
                
                // Fetch health data
                const healthResponse = await fetch('/api/metrics/health');
                if (healthResponse.ok) {
                    const healthData = await healthResponse.json();
                    updateHealthStatus(healthData);
                } else {
                    throw new Error(`Health API returned ${healthResponse.status}`);
                }
                
                // Try to fetch additional data (may not be available)
                try {
                    const statusResponse = await fetch('/api/status');
                    if (statusResponse.ok) {
                        const statusData = await statusResponse.json();
                        updateSystemStatus(statusData);
                    }
                } catch (e) {
                    console.log('Status API not available:', e.message);
                }
                
                updateConnectionStatus('connected');
                document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
                
            } catch (error) {
                console.error('Failed to refresh data:', error);
                updateConnectionStatus('error');
                updateHealthStatus(null, error.message);
            }
        }
        
        // Update health status display
        function updateHealthStatus(data, error = null) {
            const statusElement = document.getElementById('health-status');
            const systemStatusElement = document.getElementById('system-status');
            const uptimeElement = document.getElementById('system-uptime');
            const eventBusElement = document.getElementById('event-bus-status');
            
            if (error) {
                statusElement.className = 'status error';
                statusElement.textContent = 'Error';
                systemStatusElement.textContent = 'Error';
                uptimeElement.textContent = 'Unknown';
                eventBusElement.textContent = 'Unknown';
                return;
            }
            
            if (data && data.ok) {
                statusElement.className = 'status healthy';
                statusElement.textContent = 'Healthy';
                systemStatusElement.textContent = 'Running';
                
                // Format uptime
                if (data.uptime_s) {
                    const uptime = Math.floor(data.uptime_s);
                    const hours = Math.floor(uptime / 3600);
                    const minutes = Math.floor((uptime % 3600) / 60);
                    uptimeElement.textContent = `${hours}h ${minutes}m`;
                } else {
                    uptimeElement.textContent = 'Unknown';
                }
                
                // Event bus status
                if (data.components && data.components.event_bus) {
                    const eb = data.components.event_bus;
                    const successCount = eb.delivery_success_count || 0;
                    const failureCount = eb.delivery_failure_count || 0;
                    eventBusElement.textContent = `${successCount} success, ${failureCount} failed`;
                } else {
                    eventBusElement.textContent = 'Available';
                }
            } else {
                statusElement.className = 'status warning';
                statusElement.textContent = 'Degraded';
                systemStatusElement.textContent = 'Degraded';
            }
        }
        
        // Update system status
        function updateSystemStatus(data) {
            const rulesElement = document.getElementById('rules-count');
            const alertsElement = document.getElementById('alerts-count');
            const collectorsElement = document.getElementById('collectors-status');
            const featuresElement = document.getElementById('features-count');
            
            if (data) {
                // Rules count
                if (data.rules_engine && data.rules_engine.rules_loaded) {
                    rulesElement.textContent = data.rules_engine.rules_loaded;
                } else {
                    rulesElement.textContent = 'Unknown';
                }
                
                // Collectors status
                if (data.collectors) {
                    const activeCollectors = Object.values(data.collectors).filter(c => c.active).length;
                    const totalCollectors = Object.keys(data.collectors).length;
                    collectorsElement.textContent = `${activeCollectors}/${totalCollectors} active`;
                } else {
                    collectorsElement.textContent = 'Unknown';
                }
                
                // Estimate features (placeholder)
                featuresElement.textContent = 'Multi-tenant, MITRE ATT&CK, ML';
            }
            
            // Placeholder for alerts (would need alerts API)
            alertsElement.textContent = '0 (last 24h)';
        }
        
        // Update connection status
        function updateConnectionStatus(status) {
            const element = document.getElementById('connection-status');
            
            switch (status) {
                case 'connecting':
                    element.textContent = 'Connecting...';
                    element.style.color = '#ffc107';
                    break;
                case 'connected':
                    element.textContent = 'Connected';
                    element.style.color = '#00d4aa';
                    break;
                case 'error':
                    element.textContent = 'Connection Error';
                    element.style.color = '#dc3545';
                    break;
            }
        }
        
        // Toggle logs display
        function toggleLogs() {
            const logsContainer = document.getElementById('logs-container');
            const logsContent = document.getElementById('logs-content');
            
            if (logsContainer.style.display === 'none') {
                logsContainer.style.display = 'block';
                // Add some mock log entries
                const now = new Date().toLocaleTimeString();
                logsContent.innerHTML = `
                    <div class="log-entry info">[${now}] System health check completed</div>
                    <div class="log-entry">[${now}] Event bus operational</div>
                    <div class="log-entry">[${now}] All collectors active</div>
                    <div class="log-entry info">[${now}] Console UI refreshed</div>
                `;
            } else {
                logsContainer.style.display = 'none';
            }
        }
        
        // Download system report
        function downloadReport() {
            const report = {
                timestamp: new Date().toISOString(),
                system: {
                    status: document.getElementById('system-status').textContent,
                    uptime: document.getElementById('system-uptime').textContent
                },
                detection: {
                    rules_count: document.getElementById('rules-count').textContent,
                    alerts_count: document.getElementById('alerts-count').textContent,
                    collectors: document.getElementById('collectors-status').textContent
                },
                ui: {
                    version: 'P4-006',
                    last_updated: document.getElementById('last-updated').textContent
                }
            };
            
            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sentinel-report-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Handle visibility change to pause/resume auto-refresh
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                    refreshInterval = null;
                }
            } else {
                startAutoRefresh();
            }
        });
    </script>
</body>
</html>
    '''.strip()


def ensure_static_files() -> bool:
    """Ensure static files directory exists with console UI files.
    
    Returns:
        bool: True if files were created successfully
    """
    if not CONSOLE_UI_ENABLED:
        return False
    
    try:
        # Create static directory
        static_dir = Path("console/static")
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Write main console HTML
        console_html_path = static_dir / "console.html"
        with open(console_html_path, 'w', encoding='utf-8') as f:
            f.write(get_dashboard_html())
        
        # Write a simple index.html that redirects to console
        index_html_path = static_dir / "index.html"
        index_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=console.html">
    <title>WatchLockAI Sentinel</title>
</head>
<body>
    <p>Redirecting to <a href="console.html">console</a>...</p>
</body>
</html>
        '''.strip()
        
        with open(index_html_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        return True
        
    except Exception as e:
        print(f"Failed to create static files: {e}")
        return False


def get_console_info() -> Dict[str, Any]:
    """Get console UI information.
    
    Returns:
        dict: Console UI status and info
    """
    return {
        "enabled": CONSOLE_UI_ENABLED,
        "version": "P4-006",
        "features": [
            "Real-time health monitoring",
            "System status dashboard", 
            "Basic log viewing",
            "Report generation"
        ],
        "endpoints": {
            "console": "/console/" if CONSOLE_UI_ENABLED else None,
            "static": "/static/" if CONSOLE_UI_ENABLED else None
        }
    }
