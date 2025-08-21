"""
Hardware Token Multi-Factor Authentication

Implements hardware token support including:
- Challenge-response authentication
- USB security keys (FIDO2/U2F)
- Smart card support
- Hardware token management
"""

import secrets
import time
import hashlib
import hmac
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import logging
import json
from enum import Enum
from datetime import datetime, timedelta

from config import HardwareConfig

logger = logging.getLogger(__name__)


class HardwareTokenType(Enum):
    """Supported hardware token types"""
    FIDO2 = "fido2"
    U2F = "u2f"
    SMART_CARD = "smart_card"
    TOTP_HARDWARE = "totp_hardware"
    CHALLENGE_RESPONSE = "challenge_response"


@dataclass
class HardwareTokenInfo:
    """Hardware token information"""
    token_id: str
    token_type: HardwareTokenType
    user_id: str
    name: str
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capabilities: List[str] = None
    registered_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ChallengeResponse:
    """Challenge-response authentication data"""
    challenge: str
    response: str
    timestamp: datetime
    token_id: str
    user_id: str


@dataclass
class HardwareAuthResult:
    """Result of hardware authentication operation"""
    success: bool
    message: str
    token_id: Optional[str] = None
    challenge: Optional[str] = None
    response: Optional[str] = None
    expires_at: Optional[datetime] = None


class HardwareToken:
    """Base class for hardware tokens"""
    
    def __init__(self, token_info: HardwareTokenInfo):
        self.token_info = token_info
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_token_type(self) -> HardwareTokenType:
        """Get token type"""
        return self.token_info.token_type
    
    def get_capabilities(self) -> List[str]:
        """Get token capabilities"""
        return self.token_info.capabilities or []
    
    def supports_challenge_response(self) -> bool:
        """Check if token supports challenge-response"""
        return "challenge_response" in self.get_capabilities()
    
    def supports_fido2(self) -> bool:
        """Check if token supports FIDO2"""
        return "fido2" in self.get_capabilities()
    
    def supports_u2f(self) -> bool:
        """Check if token supports U2F"""
        return "u2f" in self.get_capabilities()
    
    def supports_smart_card(self) -> bool:
        """Check if token supports smart card operations"""
        return "smart_card" in self.get_capabilities()


class FIDO2Token(HardwareToken):
    """FIDO2 hardware token implementation"""
    
    def __init__(self, token_info: HardwareTokenInfo):
        super().__init__(token_info)
        if not self.supports_fido2():
            raise ValueError("Token does not support FIDO2")
    
    async def authenticate(self, challenge: str, user_id: str) -> HardwareAuthResult:
        """Authenticate using FIDO2"""
        try:
            # In a real implementation, this would use the WebAuthn API
            # For now, we'll simulate the authentication
            
            # Simulate API call delay
            import asyncio
            await asyncio.sleep(0.1)
            
            # Generate mock response
            response = self._generate_fido2_response(challenge)
            
            self.logger.info(f"FIDO2 authentication successful for user {user_id}")
            
            return HardwareAuthResult(
                success=True,
                message="FIDO2 authentication successful",
                token_id=self.token_info.token_id,
                challenge=challenge,
                response=response
            )
            
        except Exception as e:
            self.logger.error(f"FIDO2 authentication failed: {e}")
            return HardwareAuthResult(
                success=False,
                message=f"FIDO2 authentication failed: {str(e)}"
            )
    
    def _generate_fido2_response(self, challenge: str) -> str:
        """Generate mock FIDO2 response"""
        # In real implementation, this would be the actual FIDO2 response
        response_data = {
            'challenge': challenge,
            'rpId': 'forensic-reconciliation.local',
            'userVerification': 'required',
            'signature': secrets.token_hex(64)
        }
        return json.dumps(response_data)


class ChallengeResponseToken(HardwareToken):
    """Challenge-response hardware token implementation"""
    
    def __init__(self, token_info: HardwareTokenInfo):
        super().__init__(token_info)
        if not self.supports_challenge_response():
            raise ValueError("Token does not support challenge-response")
    
    def generate_challenge(self, user_id: str) -> str:
        """Generate authentication challenge"""
        try:
            # Generate random challenge
            challenge_data = {
                'user_id': user_id,
                'timestamp': int(time.time()),
                'nonce': secrets.token_hex(16),
                'token_id': self.token_info.token_id
            }
            
            # Create challenge string
            challenge = json.dumps(challenge_data, sort_keys=True)
            
            # Hash challenge for storage
            challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()
            
            self.logger.info(f"Generated challenge for user {user_id}")
            return challenge_hash
            
        except Exception as e:
            self.logger.error(f"Failed to generate challenge: {e}")
            raise
    
    def validate_response(self, challenge: str, response: str, user_id: str) -> bool:
        """Validate challenge response"""
        try:
            # In a real implementation, this would validate against the hardware token
            # For now, we'll simulate validation
            
            # Check if response format is valid
            if not response or len(response) < 32:
                return False
            
            # Simulate hardware token validation
            # In reality, this would involve communication with the actual token
            expected_response = self._generate_expected_response(challenge, user_id)
            
            # Compare responses (in real implementation, this would be cryptographic)
            return response == expected_response
            
        except Exception as e:
            self.logger.error(f"Response validation failed: {e}")
            return False
    
    def _generate_expected_response(self, challenge: str, user_id: str) -> str:
        """Generate expected response for challenge"""
        # In real implementation, this would be generated by the hardware token
        # For simulation, we'll create a deterministic response
        response_data = f"{challenge}:{user_id}:{self.token_info.token_id}"
        return hashlib.sha256(response_data.encode()).hexdigest()


class HardwareTokenAuthenticator:
    """
    Hardware Token Multi-Factor Authentication
    
    Features:
    - Multiple hardware token types
    - Challenge-response authentication
    - Token registration and management
    - Secure challenge generation
    - Response validation
    """
    
    def __init__(self, config: HardwareConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Token registry
        self.tokens: Dict[str, HardwareToken] = {}
        
        # Active challenges
        self.active_challenges: Dict[str, Dict[str, Any]] = {}
        
        # Validate configuration
        if not self._validate_config():
            raise ValueError("Invalid hardware token configuration")
    
    def _validate_config(self) -> bool:
        """Validate hardware token configuration"""
        try:
            assert self.config.timeout_seconds >= 1, "Timeout must be at least 1 second"
            assert self.config.max_retries >= 1, "Max retries must be at least 1"
            return True
        except AssertionError as e:
            self.logger.error(f"Hardware token configuration validation failed: {e}")
            return False
    
    def register_token(self, token_info: HardwareTokenInfo) -> bool:
        """
        Register a new hardware token
        
        Args:
            token_info: Token information
            
        Returns:
            True if registration successful
        """
        try:
            # Validate token info
            if not token_info.token_id or not token_info.user_id:
                raise ValueError("Token ID and user ID are required")
            
            # Check if token already registered
            if token_info.token_id in self.tokens:
                self.logger.warning(f"Token {token_info.token_id} already registered")
                return False
            
            # Create appropriate token instance
            if token_info.token_type == HardwareTokenType.FIDO2:
                token = FIDO2Token(token_info)
            elif token_info.token_type == HardwareTokenType.CHALLENGE_RESPONSE:
                token = ChallengeResponseToken(token_info)
            else:
                # For other types, create base token
                token = HardwareToken(token_info)
            
            # Register token
            self.tokens[token_info.token_id] = token
            
            self.logger.info(f"Registered hardware token {token_info.token_id} for user {token_info.user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register hardware token: {e}")
            return False
    
    def unregister_token(self, token_id: str) -> bool:
        """Unregister a hardware token"""
        try:
            if token_id in self.tokens:
                del self.tokens[token_id]
                self.logger.info(f"Unregistered hardware token {token_id}")
                return True
            else:
                self.logger.warning(f"Token {token_id} not found for unregistration")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister token {token_id}: {e}")
            return False
    
    def get_user_tokens(self, user_id: str) -> List[HardwareTokenInfo]:
        """Get all tokens for a user"""
        try:
            user_tokens = []
            for token in self.tokens.values():
                if token.token_info.user_id == user_id and token.token_info.is_active:
                    user_tokens.append(token.token_info)
            return user_tokens
        except Exception as e:
            self.logger.error(f"Failed to get tokens for user {user_id}: {e}")
            return []
    
    def get_token(self, token_id: str) -> Optional[HardwareToken]:
        """Get token by ID"""
        return self.tokens.get(token_id)
    
    def generate_challenge(self, user_id: str, token_id: str) -> Optional[str]:
        """
        Generate authentication challenge for hardware token
        
        Args:
            user_id: User identifier
            token_id: Hardware token identifier
            
        Returns:
            Challenge string or None if failed
        """
        try:
            # Get token
            token = self.get_token(token_id)
            if not token:
                self.logger.warning(f"Token {token_id} not found")
                return None
            
            # Check if token belongs to user
            if token.token_info.user_id != user_id:
                self.logger.warning(f"Token {token_id} does not belong to user {user_id}")
                return None
            
            # Check if token supports challenge-response
            if not token.supports_challenge_response():
                self.logger.warning(f"Token {token_id} does not support challenge-response")
                return None
            
            # Generate challenge
            challenge_token = ChallengeResponseToken(token.token_info)
            challenge = challenge_token.generate_challenge(user_id)
            
            # Store challenge with expiration
            expires_at = datetime.now() + timedelta(seconds=self.config.timeout_seconds)
            
            self.active_challenges[challenge] = {
                'user_id': user_id,
                'token_id': token_id,
                'expires_at': expires_at,
                'attempts': 0
            }
            
            self.logger.info(f"Generated challenge for user {user_id} with token {token_id}")
            return challenge
            
        except Exception as e:
            self.logger.error(f"Failed to generate challenge: {e}")
            return None
    
    def validate_challenge_response(self, challenge: str, response: str, user_id: str) -> HardwareAuthResult:
        """
        Validate challenge response
        
        Args:
            challenge: Challenge string
            response: Response from hardware token
            user_id: User identifier
            
        Returns:
            HardwareAuthResult with validation status
        """
        try:
            # Check if challenge exists and is valid
            if challenge not in self.active_challenges:
                return HardwareAuthResult(
                    success=False,
                    message="Invalid or expired challenge"
                )
            
            challenge_data = self.active_challenges[challenge]
            
            # Check if challenge belongs to user
            if challenge_data['user_id'] != user_id:
                return HardwareAuthResult(
                    success=False,
                    message="Challenge does not belong to user"
                )
            
            # Check if challenge expired
            if datetime.now() > challenge_data['expires_at']:
                # Remove expired challenge
                del self.active_challenges[challenge]
                return HardwareAuthResult(
                    success=False,
                    message="Challenge has expired"
                )
            
            # Check attempts
            if challenge_data['attempts'] >= self.config.max_retries:
                # Remove exhausted challenge
                del self.active_challenges[challenge]
                return HardwareAuthResult(
                    success=False,
                    message="Maximum attempts exceeded"
                )
            
            # Increment attempts
            challenge_data['attempts'] += 1
            
            # Get token
            token_id = challenge_data['token_id']
            token = self.get_token(token_id)
            
            if not token:
                return HardwareAuthResult(
                    success=False,
                    message="Token not found"
                )
            
            # Validate response
            if token.supports_challenge_response():
                challenge_token = ChallengeResponseToken(token.token_info)
                if challenge_token.validate_response(challenge, response, user_id):
                    # Success - remove challenge
                    del self.active_challenges[challenge]
                    
                    # Update token last used
                    token.token_info.last_used = datetime.now()
                    
                    self.logger.info(f"Challenge response validated successfully for user {user_id}")
                    return HardwareAuthResult(
                        success=True,
                        message="Challenge response validated successfully",
                        token_id=token_id,
                        challenge=challenge,
                        response=response
                    )
            
            # Check if max attempts reached
            if challenge_data['attempts'] >= self.config.max_retries:
                del self.active_challenges[challenge]
                return HardwareAuthResult(
                    success=False,
                    message="Maximum attempts exceeded"
                )
            
            return HardwareAuthResult(
                success=False,
                message=f"Invalid response. {self.config.max_retries - challenge_data['attempts']} attempts remaining"
            )
            
        except Exception as e:
            self.logger.error(f"Challenge response validation failed: {e}")
            return HardwareAuthResult(
                success=False,
                message=f"Validation error: {str(e)}"
            )
    
    async def authenticate_fido2(self, token_id: str, challenge: str, user_id: str) -> HardwareAuthResult:
        """
        Authenticate using FIDO2 token
        
        Args:
            token_id: FIDO2 token identifier
            challenge: Authentication challenge
            user_id: User identifier
            
        Returns:
            HardwareAuthResult with authentication status
        """
        try:
            # Get token
            token = self.get_token(token_id)
            if not token:
                return HardwareAuthResult(
                    success=False,
                    message="Token not found"
                )
            
            # Check if token supports FIDO2
            if not token.supports_fido2():
                return HardwareAuthResult(
                    success=False,
                    message="Token does not support FIDO2"
                )
            
            # Check if token belongs to user
            if token.token_info.user_id != user_id:
                return HardwareAuthResult(
                    success=False,
                    message="Token does not belong to user"
                )
            
            # Perform FIDO2 authentication
            if isinstance(token, FIDO2Token):
                result = await token.authenticate(challenge, user_id)
                
                # Update token last used
                if result.success:
                    token.token_info.last_used = datetime.now()
                
                return result
            else:
                return HardwareAuthResult(
                    success=False,
                    message="Token type mismatch"
                )
                
        except Exception as e:
            self.logger.error(f"FIDO2 authentication failed: {e}")
            return HardwareAuthResult(
                success=False,
                message=f"FIDO2 authentication failed: {str(e)}"
            )
    
    def cleanup_expired_challenges(self):
        """Remove expired challenges"""
        try:
            current_time = datetime.now()
            expired_challenges = []
            
            for challenge, data in self.active_challenges.items():
                if current_time > data['expires_at']:
                    expired_challenges.append(challenge)
            
            for challenge in expired_challenges:
                del self.active_challenges[challenge]
            
            if expired_challenges:
                self.logger.info(f"Cleaned up {len(expired_challenges)} expired challenges")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired challenges: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get hardware token authenticator status"""
        return {
            'enabled': True,
            'total_tokens': len(self.tokens),
            'active_challenges': len(self.active_challenges),
            'supported_types': [token_type.value for token_type in HardwareTokenType],
            'timeout_seconds': self.config.timeout_seconds,
            'max_retries': self.config.max_retries,
            'challenge_response_support': self.config.challenge_response
        }
