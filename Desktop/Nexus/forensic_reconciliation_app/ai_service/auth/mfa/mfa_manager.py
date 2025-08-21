"""
Multi-Factor Authentication Manager

Orchestrates all MFA methods and provides unified interface for:
- TOTP authentication
- SMS authentication  
- Hardware token authentication
- Multi-method authentication
- User MFA setup and management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib

from config import MFAConfig, MFAMethod, MFALevel
from totp_auth import TOTPAuthenticator
from sms_auth import SMSAuthenticator
from hardware_auth import HardwareTokenAuthenticator, HardwareTokenInfo, HardwareTokenType

logger = logging.getLogger(__name__)


@dataclass
class MFASetupResult:
    """Result of MFA setup operation"""
    success: bool
    message: str
    setup_data: Optional[Dict[str, Any]] = None
    required_methods: Optional[List[str]] = None
    setup_complete: bool = False


@dataclass
class MFAAuthResult:
    """Result of MFA authentication operation"""
    success: bool
    message: str
    user_id: Optional[str] = None
    auth_methods_used: Optional[List[str]] = None
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class UserMFAStatus:
    """User MFA status information"""
    user_id: str
    mfa_enabled: bool
    methods_enabled: List[str]
    setup_complete: bool
    security_level: MFALevel
    requires_setup: bool
    last_used: Optional[datetime] = None


class MFAManager:
    """
    Multi-Factor Authentication Manager
    
    Features:
    - Unified interface for all MFA methods
    - Multi-method authentication
    - User MFA setup and management
    - Security level enforcement
    - Session management
    - Audit logging
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize authenticators
        self.totp_auth: Optional[TOTPAuthenticator] = None
        self.sms_auth: Optional[SMSAuthenticator] = None
        self.hardware_auth: Optional[HardwareTokenAuthenticator] = None
        
        # User MFA configurations
        self.user_mfa_configs: Dict[str, Dict[str, Any]] = {}
        
        # Active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components
        self._initialize_authenticators()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid MFA configuration")
    
    def _initialize_authenticators(self):
        """Initialize MFA authenticators based on configuration"""
        try:
            # Initialize TOTP authenticator
            if MFAMethod.TOTP in self.config.methods:
                self.totp_auth = TOTPAuthenticator(self.config.totp)
                self.logger.info("TOTP authenticator initialized")
            
            # Initialize SMS authenticator
            if MFAMethod.SMS in self.config.methods:
                # Note: Redis client would be passed here in real implementation
                self.sms_auth = SMSAuthenticator(self.config.sms, redis_client=None)
                self.logger.info("SMS authenticator initialized")
            
            # Initialize hardware token authenticator
            if MFAMethod.HARDWARE in self.config.methods:
                self.hardware_auth = HardwareTokenAuthenticator(self.config.hardware)
                self.logger.info("Hardware token authenticator initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MFA authenticators: {e}")
            raise
    
    def setup_user_mfa(self, user_id: str, email: Optional[str] = None, phone: Optional[str] = None) -> MFASetupResult:
        """
        Setup MFA for a user
        
        Args:
            user_id: User identifier
            email: User email for TOTP setup
            phone: User phone for SMS setup
            
        Returns:
            MFASetupResult with setup information
        """
        try:
            # Check if user already has MFA setup
            if user_id in self.user_mfa_configs:
                current_config = self.user_mfa_configs[user_id]
                if current_config.get('setup_complete', False):
                    return MFASetupResult(
                        success=True,
                        message="MFA already setup for user",
                        setup_complete=True
                    )
            
            # Determine required methods based on security level
            required_methods = self._get_required_methods_for_level(self.config.default_level)
            
            setup_data = {
                'user_id': user_id,
                'required_methods': required_methods,
                'setup_complete': False,
                'methods': {}
            }
            
            # Setup TOTP if required and available
            if MFAMethod.TOTP in required_methods and self.totp_auth:
                try:
                    totp_setup = self.totp_auth.setup_user_mfa(user_id, email)
                    setup_data['methods']['totp'] = {
                        'secret': totp_setup['secret'],
                        'qr_uri': totp_setup['qr_uri'],
                        'qr_image': totp_setup['qr_image'],
                        'current_code': totp_setup['current_code'],
                        'setup_complete': False
                    }
                except Exception as e:
                    self.logger.error(f"Failed to setup TOTP for user {user_id}: {e}")
                    setup_data['methods']['totp'] = {'error': str(e)}
            
            # Setup SMS if required and available
            if MFAMethod.SMS in required_methods and self.sms_auth and phone:
                try:
                    # SMS setup is done when sending first code
                    setup_data['methods']['sms'] = {
                        'phone': phone,
                        'setup_complete': False
                    }
                except Exception as e:
                    self.logger.error(f"Failed to setup SMS for user {user_id}: {e}")
                    setup_data['methods']['sms'] = {'error': str(e)}
            
            # Setup hardware tokens if required and available
            if MFAMethod.HARDWARE in required_methods and self.hardware_auth:
                setup_data['methods']['hardware'] = {
                    'tokens': [],
                    'setup_complete': False
                }
            
            # Store user configuration
            self.user_mfa_configs[user_id] = setup_data
            
            self.logger.info(f"MFA setup initiated for user {user_id}")
            
            return MFASetupResult(
                success=True,
                message="MFA setup initiated successfully",
                setup_data=setup_data,
                required_methods=required_methods,
                setup_complete=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup MFA for user {user_id}: {e}")
            return MFASetupResult(
                success=False,
                message=f"Failed to setup MFA: {str(e)}"
            )
    
    def _get_required_methods_for_level(self, level: MFALevel) -> List[str]:
        """Get required MFA methods for security level"""
        if level == MFALevel.BASIC:
            return [MFAMethod.TOTP.value]
        elif level == MFALevel.ENHANCED:
            return [MFAMethod.TOTP.value, MFAMethod.SMS.value]
        elif level == MFALevel.MAXIMUM:
            return [MFAMethod.TOTP.value, MFAMethod.SMS.value, MFAMethod.HARDWARE.value]
        else:
            return [MFAMethod.TOTP.value]
    
    def verify_totp_setup(self, user_id: str, code: str) -> bool:
        """Verify TOTP setup by validating a code"""
        try:
            if user_id not in self.user_mfa_configs:
                return False
            
            user_config = self.user_mfa_configs[user_id]
            if 'totp' not in user_config.get('methods', {}):
                return False
            
            totp_config = user_config['methods']['totp']
            if 'secret' not in totp_config:
                return False
            
            # Verify code
            if self.totp_auth:
                result = self.totp_auth.verify_setup(totp_config['secret'], code)
                if result:
                    # Mark TOTP setup as complete
                    user_config['methods']['totp']['setup_complete'] = True
                    self._check_setup_completion(user_id)
                
                return result
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify TOTP setup for user {user_id}: {e}")
            return False
    
    async def verify_sms_setup(self, user_id: str, phone: str, code: str) -> bool:
        """Verify SMS setup by validating a code"""
        try:
            if user_id not in self.user_mfa_configs:
                return False
            
            user_config = self.user_mfa_configs[user_id]
            if 'sms' not in user_config.get('methods', {}):
                return False
            
            # Validate SMS code
            if self.sms_auth:
                result = self.sms_auth.validate_code(phone, code)
                if result.success:
                    # Mark SMS setup as complete
                    user_config['methods']['sms']['setup_complete'] = True
                    self._check_setup_completion(user_id)
                
                return result.success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify SMS setup for user {user_id}: {e}")
            return False
    
    def register_hardware_token(self, user_id: str, token_info: HardwareTokenInfo) -> bool:
        """Register a hardware token for a user"""
        try:
            if user_id not in self.user_mfa_configs:
                return False
            
            if not self.hardware_auth:
                return False
            
            # Register token
            success = self.hardware_auth.register_token(token_info)
            
            if success:
                # Update user configuration
                user_config = self.user_mfa_configs[user_id]
                if 'hardware' not in user_config['methods']:
                    user_config['methods']['hardware'] = {'tokens': [], 'setup_complete': False}
                
                user_config['methods']['hardware']['tokens'].append(token_info.token_id)
                
                # Check if hardware setup is complete
                if len(user_config['methods']['hardware']['tokens']) >= 1:
                    user_config['methods']['hardware']['setup_complete'] = True
                    self._check_setup_completion(user_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to register hardware token for user {user_id}: {e}")
            return False
    
    def _check_setup_completion(self, user_id: str):
        """Check if user MFA setup is complete"""
        try:
            if user_id not in self.user_mfa_configs:
                return
            
            user_config = self.user_mfa_configs[user_id]
            required_methods = user_config.get('required_methods', [])
            
            setup_complete = True
            for method in required_methods:
                if method in user_config.get('methods', {}):
                    method_config = user_config['methods'][method]
                    if not method_config.get('setup_complete', False):
                        setup_complete = False
                        break
                else:
                    setup_complete = False
                    break
            
            user_config['setup_complete'] = setup_complete
            
            if setup_complete:
                self.logger.info(f"MFA setup completed for user {user_id}")
            else:
                self.logger.info(f"MFA setup progress for user {user_id}: {self._get_setup_progress(user_id)}")
                
        except Exception as e:
            self.logger.error(f"Failed to check setup completion for user {user_id}: {e}")
    
    def _get_setup_progress(self, user_id: str) -> Dict[str, Any]:
        """Get MFA setup progress for a user"""
        try:
            if user_id not in self.user_mfa_configs:
                return {}
            
            user_config = self.user_mfa_configs[user_id]
            methods = user_config.get('methods', {})
            
            progress = {}
            for method_name, method_config in methods.items():
                progress[method_name] = {
                    'setup_complete': method_config.get('setup_complete', False),
                    'status': 'complete' if method_config.get('setup_complete', False) else 'pending'
                }
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Failed to get setup progress for user {user_id}: {e}")
            return {}
    
    async def authenticate_user(self, user_id: str, auth_data: Dict[str, Any]) -> MFAAuthResult:
        """
        Authenticate user with MFA
        
        Args:
            user_id: User identifier
            auth_data: Authentication data for each method
            
        Returns:
            MFAAuthResult with authentication status
        """
        try:
            # Check if user has MFA setup
            if user_id not in self.user_mfa_configs:
                return MFAAuthResult(
                    success=False,
                    message="User MFA not configured"
                )
            
            user_config = self.user_mfa_configs[user_id]
            if not user_config.get('setup_complete', False):
                return MFAAuthResult(
                    success=False,
                    message="MFA setup not complete"
                )
            
            # Get required methods
            required_methods = user_config.get('required_methods', [])
            auth_methods_used = []
            
            # Validate each required method
            for method in required_methods:
                if method not in auth_data:
                    return MFAAuthResult(
                        success=False,
                        message=f"Missing authentication data for {method}"
                    )
                
                method_success = False
                
                if method == MFAMethod.TOTP.value:
                    method_success = await self._authenticate_totp(user_id, auth_data[method])
                elif method == MFAMethod.SMS.value:
                    method_success = await self._authenticate_sms(user_id, auth_data[method])
                elif method == MFAMethod.HARDWARE.value:
                    method_success = await self._authenticate_hardware(user_id, auth_data[method])
                
                if not method_success:
                    return MFAAuthResult(
                        success=False,
                        message=f"Authentication failed for {method}"
                    )
                
                auth_methods_used.append(method)
            
            # All methods authenticated successfully
            # Generate session token
            session_token = self._generate_session_token(user_id)
            expires_at = datetime.now() + timedelta(hours=self.config.session_timeout_hours)
            
            # Store session
            self.active_sessions[session_token] = {
                'user_id': user_id,
                'auth_methods_used': auth_methods_used,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }
            
            # Update user last used
            user_config['last_used'] = datetime.now()
            
            self.logger.info(f"MFA authentication successful for user {user_id}")
            
            return MFAAuthResult(
                success=True,
                message="Multi-factor authentication successful",
                user_id=user_id,
                auth_methods_used=auth_methods_used,
                session_token=session_token,
                expires_at=expires_at
            )
            
        except Exception as e:
            self.logger.error(f"MFA authentication failed for user {user_id}: {e}")
            return MFAAuthResult(
                success=False,
                message=f"Authentication error: {str(e)}"
            )
    
    async def _authenticate_totp(self, user_id: str, auth_data: Dict[str, Any]) -> bool:
        """Authenticate user with TOTP"""
        try:
            if not self.totp_auth:
                return False
            
            code = auth_data.get('code')
            if not code:
                return False
            
            # Get user's TOTP secret
            if user_id not in self.user_mfa_configs:
                return False
            
            user_config = self.user_mfa_configs[user_id]
            totp_config = user_config.get('methods', {}).get('totp', {})
            secret = totp_config.get('secret')
            
            if not secret:
                return False
            
            # Validate TOTP code
            result = self.totp_auth.validate_code(secret, code)
            return result.success
            
        except Exception as e:
            self.logger.error(f"TOTP authentication failed for user {user_id}: {e}")
            return False
    
    async def _authenticate_sms(self, user_id: str, auth_data: Dict[str, Any]) -> bool:
        """Authenticate user with SMS"""
        try:
            if not self.sms_auth:
                return False
            
            code = auth_data.get('code')
            phone = auth_data.get('phone')
            
            if not code or not phone:
                return False
            
            # Validate SMS code
            result = self.sms_auth.validate_code(phone, code)
            return result.success
            
        except Exception as e:
            self.logger.error(f"SMS authentication failed for user {user_id}: {e}")
            return False
    
    async def _authenticate_hardware(self, user_id: str, auth_data: Dict[str, Any]) -> bool:
        """Authenticate user with hardware token"""
        try:
            if not self.hardware_auth:
                return False
            
            token_id = auth_data.get('token_id')
            challenge = auth_data.get('challenge')
            response = auth_data.get('response')
            
            if not token_id or not challenge or not response:
                return False
            
            # Validate hardware token response
            result = self.hardware_auth.validate_challenge_response(challenge, response, user_id)
            return result.success
            
        except Exception as e:
            self.logger.error(f"Hardware authentication failed for user {user_id}: {e}")
            return False
    
    def _generate_session_token(self, user_id: str) -> str:
        """Generate secure session token"""
        try:
            # Generate token data
            token_data = {
                'user_id': user_id,
                'timestamp': int(datetime.now().timestamp()),
                'nonce': hashlib.sha256(f"{user_id}_{datetime.now()}".encode()).hexdigest()[:16]
            }
            
            # Create token string
            token_string = json.dumps(token_data, sort_keys=True)
            
            # Hash token for security
            session_token = hashlib.sha256(token_string.encode()).hexdigest()
            
            return session_token
            
        except Exception as e:
            self.logger.error(f"Failed to generate session token: {e}")
            # Fallback to simple token
            return hashlib.sha256(f"{user_id}_{datetime.now()}".encode()).hexdigest()
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return session data"""
        try:
            if session_token not in self.active_sessions:
                return None
            
            session_data = self.active_sessions[session_token]
            
            # Check if session expired
            if datetime.now() > session_data['expires_at']:
                # Remove expired session
                del self.active_sessions[session_token]
                return None
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {e}")
            return None
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session token"""
        try:
            if session_token in self.active_sessions:
                del self.active_sessions[session_token]
                self.logger.info(f"Session {session_token} invalidated")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to invalidate session {session_token}: {e}")
            return False
    
    def get_user_mfa_status(self, user_id: str) -> Optional[UserMFAStatus]:
        """Get MFA status for a user"""
        try:
            if user_id not in self.user_mfa_configs:
                return None
            
            user_config = self.user_mfa_configs[user_id]
            
            # Determine security level
            required_methods = user_config.get('required_methods', [])
            if len(required_methods) == 1:
                security_level = MFALevel.BASIC
            elif len(required_methods) == 2:
                security_level = MFALevel.ENHANCED
            elif len(required_methods) >= 3:
                security_level = MFALevel.MAXIMUM
            else:
                security_level = MFALevel.BASIC
            
            # Get enabled methods
            methods_enabled = []
            for method_name, method_config in user_config.get('methods', {}).items():
                if method_config.get('setup_complete', False):
                    methods_enabled.append(method_name)
            
            return UserMFAStatus(
                user_id=user_id,
                mfa_enabled=user_config.get('setup_complete', False),
                methods_enabled=methods_enabled,
                setup_complete=user_config.get('setup_complete', False),
                last_used=user_config.get('last_used'),
                security_level=security_level,
                requires_setup=not user_config.get('setup_complete', False)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get MFA status for user {user_id}: {e}")
            return None
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_token, session_data in self.active_sessions.items():
                if current_time > session_data['expires_at']:
                    expired_sessions.append(session_token)
            
            for session_token in expired_sessions:
                del self.active_sessions[session_token]
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get MFA manager status"""
        return {
            'enabled': self.config.enabled,
            'required_for_all_users': self.config.required_for_all_users,
            'default_security_level': self.config.default_level.value,
            'available_methods': [method.value for method in self.config.methods],
            'total_users': len(self.user_mfa_configs),
            'active_sessions': len(self.active_sessions),
            'totp_available': self.totp_auth is not None,
            'sms_available': self.sms_auth is not None,
            'hardware_available': self.hardware_auth is not None,
            'max_failed_attempts': self.config.max_failed_attempts,
            'lockout_duration_minutes': self.config.lockout_duration_minutes,
            'session_timeout_hours': self.config.session_timeout_hours
        }
