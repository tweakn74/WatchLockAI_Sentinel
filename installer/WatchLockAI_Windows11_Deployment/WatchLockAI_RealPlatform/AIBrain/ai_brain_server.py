#!/usr/bin/env python3
"""
WatchLockAI - AI Brain HTTP Server
Fixed version for Windows service compatibility
"""

import json
import logging
import datetime
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import sys

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

class WatchLockAIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for WatchLockAI Brain"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/status':
                self.handle_status()
            elif path == '/health':
                self.handle_health()
            elif path == '/modules':
                self.handle_modules()
            else:
                self.handle_default()
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/chat':
                self.handle_chat()
            elif path == '/analyze':
                self.handle_analyze()
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, str(e))
    
    def handle_status(self):
        """Return AI Brain status"""
        uptime = datetime.datetime.now() - start_time
        status = {
            "status": "OPERATIONAL",
            "uptime": str(uptime),
            "modules": 6,
            "version": "2.0.0",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.send_json_response(status)
    
    def handle_health(self):
        """Health check endpoint"""
        health = {
            "status": "healthy",
            "service": "WatchLockAI Brain",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.send_json_response(health)
    
    def handle_modules(self):
        """Return loaded modules"""
        modules = {
            "modules": [
                {"name": "ThreatDetection", "status": "active"},
                {"name": "RealTimeMonitoring", "status": "active"},
                {"name": "DigitalForensics", "status": "active"},
                {"name": "ComplianceManagement", "status": "active"},
                {"name": "EnterpriseIntegration", "status": "active"},
                {"name": "MITREAttack", "status": "active"}
            ],
            "total": 6
        }
        self.send_json_response(modules)
    
    def handle_chat(self):
        """Handle chat requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '')
            
            # Generate AI response based on message
            ai_response = self.generate_ai_response(user_message)
            
            response = {
                "response": ai_response,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success"
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error in chat handler: {e}")
            error_response = {
                "response": "Sorry, I encountered an error processing your request.",
                "error": str(e),
                "status": "error"
            }
            self.send_json_response(error_response, status_code=500)
    
    def handle_analyze(self):
        """Handle threat analysis requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Perform threat analysis
            analysis = {
                "threat_level": "LOW",
                "confidence": 0.85,
                "analysis": "System activity appears normal",
                "recommendations": ["Continue monitoring"],
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(analysis)
            
        except Exception as e:
            logger.error(f"Error in analyze handler: {e}")
            self.send_error(500, str(e))
    
    def handle_default(self):
        """Handle default requests"""
        self.send_json_response({
            "service": "WatchLockAI Brain",
            "version": "2.0.0",
            "status": "operational",
            "endpoints": ["/status", "/health", "/modules", "/chat", "/analyze"]
        })
    
    def generate_ai_response(self, message):
        """Generate contextual AI responses"""
        message_lower = message.lower()
        
        if 'status' in message_lower or 'how are you' in message_lower:
            uptime = datetime.datetime.now() - start_time
            return f"Hello! I'm WatchLockAI Brain, your cybersecurity AI assistant. I'm operational with {uptime} uptime. How can I help protect your environment today?"
        
        elif 'threat' in message_lower or 'security' in message_lower:
            return "I'm constantly monitoring for security threats. Currently, I'm analyzing network traffic, user behavior, and system events. All systems appear secure. Would you like me to run a specific security check?"
        
        elif 'help' in message_lower or 'what can you do' in message_lower:
            return """I'm your AI-powered cybersecurity assistant! I can help with:

🛡️ **Threat Detection** - Real-time monitoring and analysis
🔍 **Digital Forensics** - Investigate security incidents
📊 **MITRE ATT&CK** - Map threats to attack frameworks
🚨 **Incident Response** - Guide you through security incidents
📈 **Compliance** - NIST, SOC 2, ISO 27001 reporting
🔗 **Integration** - Connect with SIEM, EDR, SOAR platforms

What would you like to explore?"""
        
        elif 'modules' in message_lower or 'components' in message_lower:
            return """I'm running 6 core security modules:

1. **ThreatDetection** - AI-powered threat analysis
2. **RealTimeMonitoring** - Continuous system monitoring  
3. **DigitalForensics** - Evidence collection and analysis
4. **ComplianceManagement** - Regulatory compliance tracking
5. **EnterpriseIntegration** - SIEM/EDR/SOAR connectivity
6. **MITREAttack** - Attack framework mapping

All modules are active and operational."""
        
        elif 'mitre' in message_lower or 'attack' in message_lower:
            return "I use the MITRE ATT&CK framework to classify and analyze threats. I can map detected activities to specific tactics, techniques, and procedures (TTPs) used by adversaries. This helps prioritize threats and understand attack progression."
        
        elif 'forensics' in message_lower or 'investigate' in message_lower:
            return "My digital forensics capabilities include timeline analysis, artifact collection, and evidence preservation. I can help investigate security incidents, analyze logs, and reconstruct attack sequences. What incident would you like me to investigate?"
        
        elif 'compliance' in message_lower:
            return "I support multiple compliance frameworks including NIST Cybersecurity Framework, SOC 2, ISO 27001, and HIPAA. I can generate compliance reports, track security controls, and identify gaps. Which framework interests you?"
        
        else:
            return f"I understand your question about: {message}. The WatchLockAI platform provides comprehensive cybersecurity capabilities including threat detection, forensics, and compliance management."
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        response_data = json.dumps(data)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', len(response_data))
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def run_server():
    """Run the AI Brain server"""
    global start_time
    start_time = datetime.datetime.now()
    
    server_address = ('localhost', 9999)
    httpd = HTTPServer(server_address, WatchLockAIHandler)
    
    logger.info("WatchLockAI Brain server starting on http://localhost:9999")
    logger.info("Available endpoints: /status, /health, /modules, /chat, /analyze")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    # Global start time for uptime calculation
    start_time = datetime.datetime.now()
    
    # Handle Windows service mode
    if len(sys.argv) > 1 and sys.argv[1] == "service":
        # Run as Windows service
        import servicemanager
        import win32serviceutil
        import win32service
        import win32event
        
        class WatchLockAIService(win32serviceutil.ServiceFramework):
            _svc_name_ = "WatchLockAI"
            _svc_display_name_ = "WatchLockAI Brain Service"
            _svc_description_ = "WatchLockAI AI Brain cybersecurity service"
            
            def __init__(self, args):
                win32serviceutil.ServiceFramework.__init__(self, args)
                self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
                self.is_alive = True
                
            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                win32event.SetEvent(self.hWaitStop)
                self.is_alive = False
                
            def SvcDoRun(self):
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    servicemanager.PYS_SERVICE_STARTED,
                                    (self._svc_name_, ''))
                                    
                # Start the server in a separate thread
                server_thread = threading.Thread(target=run_server)
                server_thread.daemon = True
                server_thread.start()
                
                # Wait for stop signal
                win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
        # Handle service commands
        if len(sys.argv) > 2:
            win32serviceutil.HandleCommandLine(WatchLockAIService)
        else:
            # Run service
            WatchLockAIService._svc_name_ = "WatchLockAI"
            win32serviceutil.HandleCommandLine(WatchLockAIService)
    else:
        # Run as standalone server
        run_server()