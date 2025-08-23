"""
Multi-Factor Authentication Manager
Coordinates TOTP, SMS, and hardware token authentication
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import asyncio

logger = logging.getLogger(__name__)


class MFAType(Enum):
    """Supported MFA types"""
    TOTP = "totp"
    SMS = "sms"
    HARDWARE = "hardware"


class MFAStatus(Enum):
    """MFA verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class MFAChallenge:
    """MFA challenge for user verification"""
    id: str
    user_id: str
    mfa_type: MFAType
    challenge_data: str
    expires_at: datetime
    status: MFAStatus
    attempts: int
    max_attempts: int = 3


class MFAManager:
    """Central MFA management system"""
    
    def __init__(self):
        self.active_challenges: Dict[str, MFAChallenge] = {}
        self.user_mfa_settings: Dict[str, Dict[str, bool]] = {}
        self.mfa_config = {
            "totp_enabled": True,
            "sms_enabled": True,
            "hardware_enabled": True,
            "challenge_timeout": 300,  # 5 minutes
            "max_attempts": 3
        }
        
        # Initialize MFA services
        self.totp_service = None
        self.sms_service = None
        self.hardware_service = None
        
        logger.info("MFA Manager initialized")
    
    async def setup_mfa_services(self):
        """Initialize all MFA service components"""
        try:
            # Initialize TOTP service
            from .totp_auth import TOTPService
            self.totp_service = TOTPService()
            logger.info("TOTP service initialized")
            
            # Initialize SMS service
            from .sms_auth import SMSService
            self.sms_service = SMSService()
            logger.info("SMS service initialized")
            
            # Initialize hardware token service
            from .hardware_auth import HardwareTokenService
            self.hardware_service = HardwareTokenService()
            logger.info("Hardware token service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MFA services: {e}")
            raise
    
    async def create_mfa_challenge(self, user_id: str, mfa_type: MFAType) -> Optional[MFAChallenge]:
        """Create a new MFA challenge for user verification"""
        try:
            # Check if user has this MFA type enabled
            if not self._is_mfa_enabled_for_user(user_id, mfa_type):
                logger.warning(
    f"MFA type {mfa_type.value} not enabled for user {user_id}",
)
                return None
            
            # Generate challenge based on MFA type
            challenge_data = await self._generate_challenge_data(user_id, mfa_type)
            if not challenge_data:
                logger.error(f"Failed to generate challenge data for {mfa_type.value}")
                return None
            
            # Create challenge
            challenge = MFAChallenge(
                id=self._generate_challenge_id(),
                user_id=user_id,
                mfa_type=mfa_type,
                challenge_data=challenge_data,
                expires_at=datetime.now() + timedelta(seconds=self.mfa_config["challenge_timeout"]),
                status=MFAStatus.PENDING,
                attempts=0,
                max_attempts=self.mfa_config["max_attempts"]
            )
            
            # Store challenge
            self.active_challenges[challenge.id] = challenge
            
            logger.info(f"Created MFA challenge {challenge.id} for user {user_id} ({mfa_type.value})")
            return challenge
            
        except Exception as e:
            logger.error(f"Failed to create MFA challenge: {e}")
            return None
    
    async def verify_mfa_challenge(self, challenge_id: str, response: str) -> Tuple[bool, str]:
        """Verify MFA challenge response"""
        try:
            # Get challenge
            challenge = self.active_challenges.get(challenge_id)
            if not challenge:
                return False, "Challenge not found"
            
            # Check if expired
            if datetime.now() > challenge.expires_at:
                challenge.status = MFAStatus.EXPIRED
                return False, "Challenge expired"
            
            # Check attempts
            if challenge.attempts >= challenge.max_attempts:
                challenge.status = MFAStatus.FAILED
                return False, "Maximum attempts exceeded"
            
            # Increment attempts
            challenge.attempts += 1
            
            # Verify response based on MFA type
            is_valid = await self._verify_response(challenge, response)
            
            if is_valid:
                challenge.status = MFAStatus.VERIFIED
                logger.info(f"MFA challenge {challenge_id} verified successfully")
                return True, "Verification successful"
            else:
                if challenge.attempts >= challenge.max_attempts:
                    challenge.status = MFAStatus.FAILED
                    return False, "Maximum attempts exceeded"
                return False, "Invalid response"
                
        except Exception as e:
            logger.error(f"Failed to verify MFA challenge: {e}")
            return False, "Verification failed"
    
    async def _generate_challenge_data(self, user_id: str, mfa_type: MFAType) -> Optional[str]:
        """Generate challenge data based on MFA type"""
        try:
            if mfa_type == MFAType.TOTP:
                # TOTP service is sync, no need to await
                return self.totp_service.generate_totp_secret(user_id)
            elif mfa_type == MFAType.SMS:
                # SMS service is async
                return await self.sms_service.generate_sms_code(user_id, "+1234567890")  # Default phone
            elif mfa_type == MFAType.HARDWARE:
                # Hardware service is async
                return await self.hardware_service.generate_challenge(user_id)
            else:
                logger.error(f"Unsupported MFA type: {mfa_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate challenge data: {e}")
            return None
    
    async def _verify_response(self, challenge: MFAChallenge, response: str) -> bool:
        """Verify response based on MFA type"""
        try:
            if challenge.mfa_type == MFAType.TOTP:
                return await self.totp_service.verify_totp(challenge.user_id, response)
            elif challenge.mfa_type == MFAType.SMS:
                return await self.sms_service.verify_sms_code(challenge.user_id, response)
            elif challenge.mfa_type == MFAType.HARDWARE:
                return await self.hardware_service.verify_response(challenge.user_id, response)
            else:
                logger.error(f"Unsupported MFA type: {challenge.mfa_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify response: {e}")
            return False
    
    def _is_mfa_enabled_for_user(self, user_id: str, mfa_type: MFAType) -> bool:
        """Check if specific MFA type is enabled for user"""
        user_settings = self.user_mfa_settings.get(user_id, {})
        return user_settings.get(mfa_type.value, False)
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        import uuid
        return str(uuid.uuid4())
    
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
                logger.info(f"Cleaned up {len(expired_ids)} expired challenges")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired challenges: {e}")
    
    def get_user_mfa_status(self, user_id: str) -> Dict[str, bool]:
        """Get MFA status for user"""
        return self.user_mfa_settings.get(user_id, {})
    
    async def enable_mfa_for_user(
    self,
    user_id: str,
    mfa_type: MFAType,
    enabled: bool = True
)
        """Enable/disable MFA type for user"""
        if user_id not in self.user_mfa_settings:
            self.user_mfa_settings[user_id] = {}
        
        self.user_mfa_settings[user_id][mfa_type.value] = enabled
        logger.info(
    f"MFA {mfa_type.value} {'enabled' if enabled else 'disabled'} for user {user_id}",
)
    
    def get_system_status(self) -> Dict[str, any]:
        """Get MFA system status"""
        return {
            "active_challenges": len(self.active_challenges),
            "total_users": len(self.user_mfa_settings),
            "mfa_config": self.mfa_config,
            "services_status": {
                "totp": self.totp_service is not None,
                "sms": self.sms_service is not None,
                "hardware": self.hardware_service is not None
            }
        }


# Global MFA manager instance
mfa_manager = MFAManager()
