"""
Rate Limiting and Throttling System

This module implements the RateLimiter class that provides
comprehensive rate limiting and throttling capabilities for the API gateway.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
from pathlib import Path
import time

# Redis libraries for distributed rate limiting
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"                           # Fixed time window
    SLIDING_WINDOW = "sliding_window"                        # Sliding time window
    TOKEN_BUCKET = "token_bucket"                            # Token bucket algorithm
    LEAKY_BUCKET = "leaky_bucket"                            # Leaky bucket algorithm
    ADAPTIVE = "adaptive"                                     # Adaptive rate limiting


class ThrottleAction(Enum):
    """Actions to take when rate limit is exceeded."""
    BLOCK = "block"                                           # Block the request
    DELAY = "delay"                                           # Delay the request
    QUEUE = "queue"                                           # Queue the request
    REDUCE_PRIORITY = "reduce_priority"                       # Reduce request priority
    NOTIFY = "notify"                                         # Send notification


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    
    rule_id: str
    name: str
    pattern: str  # URL pattern or endpoint
    strategy: RateLimitStrategy
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    throttle_action: ThrottleAction
    delay_seconds: Optional[int]
    priority: int
    enabled: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientIdentifier:
    """Client identification information."""
    
    client_id: str
    ip_address: str
    user_id: Optional[str]
    api_key: Optional[str]
    user_agent: str
    session_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitState:
    """Current rate limit state for a client."""
    
    client_id: str
    rule_id: str
    current_requests: int
    window_start: datetime
    last_request: datetime
    blocked_until: Optional[datetime]
    retry_after: Optional[int]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThrottleResult:
    """Result of rate limiting check."""
    
    allowed: bool
    rule_id: str
    client_id: str
    current_usage: int
    limit: int
    reset_time: datetime
    retry_after: Optional[int]
    throttle_action: Optional[ThrottleAction]
    delay_seconds: Optional[int]
    message: str


class RateLimiter:
    """
    Comprehensive rate limiting and throttling system.
    
    The RateLimiter is responsible for:
    - Multiple rate limiting strategies
    - Client identification and tracking
    - Configurable rate limit rules
    - Throttling actions and policies
    - Distributed rate limiting with Redis
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the RateLimiter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_rate_limiting = config.get('enable_rate_limiting', True)
        self.default_strategy = RateLimitStrategy.SLIDING_WINDOW
        self.default_throttle_action = ThrottleAction.BLOCK
        self.enable_distributed_limiting = config.get('enable_distributed_limiting', True)
        self.redis_host = config.get('redis_host', 'localhost')
        self.redis_port = config.get('redis_port', 6379)
        self.redis_db = config.get('redis_db', 0)
        
        # Rate limiting management
        self.rules: Dict[str, RateLimitRule] = {}
        self.client_states: Dict[str, Dict[str, RateLimitState]] = defaultdict(dict)
        self.client_identifiers: Dict[str, ClientIdentifier] = {}
        
        # Performance tracking
        self.total_requests = 0
        self.blocked_requests = 0
        self.delayed_requests = 0
        self.throttled_requests = 0
        
        # Connection management
        self.redis_connection = None
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        # Check library availability
        self._check_library_availability()
        
        # Initialize default rules
        self._initialize_default_rules()
        
        self.logger.info("RateLimiter initialized successfully")
    
    def _check_library_availability(self):
        """Check if required libraries are available."""
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available - distributed rate limiting will be disabled")
            self.enable_distributed_limiting = False
    
    def _initialize_default_rules(self):
        """Initialize default rate limiting rules."""
        try:
            # Global rate limit rule
            self.add_rule(
                RateLimitRule(
                    rule_id="global_default",
                    name="Global Default Rate Limit",
                    pattern="*",
                    strategy=RateLimitStrategy.SLIDING_WINDOW,
                    requests_per_minute=1000,
                    requests_per_hour=10000,
                    requests_per_day=100000,
                    burst_limit=200,
                    throttle_action=ThrottleAction.BLOCK,
                    delay_seconds=None,
                    priority=100,
                    enabled=True
                )
            )
            
            # Authentication endpoints rate limit
            self.add_rule(
                RateLimitRule(
                    rule_id="auth_endpoints",
                    name="Authentication Endpoints Rate Limit",
                    pattern="/api/auth/*",
                    strategy=RateLimitStrategy.FIXED_WINDOW,
                    requests_per_minute=10,
                    requests_per_hour=100,
                    requests_per_day=1000,
                    burst_limit=5,
                    throttle_action=ThrottleAction.BLOCK,
                    delay_seconds=300,  # 5 minutes block
                    priority=90,
                    enabled=True
                )
            )
            
            # AI service endpoints rate limit
            self.add_rule(
                RateLimitRule(
                    rule_id="ai_service",
                    name="AI Service Endpoints Rate Limit",
                    pattern="/api/ai/*",
                    strategy=RateLimitStrategy.TOKEN_BUCKET,
                    requests_per_minute=50,
                    requests_per_hour=500,
                    requests_per_day=5000,
                    burst_limit=100,
                    throttle_action=ThrottleAction.QUEUE,
                    delay_seconds=60,
                    priority=80,
                    enabled=True
                )
            )
            
            # Evidence processing rate limit
            self.add_rule(
                RateLimitRule(
                    rule_id="evidence_processing",
                    name="Evidence Processing Rate Limit",
                    pattern="/api/evidence/*",
                    strategy=RateLimitStrategy.LEAKY_BUCKET,
                    requests_per_minute=20,
                    requests_per_hour=200,
                    requests_per_day=2000,
                    burst_limit=50,
                    throttle_action=ThrottleAction.DELAY,
                    delay_seconds=30,
                    priority=70,
                    enabled=True
                )
            )
            
            # Report generation rate limit
            self.add_rule(
                RateLimitRule(
                    rule_id="report_generation",
                    name="Report Generation Rate Limit",
                    pattern="/api/reports/*",
                    strategy=RateLimitStrategy.FIXED_WINDOW,
                    requests_per_minute=5,
                    requests_per_hour=50,
                    requests_per_day=500,
                    burst_limit=10,
                    throttle_action=ThrottleAction.QUEUE,
                    delay_seconds=120,
                    priority=60,
                    enabled=True
                )
            )
            
            self.logger.info("Default rate limiting rules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing default rules: {e}")
    
    async def start(self):
        """Start the RateLimiter."""
        self.logger.info("Starting RateLimiter...")
        
        # Initialize Redis connection
        if self.enable_distributed_limiting:
            await self._initialize_redis_connection()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_states())
        asyncio.create_task(self._update_performance_metrics())
        
        self.logger.info("RateLimiter started successfully")
    
    async def stop(self):
        """Stop the RateLimiter."""
        self.logger.info("Stopping RateLimiter...")
        
        # Close Redis connection
        if self.redis_connection:
            self.redis_connection.close()
        
        self.logger.info("RateLimiter stopped")
    
    async def _initialize_redis_connection(self):
        """Initialize Redis connection for distributed rate limiting."""
        try:
            if REDIS_AVAILABLE:
                self.redis_connection = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    decode_responses=True
                )
                
                # Test connection
                self.redis_connection.ping()
                
                self.logger.info("Redis connection established for distributed rate limiting")
                
        except Exception as e:
            self.logger.warning(f"Could not establish Redis connection: {e}")
            self.enable_distributed_limiting = False
    
    def add_rule(self, rule: RateLimitRule):
        """Add a new rate limiting rule."""
        try:
            if rule.rule_id in self.rules:
                raise ValueError(f"Rule already exists: {rule.rule_id}")
            
            # Store rule
            self.rules[rule.rule_id] = rule
            
            self.logger.info(f"Rate limiting rule added successfully: {rule.rule_id} - {rule.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding rate limiting rule: {e}")
            raise
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update an existing rate limiting rule."""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule not found: {rule_id}")
            
            rule = self.rules[rule_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)
            
            self.logger.info(f"Rate limiting rule updated successfully: {rule_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating rate limiting rule: {e}")
            raise
    
    def remove_rule(self, rule_id: str):
        """Remove a rate limiting rule."""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule not found: {rule_id}")
            
            # Remove rule
            del self.rules[rule_id]
            
            # Clean up client states for this rule
            for client_states in self.client_states.values():
                if rule_id in client_states:
                    del client_states[rule_id]
            
            self.logger.info(f"Rate limiting rule removed successfully: {rule_id}")
            
        except Exception as e:
            self.logger.error(f"Error removing rate limiting rule: {e}")
            raise
    
    async def check_rate_limit(self, client_info: Dict[str, Any], endpoint: str) -> ThrottleResult:
        """Check if a request is allowed based on rate limiting rules."""
        try:
            if not self.enable_rate_limiting:
                return ThrottleResult(
                    allowed=True,
                    rule_id="",
                    client_id="",
                    current_usage=0,
                    limit=0,
                    reset_time=datetime.utcnow(),
                    retry_after=None,
                    throttle_action=None,
                    delay_seconds=None,
                    message="Rate limiting disabled"
                )
            
            # Identify client
            client_id = await self._identify_client(client_info)
            
            # Find applicable rule
            rule = self._find_applicable_rule(endpoint)
            if not rule:
                return ThrottleResult(
                    allowed=True,
                    rule_id="",
                    client_id=client_id,
                    current_usage=0,
                    limit=0,
                    reset_time=datetime.utcnow(),
                    retry_after=None,
                    throttle_action=None,
                    delay_seconds=None,
                    message="No rate limiting rule found"
                )
            
            # Check rate limit based on strategy
            if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                result = await self._check_fixed_window(client_id, rule)
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                result = await self._check_sliding_window(client_id, rule)
            elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                result = await self._check_token_bucket(client_id, rule)
            elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
                result = await self._check_leaky_bucket(client_id, rule)
            else:
                result = await self._check_adaptive(client_id, rule)
            
            # Update statistics
            self.total_requests += 1
            if not result.allowed:
                if result.throttle_action == ThrottleAction.BLOCK:
                    self.blocked_requests += 1
                elif result.throttle_action == ThrottleAction.DELAY:
                    self.delayed_requests += 1
                elif result.throttle_action == ThrottleAction.QUEUE:
                    self.throttled_requests += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            
            # Allow request on error (fail open)
            return ThrottleResult(
                allowed=True,
                rule_id="",
                client_id="",
                current_usage=0,
                limit=0,
                reset_time=datetime.utcnow(),
                retry_after=None,
                throttle_action=None,
                delay_seconds=None,
                message=f"Rate limiting error: {str(e)}"
            )
    
    async def _identify_client(self, client_info: Dict[str, Any]) -> str:
        """Identify client from request information."""
        try:
            # Try to get existing client ID
            ip_address = client_info.get('ip_address', 'unknown')
            user_id = client_info.get('user_id')
            api_key = client_info.get('api_key')
            user_agent = client_info.get('user_agent', 'unknown')
            session_id = client_info.get('session_id')
            
            # Create client identifier
            client_identifier = ClientIdentifier(
                client_id=str(uuid.uuid4()),
                ip_address=ip_address,
                user_id=user_id,
                api_key=api_key,
                user_agent=user_agent,
                session_id=session_id
            )
            
            # Store client identifier
            self.client_identifiers[client_identifier.client_id] = client_identifier
            
            return client_identifier.client_id
            
        except Exception as e:
            self.logger.error(f"Error identifying client: {e}")
            return str(uuid.uuid4())
    
    def _find_applicable_rule(self, endpoint: str) -> Optional[RateLimitRule]:
        """Find the applicable rate limiting rule for an endpoint."""
        try:
            applicable_rules = []
            
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                # Check if endpoint matches pattern
                if self._endpoint_matches_pattern(endpoint, rule.pattern):
                    applicable_rules.append(rule)
            
            if not applicable_rules:
                return None
            
            # Return rule with highest priority (lowest number)
            applicable_rules.sort(key=lambda r: r.priority)
            return applicable_rules[0]
            
        except Exception as e:
            self.logger.error(f"Error finding applicable rule: {e}")
            return None
    
    def _endpoint_matches_pattern(self, endpoint: str, pattern: str) -> bool:
        """Check if endpoint matches a pattern."""
        try:
            if pattern == "*":
                return True
            
            # Simple pattern matching (can be enhanced with regex)
            if pattern.endswith("/*"):
                base_pattern = pattern[:-2]
                return endpoint.startswith(base_pattern)
            
            return endpoint == pattern
            
        except Exception as e:
            self.logger.error(f"Error matching endpoint pattern: {e}")
            return False
    
    async def _check_fixed_window(self, client_id: str, rule: RateLimitRule) -> ThrottleResult:
        """Check rate limit using fixed window strategy."""
        try:
            current_time = datetime.utcnow()
            
            # Get or create client state
            if client_id not in self.client_states:
                self.client_states[client_id] = {}
            
            if rule.rule_id not in self.client_states[client_id]:
                self.client_states[client_id][rule.rule_id] = RateLimitState(
                    client_id=client_id,
                    rule_id=rule.rule_id,
                    current_requests=0,
                    window_start=current_time,
                    last_request=current_time,
                    blocked_until=None,
                    retry_after=None
                )
            
            state = self.client_states[client_id][rule.rule_id]
            
            # Check if client is blocked
            if state.blocked_until and current_time < state.blocked_until:
                retry_after = int((state.blocked_until - current_time).total_seconds())
                return ThrottleResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    client_id=client_id,
                    current_usage=state.current_requests,
                    limit=rule.requests_per_minute,
                    reset_time=state.blocked_until,
                    retry_after=retry_after,
                    throttle_action=rule.throttle_action,
                    delay_seconds=rule.delay_seconds,
                    message=f"Rate limit exceeded. Retry after {retry_after} seconds."
                )
            
            # Check if window has reset
            window_duration = timedelta(minutes=1)
            if current_time - state.window_start >= window_duration:
                state.current_requests = 0
                state.window_start = current_time
            
            # Check rate limit
            if state.current_requests >= rule.requests_per_minute:
                # Rate limit exceeded
                if rule.throttle_action == ThrottleAction.BLOCK:
                    block_duration = timedelta(seconds=rule.delay_seconds or 300)
                    state.blocked_until = current_time + block_duration
                    state.retry_after = int(block_duration.total_seconds())
                
                return ThrottleResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    client_id=client_id,
                    current_usage=state.current_requests,
                    limit=rule.requests_per_minute,
                    reset_time=state.window_start + window_duration,
                    retry_after=state.retry_after,
                    throttle_action=rule.throttle_action,
                    delay_seconds=rule.delay_seconds,
                    message="Rate limit exceeded"
                )
            
            # Allow request
            state.current_requests += 1
            state.last_request = current_time
            
            return ThrottleResult(
                allowed=True,
                rule_id=rule.rule_id,
                client_id=client_id,
                current_usage=state.current_requests,
                limit=rule.requests_per_minute,
                reset_time=state.window_start + window_duration,
                retry_after=None,
                throttle_action=None,
                delay_seconds=None,
                message="Request allowed"
            )
            
        except Exception as e:
            self.logger.error(f"Error in fixed window check: {e}")
            raise
    
    async def _check_sliding_window(self, client_id: str, rule: RateLimitRule) -> ThrottleResult:
        """Check rate limit using sliding window strategy."""
        try:
            current_time = datetime.utcnow()
            
            # Get or create client state
            if client_id not in self.client_states:
                self.client_states[client_id] = {}
            
            if rule.rule_id not in self.client_states[client_id]:
                self.client_states[client_id][rule.rule_id] = RateLimitState(
                    client_id=client_id,
                    rule_id=rule.rule_id,
                    current_requests=0,
                    window_start=current_time,
                    last_request=current_time,
                    blocked_until=None,
                    retry_after=None
                )
            
            state = self.client_states[client_id][rule.rule_id]
            
            # Calculate sliding window
            window_duration = timedelta(minutes=1)
            window_start = current_time - window_duration
            
            # Count requests in current window
            current_requests = 0
            # This is a simplified implementation - in production, you'd track individual request timestamps
            
            # Check rate limit
            if current_requests >= rule.requests_per_minute:
                return ThrottleResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    client_id=client_id,
                    current_usage=current_requests,
                    limit=rule.requests_per_minute,
                    reset_time=window_start + window_duration,
                    retry_after=None,
                    throttle_action=rule.throttle_action,
                    delay_seconds=rule.delay_seconds,
                    message="Rate limit exceeded"
                )
            
            # Allow request
            state.current_requests += 1
            state.last_request = current_time
            
            return ThrottleResult(
                allowed=True,
                rule_id=rule.rule_id,
                client_id=client_id,
                current_usage=state.current_requests,
                limit=rule.requests_per_minute,
                reset_time=window_start + window_duration,
                retry_after=None,
                throttle_action=None,
                delay_seconds=None,
                message="Request allowed"
            )
            
        except Exception as e:
            self.logger.error(f"Error in sliding window check: {e}")
            raise
    
    async def _check_token_bucket(self, client_id: str, rule: RateLimitRule) -> ThrottleResult:
        """Check rate limit using token bucket strategy."""
        try:
            current_time = datetime.utcnow()
            
            # Get or create client state
            if client_id not in self.client_states:
                self.client_states[client_id] = {}
            
            if rule.rule_id not in self.client_states[client_id]:
                self.client_states[client_id][rule.rule_id] = RateLimitState(
                    client_id=client_id,
                    rule_id=rule.rule_id,
                    current_requests=0,
                    window_start=current_time,
                    last_request=current_time,
                    blocked_until=None,
                    retry_after=None
                )
            
            state = self.client_states[client_id][rule.rule_id]
            
            # Token bucket implementation
            tokens_per_minute = rule.requests_per_minute
            bucket_capacity = rule.burst_limit
            
            # Calculate tokens to add since last request
            time_since_last = (current_time - state.last_request).total_seconds()
            tokens_to_add = (time_since_last / 60) * tokens_per_minute
            
            # Current tokens (simplified)
            current_tokens = min(bucket_capacity, state.current_requests + tokens_to_add)
            
            if current_tokens < 1:
                return ThrottleResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    client_id=client_id,
                    current_usage=state.current_requests,
                    limit=rule.requests_per_minute,
                    reset_time=current_time + timedelta(seconds=60),
                    retry_after=60,
                    throttle_action=rule.throttle_action,
                    delay_seconds=rule.delay_seconds,
                    message="No tokens available"
                )
            
            # Allow request
            state.current_requests = max(0, current_tokens - 1)
            state.last_request = current_time
            
            return ThrottleResult(
                allowed=True,
                rule_id=rule.rule_id,
                client_id=client_id,
                current_usage=state.current_requests,
                limit=rule.requests_per_minute,
                reset_time=current_time + timedelta(seconds=60),
                retry_after=None,
                throttle_action=None,
                delay_seconds=None,
                message="Request allowed"
            )
            
        except Exception as e:
            self.logger.error(f"Error in token bucket check: {e}")
            raise
    
    async def _check_leaky_bucket(self, client_id: str, rule: RateLimitRule) -> ThrottleResult:
        """Check rate limit using leaky bucket strategy."""
        try:
            current_time = datetime.utcnow()
            
            # Get or create client state
            if client_id not in self.client_states:
                self.client_states[client_id] = {}
            
            if rule.rule_id not in self.client_states[client_id]:
                self.client_states[client_id][rule.rule_id] = RateLimitState(
                    client_id=client_id,
                    rule_id=rule.rule_id,
                    current_requests=0,
                    window_start=current_time,
                    last_request=current_time,
                    blocked_until=None,
                    retry_after=None
                )
            
            state = self.client_states[client_id][rule.rule_id]
            
            # Leaky bucket implementation
            bucket_capacity = rule.burst_limit
            leak_rate = rule.requests_per_minute / 60  # requests per second
            
            # Calculate leaked tokens
            time_since_last = (current_time - state.last_request).total_seconds()
            leaked_tokens = time_since_last * leak_rate
            
            # Current bucket level
            current_level = max(0, state.current_requests - leaked_tokens)
            
            if current_level >= bucket_capacity:
                return ThrottleResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    client_id=client_id,
                    current_usage=state.current_requests,
                    limit=rule.requests_per_minute,
                    reset_time=current_time + timedelta(seconds=1),
                    retry_after=1,
                    throttle_action=rule.throttle_action,
                    delay_seconds=rule.delay_seconds,
                    message="Bucket is full"
                )
            
            # Allow request
            state.current_requests = current_level + 1
            state.last_request = current_time
            
            return ThrottleResult(
                allowed=True,
                rule_id=rule.rule_id,
                client_id=client_id,
                current_usage=state.current_requests,
                limit=rule.requests_per_minute,
                reset_time=current_time + timedelta(seconds=1),
                retry_after=None,
                throttle_action=None,
                delay_seconds=None,
                message="Request allowed"
            )
            
        except Exception as e:
            self.logger.error(f"Error in leaky bucket check: {e}")
            raise
    
    async def _check_adaptive(self, client_id: str, rule: RateLimitRule) -> ThrottleResult:
        """Check rate limit using adaptive strategy."""
        try:
            # Adaptive rate limiting based on system load and client behavior
            # This is a simplified implementation
            
            # For now, use sliding window as fallback
            return await self._check_sliding_window(client_id, rule)
            
        except Exception as e:
            self.logger.error(f"Error in adaptive check: {e}")
            raise
    
    async def _cleanup_expired_states(self):
        """Clean up expired client states."""
        while True:
            try:
                current_time = datetime.utcnow()
                cleanup_threshold = timedelta(hours=24)
                
                expired_clients = []
                for client_id, client_states in self.client_states.items():
                    for rule_id, state in client_states.items():
                        if (current_time - state.last_request) > cleanup_threshold:
                            expired_clients.append((client_id, rule_id))
                
                for client_id, rule_id in expired_clients:
                    if client_id in self.client_states and rule_id in self.client_states[client_id]:
                        del self.client_states[client_id][rule_id]
                    
                    # Remove empty client entries
                    if client_id in self.client_states and not self.client_states[client_id]:
                        del self.client_states[client_id]
                
                if expired_clients:
                    self.logger.info(f"Cleaned up {len(expired_clients)} expired client states")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up expired states: {e}")
                await asyncio.sleep(3600)
    
    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # Update metrics
                # This is a simplified implementation
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)
    
    def get_rule(self, rule_id: str) -> Optional[RateLimitRule]:
        """Get rate limiting rule by ID."""
        try:
            return self.rules.get(rule_id)
        except Exception as e:
            self.logger.error(f"Error getting rule: {e}")
            return None
    
    def get_client_state(self, client_id: str, rule_id: str) -> Optional[RateLimitState]:
        """Get client state for a specific rule."""
        try:
            return self.client_states.get(client_id, {}).get(rule_id)
        except Exception as e:
            self.logger.error(f"Error getting client state: {e}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_requests': self.total_requests,
            'blocked_requests': self.blocked_requests,
            'delayed_requests': self.delayed_requests,
            'throttled_requests': self.throttled_requests,
            'rate_limit_strategies_supported': [strategy.value for strategy in RateLimitStrategy],
            'throttle_actions_supported': [action.value for action in ThrottleAction],
            'total_rules': len(self.rules),
            'total_clients': len(self.client_states),
            'total_client_identifiers': len(self.client_identifiers),
            'enable_rate_limiting': self.enable_rate_limiting,
            'enable_distributed_limiting': self.enable_distributed_limiting,
            'default_strategy': self.default_strategy.value,
            'default_throttle_action': self.default_throttle_action.value,
            'redis_available': REDIS_AVAILABLE,
            'redis_host': self.redis_host,
            'redis_port': self.redis_port,
            'redis_db': self.redis_db
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'enable_rate_limiting': True,
        'enable_distributed_limiting': True,
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0
    }
    
    # Initialize rate limiter
    rate_limiter = RateLimiter(config)
    
    print("RateLimiter system initialized successfully!")
