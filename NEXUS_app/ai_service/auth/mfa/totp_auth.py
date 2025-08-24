TOTP (Time-based One-Time Password) Authentication Service
Implements RFC 6238 TOTP standard for secure authentication

import base64
import hashlib
import hmac
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class TOTPService:
    """TOTP authentication service implementationTOTP authentication service implementation"""
    
    def __init__(self):
        self.totp_secrets: Dict[str, str] = {}
        self.totp_config = {
            "digits": 6,
            "period": 30,  # 30 seconds
            "algorithm": "SHA1",
            "window": 1  # Accept codes within ±1 period
        }
        
        logger.info("TOTP service initialized")
    
    def generate_totp_secret(self, user_id: str) -> str:
        """Generate a new TOTP secret for userGenerate a new TOTP secret for user"""
        try:
            # Generate cryptographically secure random secret
            secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
            
            # Store secret for user
            self.totp_secrets[user_id] = secret
            
            logger.info(f"Generated TOTP secret for user {user_id}")
            return secret
            
        except Exception as e:
            logger.error(f"Failed to generate TOTP secret: {e}")
            raise
    
    def get_totp_secret(self, user_id: str) -> Optional[str]:
        """Get existing TOTP secret for userGet existing TOTP secret for user"""
        return self.totp_secrets.get(user_id)
    
    def generate_totp_code(
    self,
    user_id: str,
    timestamp: Optional[int] = None
)
        """Generate TOTP code for user at specific timestampGenerate TOTP code for user at specific timestamp"""
        try:
            secret = self.get_totp_secret(user_id)
            if not secret:
                logger.warning(f"No TOTP secret found for user {user_id}")
                return None
            
            # Use current time if timestamp not provided
            if timestamp is None:
                timestamp = int(time.time())
            
            # Generate TOTP code
            code = self._generate_totp(secret, timestamp)
            
            logger.debug(
    f"Generated TOTP code for user {user_id} at timestamp {timestamp}",
)
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate TOTP code: {e}")
            return None
    
    def verify_totp(self, user_id: str, code: str) -> bool:
        """Verify TOTP code for userVerify TOTP code for user"""
        try:
            if not code or len(code) != self.totp_config["digits"]:
                logger.warning(f"Invalid TOTP code format for user {user_id}")
                return False
            
            # Get user's TOTP secret
            secret = self.get_totp_secret(user_id)
            if not secret:
                logger.warning(f"No TOTP secret found for user {user_id}")
                return False
            
            current_time = int(time.time())
            current_period = current_time // self.totp_config["period"]
            
            # Check current period and window periods
            for period_offset in range(
    -self.totp_config["window"],
    self.totp_config["window"] + 1
)
                check_period = current_period + period_offset
                check_timestamp = check_period * self.totp_config["period"]
                
                expected_code = self._generate_totp(secret, check_timestamp)
                if expected_code == code:
                    logger.info(f"TOTP code verified for user {user_id}")
                    return True
            
            logger.warning(f"TOTP code verification failed for user {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify TOTP code: {e}")
            return False
    
    def _generate_totp(self, secret: str, timestamp: int) -> str:
        """Generate TOTP code using RFC 6238 algorithmGenerate TOTP code using RFC 6238 algorithm"""
        try:
            # Convert timestamp to period
            period = timestamp // self.totp_config["period"]
            
            # Convert period to 8-byte big-endian integer
            period_bytes = period.to_bytes(8, 'big')
            
            # Decode base32 secret
            secret_bytes = base64.b32decode(secret)
            
            # Generate HMAC-SHA1
            hmac_obj = hmac.new(secret_bytes, period_bytes, hashlib.sha1)
            hmac_result = hmac_obj.digest()
            
            # Get offset from last 4 bits of HMAC
            offset = hmac_result[-1] & 0x0f
            
            # Extract 4 bytes starting at offset
            code_bytes = hmac_result[offset:offset + 4]
            
            # Convert to integer and apply modulo
            code_int = int.from_bytes(code_bytes, 'big') & 0x7fffffff
            code = str(code_int % (10 ** self.totp_config["digits"]))
            
            # Pad with leading zeros if necessary
            code = code.zfill(self.totp_config["digits"])
            
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate TOTP: {e}")
            raise
    
    def get_qr_code_data(
    self,
    user_id: str,
    issuer: str = "Forensic Platform",
    account_name: str = None
)
        """Generate QR code data for TOTP setupGenerate QR code data for TOTP setup"""
        try:
            secret = self.get_totp_secret(user_id)
            if not secret:
                logger.warning(f"No TOTP secret found for user {user_id}")
                return None
            
            # Use user_id as account name if not provided
            if not account_name:
                account_name = user_id
            
            # Generate otpauth URL (Google Authenticator format)
            otpauth_url = (
                f"otpauth://totp/{issuer}:{account_name}"
                f"?secret={secret}"
                f"&issuer={issuer}"
                f"&algorithm={self.totp_config['algorithm']}"
                f"&digits={self.totp_config['digits']}"
                f"&period={self.totp_config['period']}"
            )
            
            logger.info(f"Generated QR code data for user {user_id}")
            return otpauth_url
            
        except Exception as e:
            logger.error(f"Failed to generate QR code data: {e}")
            return None
    
    def revoke_totp_secret(self, user_id: str) -> bool:
        """Revoke TOTP secret for userRevoke TOTP secret for user"""
        try:
            if user_id in self.totp_secrets:
                del self.totp_secrets[user_id]
                logger.info(f"TOTP secret revoked for user {user_id}")
                return True
            else:
                logger.warning(f"No TOTP secret found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to revoke TOTP secret: {e}")
            return False
    
    def get_user_totp_status(self, user_id: str) -> Dict[str, any]:
        """Get TOTP status for userGet TOTP status for user"""
        try:
            secret = self.get_totp_secret(user_id)
            return {
                "enabled": secret is not None,
                "secret_exists": secret is not None,
                "digits": self.totp_config["digits"],
                "period": self.totp_config["period"],
                "algorithm": self.totp_config["algorithm"]
            }
        except Exception as e:
            logger.error(f"Failed to get TOTP status: {e}")
            return {"enabled": False, "error": str(e)}
    
    def update_totp_config(self, **kwargs):
        """Update TOTP configurationUpdate TOTP configuration"""
        try:
            for key, value in kwargs.items():
                if key in self.totp_config:
                    self.totp_config[key] = value
                    logger.info(f"Updated TOTP config: {key} = {value}")
                else:
                    logger.warning(f"Unknown TOTP config key: {key}")
                    
        except Exception as e:
            logger.error(f"Failed to update TOTP config: {e}")
    
    def get_system_status(self) -> Dict[str, any]:
        """Get TOTP service statusGet TOTP service status"""
        return {
            "total_users": len(self.totp_secrets),
            "config": self.totp_config,
            "status": "active"
        }

# Global TOTP service instance
totp_service = TOTPService()
