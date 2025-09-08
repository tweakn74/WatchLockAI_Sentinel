"""
MITRE ATT&CK Rule DSL and Engine
Provides rule definition, parsing, and matching capabilities for attack detection.
Import-safe: gracefully degrades if optional dependencies unavailable.
"""

import os
import json
import re
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Safe imports with fallbacks
try:
    import pydantic
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    Field = lambda default=None, **kwargs: default

# Rule severity levels
SeverityLevel = Literal["low", "med", "high", "crit"]

# Event types supported
EventType = Literal[
    "AuthEvent", "ProcessEvent", "FileEvent", "RegistryEvent", 
    "NetworkEvent", "CloudEvent", "MailEvent", "WebEvent", 
    "ApiEvent", "IotEvent", "AppEvent", "UsbEvent", "VoiceMeta", "EDREvent"
]

# Where clause operators
OPERATORS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "in": lambda a, b: a in b if isinstance(b, (list, tuple, set)) else str(a) in str(b),
    "contains": lambda a, b: str(b) in str(a),
    "regex": lambda a, b: bool(re.search(str(b), str(a))),
    ">": lambda a, b: float(a) > float(b),
    "<": lambda a, b: float(a) < float(b),
    ">=": lambda a, b: float(a) >= float(b),
    "<=": lambda a, b: float(a) <= float(b),
}

if PYDANTIC_AVAILABLE:
    class Rule(BaseModel):
        """Pydantic-based rule definition"""
        id: str
        name: str
        tactic: str
        technique: str
        event: EventType
        window_s: int = Field(default=300, ge=1)
        threshold: int = Field(default=5, ge=1)
        group_by: str = Field(default="src_ip")
        key: str = Field(default="src_ip")  # For backward compatibility
        where: Optional[str] = Field(default=None)
        severity: SeverityLevel = Field(default="med")
        response: str = Field(default="")
        stage: str = Field(default="Unknown")
        description: str = Field(default="")
        
        def model_post_init(self, __context: Any) -> None:
            """Ensure key matches group_by for backward compatibility"""
            if not hasattr(self, '_post_init_done'):
                if self.key != self.group_by:
                    self.key = self.group_by
                self._post_init_done = True
else:
    @dataclass
    class Rule:
        """Dataclass fallback when pydantic unavailable"""
        id: str
        name: str
        tactic: str
        technique: str
        event: str
        window_s: int = 300
        threshold: int = 5
        group_by: str = "src_ip"
        key: str = "src_ip"
        where: Optional[str] = None
        severity: str = "med"
        response: str = ""
        stage: str = "Unknown"
        description: str = ""
        
        def __post_init__(self):
            """Ensure key matches group_by for backward compatibility"""
            if self.key != self.group_by:
                self.key = self.group_by

class SlidingWindowCounter:
    """In-memory sliding window counter using OrderedDict for timestamp tracking"""
    
    def __init__(self, window_seconds: int):
        self.window_seconds = window_seconds
        # key -> OrderedDict of timestamps -> count
        self.counters: Dict[str, OrderedDict] = {}
        
    def add_event(self, key: str, timestamp: Optional[datetime] = None) -> int:
        """Add event for key, return current count in window"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        if key not in self.counters:
            self.counters[key] = OrderedDict()
            
        # Clean old entries outside window
        cutoff = timestamp - timedelta(seconds=self.window_seconds)
        counter = self.counters[key]
        
        # Remove old timestamps
        to_remove = []
        for ts in counter:
            if ts < cutoff:
                to_remove.append(ts)
            else:
                break  # OrderedDict maintains insertion order
                
        for ts in to_remove:
            del counter[ts]
            
        # Add current timestamp
        counter[timestamp] = counter.get(timestamp, 0) + 1
        
        # Return current count in window
        return sum(counter.values())
        
    def get_current_count(self, key: str, timestamp: Optional[datetime] = None) -> int:
        """Get current count for key within window"""
        if key not in self.counters:
            return 0
            
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        cutoff = timestamp - timedelta(seconds=self.window_seconds)
        counter = self.counters[key]
        
        # Count entries within window
        count = 0
        for ts, c in counter.items():
            if ts >= cutoff:
                count += c
                
        return count

class WhereClauseEvaluator:
    """Evaluates where clause conditions against event data"""
    
    def __init__(self, where_clause: str):
        self.where_clause = where_clause
        self.parsed_conditions = self._parse_where_clause(where_clause)
        
    def _parse_where_clause(self, clause: str) -> List[Dict[str, Any]]:
        """Parse simple where clause into conditions list"""
        if not clause:
            return []
            
        conditions = []
        # Simple parsing - split by AND (could extend for OR, parentheses)
        parts = [p.strip() for p in clause.split(" AND ")]
        
        for part in parts:
            condition = self._parse_condition(part)
            if condition:
                conditions.append(condition)
                
        return conditions
        
    def _parse_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parse single condition like 'field operator value'"""
        # Find operator
        for op in sorted(OPERATORS.keys(), key=len, reverse=True):
            if f" {op} " in condition:
                field, value = condition.split(f" {op} ", 1)
                field = field.strip()
                value = value.strip().strip("'\"")  # Remove quotes
                
                # Handle list values for 'in' operator
                if op == "in" and value.startswith("[") and value.endswith("]"):
                    try:
                        value = json.loads(value)
                    except:
                        value = value[1:-1].split(",")
                        value = [v.strip().strip("'\"") for v in value]
                        
                return {
                    "field": field,
                    "operator": op,
                    "value": value
                }
                
        logger.warning(f"Could not parse condition: {condition}")
        return None
        
    def evaluate(self, event_data: Dict[str, Any]) -> bool:
        """Evaluate all conditions against event data"""
        if not self.parsed_conditions:
            return True  # No conditions = always match
            
        for condition in self.parsed_conditions:
            if not self._evaluate_condition(condition, event_data):
                return False  # All conditions must pass (AND logic)
                
        return True
        
    def _evaluate_condition(self, condition: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate single condition against event data"""
        try:
            field = condition["field"]
            operator = condition["operator"]
            expected_value = condition["value"]
            
            # Get actual value from event data (support nested fields)
            actual_value = self._get_field_value(event_data, field)
            
            if actual_value is None:
                return False
                
            # Apply operator
            op_func = OPERATORS.get(operator)
            if not op_func:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
            return op_func(actual_value, expected_value)
            
        except Exception as e:
            logger.warning(f"Error evaluating condition {condition}: {e}")
            return False
            
    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get field value from event data, supporting dot notation"""
        try:
            if "." not in field:
                return data.get(field)
                
            # Handle nested fields like "user.name"
            value = data
            for part in field.split("."):
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
                    
            return value
        except:
            return None

class RuleEngine:
    """Core rule engine for processing events against loaded rules"""
    
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.counters = {}  # rule_id -> SlidingWindowCounter
        self.evaluators = {}  # rule_id -> WhereClauseEvaluator
        
        self._initialize_rules()
        
    def _initialize_rules(self):
        """Initialize counters and evaluators for all rules"""
        for rule in self.rules:
            self.counters[rule.id] = SlidingWindowCounter(rule.window_s)
            if rule.where:
                self.evaluators[rule.id] = WhereClauseEvaluator(rule.where)
                
    def process_event(self, event_type: str, event_data: Dict[str, Any], 
                     timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Process event against all applicable rules, return list of matches"""
        matches = []
        
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        for rule in self.rules:
            try:
                # Check if rule applies to this event type
                if rule.event != event_type:
                    continue
                    
                # Apply where clause filter if present
                if rule.id in self.evaluators:
                    if not self.evaluators[rule.id].evaluate(event_data):
                        continue
                        
                # Extract key for grouping
                group_key = self._extract_group_key(rule, event_data)
                if not group_key:
                    continue
                    
                # Update counter and check threshold
                counter = self.counters[rule.id]
                current_count = counter.add_event(group_key, timestamp)
                
                if current_count >= rule.threshold:
                    match_context = {
                        "rule": rule,
                        "count": current_count,
                        "group_key": group_key,
                        "timestamp": timestamp,
                        "event_data": event_data
                    }
                    matches.append(match_context)
                    logger.info(f"Rule {rule.id} triggered: {current_count} events for {group_key}")
                    
            except Exception as e:
                logger.error(f"Error processing rule {rule.id}: {e}")
                continue
                
        return matches
        
    def _extract_group_key(self, rule: Rule, event_data: Dict[str, Any]) -> Optional[str]:
        """Extract grouping key from event data"""
        try:
            key_field = rule.group_by or rule.key
            if "." in key_field:
                # Handle nested fields
                value = event_data
                for part in key_field.split("."):
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        return None
                return str(value) if value is not None else None
            else:
                value = event_data.get(key_field)
                return str(value) if value is not None else None
        except Exception:
            return None

def parse_rules_from_dict(rules_data: List[Dict[str, Any]]) -> List[Rule]:
    """Parse rules from dictionary format"""
    rules = []
    for rule_dict in rules_data:
        try:
            if PYDANTIC_AVAILABLE:
                rule = Rule(**rule_dict)
            else:
                # Ensure all required fields present for dataclass
                required_fields = ['id', 'name', 'tactic', 'technique', 'event']
                if all(field in rule_dict for field in required_fields):
                    rule = Rule(**rule_dict)
                else:
                    logger.warning(f"Skipping rule with missing fields: {rule_dict}")
                    continue
            rules.append(rule)
        except Exception as e:
            logger.error(f"Error parsing rule {rule_dict.get('id', 'unknown')}: {e}")
            continue
    return rules


# ===== RC-3: SEQUENCE SUPPORT =====

class SequenceMatch:
    """Represents a single step match in a sequence"""
    def __init__(self, event_type: str, where_clause: Dict[str, Any], count_operator: str = ">=", count_value: int = 1):
        self.event_type = event_type
        self.where_clause = where_clause  
        self.count_operator = count_operator
        self.count_value = count_value
        
class SequenceRule:
    """Rule definition for sequence-based detection"""
    def __init__(self, rule_id: str, name: str, tactic: str, technique: str, stage: str, sequence: Dict[str, Any], severity: str = "med", response: str = ""):
        self.id = rule_id
        self.name = name
        self.tactic = tactic
        self.technique = technique
        self.stage = stage
        self.severity = severity
        self.response = response
        
        # Parse sequence definition
        self.within_s = sequence.get("within_s", 300)
        self.steps = []
        
        for step_def in sequence.get("steps", []):
            match_def = step_def.get("match", {})
            event_type = match_def.get("event", "")
            where_clause = match_def.get("where", {})
            count_spec = step_def.get("count", ">=1")
            
            # Parse count operator and value
            if isinstance(count_spec, str):
                if count_spec.startswith(">="):
                    count_op, count_val = ">=", int(count_spec[2:])
                elif count_spec.startswith(">"):
                    count_op, count_val = ">", int(count_spec[1:])
                elif count_spec.startswith("=="):
                    count_op, count_val = "==", int(count_spec[2:])
                else:
                    count_op, count_val = ">=", int(count_spec)
            else:
                count_op, count_val = ">=", int(count_spec)
                
            self.steps.append(SequenceMatch(event_type, where_clause, count_op, count_val))

class SequenceEngine:
    """Engine for detecting sequence-based attack patterns"""
    
    def __init__(self, sequence_rules: List[SequenceRule]):
        self.sequence_rules = sequence_rules
        self.sequence_state = {}  # Track ongoing sequences
        self.parameter_bindings = {}  # Track parameter bindings across steps
        
    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process event against sequence rules, return matches"""
        matches = []
        current_time = datetime.utcnow()
        
        for rule in self.sequence_rules:
            match_result = self._check_sequence_rule(rule, event_type, event_data, current_time)
            if match_result:
                matches.append({
                    "rule": rule,
                    "match_context": match_result,
                    "timestamp": current_time
                })
                
        return matches
        
    def _check_sequence_rule(self, rule: SequenceRule, event_type: str, event_data: Dict[str, Any], timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Check if event matches any step in the sequence rule"""
        rule_state_key = f"{rule.id}"
        
        if rule_state_key not in self.sequence_state:
            self.sequence_state[rule_state_key] = {
                "current_step": 0,
                "step_matches": [],
                "bindings": {},
                "start_time": None
            }
            
        state = self.sequence_state[rule_state_key]
        current_step_idx = state["current_step"]
        
        # Check if sequence timed out
        if state["start_time"] and (timestamp - state["start_time"]).total_seconds() > rule.within_s:
            # Reset sequence
            state["current_step"] = 0
            state["step_matches"] = []
            state["bindings"] = {}
            state["start_time"] = None
            current_step_idx = 0
            
        if current_step_idx >= len(rule.steps):
            return None  # Sequence already completed
            
        current_step = rule.steps[current_step_idx]
        
        # Check if event matches current step
        if event_type == current_step.event_type:
            # Evaluate where clause with parameter binding
            if self._evaluate_where_with_bindings(current_step.where_clause, event_data, state["bindings"]):
                # Update parameter bindings
                self._update_bindings(current_step.where_clause, event_data, state["bindings"])
                
                # Record step match
                state["step_matches"].append({
                    "step": current_step_idx,
                    "event_data": event_data,
                    "timestamp": timestamp
                })
                
                if state["start_time"] is None:
                    state["start_time"] = timestamp
                    
                # Check if this completes the current step count requirement
                step_count = len([m for m in state["step_matches"] if m["step"] == current_step_idx])
                
                if self._check_count_condition(step_count, current_step.count_operator, current_step.count_value):
                    # Move to next step
                    state["current_step"] += 1
                    
                    # Check if sequence is complete
                    if state["current_step"] >= len(rule.steps):
                        # Sequence complete!
                        result = {
                            "sequence_id": rule.id,
                            "steps_matched": state["step_matches"],
                            "bindings": state["bindings"],
                            "duration_s": (timestamp - state["start_time"]).total_seconds()
                        }
                        
                        # Reset for next sequence
                        state["current_step"] = 0
                        state["step_matches"] = []
                        state["bindings"] = {}
                        state["start_time"] = None
                        
                        return result
                        
        return None
        
    def _evaluate_where_with_bindings(self, where_clause: Dict[str, Any], event_data: Dict[str, Any], bindings: Dict[str, Any]) -> bool:
        """Evaluate where clause with parameter binding support"""
        for field, expected_value in where_clause.items():
            if isinstance(expected_value, str) and expected_value.startswith("{") and expected_value.endswith("}"):
                # Parameter binding
                param_name = expected_value[1:-1]
                if param_name in bindings:
                    # Check if bound value matches
                    if event_data.get(field) != bindings[param_name]:
                        return False
                else:
                    # First occurrence - any value is acceptable for binding
                    continue
            else:
                # Direct value comparison
                actual_value = event_data.get(field)
                if actual_value != expected_value:
                    return False
                    
        return True
        
    def _update_bindings(self, where_clause: Dict[str, Any], event_data: Dict[str, Any], bindings: Dict[str, Any]):
        """Update parameter bindings from event data"""
        for field, expected_value in where_clause.items():
            if isinstance(expected_value, str) and expected_value.startswith("{") and expected_value.endswith("}"):
                param_name = expected_value[1:-1]
                if param_name not in bindings:
                    bindings[param_name] = event_data.get(field)
                    
    def _check_count_condition(self, actual_count: int, operator: str, expected_count: int) -> bool:
        """Check if count meets the specified condition"""
        if operator == ">=":
            return actual_count >= expected_count
        elif operator == ">":
            return actual_count > expected_count
        elif operator == "==":
            return actual_count == expected_count
        return False


def parse_sequence_rules(rules_data: List[Dict[str, Any]]) -> List[SequenceRule]:
    """Parse sequence rules from rule definitions"""
    sequence_rules = []
    
    for rule_dict in rules_data:
        if "sequence" in rule_dict:
            try:
                rule = SequenceRule(
                    rule_id=rule_dict["id"],
                    name=rule_dict["name"],
                    tactic=rule_dict["tactic"],
                    technique=rule_dict["technique"],
                    stage=rule_dict.get("stage", "Unknown"),
                    sequence=rule_dict["sequence"],
                    severity=rule_dict.get("severity", "med"),
                    response=rule_dict.get("response", "")
                )
                sequence_rules.append(rule)
            except Exception as e:
                logger.error(f"Error parsing sequence rule {rule_dict.get('id', 'unknown')}: {e}")
                
    return sequence_rules