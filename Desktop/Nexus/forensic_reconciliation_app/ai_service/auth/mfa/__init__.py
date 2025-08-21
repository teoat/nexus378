"""
Multi-Factor Authentication (MFA) Package

This package provides comprehensive MFA implementation including:
- TOTP (Time-based One-Time Password)
- SMS-based authentication
- Hardware token support
- Configuration management
"""

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"
__description__ = "Multi-Factor Authentication System"

from .totp_auth import TOTPAuthenticator
from .sms_auth import SMSAuthenticator
from .hardware_auth import HardwareTokenAuthenticator
from .mfa_manager import MFAManager
from .config import MFAConfig

__all__ = [
    "TOTPAuthenticator",
    "SMSAuthenticator", 
    "HardwareTokenAuthenticator",
    "MFAManager",
    "MFAConfig"
]
