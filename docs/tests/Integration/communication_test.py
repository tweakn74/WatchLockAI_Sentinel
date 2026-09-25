#!/usr/bin/env python3
'''
WatchLockAI Agent-Console Communication Testing Suite
Tests secure communication between endpoints and management console
'''

import asyncio
import aiohttp
import json
import ssl
import time
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    success: bool
    duration: float
    message: str
    details: Dict[str, Any] = None

class CommunicationTester:
    def __init__(self, console_endpoint: str, agent_id: str = None):
        self.console_endpoint = console_endpoint.rstrip('/')
        self.agent_id = agent_id or f"test-agent-{uuid.uuid4().hex[:8]}"
        self.session: aiohttp.ClientSession = None
        self.results: List[TestResult] = []
    
    async def __aenter__(self):
        # Create SSL context for secure communication
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False  # For testing only
        ssl_context.verify_mode = ssl.CERT_NONE  # For testing only
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers={
                'User-Agent': 'WatchLockAI-Agent-Test/1.0',
                'X-Agent-Id': self.agent_id,
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_console_health(self) -> TestResult:
        '''Test console health endpoint connectivity'''
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.console_endpoint}/api/health") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        test_name="Console Health Check",
                        success=True,
                        duration=duration,
                        message="Console is healthy and responding",
                        details={"status_code": response.status, "response": data}
                    )
                else:
                    return TestResult(
                        test_name="Console Health Check",
                        success=False,
                        duration=duration,
                        message=f"Health check failed with status {response.status}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Console Health Check",
                success=False,
                duration=duration,
                message=f"Health check failed: {str(e)}"
            )
    
    async def test_agent_registration(self) -> TestResult:
        '''Test agent registration with console'''
        start_time = time.time()
        
        registration_data = {
            "agent_id": self.agent_id,
            "hostname": "test-endpoint",
            "os_version": "Windows 11 Pro",
            "agent_version": "1.0.0",
            "capabilities": [
                "threat_detection",
                "behavioral_analysis", 
                "automated_response",
                "forensic_investigation"
            ],
            "timestamp": time.time()
        }
        
        try:
            async with self.session.post(
                f"{self.console_endpoint}/api/agents/register",
                json=registration_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status in [200, 201]:
                    data = await response.json()
                    return TestResult(
                        test_name="Agent Registration",
                        success=True,
                        duration=duration,
                        message="Agent registered successfully",
                        details={"status_code": response.status, "response": data}
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        test_name="Agent Registration",
                        success=False,
                        duration=duration,
                        message=f"Registration failed with status {response.status}: {error_text}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Agent Registration",
                success=False,
                duration=duration,
                message=f"Registration failed: {str(e)}"
            )
    
    async def test_heartbeat_communication(self) -> TestResult:
        '''Test heartbeat communication'''
        start_time = time.time()
        
        heartbeat_data = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "status": "online",
            "system_metrics": {
                "cpu_usage": 15.2,
                "memory_usage": 234.5,
                "disk_usage": 67.3,
                "threat_count": 0,
                "last_scan": time.time() - 300
            }
        }
        
        try:
            async with self.session.post(
                f"{self.console_endpoint}/api/agents/heartbeat",
                json=heartbeat_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        test_name="Heartbeat Communication",
                        success=True,
                        duration=duration,
                        message="Heartbeat sent successfully",
                        details={"status_code": response.status, "response": data}
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        test_name="Heartbeat Communication",
                        success=False,
                        duration=duration,
                        message=f"Heartbeat failed with status {response.status}: {error_text}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Heartbeat Communication",
                success=False,
                duration=duration,
                message=f"Heartbeat failed: {str(e)}"
            )
    
    async def test_threat_reporting(self) -> TestResult:
        '''Test threat event reporting'''
        start_time = time.time()
        
        threat_data = {
            "agent_id": self.agent_id,
            "threat_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "threat_type": "Suspicious PowerShell Execution",
            "severity": "high",
            "mitre_technique": "T1059.001",
            "kill_chain_phase": "Execution",
            "description": "Detected encoded PowerShell command execution",
            "evidence": {
                "process_name": "powershell.exe",
                "command_line": "powershell.exe -EncodedCommand <base64>",
                "user": "SYSTEM",
                "pid": 1234
            },
            "investigation_id": str(uuid.uuid4()),
            "response_actions": [
                {
                    "action": "process_quarantine",
                    "status": "completed",
                    "timestamp": time.time()
                }
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.console_endpoint}/api/threats",
                json=threat_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status in [200, 201]:
                    data = await response.json()
                    return TestResult(
                        test_name="Threat Reporting",
                        success=True,
                        duration=duration,
                        message="Threat reported successfully",
                        details={"status_code": response.status, "response": data}
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        test_name="Threat Reporting",
                        success=False,
                        duration=duration,
                        message=f"Threat reporting failed with status {response.status}: {error_text}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Threat Reporting",
                success=False,
                duration=duration,
                message=f"Threat reporting failed: {str(e)}"
            )
    
    async def test_policy_retrieval(self) -> TestResult:
        '''Test policy configuration retrieval'''
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{self.console_endpoint}/api/policies/{self.agent_id}"
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        test_name="Policy Retrieval",
                        success=True,
                        duration=duration,
                        message="Policy retrieved successfully",
                        details={"status_code": response.status, "response": data}
                    )
                elif response.status == 404:
                    return TestResult(
                        test_name="Policy Retrieval",
                        success=True,
                        duration=duration,
                        message="No policies configured (expected for new agent)"
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        test_name="Policy Retrieval",
                        success=False,
                        duration=duration,
                        message=f"Policy retrieval failed with status {response.status}: {error_text}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Policy Retrieval",
                success=False,
                duration=duration,
                message=f"Policy retrieval failed: {str(e)}"
            )
    
    async def run_all_tests(self) -> List[TestResult]:
        '''Run complete communication test suite'''
        logger.info(f"Starting WatchLockAI communication tests against {self.console_endpoint}")
        logger.info(f"Test Agent ID: {self.agent_id}")
        
        tests = [
            self.test_console_health,
            self.test_agent_registration,
            self.test_heartbeat_communication,
            self.test_threat_reporting,
            self.test_policy_retrieval
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
                
                status = "[PASS] PASS" if result.success else "[FAIL] FAIL"
                logger.info(f"{status} {result.test_name}: {result.message} ({result.duration:.2f}s)")
                
                if result.details:
                    logger.debug(f"Details: {json.dumps(result.details, indent=2)}")
                
                # Brief pause between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                error_result = TestResult(
                    test_name=test.__name__,
                    success=False,
                    duration=0.0,
                    message=f"Test execution failed: {str(e)}"
                )
                results.append(error_result)
                logger.error(f"[FAIL] FAIL {test.__name__}: {str(e)}")
        
        return results
    
    def print_summary(self, results: List[TestResult]):
        '''Print test results summary'''
        passed = sum(1 for r in results if r.success)
        total = len(results)
        
        print("\n" + "="*60)
        print("WatchLockAI Communication Test Summary")
        print("="*60)
        print(f"Console Endpoint: {self.console_endpoint}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n[U+1F389] All communication tests passed! Agent-Console communication is working correctly.")
        else:
            print("\n[WARN]  Some tests failed. Please review the issues above.")
            
            failed_tests = [r for r in results if not r.success]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test.test_name}: {test.message}")
        
        print("="*60)

async def main():
    '''Main test execution'''
    import argparse
    
    parser = argparse.ArgumentParser(description='WatchLockAI Communication Tester')
    parser.add_argument('--console', required=True, help='Console endpoint URL')
    parser.add_argument('--agent-id', help='Agent ID for testing (auto-generated if not provided)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async with CommunicationTester(args.console, args.agent_id) as tester:
        results = await tester.run_all_tests()
        tester.print_summary(results)
        
        # Return exit code based on results
        failed_count = sum(1 for r in results if not r.success)
        return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
