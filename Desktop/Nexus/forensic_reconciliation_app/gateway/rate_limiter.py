"""
Rate Limiting System - Request Throttling and Protection

This module implements the RateLimiter class that provides
comprehensive rate limiting capabilities for the forensic platform.
"""

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import asyncio

from ..ai_service.taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class RateLimitType(Enum):
    """Types of rate limiting."""

    FIXED_WINDOW = "fixed_window"  # Fixed time window
    SLIDING_WINDOW = "sliding_window"  # Sliding time window
    TOKEN_BUCKET = "token_bucket"  # Token bucket algorithm
    LEAKY_BUCKET = "leaky_bucket"  # Leaky bucket algorithm
    ADAPTIVE = "adaptive"  # Adaptive rate limiting


class LimitScope(Enum):
    """Scope of rate limiting."""

    GLOBAL = "global"  # Global rate limit
    PER_USER = "per_user"  # Per-user rate limit
    PER_IP = "per_ip"  # Per-IP rate limit
    PER_ENDPOINT = "per_endpoint"  # Per-endpoint rate limit
    PER_API_KEY = "per_api_key"  # Per-API key rate limit


class LimitAction(Enum):
    """Actions to take when rate limit is exceeded."""

    BLOCK = "block"  # Block the request
    DELAY = "delay"  # Delay the request
    THROTTLE = "throttle"  # Throttle the request
    CHALLENGE = "challenge"  # Present a challenge (CAPTCHA)
    WARN = "warn"  # Warn but allow


@dataclass
class RateLimitRule:
    """A rate limiting rule."""

    rule_id: str
    rule_name: str
    limit_type: RateLimitType
    limit_scope: LimitScope
    max_requests: int
    time_window: int  # seconds
    limit_action: LimitAction
    burst_limit: int
    is_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitState:
    """Current state of rate limiting for an entity."""

    entity_id: str
    rule_id: str
    current_requests: int
    window_start: datetime
    last_request: datetime
    blocked_until: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    request_id: str
    entity_id: str
    rule_id: str
    allowed: bool
    limit_exceeded: bool
    remaining_requests: int
    reset_time: datetime
    action_taken: LimitAction
    delay_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitMetrics:
    """Metrics for rate limiting."""

    total_requests: int
    allowed_requests: int
    blocked_requests: int
    delayed_requests: int
    throttled_requests: int
    challenge_requests: int
    average_response_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """
    Comprehensive rate limiting system.

    The RateLimiter is responsible for:
    - Implementing multiple rate limiting algorithms
    - Managing rate limit rules and policies
    - Tracking request patterns and limits
    - Enforcing rate limits with various actions
    - Providing rate limiting metrics and monitoring
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the RateLimiter."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_max_requests = config.get("default_max_requests", 100)
        self.default_time_window = config.get("default_time_window", 60)  # 1 minute
        self.default_burst_limit = config.get("default_burst_limit", 10)
        self.enable_adaptive_limiting = config.get("enable_adaptive_limiting", True)

        # Rate limiting rules
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.rule_index: Dict[str, List[str]] = defaultdict(list)

        # Rate limiting state
        self.rate_limit_states: Dict[str, RateLimitState] = {}
        self.entity_states: Dict[str, Dict[str, RateLimitState]] = defaultdict(dict)

        # Request tracking
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_entities: Dict[str, datetime] = {}

        # Performance tracking
        self.total_requests = 0
        self.allowed_requests = 0
        self.blocked_requests = 0
        self.delayed_requests = 0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize rate limiting components
        self._initialize_rate_limiting_components()

        self.logger.info("RateLimiter initialized successfully")

    async def start(self):
        """Start the RateLimiter."""
        self.logger.info("Starting RateLimiter...")

        # Initialize rate limiting components
        await self._initialize_rate_limiting_components()

        # Start background tasks
        asyncio.create_task(self._cleanup_expired_states())
        asyncio.create_task(self._update_adaptive_limits())

        self.logger.info("RateLimiter started successfully")

    async def stop(self):
        """Stop the RateLimiter."""
        self.logger.info("Stopping RateLimiter...")
        self.logger.info("RateLimiter stopped")

    def _initialize_rate_limiting_components(self):
        """Initialize rate limiting components."""
        try:
            # Initialize default rate limiting rules
            self._initialize_default_rules()

            self.logger.info("Rate limiting components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing rate limiting components: {e}")

    def _initialize_default_rules(self):
        """Initialize default rate limiting rules."""
        try:
            # Global rate limit rule
            global_rule = RateLimitRule(
                rule_id="global_001",
                rule_name="Global Rate Limit",
                limit_type=RateLimitType.SLIDING_WINDOW,
                limit_scope=LimitScope.GLOBAL,
                max_requests=1000,
                time_window=60,
                limit_action=LimitAction.THROTTLE,
                burst_limit=100,
                is_active=True,
            )

            # Per-user rate limit rule
            user_rule = RateLimitRule(
                rule_id="user_001",
                rule_name="Per-User Rate Limit",
                limit_type=RateLimitType.FIXED_WINDOW,
                limit_scope=LimitScope.PER_USER,
                max_requests=100,
                time_window=60,
                limit_action=LimitAction.BLOCK,
                burst_limit=10,
                is_active=True,
            )

            # Per-IP rate limit rule
            ip_rule = RateLimitRule(
                rule_id="ip_001",
                rule_name="Per-IP Rate Limit",
                limit_type=RateLimitType.SLIDING_WINDOW,
                limit_scope=LimitScope.PER_IP,
                max_requests=200,
                time_window=60,
                limit_action=LimitAction.DELAY,
                burst_limit=20,
                is_active=True,
            )

            # Per-endpoint rate limit rule
            endpoint_rule = RateLimitRule(
                rule_id="endpoint_001",
                rule_name="Per-Endpoint Rate Limit",
                limit_type=RateLimitType.TOKEN_BUCKET,
                limit_scope=LimitScope.PER_ENDPOINT,
                max_requests=50,
                time_window=60,
                limit_action=LimitAction.WARN,
                burst_limit=5,
                is_active=True,
            )

            # Store rules
            self.rate_limit_rules[global_rule.rule_id] = global_rule
            self.rate_limit_rules[user_rule.rule_id] = user_rule
            self.rate_limit_rules[ip_rule.rule_id] = ip_rule
            self.rate_limit_rules[endpoint_rule.rule_id] = endpoint_rule

            # Index rules by scope
            for rule in [global_rule, user_rule, ip_rule, endpoint_rule]:
                self.rule_index[rule.limit_scope.value].append(rule.rule_id)

            self.logger.info(
                f"Initialized {len(self.rate_limit_rules)} default rate limiting rules"
            )

        except Exception as e:
            self.logger.error(f"Error initializing default rules: {e}")

    async def create_rate_limit_rule(
        self,
        rule_name: str,
        limit_type: RateLimitType,
        limit_scope: LimitScope,
        max_requests: int,
        time_window: int,
        limit_action: LimitAction,
        burst_limit: int = None,
    ) -> str:
        """Create a new rate limiting rule."""
        try:
            rule_id = str(uuid.uuid4())

            if burst_limit is None:
                burst_limit = max(1, max_requests // 10)

            rule = RateLimitRule(
                rule_id=rule_id,
                rule_name=rule_name,
                limit_type=limit_type,
                limit_scope=limit_scope,
                max_requests=max_requests,
                time_window=time_window,
                limit_action=limit_action,
                burst_limit=burst_limit,
                is_active=True,
            )

            # Store rule
            self.rate_limit_rules[rule_id] = rule
            self.rule_index[limit_scope.value].append(rule_id)

            self.logger.info(f"Created rate limit rule: {rule_id} - {rule_name}")

            return rule_id

        except Exception as e:
            self.logger.error(f"Error creating rate limit rule: {e}")
            raise

    async def check_rate_limit(
        self, entity_id: str, rule_id: str = None, endpoint_path: str = None
    ) -> RateLimitResult:
        """Check if a request is allowed based on rate limiting rules."""
        try:
            self.total_requests += 1

            # Determine which rules to check
            rules_to_check = []

            if rule_id:
                # Check specific rule
                if rule_id in self.rate_limit_rules:
                    rules_to_check.append(self.rate_limit_rules[rule_id])
            else:
                # Check applicable rules based on entity type
                if entity_id.startswith("user_"):
                    # User entity
                    for rule_id in self.rule_index[LimitScope.PER_USER.value]:
                        rules_to_check.append(self.rate_limit_rules[rule_id])
                elif entity_id.startswith("ip_"):
                    # IP entity
                    for rule_id in self.rule_index[LimitScope.PER_IP.value]:
                        rules_to_check.append(self.rate_limit_rules[rule_id])
                elif endpoint_path:
                    # Endpoint entity
                    for rule_id in self.rule_index[LimitScope.PER_ENDPOINT.value]:
                        rules_to_check.append(self.rate_limit_rules[rule_id])

                # Always check global rules
                for rule_id in self.rule_index[LimitScope.GLOBAL.value]:
                    rules_to_check.append(self.rate_limit_rules[rule_id])

            # Check each rule
            allowed = True
            limit_exceeded = False
            action_taken = LimitAction.WARN
            delay_seconds = 0.0
            remaining_requests = float("inf")
            reset_time = datetime.utcnow()

            for rule in rules_to_check:
                if not rule.is_active:
                    continue

                rule_result = await self._check_single_rule(entity_id, rule)

                if not rule_result["allowed"]:
                    allowed = False
                    limit_exceeded = True
                    action_taken = rule.limit_action
                    delay_seconds = rule_result.get("delay_seconds", 0.0)

                # Track remaining requests and reset time
                if rule_result.get("remaining_requests", 0) < remaining_requests:
                    remaining_requests = rule_result.get("remaining_requests", 0)
                    reset_time = rule_result.get("reset_time", datetime.utcnow())

            # Create result
            result = RateLimitResult(
                request_id=str(uuid.uuid4()),
                entity_id=entity_id,
                rule_id=rule_id or "multiple",
                allowed=allowed,
                limit_exceeded=limit_exceeded,
                remaining_requests=(
                    int(remaining_requests)
                    if remaining_requests != float("inf")
                    else -1
                ),
                reset_time=reset_time,
                action_taken=action_taken,
                delay_seconds=delay_seconds,
            )

            # Update statistics
            if allowed:
                self.allowed_requests += 1
            else:
                if action_taken == LimitAction.BLOCK:
                    self.blocked_requests += 1
                elif action_taken == LimitAction.DELAY:
                    self.delayed_requests += 1

            # Record request
            self.request_history[entity_id].append(
                {
                    "timestamp": datetime.utcnow(),
                    "allowed": allowed,
                    "action_taken": action_taken.value,
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            # Default to allowing the request on error
            return RateLimitResult(
                request_id=str(uuid.uuid4()),
                entity_id=entity_id,
                rule_id=rule_id or "error",
                allowed=True,
                limit_exceeded=False,
                remaining_requests=-1,
                reset_time=datetime.utcnow(),
                action_taken=LimitAction.WARN,
                delay_seconds=0.0,
            )

    async def _check_single_rule(
        self, entity_id: str, rule: RateLimitRule
    ) -> Dict[str, Any]:
        """Check a single rate limiting rule."""
        try:
            current_time = datetime.utcnow()

            # Get or create rate limit state
            state_key = f"{entity_id}_{rule.rule_id}"
            if state_key not in self.rate_limit_states:
                state = RateLimitState(
                    entity_id=entity_id,
                    rule_id=rule.rule_id,
                    current_requests=0,
                    window_start=current_time,
                    last_request=current_time,
                    blocked_until=None,
                )
                self.rate_limit_states[state_key] = state
            else:
                state = self.rate_limit_states[state_key]

            # Check if entity is blocked
            if state.blocked_until and current_time < state.blocked_until:
                return {
                    "allowed": False,
                    "delay_seconds": (
                        state.blocked_until - current_time
                    ).total_seconds(),
                }

            # Apply rate limiting algorithm
            if rule.limit_type == RateLimitType.FIXED_WINDOW:
                result = self._check_fixed_window(state, rule, current_time)
            elif rule.limit_type == RateLimitType.SLIDING_WINDOW:
                result = self._check_sliding_window(state, rule, current_time)
            elif rule.limit_type == RateLimitType.TOKEN_BUCKET:
                result = self._check_token_bucket(state, rule, current_time)
            elif rule.limit_type == RateLimitType.LEAKY_BUCKET:
                result = self._check_leaky_bucket(state, rule, current_time)
            else:
                # Default to fixed window
                result = self._check_fixed_window(state, rule, current_time)

            # Update state
            state.current_requests = result.get(
                "current_requests", state.current_requests
            )
            state.window_start = result.get("window_start", state.window_start)
            state.last_request = current_time

            # Handle limit exceeded
            if not result["allowed"]:
                if rule.limit_action == LimitAction.BLOCK:
                    # Block for the time window
                    state.blocked_until = current_time + timedelta(
                        seconds=rule.time_window
                    )
                elif rule.limit_action == LimitAction.DELAY:
                    # Calculate delay
                    delay_seconds = rule.time_window / rule.max_requests
                    result["delay_seconds"] = delay_seconds

            return result

        except Exception as e:
            self.logger.error(f"Error checking single rule: {e}")
            return {"allowed": True, "current_requests": 0}

    def _check_fixed_window(
        self, state: RateLimitState, rule: RateLimitRule, current_time: datetime
    ) -> Dict[str, Any]:
        """Check rate limit using fixed window algorithm."""
        try:
            # Check if window has expired
            if current_time - state.window_start >= timedelta(seconds=rule.time_window):
                # Reset window
                state.window_start = current_time
                state.current_requests = 0

            # Check if limit exceeded
            if state.current_requests >= rule.max_requests:
                return {
                    "allowed": False,
                    "current_requests": state.current_requests,
                    "window_start": state.window_start,
                    "remaining_requests": 0,
                    "reset_time": state.window_start
                    + timedelta(seconds=rule.time_window),
                }

            # Allow request
            state.current_requests += 1

            return {
                "allowed": True,
                "current_requests": state.current_requests,
                "window_start": state.window_start,
                "remaining_requests": rule.max_requests - state.current_requests,
                "reset_time": state.window_start + timedelta(seconds=rule.time_window),
            }

        except Exception as e:
            self.logger.error(f"Error in fixed window check: {e}")
            return {"allowed": True, "current_requests": 0}

    def _check_sliding_window(
        self, state: RateLimitState, rule: RateLimitRule, current_time: datetime
    ) -> Dict[str, Any]:
        """Check rate limit using sliding window algorithm."""
        try:
            # Calculate window start (sliding)
            window_start = current_time - timedelta(seconds=rule.time_window)

            # Count requests in current window
            current_requests = 0
            for request in self.request_history[state.entity_id]:
                if request["timestamp"] >= window_start:
                    current_requests += 1

            # Check if limit exceeded
            if current_requests >= rule.max_requests:
                return {
                    "allowed": False,
                    "current_requests": current_requests,
                    "window_start": window_start,
                    "remaining_requests": 0,
                    "reset_time": current_time + timedelta(seconds=rule.time_window),
                }

            # Allow request
            return {
                "allowed": True,
                "current_requests": current_requests + 1,
                "window_start": window_start,
                "remaining_requests": rule.max_requests - (current_requests + 1),
                "reset_time": current_time + timedelta(seconds=rule.time_window),
            }

        except Exception as e:
            self.logger.error(f"Error in sliding window check: {e}")
            return {"allowed": True, "current_requests": 0}

    def _check_token_bucket(
        self, state: RateLimitState, rule: RateLimitRule, current_time: datetime
    ) -> Dict[str, Any]:
        """Check rate limit using token bucket algorithm."""
        try:
            # Calculate tokens to add
            time_passed = (current_time - state.window_start).total_seconds
            tokens_to_add = int(time_passed * (rule.max_requests / rule.time_window))

            # Add tokens (with burst limit)
            new_tokens = min(rule.max_requests, state.current_requests + tokens_to_add)

            # Check if tokens available
            if new_tokens <= 0:
                return {
                    "allowed": False,
                    "current_requests": 0,
                    "window_start": state.window_start,
                    "remaining_requests": 0,
                    "reset_time": current_time + timedelta(seconds=rule.time_window),
                }

            # Consume token
            new_tokens -= 1

            return {
                "allowed": True,
                "current_requests": new_tokens,
                "window_start": state.window_start,
                "remaining_requests": new_tokens,
                "reset_time": current_time + timedelta(seconds=rule.time_window),
            }

        except Exception as e:
            self.logger.error(f"Error in token bucket check: {e}")
            return {"allowed": True, "current_requests": 0}

    def _check_leaky_bucket(
        self, state: RateLimitState, rule: RateLimitRule, current_time: datetime
    ) -> Dict[str, Any]:
        """Check rate limit using leaky bucket algorithm."""
        try:
            # Calculate leaked tokens
            time_passed = (current_time - state.window_start).total_seconds
            leaked_tokens = int(time_passed * (rule.max_requests / rule.time_window))

            # Remove leaked tokens
            new_tokens = max(0, state.current_requests - leaked_tokens)

            # Check if bucket is full
            if new_tokens >= rule.max_requests:
                return {
                    "allowed": False,
                    "current_requests": new_tokens,
                    "window_start": state.window_start,
                    "remaining_requests": 0,
                    "reset_time": current_time + timedelta(seconds=rule.time_window),
                }

            # Add request to bucket
            new_tokens += 1

            return {
                "allowed": True,
                "current_requests": new_tokens,
                "window_start": state.window_start,
                "remaining_requests": rule.max_requests - new_tokens,
                "reset_time": current_time + timedelta(seconds=rule.time_window),
            }

        except Exception as e:
            self.logger.error(f"Error in leaky bucket check: {e}")
            return {"allowed": True, "current_requests": 0}

    async def _cleanup_expired_states(self):
        """Clean up expired rate limit states."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_states = []

                for state_key, state in self.rate_limit_states.items():
                    # Check if state is old (more than 1 hour)
                    if current_time - state.last_request > timedelta(hours=1):
                        expired_states.append(state_key)

                for state_key in expired_states:
                    del self.rate_limit_states[state_key]

                if expired_states:
                    self.logger.info(
                        f"Cleaned up {len(expired_states)} expired rate limit states"
                    )

                await asyncio.sleep(300)  # Clean up every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up expired states: {e}")
                await asyncio.sleep(300)

    async def _update_adaptive_limits(self):
        """Update rate limits based on adaptive algorithms."""
        while True:
            try:
                if not self.enable_adaptive_limiting:
                    await asyncio.sleep(300)
                    continue

                # Analyze request patterns and adjust limits
                for entity_id, requests in self.request_history.items():
                    if len(requests) < 10:  # Need minimum data
                        continue

                    # Calculate success rate
                    recent_requests = list(requests)[-100:]  # Last 100 requests
                    success_rate = sum(
                        1 for req in recent_requests if req["allowed"]
                    ) / len(recent_requests)

                    # Adjust limits based on success rate
                    if success_rate < 0.5:  # Low success rate
                        # Increase limits
                        await self._adjust_entity_limits(entity_id, "increase")
                    elif success_rate > 0.9:  # High success rate
                        # Decrease limits
                        await self._adjust_entity_limits(entity_id, "decrease")

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating adaptive limits: {e}")
                await asyncio.sleep(300)

    async def _adjust_entity_limits(self, entity_id: str, action: str):
        """Adjust rate limits for an entity."""
        try:
            # Find applicable rules
            applicable_rules = []
            for rule in self.rate_limit_rules.values():
                if rule.is_active:
                    applicable_rules.append(rule)

            # Adjust limits
            for rule in applicable_rules:
                if action == "increase":
                    # Increase limits by 10%
                    rule.max_requests = int(rule.max_requests * 1.1)
                    rule.burst_limit = int(rule.burst_limit * 1.1)
                elif action == "decrease":
                    # Decrease limits by 10%
                    rule.max_requests = max(1, int(rule.max_requests * 0.9))
                    rule.burst_limit = max(1, int(rule.burst_limit * 0.9))

            self.logger.info(f"Adjusted rate limits for entity {entity_id}: {action}")

        except Exception as e:
            self.logger.error(f"Error adjusting entity limits: {e}")

    def get_performance_metrics(self) -> RateLimitMetrics:
        """Get performance metrics."""
        return RateLimitMetrics(
            total_requests=self.total_requests,
            allowed_requests=self.allowed_requests,
            blocked_requests=self.blocked_requests,
            delayed_requests=self.delayed_requests,
            throttled_requests=0,  # Not implemented yet
            challenge_requests=0,  # Not implemented yet
            average_response_time=0.0,  # Not implemented yet
            metadata={
                "active_rules": len(self.rate_limit_rules),
                "active_states": len(self.rate_limit_states),
                "blocked_entities": len(self.blocked_entities),
                "rate_limit_types_supported": [t.value for t in RateLimitType],
                "limit_scopes_supported": [s.value for s in LimitScope],
                "limit_actions_supported": [a.value for a in LimitAction],
            },
        )


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_max_requests": 100,
        "default_time_window": 60,
        "default_burst_limit": 10,
        "enable_adaptive_limiting": True,
    }

    # Initialize rate limiter
    rate_limiter = RateLimiter(config)

    print("RateLimiter system initialized successfully!")
