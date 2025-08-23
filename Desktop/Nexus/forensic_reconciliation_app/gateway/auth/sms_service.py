"""
SMS Service for Multi-Factor Authentication
Handles SMS code generation, delivery, and validation
"""

import logging
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

@dataclass
class SMSCode:
    """SMS code data structure"""
    code: str
    user_id: str
    phone_number: str
    created_at: datetime
    expires_at: datetime
    attempts_remaining: int
    is_verified: bool = False

class SMSService:
    """SMS service for MFA authentication"""
    
    def __init__(
    self,
    code_length: int = 6,
    expiry_minutes: int = 10,
    max_attempts: int = 3
)
        self.code_length = code_length
        self.expiry_minutes = expiry_minutes
        self.max_attempts = max_attempts
        self.active_codes: Dict[str, SMSCode] = {}
        
    def generate_sms_code(self, user_id: str, phone_number: str) -> Tuple[str, str]:
        """Generate a new SMS code for a user"""
        # Generate random numeric code
        code = str(secrets.randbelow(10 ** self.code_length)).zfill(self.code_length)
        
        # Create unique identifier for this code
        code_id = secrets.token_urlsafe(16)
        
        # Create SMS code object
        now = datetime.utcnow()
        sms_code = SMSCode(
            code=code,
            user_id=user_id,
            phone_number=phone_number,
            created_at=now,
            expires_at=now + timedelta(minutes=self.expiry_minutes),
            attempts_remaining=self.max_attempts
        )
        
        # Store the code
        self.active_codes[code_id] = sms_code
        
        # In production, this would send the actual SMS
        self._send_sms(phone_number, code)
        
        logger.info(f"SMS code {code} generated for user {user_id} at {phone_number}")
        
        return code_id, code
    
    def verify_sms_code(self, code_id: str, code: str) -> Tuple[bool, str]:
        """Verify an SMS code"""
        if code_id not in self.active_codes:
            return False, "Invalid or expired code ID"
        
        sms_code = self.active_codes[code_id]
        
        # Check if expired
        if datetime.utcnow() > sms_code.expires_at:
            del self.active_codes[code_id]
            return False, "SMS code has expired"
        
        # Check attempts remaining
        if sms_code.attempts_remaining <= 0:
            del self.active_codes[code_id]
            return False, "Maximum attempts exceeded"
        
        # Verify code
        if sms_code.code == code:
            sms_code.is_verified = True
            sms_code.attempts_remaining = self.max_attempts
            return True, "SMS code verified successfully"
        
        # Decrement attempts
        sms_code.attempts_remaining -= 1
        return False, f"Invalid SMS code. {sms_code.attempts_remaining} attempts remaining"
    
    def resend_sms_code(self, code_id: str) -> Tuple[bool, str]:
        """Resend SMS code (generate new code with same ID)"""
        if code_id not in self.active_codes:
            return False, "Invalid code ID"
        
        sms_code = self.active_codes[code_id]
        
        # Generate new code
        new_code = (
    str(secrets.randbelow(10 ** self.code_length)).zfill(self.code_length)
)
        
        # Update existing SMS code object
        now = datetime.utcnow()
        sms_code.code = new_code
        sms_code.created_at = now
        sms_code.expires_at = now + timedelta(minutes=self.expiry_minutes)
        sms_code.attempts_remaining = self.max_attempts
        sms_code.is_verified = False
        
        # Send new SMS
        self._send_sms(sms_code.phone_number, new_code)
        
        logger.info(f"SMS code resent: {new_code} for user {sms_code.user_id}")
        
        return True, "SMS code resent successfully"
    
    def _send_sms(self, phone_number: str, code: str) -> bool:
        """Send SMS with code (production implementation would use SMS provider)"""
        try:
            # In production, integrate with SMS provider like Twilio, AWS SNS, etc.
            # For now, just log the SMS
            logger.info(f"SMS sent to {phone_number}: Your verification code is {code}")
            
            # Simulate SMS delivery delay
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False
    
    def get_code_status(self, code_id: str) -> Optional[Dict]:
        """Get status of an SMS code"""
        if code_id not in self.active_codes:
            return None
        
        sms_code = self.active_codes[code_id]
        now = datetime.utcnow()
        
        return {
            'code_id': code_id,
            'user_id': sms_code.user_id,
            'phone_number': sms_code.phone_number,
            'is_expired': now > sms_code.expires_at,
            'is_verified': sms_code.is_verified,
            'attempts_remaining': sms_code.attempts_remaining,
            'expires_at': sms_code.expires_at.isoformat(),
            'time_remaining': max(0, (sms_code.expires_at - now).total_seconds())
        }
    
    def revoke_code(self, code_id: str) -> bool:
        """Revoke an SMS code"""
        if code_id in self.active_codes:
            del self.active_codes[code_id]
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired SMS codes"""
        now = datetime.utcnow()
        expired_codes = [k for k, v in self.active_codes.items() if v.expires_at < now]
        
        for code_id in expired_codes:
            del self.active_codes[code_id]
        
        return len(expired_codes)
    
    def get_user_active_codes(self, user_id: str) -> list:
        """Get all active codes for a user"""
        now = datetime.utcnow()
        user_codes = []
        
        for code_id, sms_code in self.active_codes.items():
            if sms_code.user_id == user_id and sms_code.expires_at > now:
                user_codes.append({
                    'code_id': code_id,
                    'phone_number': sms_code.phone_number,
                    'expires_at': sms_code.expires_at.isoformat(),
                    'is_verified': sms_code.is_verified
                })
        
        return user_codes

# Global SMS service instance
sms_service = SMSService(
    code_length=6,
    expiry_minutes=10,
    max_attempts=3
)
