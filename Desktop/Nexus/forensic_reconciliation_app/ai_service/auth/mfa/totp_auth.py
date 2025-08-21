"""
TOTP (Time-based One-Time Password) Authenticator

Implements RFC 6238 TOTP standard for secure authentication
"""

import base64
import hashlib
import hmac
import time
import secrets
import qrcode
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
import logging

from config import TOTPConfig

logger = logging.getLogger(__name__)


@dataclass
class TOTPResult:
    """Result of TOTP operation"""
    success: bool
    message: str
    code: Optional[str] = None
    qr_code: Optional[str] = None
    secret: Optional[str] = None
    remaining_time: Optional[int] = None


class TOTPAuthenticator:
    """
    TOTP Authenticator implementation
    
    Supports:
    - Secret generation
    - QR code generation for authenticator apps
    - Code validation
    - Time window validation
    - Multiple algorithms (SHA1, SHA256, SHA512)
    """
    
    def __init__(self, config: TOTPConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Validate configuration
        if not self._validate_config():
            raise ValueError("Invalid TOTP configuration")
    
    def _validate_config(self) -> bool:
        """Validate TOTP configuration"""
        try:
            assert self.config.digits in [6, 8], "TOTP digits must be 6 or 8"
            assert self.config.period >= 15, "TOTP period must be at least 15 seconds"
            assert self.config.algorithm in ["SHA1", "SHA256", "SHA512"], "Invalid algorithm"
            assert self.config.window >= 0, "Window must be non-negative"
            assert self.config.secret_length >= 16, "Secret length must be at least 16 bytes"
            return True
        except AssertionError as e:
            self.logger.error(f"TOTP configuration validation failed: {e}")
            return False
    
    def generate_secret(self, user_id: str, issuer: Optional[str] = None) -> str:
        """
        Generate a new TOTP secret for a user
        
        Args:
            user_id: Unique identifier for the user
            issuer: Issuer name (defaults to config issuer)
            
        Returns:
            Base32 encoded secret
        """
        try:
            # Generate cryptographically secure random bytes
            secret_bytes = secrets.token_bytes(self.config.secret_length)
            
            # Encode to base32 (standard for TOTP)
            secret = base64.b32encode(secret_bytes).decode('utf-8')
            
            # Remove padding for cleaner display
            secret = secret.rstrip('=')
            
            self.logger.info(f"Generated TOTP secret for user {user_id}")
            return secret
            
        except Exception as e:
            self.logger.error(f"Failed to generate TOTP secret for user {user_id}: {e}")
            raise
    
    def generate_qr_code(self, user_id: str, secret: str, email: Optional[str] = None) -> str:
        """
        Generate QR code URI for authenticator apps
        
        Args:
            user_id: User identifier
            secret: TOTP secret
            email: User email (optional)
            
        Returns:
            QR code URI string
        """
        try:
            # Build TOTP URI according to RFC 6238
            issuer = self.config.issuer.replace(' ', '%20')
            account = email if email else user_id
            
            # Format: otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}&algorithm={algorithm}&digits={digits}&period={period}
            uri = (
                f"otpauth://totp/{issuer}:{account}"
                f"?secret={secret}"
                f"&issuer={issuer}"
                f"&algorithm={self.config.algorithm}"
                f"&digits={self.config.digits}"
                f"&period={self.config.period}"
            )
            
            self.logger.info(f"Generated QR code URI for user {user_id}")
            return uri
            
        except Exception as e:
            self.logger.error(f"Failed to generate QR code URI for user {user_id}: {e}")
            raise
    
    def generate_qr_code_image(self, uri: str, size: int = 200) -> bytes:
        """
        Generate QR code image from URI
        
        Args:
            uri: TOTP URI
            size: Image size in pixels
            
        Returns:
            PNG image bytes
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            import io
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            return img_bytes.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to generate QR code image: {e}")
            raise
    
    def generate_code(self, secret: str, timestamp: Optional[int] = None) -> str:
        """
        Generate TOTP code for a given secret and timestamp
        
        Args:
            secret: TOTP secret
            timestamp: Unix timestamp (defaults to current time)
            
        Returns:
            TOTP code string
        """
        try:
            if timestamp is None:
                timestamp = int(time.time())
            
            # Calculate time step
            time_step = timestamp // self.config.period
            
            # Decode base32 secret
            secret_bytes = base64.b32decode(secret + '=' * (-len(secret) % 8))
            
            # Convert time step to bytes (big-endian)
            time_bytes = time_step.to_bytes(8, 'big')
            
            # Calculate HMAC
            if self.config.algorithm == "SHA1":
                hash_algorithm = hashlib.sha1
            elif self.config.algorithm == "SHA256":
                hash_algorithm = hashlib.sha256
            elif self.config.algorithm == "SHA512":
                hash_algorithm = hashlib.sha512
            else:
                raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
            
            hmac_obj = hmac.new(secret_bytes, time_bytes, hash_algorithm)
            hmac_result = hmac_obj.digest()
            
            # Get offset (last 4 bits of HMAC)
            offset = hmac_result[-1] & 0x0F
            
            # Extract 4 bytes starting at offset
            code_bytes = hmac_result[offset:offset + 4]
            
            # Convert to integer (big-endian)
            code_int = int.from_bytes(code_bytes, 'big')
            
            # Apply mask to get required number of digits
            mask = (1 << self.config.digits) - 1
            code_int = code_int & mask
            
            # Format code with leading zeros
            code = str(code_int).zfill(self.config.digits)
            
            return code
            
        except Exception as e:
            self.logger.error(f"Failed to generate TOTP code: {e}")
            raise
    
    def validate_code(self, secret: str, code: str, timestamp: Optional[int] = None) -> TOTPResult:
        """
        Validate a TOTP code
        
        Args:
            secret: TOTP secret
            code: Code to validate
            timestamp: Timestamp for validation (defaults to current time)
            
        Returns:
            TOTPResult with validation status
        """
        try:
            if timestamp is None:
                timestamp = int(time.time())
            
            current_time_step = timestamp // self.config.period
            
            # Check current time step and window
            for i in range(-self.config.window, self.config.window + 1):
                check_timestamp = timestamp + (i * self.config.period)
                expected_code = self.generate_code(secret, check_timestamp)
                
                if code == expected_code:
                    # Calculate remaining time
                    remaining_time = self.config.period - (timestamp % self.config.period)
                    
                    self.logger.info(f"TOTP code validated successfully")
                    return TOTPResult(
                        success=True,
                        message="Code validated successfully",
                        code=code,
                        remaining_time=remaining_time
                    )
            
            # Code not found in valid time windows
            self.logger.warning(f"TOTP code validation failed: invalid code")
            return TOTPResult(
                success=False,
                message="Invalid or expired code"
            )
            
        except Exception as e:
            self.logger.error(f"TOTP code validation error: {e}")
            return TOTPResult(
                success=False,
                message=f"Validation error: {str(e)}"
            )
    
    def get_remaining_time(self, timestamp: Optional[int] = None) -> int:
        """
        Get remaining time until next code generation
        
        Args:
            timestamp: Current timestamp (defaults to current time)
            
        Returns:
            Seconds remaining until next code
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        return self.config.period - (timestamp % self.config.period)
    
    def setup_user_mfa(self, user_id: str, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete MFA setup for a user
        
        Args:
            user_id: User identifier
            email: User email (optional)
            
        Returns:
            Dictionary with setup information
        """
        try:
            # Generate secret
            secret = self.generate_secret(user_id)
            
            # Generate QR code URI
            uri = self.generate_qr_code(user_id, secret, email)
            
            # Generate QR code image
            qr_image = self.generate_qr_code_image(uri)
            
            # Generate current code for verification
            current_code = self.generate_code(secret)
            
            setup_data = {
                'user_id': user_id,
                'secret': secret,
                'qr_uri': uri,
                'qr_image': qr_image,
                'current_code': current_code,
                'algorithm': self.config.algorithm,
                'digits': self.config.digits,
                'period': self.config.period,
                'issuer': self.config.issuer
            }
            
            self.logger.info(f"MFA setup completed for user {user_id}")
            return setup_data
            
        except Exception as e:
            self.logger.error(f"Failed to setup MFA for user {user_id}: {e}")
            raise
    
    def verify_setup(self, secret: str, code: str) -> bool:
        """
        Verify MFA setup by validating a code
        
        Args:
            secret: TOTP secret
            code: Code to verify
            
        Returns:
            True if verification successful
        """
        result = self.validate_code(secret, code)
        return result.success
    
    def get_status(self) -> Dict[str, Any]:
        """Get TOTP authenticator status"""
        return {
            'enabled': True,
            'algorithm': self.config.algorithm,
            'digits': self.config.digits,
            'period': self.config.period,
            'window': self.config.window,
            'issuer': self.config.issuer,
            'secret_length': self.config.secret_length
        }
