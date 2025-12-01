# component_id: forensic_trace_generator
# kind: code
# area: examples
# status: candidate
# authority_level: 3
# license: Apache-2.0
# purpose: Generates high-fidelity simulated production logs with infrastructure noise and entropy for forensic validation.

"""
Realistic Production Log Data Generator (Revised)

Improvements:
1. Timestamps: Added microsecond-level random jitter
2. Eliminated fixed values: Added variation to completion_tokens, token_cost, etc.
3. Expanded numeric distribution: Realistic ranges for confidence_score, risk_val
4. Introduced errors/exceptions: Probabilistic timeouts, retries, warnings
5. Scenario branching: Success path, multiple retries, partial failures
6. span_id consistency: Same span_id for request/response pairs
7. Added debug/warning logs
8. Realistic latency jitter
"""

import json
import uuid
import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# =============================================================================
# Configuration
# =============================================================================

class Config:
    # Error occurrence probabilities
    PROB_TIMEOUT = 0.05          # 5% timeout
    PROB_RETRY_NEEDED = 0.15     # 15% additional retry needed
    PROB_PARTIAL_FAILURE = 0.08  # 8% partial failure
    PROB_WARNING_LOG = 0.20      # 20% warning log output
    PROB_DEBUG_LOG = 0.30        # 30% debug log output
    PROB_GC_SPIKE = 0.10         # 10% GC spike (latency increase)
    PROB_NO_VIOLATION = 0.25     # 25% no violation (normal path)
    
    # Environment settings
    ENVIRONMENTS = ["prod-us-east-1", "prod-us-west-2", "prod-eu-west-1"]
    AGENT_VERSIONS = ["v2.1.4-stable", "v2.1.5-stable", "v2.2.0-rc1"]


# =============================================================================
# Utility Functions
# =============================================================================

def generate_random_hex(length: int = 16) -> str:
    """Generate completely random HEX string"""
    return uuid.uuid4().hex[:length]

def generate_trace_id() -> str:
    """Generate 32-char UUIDv4 (no hyphens)"""
    return uuid.uuid4().hex

def calc_hash(content: Any) -> str:
    """Calculate actual SHA-256 hash"""
    salt = uuid.uuid4().hex
    if isinstance(content, dict):
        content_str = json.dumps(content, sort_keys=True)
    else:
        content_str = str(content)
    return hashlib.sha256((content_str + salt).encode()).hexdigest()

def calc_md5(content: Any) -> str:
    """Calculate MD5 hash (for short digests)"""
    salt = uuid.uuid4().hex
    if isinstance(content, dict):
        content_str = json.dumps(content, sort_keys=True)
    else:
        content_str = str(content)
    return hashlib.md5((content_str + salt).encode()).hexdigest()

def get_time_with_jitter(base_time: datetime, offset_ms: float, jitter_range_us: int = 500) -> str:
    """
    Generate timestamp with microsecond-level jitter
    
    Args:
        base_time: Base timestamp
        offset_ms: Offset in milliseconds
        jitter_range_us: Jitter range in microseconds (±)
    """
    # Add jitter in microseconds
    jitter_us = random.randint(-jitter_range_us, jitter_range_us)
    total_us = int(offset_ms * 1000) + jitter_us
    
    t = base_time + timedelta(microseconds=total_us)
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"

def add_gc_spike(base_latency: float) -> float:
    """Simulate latency increase due to GC spike"""
    if random.random() < Config.PROB_GC_SPIKE:
        return base_latency + random.uniform(50, 200)  # Add 50-200ms
    return base_latency

def generate_realistic_latency(base: float, variance_pct: float = 0.15) -> float:
    """Generate realistic latency distribution (normal distribution based)"""
    import math
    # Log-normal-like distribution (closer to actual latency)
    mean = base
    std = base * variance_pct
    latency = random.gauss(mean, std)
    return max(1.0, latency)  # Minimum 1ms


# =============================================================================
# Log Event Generator Class
# =============================================================================

class RealisticLogGenerator:
    def __init__(self):
        self.trace_id = generate_trace_id()
        self.session_id = str(uuid.uuid4())
        self.base_time = datetime(2025, 11, 30, 10, 0, 1, random.randint(100000, 300000))
        self.events: List[Dict[str, Any]] = []
        self.current_offset_ms = 0.0
        self.env = random.choice(Config.ENVIRONMENTS)
        self.agent_version = random.choice(Config.AGENT_VERSIONS)
        
        # Scenario flags
        self.has_violation = random.random() > Config.PROB_NO_VIOLATION
        self.retry_count = 0
        if self.has_violation:
            self.retry_count = 1
            if random.random() < Config.PROB_RETRY_NEEDED:
                self.retry_count = random.randint(2, 3)
    
    def _add_event(self, span_id: str, component: str, event_type: str, 
                   phase: str, payload: Dict[str, Any], 
                   latency_ms: Optional[float] = None) -> str:
        """Add event and return span_id"""
        if latency_ms is not None:
            self.current_offset_ms += latency_ms
        
        event = {
            "timestamp": get_time_with_jitter(self.base_time, self.current_offset_ms),
            "trace_id": self.trace_id,
            "span_id": span_id,
            "component": component,
            "event_type": event_type,
            "phase": phase,
            "payload": payload
        }
        self.events.append(event)
        return span_id
    
    def _maybe_add_debug_log(self, context: str):
        """Probabilistically add debug log"""
        if random.random() < Config.PROB_DEBUG_LOG:
            self._add_event(
                span_id=generate_random_hex(),
                component="debug",
                event_type="trace",
                phase="internal",
                payload={
                    "level": "DEBUG",
                    "msg": f"Checkpoint: {context}",
                    "mem_usage_mb": random.randint(512, 2048),
                    "goroutines": random.randint(50, 200)
                },
                latency_ms=random.uniform(0.1, 0.5)
            )
    
    def _maybe_add_warning_log(self, context: str):
        """Probabilistically add warning log"""
        if random.random() < Config.PROB_WARNING_LOG:
            warnings = [
                ("HIGH_LATENCY", f"Latency exceeded threshold in {context}"),
                ("MEMORY_PRESSURE", "Memory usage approaching limit"),
                ("CONNECTION_POOL", "Connection pool utilization > 80%"),
                ("RATE_LIMIT_WARN", "Approaching rate limit threshold"),
            ]
            warn_code, warn_msg = random.choice(warnings)
            self._add_event(
                span_id=generate_random_hex(),
                component="monitor",
                event_type="warning",
                phase="internal",
                payload={
                    "level": "WARN",
                    "code": warn_code,
                    "msg": warn_msg,
                    "threshold_pct": random.randint(75, 95)
                },
                latency_ms=random.uniform(0.1, 0.3)
            )
    
    def generate_session_init(self):
        """1. Session initialization"""
        self._add_event(
            span_id=generate_random_hex(),
            component="system",
            event_type="session_init",
            phase="init",
            payload={
                "session_id": self.session_id,
                "env": self.env,
                "agent_version": self.agent_version,
                "system_fingerprint": "fp_" + generate_random_hex(6),
                "request_id": "req_" + generate_random_hex(8),
                "client_ip_hash": calc_md5(f"192.168.{random.randint(1,255)}.{random.randint(1,255)}")[:16]
            }
        )
        self._maybe_add_debug_log("session_init")
    
    def generate_user_interaction(self, user_content: str):
        """2. User input"""
        latency = generate_realistic_latency(40, 0.2)
        self._add_event(
            span_id=generate_random_hex(),
            component="user",
            event_type="interaction",
            phase="input",
            payload={
                "content_hash": calc_hash(user_content),
                "content_len_bytes": len(user_content.encode('utf-8')),
                "content_preview": user_content[:20] + "...",
                "input_type": "text",
                "locale": "en-US"
            },
            latency_ms=latency
        )
    
    def generate_constraint_extraction(self, constraints: List[Dict]):
        """3. Constraint extraction"""
        base_latency = generate_realistic_latency(230, 0.15)
        base_latency = add_gc_spike(base_latency)
        
        # confidence_score distributed across wide range
        confidence = round(random.uniform(0.82, 0.99), 4)
        
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="constraint_extraction",
            phase="monitoring",
            payload={
                "constraints": constraints,
                "extracted_hash": calc_hash(constraints),
                "model_latency_ms": round(base_latency, 1),
                "confidence_score": confidence,
                "extraction_method": "llm_v2" if confidence > 0.9 else "hybrid"
            },
            latency_ms=base_latency
        )
        self._maybe_add_debug_log("constraint_extraction")
    
    def generate_agent_thought(self, phase: str = "processing", content: str = ""):
        """4. Agent thought"""
        base_latency = generate_realistic_latency(1400, 0.25)
        base_latency = add_gc_spike(base_latency)
        
        # Add variation to completion_tokens
        completion_tokens = random.randint(28, 67)
        
        self._add_event(
            span_id=generate_random_hex(),
            component="agent",
            event_type="thought",
            phase=phase,
            payload={
                "model": "gpt-4o-2024-08-06",
                "completion_tokens": completion_tokens,
                "prompt_tokens": random.randint(1200, 1800),
                "content_snippet": content or "User prioritizes 'cheap'... considering constraint relaxation...",
                "thinking_time_ms": round(base_latency * 0.8, 1)
            },
            latency_ms=base_latency
        )
    
    def generate_risk_assessment(self):
        """5. Risk assessment"""
        # risk_val distributed across wide range
        risk_val = round(random.uniform(0.15, 0.75), 4)
        
        flags = []
        if risk_val > 0.4:
            flags.append("potential_relaxation")
        if risk_val > 0.6:
            flags.append("high_risk_strategy")
        if random.random() < 0.3:
            flags.append("uncertainty_detected")
        
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="risk_assessment",
            phase="monitoring",
            payload={
                "risk_val": risk_val,
                "detectors": ["semantic_drift_v2", "strategy_monitor", "constraint_checker"],
                "flags": flags if flags else ["nominal"],
                "model_version": "risk_model_v3.2"
            },
            latency_ms=generate_realistic_latency(5, 0.3)
        )
        self._maybe_add_warning_log("risk_assessment")
    
    def generate_tool_call_attempt(self, tool_args: Dict, include_parking: bool = False) -> str:
        """6. Tool call attempt"""
        call_id = "call_" + generate_random_hex(10)
        
        args = tool_args.copy()
        if include_parking:
            args["amenities"] = ["wifi", "parking"]
        
        self._add_event(
            span_id=generate_random_hex(),
            component="agent",
            event_type="tool_call_attempt",
            phase="execution",
            payload={
                "tool": "hotel_aggregator_v3",
                "call_id": call_id,
                "args_hash": calc_hash(args),
                "args_preview": args,
                "retry_attempt": 0 if include_parking else None
            },
            latency_ms=generate_realistic_latency(190, 0.2)
        )
        return call_id
    
    def generate_drift_check(self, has_violation: bool):
        """7. Drift check"""
        status = "VIOLATION" if has_violation else "PASS"
        
        payload = {
            "status": status,
            "policy_id": "pol_" + generate_random_hex(6),
            "eval_latency_ms": round(random.uniform(10.0, 18.0), 1),
            "checks_performed": random.randint(3, 7)
        }
        
        if has_violation:
            payload["violation_type"] = "hard_constraint"
            payload["severity"] = "HIGH"
        
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="drift_check",
            phase="drift",
            payload=payload,
            latency_ms=generate_realistic_latency(14, 0.2)
        )
    
    def generate_execution_blocked(self, param: str):
        """8. Execution blocked"""
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="execution_blocked",
            phase="repair",
            payload={
                "block_id": "blk_" + generate_random_hex(6),
                "reason_code": "MISSING_MANDATORY_PARAM",
                "param": param,
                "suggestion": f"Include '{param}' in amenities filter"
            },
            latency_ms=generate_realistic_latency(1.5, 0.3)
        )
    
    def generate_system_injection(self):
        """9. System injection"""
        # Add variation to token_cost
        token_cost = random.randint(38, 55)
        
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="system_injection",
            phase="repair",
            payload={
                "injection_type": "feedback_frame",
                "token_cost": token_cost,
                "template_id": "tmpl_constraint_reminder_v2",
                "priority": "high"
            },
            latency_ms=generate_realistic_latency(14, 0.2)
        )
    
    def generate_recovery_thought(self):
        """10. Recovery thought"""
        self.generate_agent_thought(
            phase="recovery",
            content="Block detected. Re-applying constraints. Adding parking condition and retrying."
        )
    
    def generate_tool_retry(self) -> str:
        """11. Tool retry"""
        call_id = "call_" + generate_random_hex(10)
        
        self._add_event(
            span_id=generate_random_hex(),
            component="agent",
            event_type="tool_call_retry",
            phase="execution",
            payload={
                "tool": "hotel_aggregator_v3",
                "call_id": call_id,
                "retry_count": 1,
                "corrected_params": ["amenities"]
            },
            latency_ms=generate_realistic_latency(250, 0.2)
        )
        return call_id
    
    def generate_execution_allowed(self):
        """12. Execution allowed"""
        self._add_event(
            span_id=generate_random_hex(),
            component="pld_runtime",
            event_type="execution_allowed",
            phase="reentry",
            payload={
                "audit_id": "aud_" + generate_random_hex(6),
                "approval_type": "auto",
                "policy_version": "v2.3.1"
            },
            latency_ms=generate_realistic_latency(16, 0.2)
        )
    
    def generate_outbound_request_response(self, simulate_timeout: bool = False):
        """13-14. Outbound request/response (same span_id)"""
        span_id = generate_random_hex()  # Same for request and response
        
        # Request
        self._add_event(
            span_id=span_id,
            component="infra_adapter",
            event_type="outbound_request",
            phase="external",
            payload={
                "host": "gw-internal-api.prod.svc.cluster.local",
                "path": "/v3/integration/hotels/search",
                "method": "POST",
                "timeout_ms": 5000,
                "connection_id": "conn_" + generate_random_hex(8)
            },
            latency_ms=generate_realistic_latency(7, 0.3)
        )
        
        if simulate_timeout:
            # Timeout case
            self._add_event(
                span_id=span_id,
                component="infra_adapter",
                event_type="outbound_timeout",
                phase="external",
                payload={
                    "status_code": 504,
                    "error": "GATEWAY_TIMEOUT",
                    "elapsed_ms": 5001,
                    "retry_scheduled": True
                },
                latency_ms=5001
            )
            return False
        
        # Normal response
        latency = generate_realistic_latency(820, 0.15)
        latency = add_gc_spike(latency)
        
        content_len = random.randint(3800, 4500)
        
        self._add_event(
            span_id=span_id,
            component="infra_adapter",
            event_type="outbound_response",
            phase="external",
            payload={
                "status_code": 200,
                "latency_ms": round(latency, 1),
                "content_len": content_len,
                "headers_digest": generate_random_hex(12),
                "cache_hit": random.random() < 0.2  # 20% cache hit
            },
            latency_ms=latency
        )
        
        self._maybe_add_warning_log("outbound_response")
        return True
    
    def generate_tool_result(self, partial_failure: bool = False):
        """15. Tool result"""
        # Add variation to item_count
        item_count = random.randint(0, 8)
        
        payload = {
            "item_count": item_count,
            "data_hash": calc_md5(f"results_{uuid.uuid4()}")
        }
        
        if partial_failure:
            payload["warnings"] = ["some_providers_unavailable"]
            payload["failed_sources"] = random.randint(1, 2)
            payload["total_sources"] = random.randint(4, 6)
        
        if item_count == 0:
            payload["empty_reason"] = "no_matches_found"
        
        self._add_event(
            span_id=generate_random_hex(),
            component="tool",
            event_type="tool_result",
            phase="outcome",
            payload=payload,
            latency_ms=generate_realistic_latency(11, 0.25)
        )
    
    def generate(self, user_content: str) -> List[Dict[str, Any]]:
        """Generate complete log sequence"""
        
        constraints = [
            {"key": "location", "val": "demo_city_center", "src_idx": [0, 12]},
            {"key": "wifi", "req": True, "src_idx": [24, 30]},
            {"key": "parking", "req": True, "src_idx": [15, 20]},
            {"key": "price", "val": "cheap", "src_idx": [35, 37]}
        ]
        
        tool_args = {"location": "demo_city_center", "amenities": ["wifi"]}
        
        # 1. Session initialization
        self.generate_session_init()
        
        # 2. User input
        self.generate_user_interaction(user_content)
        
        # 3. Constraint extraction
        self.generate_constraint_extraction(constraints)
        
        # 4. Agent thought
        self.generate_agent_thought()
        
        # 5. Risk assessment
        self.generate_risk_assessment()
        
        # 6. Tool call attempt
        self.generate_tool_call_attempt(tool_args, include_parking=not self.has_violation)
        
        if self.has_violation:
            # Violation path
            for retry in range(self.retry_count):
                # 7. Drift check (violation)
                self.generate_drift_check(has_violation=True)
                
                # 8. Execution blocked
                self.generate_execution_blocked("parking")
                
                # 9. System injection
                self.generate_system_injection()
                
                # 10. Recovery thought
                self.generate_recovery_thought()
                
                if retry < self.retry_count - 1:
                    # Additional retry needed
                    self.generate_tool_call_attempt(tool_args, include_parking=False)
                else:
                    # Final retry (corrected)
                    self.generate_tool_retry()
            
            # 12. Execution allowed
            self.generate_execution_allowed()
        else:
            # Normal path (no violation)
            self.generate_drift_check(has_violation=False)
        
        # 13-14. Outbound request/response
        simulate_timeout = random.random() < Config.PROB_TIMEOUT
        success = self.generate_outbound_request_response(simulate_timeout)
        
        if not success:
            # Retry after timeout
            self._maybe_add_debug_log("timeout_retry")
            self.generate_outbound_request_response(simulate_timeout=False)
        
        # 15. Tool result
        partial_failure = random.random() < Config.PROB_PARTIAL_FAILURE
        self.generate_tool_result(partial_failure)
        
        return self.events


# =============================================================================
# Main Execution
# =============================================================================

def main():
    user_content = "Find me a cheap hotel in the city center with parking and free WiFi"
    
    generator = RealisticLogGenerator()
    logs = generator.generate(user_content)
    
    for log in logs:
        print(json.dumps(log, ensure_ascii=False))


if __name__ == "__main__":
    main()
