#!/usr/bin/env python3
"""
MITRE ATT&CK Minimal Playbooks
Safe, mode-aware automated response triggers.
"""

import os
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class Playbooks:
    """Minimal playbook responder for MITRE ATT&CK rules"""
    
    def __init__(self, bus, mode_provider: Callable[[], str]):
        self.bus = bus
        self.mode_provider = mode_provider
    
    async def trigger(self, rule, ctx: Dict[str, Any]) -> None:
        """Trigger playbook response for matched rule
        
        Args:
            rule: The matched detection rule
            ctx: Alert context with trigger data
        """
        try:
            # Always publish an AlertEvent first
            alert_event = {
                "rule_id": rule.id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "context": ctx,
                "playbook_triggered": True
            }
            
            if self.bus:
                self.bus.publish("AlertEvent", alert_event)
                logger.info(f"Published AlertEvent for rule {rule.id}")
            
            # Check operational mode for reactive responses
            current_mode = self.mode_provider()
            logger.info(f"Current operational mode: {current_mode}")
            
            # Only execute reactive responses in contain/quarantine modes
            if current_mode not in ("contain", "quarantine"):
                logger.info(f"Mode {current_mode} - skipping reactive response")
                return
            
            # Execute response based on rule.response
            if not rule.response:
                logger.info(f"No response defined for rule {rule.id}")
                return
            
            await self._execute_response(rule.response, rule, ctx)
            
        except Exception as e:
            logger.error(f"Error in playbook trigger for rule {rule.id}: {e}")
            # Never raise - playbooks must be resilient
    
    async def _execute_response(self, response: str, rule, ctx: Dict[str, Any]) -> None:
        """Execute specific response action"""
        
        try:
            trigger_data = ctx.get("trigger_data", {})
            
            if response == "disable_account":
                username = trigger_data.get("username")
                if username:
                    action_request = {
                        "action": "disable_account",
                        "target_user": username,
                        "rule_id": rule.id,
                        "severity": rule.severity,
                        "reason": f"Triggered by MITRE rule: {rule.name}"
                    }
                    
                    if self.bus:
                        self.bus.publish("ActionRequestEvent", action_request)
                        logger.warning(f"Account disable requested for user: {username}")
                    
                else:
                    logger.warning(f"disable_account response triggered but no username in context")
            
            elif response == "isolate_host":
                host_ip = trigger_data.get("src_ip") or trigger_data.get("host_ip")
                if host_ip:
                    action_request = {
                        "action": "isolate_host", 
                        "target_host": host_ip,
                        "isolate": 1,
                        "rule_id": rule.id,
                        "severity": rule.severity,
                        "reason": f"Triggered by MITRE rule: {rule.name}"
                    }
                    
                    if self.bus:
                        self.bus.publish("ActionRequestEvent", action_request)
                        logger.warning(f"Host isolation requested for: {host_ip}")
                        
                else:
                    logger.warning(f"isolate_host response triggered but no host_ip in context")
            
            elif response == "kill_process":
                pid = trigger_data.get("pid") or trigger_data.get("process_id")
                process_name = trigger_data.get("process_name")
                
                if pid or process_name:
                    action_request = {
                        "action": "kill_process",
                        "pid": pid,
                        "process_name": process_name,
                        "rule_id": rule.id,
                        "severity": rule.severity,
                        "reason": f"Triggered by MITRE rule: {rule.name}"
                    }
                    
                    if self.bus:
                        self.bus.publish("ActionRequestEvent", action_request)
                        logger.warning(f"Process kill requested - PID: {pid}, Name: {process_name}")
                        
                else:
                    logger.warning(f"kill_process response triggered but no pid/process_name in context")
            
            else:
                logger.warning(f"Unknown response type: {response}")
                
        except Exception as e:
            logger.error(f"Error executing response '{response}': {e}")
            # Log but don't raise - playbooks must be resilient
