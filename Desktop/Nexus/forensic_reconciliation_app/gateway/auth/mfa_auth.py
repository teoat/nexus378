"""
Multi-Factor Authentication (MFA) Implementation
Provides TOTP and SMS-based authentication for enhanced security
"""

import jwt
import time
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MFAToken:
    """MFA token data structure"""
    user_id: str
    token_type: str  # 'totp' or 'sms'
    secret: str
    expires_at: datetime
    attempts_remaining: int = 3
    is_verified: bool = False

@dataclass
class MFAChallenge:
    """MFA challenge response structure"""
    challenge_id: str
    challenge_type: str
    expires_at: datetime
    user_id: str
    metadata: Dict[str, Any]

class MFAAuthenticator:
    """Main MFA authentication handler"""
    
    def __init__(self, secret_key: str, totp_window: int = 2, max_attempts: int = 3):
        self.secret_key = secret_key
        self.totp_window = totp_window  # Time window for TOTP validation
        self.max_attempts = max_attempts
        self.active_challenges: Dict[str, MFAChallenge] = {}
        self.active_tokens: Dict[str, MFAToken] = {}
        
    def generate_totp_secret(self, user_id: str) -> str:
        """Generate a new TOTP secret for a user"""
        # Generate a cryptographically secure secret
        secret = secrets.token_urlsafe(32)
        
        # Store the secret (in production, this would go to a secure database)
        token = MFAToken(
            user_id=user_id,
            token_type='totp',
            secret=secret,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            attempts_remaining=self.max_attempts
        )
        
        self.active_tokens[secret] = token
        return secret
    
    def generate_sms_code(self, user_id: str, phone_number: str) -> Tuple[str, str]:
        """Generate a 6-digit SMS code for a user"""
        # Generate a 6-digit code
        code = str(secrets.randbelow(1000000)).zfill(6)
        
        # Create challenge
        challenge_id = secrets.token_urlsafe(16)
        challenge = MFAChallenge(
            challenge_id=challenge_id,
            challenge_type='sms',
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            user_id=user_id,
            metadata={'phone_number': phone_number, 'code': code}
        )
        
        self.active_challenges[challenge_id] = challenge
        
        # In production, this would send the SMS
        logger.info(f"SMS code {code} generated for user {user_id} at {phone_number}")
        
        return challenge_id, code
    
    def verify_totp(self, secret: str, token: str) -> Tuple[bool, str]:
        """Verify a TOTP token"""
        if secret not in self.active_tokens:
            return False, "Invalid or expired secret"
        
        mfa_token = self.active_tokens[secret]
        
        # Check if expired
        if datetime.utcnow() > mfa_token.expires_at:
            del self.active_tokens[secret]
            return False, "Secret has expired"
        
        # Check attempts remaining
        if mfa_token.attempts_remaining <= 0:
            del self.active_tokens[secret]
            return False, "Maximum attempts exceeded"
        
        # Verify TOTP (simplified - in production use pyotp)
        current_time = int(time.time())
        expected_token = self._generate_totp_token(mfa_token.secret, current_time)
        
        # Check current and adjacent time windows
        for i in range(-self.totp_window, self.totp_window + 1):
            if self._generate_totp_token(mfa_token.secret, current_time + i * 30) == token:
                mfa_token.is_verified = True
                mfa_token.attempts_remaining = self.max_attempts
                return True, "TOTP verified successfully"
        
        # Decrement attempts
        mfa_token.attempts_remaining -= 1
        return False, f"Invalid TOTP token. {mfa_token.attempts_remaining} attempts remaining"
    
    def verify_sms_code(self, challenge_id: str, code: str) -> Tuple[bool, str]:
        """Verify an SMS code"""
        if challenge_id not in self.active_challenges:
            return False, "Invalid or expired challenge"
        
        challenge = self.active_challenges[challenge_id]
        
        # Check if expired
        if datetime.utcnow() > challenge.expires_at:
            del self.active_challenges[challenge_id]
            return False, "Challenge has expired"
        
        # Verify code
        if challenge.metadata['code'] == code:
            # Create verified token
            token = MFAToken(
                user_id=challenge.user_id,
                token_type='sms',
                secret=challenge_id,
                expires_at=datetime.utcnow() + timedelta(hours=1),
                is_verified=True
            )
            
            self.active_tokens[challenge_id] = token
            del self.active_challenges[challenge_id]
            
            return True, "SMS code verified successfully"
        
        return False, "Invalid SMS code"
    
    def _generate_totp_token(self, secret: str, timestamp: int) -> str:
        """Generate TOTP token for a given timestamp (simplified)"""
        # In production, use pyotp library for proper TOTP generation
        time_step = timestamp // 30
        message = f"{secret}{time_step}".encode()
        hash_obj = hashlib.sha256(message)
        hash_hex = hash_obj.hexdigest()
        
        # Take last 6 digits
        return hash_hex[-6:]
    
    def create_mfa_jwt(self, user_id: str, mfa_type: str) -> str:
        """Create a JWT token after successful MFA verification"""
        payload = {
            'user_id': user_id,
            'mfa_type': mfa_type,
            'mfa_verified': True,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_mfa_jwt(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """Verify an MFA JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}
    
    def revoke_mfa_token(self, secret: str) -> bool:
        """Revoke an MFA token"""
        if secret in self.active_tokens:
            del self.active_tokens[secret]
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired tokens and challenges"""
        now = datetime.utcnow()
        expired_tokens = [k for k, v in self.active_tokens.items() if v.expires_at < now]
        expired_challenges = [k for k, v in self.active_challenges.items() if v.expires_at < now]
        
        for k in expired_tokens:
            del self.active_tokens[k]
        for k in expired_challenges:
            del self.active_challenges[k]
        
        return len(expired_tokens) + len(expired_challenges)

# Global MFA authenticator instance
mfa_authenticator = MFAAuthenticator(
    secret_key="your-secret-key-change-in-production",
    totp_window=2,
    max_attempts=3
)
