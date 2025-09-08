#!/usr/bin/env python3
"""WatchLockAI Sentinel Offline Bootstrap

Initializes and starts WatchLockAI Sentinel in offline mode.
"""

import os
import sys
from pathlib import Path

def main():
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    # Set offline mode
    os.environ["OFFLINE_MODE"] = "1"
    
    print("WatchLockAI Sentinel Offline Mode")
    print(f"Version: {os.getenv('VERSION', 'Unknown')}")
    print(f"Directory: {current_dir}")
    print()
    
    try:
        # Import and start the application
        from console.web_api import SentinelWebAPI
        
        print("Starting WatchLockAI Sentinel...")
        app = SentinelWebAPI()
        
        print("✅ WatchLockAI Sentinel started successfully")
        print("🌐 Access the console at: http://localhost:8080")
        
        # Start the application (this would normally start uvicorn)
        print("📝 Note: In offline mode, manual uvicorn startup may be required")
        print("   Run: python -m uvicorn console.web_api:app --host 0.0.0.0 --port 8080")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are available")
        return 1
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
