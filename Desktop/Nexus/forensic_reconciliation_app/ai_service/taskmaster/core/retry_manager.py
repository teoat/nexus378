"""
Retry Manager - Job Retry and Error Handling Engine

This module implements the RetryManager class that handles job retries,
error recovery, and failure analysis for the Taskmaster system.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import traceback

from ..models.job import Job, JobStatus, JobRetryPolicy


class RetryStrategy(Enum):
    """Retry strategy types."""
    IMMEDIATE = "immediate"           # Retry immediately
    FIXED_DELAY = "fixed_delay"      # Retry after fixed delay
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # Exponential backoff
    LINEAR_BACKOFF = "linear_backoff"  # Linear backoff
    RANDOM_BACKOFF = "random_backoff"  # Random backoff
    CUSTOM = "custom"                 # Custom retry logic


class ErrorCategory(Enum):
    """Error categories for classification."""
    TRANSIENT = "transient"          # Temporary error, retry likely to succeed
    PERMANENT = "permanent"          # Permanent error, retry unlikely to succeed
    RESOURCE = "resource"            # Resource-related error
    NETWORK = "network"              # Network-related error
    TIMEOUT = "timeout"              # Timeout error
    DEPENDENCY = "dependency"        # Dependency-related error
    VALIDATION = "validation"        # Validation error
    SYSTEM = "system"                # System-level error
    UNKNOWN = "unknown"              # Unknown error type


class RetryDecision(Enum):
    """Retry decision types."""
    RETRY = "retry"                  # Should retry
    FAIL = "fail"                    # Should fail permanently
    WAIT = "wait"                    # Should wait before retry
    SKIP = "skip"                    # Should skip retry


@dataclass
class ErrorInfo:
    """Error information for analysis."""
    
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    category: ErrorCategory = ErrorCategory.UNKNOWN
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class RetryAttempt:
    """Retry attempt information."""
    
    attempt_number: int
    timestamp: datetime
    error_info: ErrorInfo
    delay: timedelta
    strategy: RetryStrategy
    success: bool = False
    result: Optional[Any] = None
    duration: Optional[timedelta] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class RetryMetrics:
    """Retry performance metrics."""
    
    total_retries: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    average_retry_delay: float = 0.0
    average_retry_duration: float = 0.0
    retry_success_rate: float = 0.0
    error_distribution: Dict[str, int] = field(default_factory=dict)
    
    def update_success_rate(self):
        """Update retry success rate."""
        if self.total_retries > 0:
            self.retry_success_rate = self.successful_retries / self.total_retries
    
    def update_average_retry_delay(self, new_delay: float):
        """Update average retry delay."""
        self.average_retry_delay = (
            (self.average_retry_delay * self.total_retries + new_delay) /
            (self.total_retries + 1)
        )
    
    def update_average_retry_duration(self, new_duration: float):
        """Update average retry duration."""
        self.average_retry_duration = (
            (self.average_retry_duration * self.total_retries + new_duration) /
            (self.total_retries + 1)
        )


class RetryManager:
    """
    Retry management engine for the Taskmaster system.
    
    The RetryManager is responsible for:
    - Managing job retry policies and strategies
    - Analyzing errors and determining retry decisions
    - Implementing various retry strategies
    - Tracking retry performance and metrics
    - Providing error recovery recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the RetryManager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.default_max_retries = config.get('default_max_retries', 3)
        self.default_retry_delay = timedelta(minutes=config.get('default_retry_delay_minutes', 5))
        self.max_retry_delay = timedelta(hours=config.get('max_retry_delay_hours', 24))
        self.enable_error_analysis = config.get('enable_error_analysis', True)
        self.error_analysis_threshold = config.get('error_analysis_threshold', 10)
        
        # Internal state
        self.retry_policies: Dict[str, JobRetryPolicy] = {}
        self.retry_attempts: Dict[str, List[RetryAttempt]] = defaultdict(list)
        self.error_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.retry_metrics = RetryMetrics()
        
        # Error analysis
        self.error_history: List[ErrorInfo] = []
        self.error_classifiers: Dict[str, Callable] = {}
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("RetryManager initialized successfully")
    
    async def start(self):
        """Start the RetryManager."""
        self.logger.info("Starting RetryManager...")
        
        # Initialize error classifiers
        await self._initialize_error_classifiers()
        
        # Start background tasks
        asyncio.create_task(self._analyze_error_patterns())
        asyncio.create_task(self._cleanup_old_retry_data())
        asyncio.create_task(self._update_retry_metrics())
        
        self.logger.info("RetryManager started successfully")
    
    async def stop(self):
        """Stop the RetryManager."""
        self.logger.info("Stopping RetryManager...")
        self.logger.info("RetryManager stopped")
    
    async def set_retry_policy(self, job_id: str, policy: JobRetryPolicy):
        """Set retry policy for a specific job."""
        self.retry_policies[job_id] = policy
        self.logger.info(f"Set retry policy for job {job_id}")
    
    async def get_retry_policy(self, job_id: str) -> JobRetryPolicy:
        """Get retry policy for a specific job."""
        return self.retry_policies.get(job_id, JobRetryPolicy())
    
    async def should_retry(self, job: Job, error: Exception) -> RetryDecision:
        """Determine if a job should be retried."""
        try:
            policy = await self.get_retry_policy(job.id)
            
            # Check if max retries exceeded
            if job.retry_count >= policy.max_retries:
                return RetryDecision.FAIL
            
            # Analyze error
            error_info = await self._analyze_error(error, job)
            
            # Check if error is retryable
            if not self._is_error_retryable(error_info):
                return RetryDecision.FAIL
            
            # Check retry policy conditions
            if not self._meets_retry_conditions(job, error_info, policy):
                return RetryDecision.FAIL
            
            # Determine retry strategy
            strategy = self._determine_retry_strategy(job, error_info, policy)
            
            if strategy == RetryStrategy.IMMEDIATE:
                return RetryDecision.RETRY
            elif strategy in [RetryStrategy.FIXED_DELAY, RetryStrategy.EXPONENTIAL_BACKOFF]:
                return RetryDecision.WAIT
            
            return RetryDecision.RETRY
            
        except Exception as e:
            self.logger.error(f"Error determining retry decision: {e}")
            return RetryDecision.FAIL
    
    async def calculate_retry_delay(self, job: Job, error: Exception) -> timedelta:
        """Calculate delay before next retry."""
        try:
            policy = await self.get_retry_policy(job.id)
            strategy = self._determine_retry_strategy(job, await self._analyze_error(error, job), policy)
            
            if strategy == RetryStrategy.IMMEDIATE:
                return timedelta(0)
            
            elif strategy == RetryStrategy.FIXED_DELAY:
                return policy.retry_delay
            
            elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                delay = policy.retry_delay * (policy.backoff_multiplier ** job.retry_count)
                return min(delay, policy.max_retry_delay)
            
            elif strategy == RetryStrategy.LINEAR_BACKOFF:
                delay = policy.retry_delay * (1 + job.retry_count)
                return min(delay, policy.max_retry_delay)
            
            elif strategy == RetryStrategy.RANDOM_BACKOFF:
                import random
                base_delay = policy.retry_delay.total_seconds()
                jitter = random.uniform(0.5, 1.5)
                delay = base_delay * jitter * (policy.backoff_multiplier ** job.retry_count)
                return min(timedelta(seconds=delay), policy.max_retry_delay)
            
            else:
                return policy.retry_delay
            
        except Exception as e:
            self.logger.error(f"Error calculating retry delay: {e}")
            return self.default_retry_delay
    
    async def record_retry_attempt(self, job: Job, error: Exception, 
                                 success: bool, result: Any = None, duration: timedelta = None):
        """Record a retry attempt."""
        try:
            error_info = await self._analyze_error(error, job)
            policy = await self.get_retry_policy(job.id)
            strategy = self._determine_retry_strategy(job, error_info, policy)
            
            # Calculate delay
            delay = await self.calculate_retry_delay(job, error)
            
            # Create retry attempt record
            attempt = RetryAttempt(
                attempt_number=job.retry_count,
                timestamp=datetime.utcnow(),
                error_info=error_info,
                delay=delay,
                strategy=strategy,
                success=success,
                result=result,
                duration=duration
            )
            
            # Store retry attempt
            self.retry_attempts[job.id].append(attempt)
            
            # Update metrics
            self.retry_metrics.total_retries += 1
            if success:
                self.retry_metrics.successful_retries += 1
            else:
                self.retry_metrics.failed_retries += 1
            
            # Update error distribution
            error_type = error_info.error_type
            self.retry_metrics.error_distribution[error_type] = \
                self.retry_metrics.error_distribution.get(error_type, 0) + 1
            
            self.logger.info(f"Recorded retry attempt {job.retry_count} for job {job.id}")
            
        except Exception as e:
            self.logger.error(f"Error recording retry attempt: {e}")
    
    async def get_retry_history(self, job_id: str) -> List[RetryAttempt]:
        """Get retry history for a specific job."""
        return self.retry_attempts.get(job_id, [])
    
    async def get_retry_metrics(self) -> RetryMetrics:
        """Get retry performance metrics."""
        return self.retry_metrics
    
    async def analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns for insights."""
        try:
            if not self.error_history:
                return {}
            
            # Group errors by type
            error_types = defaultdict(list)
            for error in self.error_history:
                error_types[error.error_type].append(error)
            
            # Analyze patterns
            patterns = {}
            for error_type, errors in error_types.items():
                if len(errors) >= self.error_analysis_threshold:
                    pattern = self._analyze_error_pattern(error_type, errors)
                    patterns[error_type] = pattern
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing error patterns: {e}")
            return {}
    
    async def get_error_recovery_recommendations(self, error: Exception, job: Job) -> List[str]:
        """Get recommendations for error recovery."""
        try:
            error_info = await self._analyze_error(error, job)
            recommendations = []
            
            # Category-based recommendations
            if error_info.category == ErrorCategory.TRANSIENT:
                recommendations.append("This appears to be a temporary error. Retry is recommended.")
                recommendations.append("Consider increasing retry delay for better success rate.")
            
            elif error_info.category == ErrorCategory.RESOURCE:
                recommendations.append("Resource-related error detected. Check system resources.")
                recommendations.append("Consider scaling up resources or reducing load.")
            
            elif error_info.category == ErrorCategory.NETWORK:
                recommendations.append("Network-related error detected. Check network connectivity.")
                recommendations.append("Consider implementing circuit breaker pattern.")
            
            elif error_info.category == ErrorCategory.TIMEOUT:
                recommendations.append("Timeout error detected. Consider increasing timeout values.")
                recommendations.append("Check if system is under heavy load.")
            
            elif error_info.category == ErrorCategory.PERMANENT:
                recommendations.append("Permanent error detected. Retry is unlikely to succeed.")
                recommendations.append("Investigate root cause and fix underlying issue.")
            
            # Strategy-based recommendations
            if job.retry_count > 0:
                recommendations.append(f"Job has been retried {job.retry_count} times.")
                if job.retry_count >= 2:
                    recommendations.append("Consider exponential backoff strategy.")
            
            # Historical recommendations
            if error_info.error_type in self.error_patterns:
                pattern = self.error_patterns[error_info.error_type]
                if pattern.get('retry_success_rate', 0) < 0.3:
                    recommendations.append("Historical data shows low retry success rate for this error type.")
                    recommendations.append("Consider implementing alternative error handling strategies.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recovery recommendations: {e}")
            return ["Unable to provide specific recommendations due to error analysis failure."]
    
    async def _analyze_error(self, error: Exception, job: Job) -> ErrorInfo:
        """Analyze an error for classification and context."""
        try:
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
            
            # Classify error
            category = await self._classify_error(error, job)
            
            # Determine severity
            severity = self._determine_error_severity(error, category)
            
            # Create error info
            error_info = ErrorInfo(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                category=category,
                severity=severity,
                context={
                    'job_id': job.id,
                    'job_type': job.job_type.value,
                    'retry_count': job.retry_count,
                    'assigned_agent': job.assigned_agent_id
                }
            )
            
            # Store in history
            self.error_history.append(error_info)
            
            return error_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing error: {e}")
            return ErrorInfo(
                error_type="AnalysisError",
                error_message="Failed to analyze error",
                category=ErrorCategory.UNKNOWN
            )
    
    async def _classify_error(self, error: Exception, job: Job) -> ErrorCategory:
        """Classify an error into a category."""
        try:
            error_type = type(error).__name__
            error_message = str(error).lower()
            
            # Use custom classifiers if available
            if error_type in self.error_classifiers:
                classifier = self.error_classifiers[error_type]
                try:
                    return classifier(error, job)
                except Exception:
                    pass
            
            # Default classification logic
            if any(word in error_message for word in ['timeout', 'timed out', 'deadline']):
                return ErrorCategory.TIMEOUT
            
            elif any(word in error_message for word in ['network', 'connection', 'socket']):
                return ErrorCategory.NETWORK
            
            elif any(word in error_message for word in ['memory', 'disk', 'resource', 'quota']):
                return ErrorCategory.RESOURCE
            
            elif any(word in error_message for word in ['validation', 'invalid', 'malformed']):
                return ErrorCategory.VALIDATION
            
            elif any(word in error_message for word in ['dependency', 'missing', 'not found']):
                return ErrorCategory.DEPENDENCY
            
            elif any(word in error_message for word in ['system', 'internal', 'fatal']):
                return ErrorCategory.SYSTEM
            
            # Check for transient vs permanent indicators
            if any(word in error_message for word in ['temporary', 'retry', 'busy', 'overloaded']):
                return ErrorCategory.TRANSIENT
            
            elif any(word in error_message for word in ['permanent', 'fatal', 'unrecoverable']):
                return ErrorCategory.PERMANENT
            
            return ErrorCategory.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Error classifying error: {e}")
            return ErrorCategory.UNKNOWN
    
    def _determine_error_severity(self, error: Exception, category: ErrorCategory) -> str:
        """Determine error severity level."""
        if category == ErrorCategory.PERMANENT:
            return "high"
        elif category == ErrorCategory.SYSTEM:
            return "high"
        elif category == ErrorCategory.RESOURCE:
            return "medium"
        elif category == ErrorCategory.TRANSIENT:
            return "low"
        else:
            return "medium"
    
    def _is_error_retryable(self, error_info: ErrorInfo) -> bool:
        """Check if an error is retryable."""
        non_retryable_categories = [ErrorCategory.PERMANENT, ErrorCategory.VALIDATION]
        return error_info.category not in non_retryable_categories
    
    def _meets_retry_conditions(self, job: Job, error_info: ErrorInfo, policy: JobRetryPolicy) -> bool:
        """Check if job meets retry policy conditions."""
        # Check if error type is in retry-on-exceptions list
        if policy.retry_on_exceptions:
            if error_info.error_type not in policy.retry_on_exceptions:
                return False
        
        # Check if error status is in retry-on-statuses list
        if policy.retry_on_statuses:
            if job.status not in policy.retry_on_statuses:
                return False
        
        return True
    
    def _determine_retry_strategy(self, job: Job, error_info: ErrorInfo, policy: JobRetryPolicy) -> RetryStrategy:
        """Determine the appropriate retry strategy."""
        # Use policy-specific strategy if available
        if hasattr(policy, 'strategy'):
            return policy.strategy
        
        # Default strategy based on error category
        if error_info.category == ErrorCategory.TRANSIENT:
            return RetryStrategy.EXPONENTIAL_BACKOFF
        elif error_info.category == ErrorCategory.RESOURCE:
            return RetryStrategy.FIXED_DELAY
        elif error_info.category == ErrorCategory.NETWORK:
            return RetryStrategy.EXPONENTIAL_BACKOFF
        elif error_info.category == ErrorCategory.TIMEOUT:
            return RetryStrategy.LINEAR_BACKOFF
        else:
            return RetryStrategy.FIXED_DELAY
    
    async def _initialize_error_classifiers(self):
        """Initialize custom error classifiers."""
        try:
            # Example custom classifiers
            self.error_classifiers = {
                'ConnectionError': lambda e, j: ErrorCategory.NETWORK,
                'TimeoutError': lambda e, j: ErrorCategory.TIMEOUT,
                'MemoryError': lambda e, j: ErrorCategory.RESOURCE,
                'ValueError': lambda e, j: ErrorCategory.VALIDATION,
                'FileNotFoundError': lambda e, j: ErrorCategory.DEPENDENCY,
                'PermissionError': lambda e, j: ErrorCategory.SYSTEM
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing error classifiers: {e}")
    
    async def _analyze_error_patterns(self):
        """Analyze error patterns for insights."""
        while True:
            try:
                if len(self.error_history) >= self.error_analysis_threshold:
                    patterns = await self.analyze_error_patterns()
                    
                    # Update error patterns
                    for error_type, pattern in patterns.items():
                        self.error_patterns[error_type] = pattern
                    
                    if patterns:
                        self.logger.info(f"Updated error patterns for {len(patterns)} error types")
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error analyzing error patterns: {e}")
                await asyncio.sleep(300)
    
    def _analyze_error_pattern(self, error_type: str, errors: List[ErrorInfo]) -> Dict[str, Any]:
        """Analyze pattern for a specific error type."""
        try:
            # Calculate retry success rate
            total_retries = len(errors)
            successful_retries = sum(1 for e in errors if e.severity == "low")
            retry_success_rate = successful_retries / total_retries if total_retries > 0 else 0
            
            # Calculate frequency
            frequency = len(errors) / max(1, (datetime.utcnow() - errors[0].timestamp).total_seconds() / 3600)
            
            # Determine trend
            recent_errors = [e for e in errors if (datetime.utcnow() - e.timestamp).total_seconds() < 3600]
            recent_frequency = len(recent_errors)
            
            if recent_frequency > frequency:
                trend = "increasing"
            elif recent_frequency < frequency:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                'total_occurrences': total_retries,
                'retry_success_rate': retry_success_rate,
                'frequency_per_hour': frequency,
                'recent_frequency': recent_frequency,
                'trend': trend,
                'most_common_category': max(set(e.category.value for e in errors), 
                                         key=lambda x: sum(1 for e in errors if e.category.value == x)),
                'average_severity': sum(1 for e in errors if e.severity == "high") / total_retries
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing pattern for {error_type}: {e}")
            return {}
    
    async def _cleanup_old_retry_data(self):
        """Clean up old retry data."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=7)
                
                # Clean up old retry attempts
                for job_id in list(self.retry_attempts.keys()):
                    self.retry_attempts[job_id] = [
                        attempt for attempt in self.retry_attempts[job_id]
                        if attempt.timestamp > cutoff_time
                    ]
                    
                    # Remove empty job entries
                    if not self.retry_attempts[job_id]:
                        del self.retry_attempts[job_id]
                
                # Clean up old error history
                self.error_history = [
                    error for error in self.error_history
                    if error.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old retry data: {e}")
                await asyncio.sleep(3600)
    
    async def _update_retry_metrics(self):
        """Update retry performance metrics."""
        while True:
            try:
                # Update success rate
                self.retry_metrics.update_success_rate()
                
                # Calculate average delays and durations
                total_delays = 0
                total_durations = 0
                count = 0
                
                for attempts in self.retry_attempts.values():
                    for attempt in attempts:
                        total_delays += attempt.delay.total_seconds()
                        if attempt.duration:
                            total_durations += attempt.duration.total_seconds()
                        count += 1
                
                if count > 0:
                    self.retry_metrics.update_average_retry_delay(total_delays / count)
                    if total_durations > 0:
                        self.retry_metrics.update_average_retry_duration(total_durations / count)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating retry metrics: {e}")
                await asyncio.sleep(300)


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'default_max_retries': 3,
        'default_retry_delay_minutes': 5,
        'max_retry_delay_hours': 24,
        'enable_error_analysis': True,
        'error_analysis_threshold': 10
    }
    
    # Initialize retry manager
    manager = RetryManager(config)
    
    print("RetryManager system initialized successfully!")
