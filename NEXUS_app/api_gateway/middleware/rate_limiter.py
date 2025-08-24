Rate Limiting and Throttling System

This module implements the RateLimiter class that provides
comprehensive rate limiting and throttling capabilities for the API gateway.

import asyncio
import json
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Redis libraries for distributed rate limiting
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType

class RateLimitStrategy(Enum):

    FIXED_WINDOW = "fixed_window"                           # Fixed time window
    SLIDING_WINDOW = "sliding_window"                        # Sliding time window
    TOKEN_BUCKET = "token_bucket"                            # Token bucket algorithm
    LEAKY_BUCKET = "leaky_bucket"                            # Leaky bucket algorithm
    ADAPTIVE = "adaptive"                                     # Adaptive rate limiting

class ThrottleAction(Enum):

    BLOCK = "block"                                           # Block the request
    DELAY = "delay"                                           # Delay the request
    QUEUE = "queue"                                           # Queue the request
    REDUCE_PRIORITY = "reduce_priority"                       # Reduce request priority
    NOTIFY = "notify"                                         # Send notification

@dataclass
class RateLimitRule:

        self.logger.info("RateLimiter initialized successfully")
    
    def _check_library_availability(self):

    "Redis not available - distributed rate limiting will be disabled",
)
            self.enable_distributed_limiting = False
    
    def _initialize_default_rules(self):

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

        self.logger.info("Starting RateLimiter...")
        
        # Initialize Redis connection
        if self.enable_distributed_limiting:
            await self._initialize_redis_connection()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_states())
        asyncio.create_task(self._update_performance_metrics())
        
        self.logger.info("RateLimiter started successfully")
    
    async def stop(self):

        self.logger.info("Stopping RateLimiter...")
        
        # Close Redis connection
        if self.redis_connection:
            self.redis_connection.close()
        
        self.logger.info("RateLimiter stopped")
    
    async def _initialize_redis_connection(self):

                    "Redis connection established for distributed rate limiting"
                )
                
        except Exception as e:
            self.logger.warning(f"Could not establish Redis connection: {e}")
            self.enable_distributed_limiting = False
    
    def add_rule(self, rule: RateLimitRule):

                raise ValueError(f"Rule already exists: {rule.rule_id}")
            
            # Store rule
            self.rules[rule.rule_id] = rule
            
            self.logger.info(
                f"Rate limiting rule added successfully: {rule.rule_id} - {rule.name}"
            )
            
        except Exception as e:
            self.logger.error(f"Error adding rate limiting rule: {e}")
            raise
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]):

                raise ValueError(f"Rule not found: {rule_id}")
            
            rule = self.rules[rule_id]
            
            # Update fields
            for field, value in updates.items()
                if hasattr(rule, field)
                    setattr(rule, field, value)
            
            self.logger.info(f"Rate limiting rule updated successfully: {rule_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating rate limiting rule: {e}")
            raise
    
    def remove_rule(self, rule_id: str):

                raise ValueError(f"Rule not found: {rule_id}")
            
            # Remove rule
            del self.rules[rule_id]
            
            # Clean up client states for this rule
            for client_states in self.client_states.values()
                if rule_id in client_states:
                    del client_states[rule_id]
            
            self.logger.info(f"Rate limiting rule removed successfully: {rule_id}")
            
        except Exception as e:
            self.logger.error(f"Error removing rate limiting rule: {e}")
            raise
    
    async def check_rate_limit(
        self,
        client_info: Dict[str, Any],
        endpoint: str
    ):

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

            self.logger.error(f"Error identifying client: {e}")
            return str(uuid.uuid4())
    
    def _find_applicable_rule(self, endpoint: str) -> Optional[RateLimitRule]:

            self.logger.error(f"Error finding applicable rule: {e}")
            return None
    
    def _endpoint_matches_pattern(self, endpoint: str, pattern: str) -> bool:

            if pattern == "*":
                return True
            
            # Simple pattern matching (can be enhanced with regex)
            if pattern.endswith("/*")
                base_pattern = pattern[:-2]
                return endpoint.startswith(base_pattern)
            
            return endpoint == pattern
            
        except Exception as e:
            self.logger.error(f"Error matching endpoint pattern: {e}")
            return False
    
    async def _check_fixed_window(
        self,
        client_id: str,
        rule: RateLimitRule
    ):

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
    
    async def _check_sliding_window(
        self,
        client_id: str,
        rule: RateLimitRule
    ):

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
    
    async def _check_token_bucket(
        self,
        client_id: str,
        rule: RateLimitRule
    ):

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
    
    async def _check_leaky_bucket(
        self,
        client_id: str,
        rule: RateLimitRule
    ):

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
    
    async def _check_adaptive(
        self,
        client_id: str,
        rule: RateLimitRule
    ):

            self.logger.error(f"Error in adaptive check: {e}")
            raise
    
    async def _cleanup_expired_states(self):

                    self.logger.info(f"Cleaned up {len(expired_clients)} expired client states")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up expired states: {e}")
                await asyncio.sleep(3600)
    
    async def _update_performance_metrics(self):

                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)
    
    def get_rule(self, rule_id: str) -> Optional[RateLimitRule]:

            self.logger.error(f"Error getting rule: {e}")
            return None
    
    def get_client_state(self, client_id: str, rule_id: str) -> Optional[RateLimitState]:

            self.logger.error(f"Error getting client state: {e}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:

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
