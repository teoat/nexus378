"""
Time-based One-Time Password (TOTP) Service
Implements RFC 6238 TOTP algorithm for secure authentication
"""

import base64
import hmac
import hashlib
import time
import secrets
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TOTPService:
    """TOTP service implementation following RFC 6238"""
    
    def __init__(self, algorithm: str = 'sha1', digits: int = 6, period: int = 30, window: int = 2):
        self.algorithm = algorithm
        self.digits = digits
        self.period = period
        self.window = window
    
    def generate_secret(self, length: int = 32) -> str:
        """Generate a cryptographically secure TOTP secret"""
        random_bytes = secrets.token_bytes(length)
        secret = base64.b32encode(random_bytes).decode('utf-8')
        return secret.rstrip('=')
    
    def generate_totp(self, secret: str, timestamp: Optional[int] = None) -> str:
        """Generate TOTP for a given timestamp"""
        if timestamp is None:
            timestamp = int(time.time())
        
        time_step = timestamp // self.period
        hmac_obj = self._generate_hmac(secret, time_step)
        totp = self._generate_totp_from_hmac(hmac_obj)
        return totp
    
    def verify_totp(self, secret: str, token: str, timestamp: Optional[int] = None) -> bool:
        """Verify a TOTP token within the configured window"""
        if timestamp is None:
            timestamp = int(time.time())
        
        for i in range(-self.window, self.window + 1):
            check_time = timestamp + (i * self.period)
            expected_token = self.generate_totp(secret, check_time)
            if token == expected_token:
                return True
        return False
    
    def _generate_hmac(self, secret: str, time_step: int) -> bytes:
        """Generate HMAC for TOTP calculation"""
        time_bytes = time_step.to_bytes(8, 'big')
        secret_bytes = base64.b32decode(secret + '=' * (-len(secret) % 8))
        
        if self.algorithm == 'sha1':
            hash_func = hashlib.sha1
        elif self.algorithm == 'sha256':
            hash_func = hashlib.sha256
        else:
            hash_func = hashlib.sha512
        
        hmac_obj = hmac.new(secret_bytes, time_bytes, hash_func)
        return hmac_obj.digest()
    
    def _generate_totp_from_hmac(self, hmac_obj: bytes) -> str:
        """Generate TOTP from HMAC using dynamic truncation"""
        offset = hmac_obj[-1] & 0x0f
        code_bytes = hmac_obj[offset:offset + 4]
        code_int = int.from_bytes(code_bytes, 'big')
        code_int = code_int & 0x7fffffff
        code_int = code_int % (10 ** self.digits)
        return str(code_int).zfill(self.digits)

# Global TOTP service instance
totp_service = TOTPService()
