"""
Hardware Token Authentication Service
Supports YubiKey and other hardware security tokens
"""

import logging
import asyncio
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HardwareTokenType(Enum):
    """Supported hardware token types"""
    YUBIKEY = "yubikey"
    FIDO2 = "fido2"
    TOTP_HARDWARE = "totp_hardware"
    SMART_CARD = "smart_card"


class HardwareTokenStatus(Enum):
    """Hardware token verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class HardwareToken:
    """Hardware token information"""
    id: str
    user_id: str
    token_type: HardwareTokenType
    serial_number: str
    public_id: str
    registered_at: datetime
    last_used: Optional[datetime]
    status: str  # active, revoked, expired


@dataclass
class HardwareChallenge:
    """Hardware token challenge for verification"""
    id: str
    user_id: str
    token_id: str
    challenge_data: str
    created_at: datetime
    expires_at: datetime
    status: HardwareTokenStatus
    attempts: int
    max_attempts: int = 3


class HardwareTokenService:
    """Hardware token authentication service implementation"""
    
    def __init__(self):
        self.registered_tokens: Dict[str, HardwareToken] = {}
        self.active_challenges: Dict[str, HardwareChallenge] = {}
        self.hardware_config = {
            "challenge_timeout": 300,  # 5 minutes
            "max_attempts": 3,
            "supported_types": [
                HardwareTokenType.YUBIKEY,
                HardwareTokenType.FIDO2,
                HardwareTokenType.TOTP_HARDWARE
            ]
        }
        
        # Mock hardware token providers (replace with actual implementations)
        self.token_providers = {
            HardwareTokenType.YUBIKEY: MockYubiKeyProvider(),
            HardwareTokenType.FIDO2: MockFIDO2Provider(),
            HardwareTokenType.TOTP_HARDWARE: MockTOTPHardwareProvider()
        }
        
        logger.info("Hardware token service initialized")
    
    async def register_hardware_token(self, user_id: str, token_type: HardwareTokenType, 
                                    serial_number: str, public_id: str) -> Optional[str]:
        """Register a new hardware token for user"""
        try:
            # Validate token type
            if token_type not in self.hardware_config["supported_types"]:
                logger.warning(f"Unsupported hardware token type: {token_type}")
                return None
            
            # Check if token already registered
            for token in self.registered_tokens.values():
                if token.serial_number == serial_number:
                    logger.warning(f"Hardware token {serial_number} already registered")
                    return None
            
            # Create token record
            token = HardwareToken(
                id=self._generate_token_id(),
                user_id=user_id,
                token_type=token_type,
                serial_number=serial_number,
                public_id=public_id,
                registered_at=datetime.now(),
                last_used=None,
                status="active"
            )
            
            # Store token
            self.registered_tokens[token.id] = token
            
            logger.info(f"Registered {token_type.value} token {serial_number} for user {user_id}")
            return token.id
            
        except Exception as e:
            logger.error(f"Failed to register hardware token: {e}")
            return None
    
    async def generate_challenge(self, user_id: str, token_id: str) -> Optional[str]:
        """Generate hardware token challenge for verification"""
        try:
            # Get token
            token = self.registered_tokens.get(token_id)
            if not token or token.user_id != user_id:
                logger.warning(f"Token {token_id} not found or not owned by user {user_id}")
                return None
            
            # Check if token is active
            if token.status != "active":
                logger.warning(f"Token {token_id} is not active (status: {token.status})")
                return None
            
            # Generate challenge based on token type
            challenge_data = await self._generate_challenge_data(token)
            if not challenge_data:
                logger.error(f"Failed to generate challenge for token {token_id}")
                return None
            
            # Create challenge
            challenge = HardwareChallenge(
                id=self._generate_challenge_id(),
                user_id=user_id,
                token_id=token_id,
                challenge_data=challenge_data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.hardware_config["challenge_timeout"]),
                status=HardwareTokenStatus.PENDING,
                attempts=0,
                max_attempts=self.hardware_config["max_attempts"]
            )
            
            # Store challenge
            self.active_challenges[challenge.id] = challenge
            
            logger.info(f"Generated challenge for hardware token {token_id}")
            return challenge.id
            
        except Exception as e:
            logger.error(f"Failed to generate hardware token challenge: {e}")
            return None
    
    async def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """Verify hardware token challenge response"""
        try:
            # Get challenge
            challenge = self.active_challenges.get(challenge_id)
            if not challenge or challenge.user_id != user_id:
                logger.warning(f"Challenge {challenge_id} not found or not owned by user {user_id}")
                return False
            
            # Check if expired
            if datetime.now() > challenge.expires_at:
                challenge.status = HardwareTokenStatus.EXPIRED
                logger.warning(f"Hardware token challenge expired")
                return False
            
            # Check attempts
            if challenge.attempts >= challenge.max_attempts:
                challenge.status = HardwareTokenStatus.FAILED
                logger.warning(f"Maximum attempts exceeded for hardware token challenge")
                return False
            
            # Increment attempts
            challenge.attempts += 1
            
            # Get token
            token = self.registered_tokens.get(challenge.token_id)
            if not token:
                logger.error(f"Token {challenge.token_id} not found")
                return False
            
            # Verify response based on token type
            is_valid = await self._verify_token_response(token, challenge, response)
            
            if is_valid:
                challenge.status = HardwareTokenStatus.VERIFIED
                token.last_used = datetime.now()
                logger.info(f"Hardware token challenge verified for user {user_id}")
                return True
            else:
                if challenge.attempts >= challenge.max_attempts:
                    challenge.status = HardwareTokenStatus.FAILED
                    return False
                logger.warning(f"Hardware token challenge verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify hardware token response: {e}")
            return False
    
    async def _generate_challenge_data(self, token: HardwareToken) -> Optional[str]:
        """Generate challenge data based on token type"""
        try:
            provider = self.token_providers.get(token.token_type)
            if not provider:
                logger.error(f"No provider found for token type {token.token_type}")
                return None
            
            return await provider.generate_challenge(token)
            
        except Exception as e:
            logger.error(f"Failed to generate challenge data: {e}")
            return None
    
    async def _verify_token_response(self, token: HardwareToken, challenge: HardwareChallenge, 
                                   response: str) -> bool:
        """Verify response based on token type"""
        try:
            provider = self.token_providers.get(token.token_type)
            if not provider:
                logger.error(f"No provider found for token type {token.token_type}")
                return False
            
            return await provider.verify_response(token, challenge, response)
            
        except Exception as e:
            logger.error(f"Failed to verify token response: {e}")
            return False
    
    def _generate_token_id(self) -> str:
        """Generate unique token ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_user_tokens(self, user_id: str) -> List[HardwareToken]:
        """Get all hardware tokens for user"""
        return [token for token in self.registered_tokens.values() if token.user_id == user_id]
    
    def revoke_hardware_token(self, token_id: str) -> bool:
        """Revoke hardware token"""
        try:
            if token_id in self.registered_tokens:
                self.registered_tokens[token_id].status = "revoked"
                logger.info(f"Hardware token {token_id} revoked")
                return True
            else:
                logger.warning(f"Hardware token {token_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to revoke hardware token: {e}")
            return False
    
    async def cleanup_expired_challenges(self):
        """Remove expired challenges"""
        try:
            current_time = datetime.now()
            expired_ids = [
                challenge_id for challenge_id, challenge in self.active_challenges.items()
                if current_time > challenge.expires_at
            ]
            
            for challenge_id in expired_ids:
                del self.active_challenges[challenge_id]
            
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired hardware token challenges")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired challenges: {e}")
    
    def get_system_status(self) -> Dict[str, any]:
        """Get hardware token service status"""
        return {
            "total_tokens": len(self.registered_tokens),
            "active_tokens": len([t for t in self.registered_tokens.values() if t.status == "active"]),
            "active_challenges": len(self.active_challenges),
            "supported_types": [t.value for t in self.hardware_config["supported_types"]],
            "status": "active"
        }


class MockYubiKeyProvider:
    """Mock YubiKey provider for development/testing"""
    
    async def generate_challenge(self, token: HardwareToken) -> str:
        """Generate mock YubiKey challenge"""
        # Simulate challenge generation
        await asyncio.sleep(0.1)
        
        # Generate random challenge data
        import secrets
        challenge = secrets.token_hex(16)
        
        logger.info(f"[MOCK YubiKey] Generated challenge for token {token.serial_number}")
        return challenge
    
    async def verify_response(self, token: HardwareToken, challenge: HardwareChallenge, 
                            response: str) -> bool:
        """Verify mock YubiKey response"""
        # Simulate verification delay
        await asyncio.sleep(0.1)
        
        # Mock verification (in production, this would verify actual YubiKey response)
        # For now, accept any response that's not empty
        is_valid = bool(response and len(response) > 0)
        
        logger.info(f"[MOCK YubiKey] Verification {'successful' if is_valid else 'failed'} for token {token.serial_number}")
        return is_valid


class MockFIDO2Provider:
    """Mock FIDO2 provider for development/testing"""
    
    async def generate_challenge(self, token: HardwareToken) -> str:
        """Generate mock FIDO2 challenge"""
        await asyncio.sleep(0.1)
        
        import secrets
        challenge = secrets.token_hex(32)
        
        logger.info(f"[MOCK FIDO2] Generated challenge for token {token.serial_number}")
        return challenge
    
    async def verify_response(self, token: HardwareToken, challenge: HardwareChallenge, 
                            response: str) -> bool:
        """Verify mock FIDO2 response"""
        await asyncio.sleep(0.1)
        
        is_valid = bool(response and len(response) > 0)
        
        logger.info(f"[MOCK FIDO2] Verification {'successful' if is_valid else 'failed'} for token {token.serial_number}")
        return is_valid


class MockTOTPHardwareProvider:
    """Mock TOTP Hardware provider for development/testing"""
    
    async def generate_challenge(self, token: HardwareToken) -> str:
        """Generate mock TOTP hardware challenge"""
        await asyncio.sleep(0.1)
        
        import secrets
        challenge = secrets.token_hex(16)
        
        logger.info(f"[MOCK TOTP Hardware] Generated challenge for token {token.serial_number}")
        return challenge
    
    async def verify_response(self, token: HardwareToken, challenge: HardwareChallenge, 
                            response: str) -> bool:
        """Verify mock TOTP hardware response"""
        await asyncio.sleep(0.1)
        
        is_valid = bool(response and len(response) > 0)
        
        logger.info(f"[MOCK TOTP Hardware] Verification {'successful' if is_valid else 'failed'} for token {token.serial_number}")
        return is_valid


# Global hardware token service instance
hardware_service = HardwareTokenService()
