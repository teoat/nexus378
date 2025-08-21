"""
SMS-based Multi-Factor Authentication

Implements SMS code generation, validation, and delivery
"""

import secrets
import time
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
import json
import redis
from datetime import datetime, timedelta

from config import SMSConfig

logger = logging.getLogger(__name__)


@dataclass
class SMSResult:
    """Result of SMS operation"""
    success: bool
    message: str
    code: Optional[str] = None
    message_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    attempts_remaining: Optional[int] = None


class SMSProvider:
    """Base class for SMS providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement send_sms")
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.__class__.__name__


class TwilioProvider(SMSProvider):
    """Twilio SMS provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.account_sid = config.get('account_sid')
        self.auth_token = config.get('auth_token')
        self.from_number = config.get('from_number')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio configuration incomplete")
    
    async def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            # In a real implementation, this would use the Twilio API
            # For now, we'll simulate the response
            
            # Simulate API call delay
            import asyncio
            await asyncio.sleep(0.1)
            
            # Generate mock message ID
            message_id = f"tw_{int(time.time())}_{secrets.token_hex(4)}"
            
            self.logger.info(f"SMS sent via Twilio to {phone_number}: {message_id}")
            
            return {
                'success': True,
                'message_id': message_id,
                'status': 'delivered',
                'provider': 'twilio',
                'to': phone_number,
                'from': self.from_number
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS via Twilio: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'twilio'
            }
    
    def get_provider_name(self) -> str:
        return "Twilio"


class MockSMSProvider(SMSProvider):
    """Mock SMS provider for testing"""
    
    async def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Mock SMS sending for testing purposes"""
        try:
            # Simulate API call delay
            import asyncio
            await asyncio.sleep(0.05)
            
            # Generate mock message ID
            message_id = f"mock_{int(time.time())}_{secrets.token_hex(4)}"
            
            self.logger.info(f"Mock SMS sent to {phone_number}: {message_id}")
            self.logger.info(f"Message content: {message}")
            
            return {
                'success': True,
                'message_id': message_id,
                'status': 'delivered',
                'provider': 'mock',
                'to': phone_number,
                'from': '+1234567890'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send mock SMS: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'mock'
            }


class SMSAuthenticator:
    """
    SMS-based Multi-Factor Authentication
    
    Features:
    - Code generation and validation
    - Rate limiting and cooldown
    - Multiple SMS providers
    - Redis-based storage for codes
    - Attempt tracking and lockout
    """
    
    def __init__(self, config: SMSConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize SMS providers
        self.providers: Dict[str, SMSProvider] = {}
        self._initialize_providers()
        
        # Validate configuration
        if not self._validate_config():
            raise ValueError("Invalid SMS configuration")
    
    def _validate_config(self) -> bool:
        """Validate SMS configuration"""
        try:
            assert self.config.code_length >= 4, "SMS code length must be at least 4 digits"
            assert self.config.expiration_minutes >= 1, "SMS expiration must be at least 1 minute"
            assert self.config.max_attempts >= 1, "SMS max attempts must be at least 1"
            assert self.config.cooldown_seconds >= 0, "SMS cooldown must be non-negative"
            return True
        except AssertionError as e:
            self.logger.error(f"SMS configuration validation failed: {e}")
            return False
    
    def _initialize_providers(self):
        """Initialize SMS providers based on configuration"""
        try:
            if self.config.provider.lower() == 'twilio':
                # In a real implementation, these would come from environment variables
                twilio_config = {
                    'account_sid': 'mock_account_sid',
                    'auth_token': 'mock_auth_token',
                    'from_number': '+1234567890'
                }
                self.providers['twilio'] = TwilioProvider(twilio_config)
            elif self.config.provider.lower() == 'mock':
                self.providers['mock'] = MockSMSProvider({})
            else:
                # Default to mock provider
                self.logger.warning(f"Unknown SMS provider '{self.config.provider}', using mock")
                self.providers['mock'] = MockSMSProvider({})
                
        except Exception as e:
            self.logger.error(f"Failed to initialize SMS providers: {e}")
            # Fallback to mock provider
            self.providers['mock'] = MockSMSProvider({})
    
    def _generate_code(self) -> str:
        """Generate random SMS code"""
        # Generate numeric code
        code = ''.join([str(secrets.randbelow(10)) for _ in range(self.config.code_length)])
        return code
    
    def _get_redis_key(self, phone_number: str, key_type: str) -> str:
        """Generate Redis key for SMS operations"""
        # Hash phone number for security
        phone_hash = hashlib.sha256(phone_number.encode()).hexdigest()[:16]
        return f"sms:{phone_hash}:{key_type}"
    
    def _is_rate_limited(self, phone_number: str) -> bool:
        """Check if phone number is rate limited"""
        if not self.redis_client:
            return False
        
        try:
            rate_limit_key = self._get_redis_key(phone_number, "rate_limit")
            last_sent = self.redis_client.get(rate_limit_key)
            
            if last_sent:
                last_sent_time = float(last_sent)
                time_since_last = time.time() - last_sent_time
                return time_since_last < self.config.cooldown_seconds
                
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
        
        return False
    
    def _set_rate_limit(self, phone_number: str):
        """Set rate limit for phone number"""
        if not self.redis_client:
            return
        
        try:
            rate_limit_key = self._get_redis_key(phone_number, "rate_limit")
            self.redis_client.setex(
                rate_limit_key,
                self.config.cooldown_seconds,
                str(time.time())
            )
        except Exception as e:
            self.logger.error(f"Failed to set rate limit: {e}")
    
    def _store_code(self, phone_number: str, code: str, expires_at: datetime):
        """Store SMS code in Redis"""
        if not self.redis_client:
            return
        
        try:
            code_key = self._get_redis_key(phone_number, "code")
            attempts_key = self._get_redis_key(phone_number, "attempts")
            
            # Store code with expiration
            code_data = {
                'code': code,
                'expires_at': expires_at.isoformat(),
                'attempts_remaining': self.config.max_attempts
            }
            
            ttl_seconds = int((expires_at - datetime.now()).total_seconds())
            if ttl_seconds > 0:
                self.redis_client.setex(
                    code_key,
                    ttl_seconds,
                    json.dumps(code_data)
                )
                
                # Store attempts counter
                self.redis_client.setex(
                    attempts_key,
                    ttl_seconds,
                    self.config.max_attempts
                )
                
        except Exception as e:
            self.logger.error(f"Failed to store SMS code: {e}")
    
    def _get_stored_code(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored SMS code from Redis"""
        if not self.redis_client:
            return None
        
        try:
            code_key = self._get_redis_key(phone_number, "code")
            code_data = self.redis_client.get(code_key)
            
            if code_data:
                return json.loads(code_data)
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve SMS code: {e}")
        
        return None
    
    def _decrement_attempts(self, phone_number: str) -> int:
        """Decrement remaining attempts for phone number"""
        if not self.redis_client:
            return 0
        
        try:
            attempts_key = self._get_redis_key(phone_number, "attempts")
            attempts = self.redis_client.get(attempts_key)
            
            if attempts:
                remaining = int(attempts) - 1
                if remaining > 0:
                    # Update attempts counter
                    code_key = self._get_redis_key(phone_number, "code")
                    code_data = self.redis_client.get(code_key)
                    if code_data:
                        code_dict = json.loads(code_data)
                        code_dict['attempts_remaining'] = remaining
                        
                        # Get remaining TTL
                        ttl = self.redis_client.ttl(code_key)
                        if ttl > 0:
                            self.redis_client.setex(code_key, ttl, json.dumps(code_dict))
                            self.redis_client.setex(attempts_key, ttl, remaining)
                
                return remaining
                
        except Exception as e:
            self.logger.error(f"Failed to decrement attempts: {e}")
        
        return 0
    
    async def send_code(self, phone_number: str, user_id: Optional[str] = None) -> SMSResult:
        """
        Send SMS verification code
        
        Args:
            phone_number: Phone number to send code to
            user_id: Optional user identifier for logging
            
        Returns:
            SMSResult with operation status
        """
        try:
            # Check rate limiting
            if self._is_rate_limited(phone_number):
                cooldown_remaining = self._get_redis_key(phone_number, "rate_limit")
                return SMSResult(
                    success=False,
                    message=f"Rate limited. Please wait {self.config.cooldown_seconds} seconds before requesting another code."
                )
            
            # Generate code
            code = self._generate_code()
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(minutes=self.config.expiration_minutes)
            
            # Store code
            self._store_code(phone_number, code, expires_at)
            
            # Set rate limit
            self._set_rate_limit(phone_number)
            
            # Format message
            message = self.config.message_template.format(code=code)
            
            # Send via provider
            provider_name = list(self.providers.keys())[0]  # Use first available provider
            provider = self.providers[provider_name]
            
            send_result = await provider.send_sms(phone_number, message)
            
            if send_result['success']:
                self.logger.info(f"SMS code sent to {phone_number} for user {user_id}")
                return SMSResult(
                    success=True,
                    message="SMS code sent successfully",
                    code=code,  # Only return code in development/testing
                    message_id=send_result.get('message_id'),
                    expires_at=expires_at,
                    attempts_remaining=self.config.max_attempts
                )
            else:
                self.logger.error(f"Failed to send SMS: {send_result.get('error')}")
                return SMSResult(
                    success=False,
                    message=f"Failed to send SMS: {send_result.get('error')}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to send SMS code to {phone_number}: {e}")
            return SMSResult(
                success=False,
                message=f"Internal error: {str(e)}"
            )
    
    def validate_code(self, phone_number: str, code: str) -> SMSResult:
        """
        Validate SMS verification code
        
        Args:
            phone_number: Phone number the code was sent to
            code: Code to validate
            
        Returns:
            SMSResult with validation status
        """
        try:
            # Get stored code
            stored_data = self._get_stored_code(phone_number)
            
            if not stored_data:
                return SMSResult(
                    success=False,
                    message="No active code found. Please request a new code."
                )
            
            # Check expiration
            expires_at = datetime.fromisoformat(stored_data['expires_at'])
            if datetime.now() > expires_at:
                return SMSResult(
                    success=False,
                    message="Code has expired. Please request a new code."
                )
            
            # Check attempts
            attempts_remaining = stored_data['attempts_remaining']
            if attempts_remaining <= 0:
                return SMSResult(
                    success=False,
                    message="Maximum attempts exceeded. Please request a new code."
                )
            
            # Validate code
            if code == stored_data['code']:
                # Success - remove stored code
                if self.redis_client:
                    code_key = self._get_redis_key(phone_number, "code")
                    attempts_key = self._get_redis_key(phone_number, "attempts")
                    self.redis_client.delete(code_key, attempts_key)
                
                self.logger.info(f"SMS code validated successfully for {phone_number}")
                return SMSResult(
                    success=True,
                    message="Code validated successfully"
                )
            else:
                # Decrement attempts
                remaining = self._decrement_attempts(phone_number)
                
                if remaining > 0:
                    return SMSResult(
                        success=False,
                        message=f"Invalid code. {remaining} attempts remaining."
                    )
                else:
                    return SMSResult(
                        success=False,
                        message="Maximum attempts exceeded. Please request a new code."
                    )
                    
        except Exception as e:
            self.logger.error(f"SMS code validation error for {phone_number}: {e}")
            return SMSResult(
                success=False,
                message=f"Validation error: {str(e)}"
            )
    
    def get_code_status(self, phone_number: str) -> Dict[str, Any]:
        """Get status of SMS code for phone number"""
        try:
            stored_data = self._get_stored_code(phone_number)
            
            if not stored_data:
                return {
                    'has_active_code': False,
                    'expires_at': None,
                    'attempts_remaining': 0
                }
            
            expires_at = datetime.fromisoformat(stored_data['expires_at'])
            attempts_remaining = stored_data['attempts_remaining']
            
            return {
                'has_active_code': True,
                'expires_at': expires_at,
                'attempts_remaining': attempts_remaining,
                'is_expired': datetime.now() > expires_at,
                'is_locked': attempts_remaining <= 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get code status for {phone_number}: {e}")
            return {
                'has_active_code': False,
                'expires_at': None,
                'attempts_remaining': 0,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get SMS authenticator status"""
        return {
            'enabled': True,
            'provider': self.config.provider,
            'code_length': self.config.code_length,
            'expiration_minutes': self.config.expiration_minutes,
            'max_attempts': self.config.max_attempts,
            'cooldown_seconds': self.config.cooldown_seconds,
            'available_providers': list(self.providers.keys()),
            'redis_available': self.redis_client is not None
        }
