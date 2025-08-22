"""
Authentication Middleware - JWT Validation and RBAC Enforcement

This module implements the AuthMiddleware class that provides
comprehensive authentication and authorization capabilities for the
forensic platform API gateway.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import uuid
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import bcrypt

from ..ai_service.taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class TokenType(Enum):
    """Types of authentication tokens."""
    ACCESS_TOKEN = "access_token"                           # Short-lived access token
    REFRESH_TOKEN = "refresh_token"                         # Long-lived refresh token
    API_KEY = "api_key"                                     # API key token
    SESSION_TOKEN = "session_token"                         # Session-based token


class PermissionLevel(Enum):
    """Permission levels for RBAC."""
    NONE = "none"                                           # No permissions
    READ = "read"                                           # Read-only access
    WRITE = "write"                                         # Write access
    ADMIN = "admin"                                         # Administrative access
    SUPER_ADMIN = "super_admin"                             # Super administrative access


class AuthStatus(Enum):
    """Authentication status."""
    AUTHENTICATED = "authenticated"                          # Successfully authenticated
    UNAUTHENTICATED = "unauthenticated"                      # Not authenticated
    UNAUTHORIZED = "unauthorized"                            # Authenticated but not authorized
    TOKEN_EXPIRED = "token_expired"                          # Token has expired
    TOKEN_INVALID = "token_invalid"                          # Token is invalid
    RATE_LIMITED = "rate_limited"                            # Rate limit exceeded


@dataclass
class UserSession:
    """A user session."""
    
    session_id: str
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    
    success: bool
    status: AuthStatus
    user_id: Optional[str]
    username: Optional[str]
    roles: List[str]
    permissions: List[str]
    token_info: Optional[Dict[str, Any]]
    error_message: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Permission:
    """A permission definition."""
    
    permission_id: str
    permission_name: str
    resource: str
    action: str
    permission_level: PermissionLevel
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """A role definition."""
    
    role_id: str
    role_name: str
    description: str
    permissions: List[str]
    is_active: bool
    created_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthMiddleware:
    """
    Comprehensive authentication and authorization middleware.
    
    The AuthMiddleware is responsible for:
    - JWT token validation and verification
    - Role-based access control (RBAC)
    - Permission checking and enforcement
    - Session management and tracking
    - Security policy enforcement
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the AuthMiddleware."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.jwt_secret = config.get('jwt_secret', 'forensic_secure_2024')
        self.jwt_algorithm = config.get('jwt_algorithm', 'HS256')
        self.access_token_expiry = config.get('access_token_expiry', 3600)  # 1 hour
        self.refresh_token_expiry = config.get('refresh_token_expiry', 86400 * 7)  # 7 days
        self.max_failed_attempts = config.get('max_failed_attempts', 5)
        self.lockout_duration = config.get('lockout_duration', 900)  # 15 minutes
        
        # User management
        self.users: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.locked_accounts: Dict[str, datetime] = {}
        
        # Role and permission management
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.role_permissions: Dict[str, List[str]] = defaultdict(list)
        
        # Security tracking
        self.auth_attempts: Dict[str, List[AuthResult]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Performance tracking
        self.total_auth_attempts = 0
        self.successful_auths = 0
        self.failed_auths = 0
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        # Initialize auth components
        self._initialize_auth_components()
        
        self.logger.info("AuthMiddleware initialized successfully")
    
    async def start(self):
        """Start the AuthMiddleware."""
        self.logger.info("Starting AuthMiddleware...")
        
        # Initialize auth components
        await self._initialize_auth_components()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_sessions())
        asyncio.create_task(self._cleanup_failed_attempts())
        
        self.logger.info("AuthMiddleware started successfully")
    
    async def stop(self):
        """Stop the AuthMiddleware."""
        self.logger.info("Stopping AuthMiddleware...")
        self.logger.info("AuthMiddleware stopped")
    
    def _initialize_auth_components(self):
        """Initialize authentication components."""
        try:
            # Initialize default users, roles, and permissions
            self._initialize_default_users()
            self._initialize_default_roles()
            self._initialize_default_permissions()
            
            self.logger.info("Auth components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing auth components: {e}")
    
    def _initialize_default_users(self):
        """Initialize default users."""
        try:
            # Create default admin user
            admin_user = {
                'user_id': 'admin_001',
                'username': 'admin',
                'email': 'admin@forensic.com',
                'password_hash': self._hash_password('admin_password_2024'),
                'roles': ['super_admin'],
                'is_active': True,
                'created_date': datetime.utcnow(),
                'last_login': None
            }
            
            self.users[admin_user['user_id']] = admin_user
            
            # Create default investigator user
            investigator_user = {
                'user_id': 'investigator_001',
                'username': 'investigator',
                'email': 'investigator@forensic.com',
                'password_hash': self._hash_password('investigator_password_2024'),
                'roles': ['investigator'],
                'is_active': True,
                'created_date': datetime.utcnow(),
                'last_login': None
            }
            
            self.users[investigator_user['user_id']] = investigator_user
            
            self.logger.info("Default users initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing default users: {e}")
    
    def _initialize_default_roles(self):
        """Initialize default roles."""
        try:
            # Super Admin role
            super_admin_role = Role(
                role_id='super_admin',
                role_name='Super Administrator',
                description='Full system access and control',
                permissions=['*'],  # All permissions
                is_active=True,
                created_date=datetime.utcnow()
            )
            
            # Admin role
            admin_role = Role(
                role_id='admin',
                role_name='Administrator',
                description='System administration and management',
                permissions=['user_management', 'system_config', 'audit_logs'],
                is_active=True,
                created_date=datetime.utcnow()
            )
            
            # Investigator role
            investigator_role = Role(
                role_id='investigator',
                role_name='Investigator',
                description='Case investigation and analysis',
                permissions=['case_read', 'case_write', 'evidence_read', 'evidence_write'],
                is_active=True,
                created_date=datetime.utcnow()
            )
            
            # Analyst role
            analyst_role = Role(
                role_id='analyst',
                role_name='Analyst',
                description='Data analysis and reporting',
                permissions=['case_read', 'evidence_read', 'report_read', 'report_write'],
                is_active=True,
                created_date=datetime.utcnow()
            )
            
            # Store roles
            self.roles[super_admin_role.role_id] = super_admin_role
            self.roles[admin_role.role_id] = admin_role
            self.roles[investigator_role.role_id] = investigator_role
            self.roles[analyst_role.role_id] = analyst_role
            
            self.logger.info("Default roles initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing default roles: {e}")
    
    def _initialize_default_permissions(self):
        """Initialize default permissions."""
        try:
            # User management permissions
            user_permissions = [
                Permission('user_001', 'user_management', 'users', 'manage', PermissionLevel.ADMIN, 'Manage user accounts'),
                Permission('user_002', 'user_read', 'users', 'read', PermissionLevel.READ, 'Read user information'),
                Permission('user_003', 'user_write', 'users', 'write', PermissionLevel.WRITE, 'Create and modify users')
            ]
            
            # Case management permissions
            case_permissions = [
                Permission('case_001', 'case_read', 'cases', 'read', PermissionLevel.READ, 'Read case information'),
                Permission('case_002', 'case_write', 'cases', 'write', PermissionLevel.WRITE, 'Create and modify cases'),
                Permission('case_003', 'case_delete', 'cases', 'delete', PermissionLevel.ADMIN, 'Delete cases')
            ]
            
            # Evidence management permissions
            evidence_permissions = [
                Permission('evidence_001', 'evidence_read', 'evidence', 'read', PermissionLevel.READ, 'Read evidence information'),
                Permission('evidence_002', 'evidence_write', 'evidence', 'write', PermissionLevel.WRITE, 'Create and modify evidence'),
                Permission('evidence_003', 'evidence_delete', 'evidence', 'delete', PermissionLevel.ADMIN, 'Delete evidence')
            ]
            
            # System permissions
            system_permissions = [
                Permission('system_001', 'system_config', 'system', 'configure', PermissionLevel.ADMIN, 'Configure system settings'),
                Permission('system_002', 'audit_logs', 'system', 'audit', PermissionLevel.ADMIN, 'Access audit logs'),
                Permission('system_003', 'system_monitoring', 'system', 'monitor', PermissionLevel.ADMIN, 'Monitor system health')
            ]
            
            # Store all permissions
            all_permissions = user_permissions + case_permissions + evidence_permissions + system_permissions
            
            for permission in all_permissions:
                self.permissions[permission.permission_id] = permission
            
            self.logger.info(f"Default permissions initialized: {len(all_permissions)} permissions")
            
        except Exception as e:
            self.logger.error(f"Error initializing default permissions: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        try:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            return password_hash.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error hashing password: {e}")
            raise
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Error verifying password: {e}")
            return False
    
    async def authenticate_user(self, username: str, password: str, ip_address: str = None,
                               user_agent: str = None) -> AuthResult:
        """Authenticate a user with username and password."""
        try:
            self.total_auth_attempts += 1
            
            # Check if account is locked
            if username in self.locked_accounts:
                lockout_time = self.locked_accounts[username]
                if datetime.utcnow() < lockout_time:
                    remaining_time = (lockout_time - datetime.utcnow()).total_seconds()
                    return AuthResult(
                        success=False,
                        status=AuthStatus.RATE_LIMITED,
                        user_id=None,
                        username=username,
                        roles=[],
                        permissions=[],
                        token_info=None,
                        error_message=f"Account locked. Try again in {int(remaining_time)} seconds."
                    )
                else:
                    # Remove lockout
                    del self.locked_accounts[username]
            
            # Find user
            user = None
            for user_data in self.users.values():
                if user_data['username'] == username:
                    user = user_data
                    break
            
            if not user:
                await self._record_failed_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    status=AuthStatus.UNAUTHENTICATED,
                    user_id=None,
                    username=username,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid username or password"
                )
            
            # Check if user is active
            if not user['is_active']:
                return AuthResult(
                    success=False,
                    status=AuthStatus.UNAUTHORIZED,
                    user_id=None,
                    username=username,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Account is deactivated"
                )
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                await self._record_failed_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    status=AuthStatus.UNAUTHENTICATED,
                    user_id=None,
                    username=username,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid username or password"
                )
            
            # Authentication successful
            self.successful_auths += 1
            
            # Clear failed attempts
            if username in self.failed_attempts:
                del self.failed_attempts[username]
            
            # Update last login
            user['last_login'] = datetime.utcnow()
            
            # Get user roles and permissions
            roles = user['roles']
            permissions = self._get_user_permissions(roles)
            
            # Generate tokens
            access_token = self._generate_access_token(user['user_id'], username, roles)
            refresh_token = self._generate_refresh_token(user['user_id'], username)
            
            # Create user session
            session = UserSession(
                session_id=str(uuid.uuid4()),
                user_id=user['user_id'],
                username=username,
                email=user['email'],
                roles=roles,
                permissions=permissions,
                token_type=TokenType.ACCESS_TOKEN,
                issued_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=self.access_token_expiry),
                last_activity=datetime.utcnow(),
                ip_address=ip_address or 'unknown',
                user_agent=user_agent or 'unknown'
            )
            
            # Store session
            self.user_sessions[session.session_id] = session
            
            # Create auth result
            auth_result = AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                user_id=user['user_id'],
                username=username,
                roles=roles,
                permissions=permissions,
                token_info={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': self.access_token_expiry,
                    'token_type': 'Bearer'
                },
                error_message=None
            )
            
            # Record successful authentication
            self.auth_attempts[username].append(auth_result)
            
            self.logger.info(f"User {username} authenticated successfully")
            
            return auth_result
            
        except Exception as e:
            self.failed_auths += 1
            self.logger.error(f"Error authenticating user {username}: {e}")
            return AuthResult(
                success=False,
                status=AuthStatus.UNAUTHENTICATED,
                user_id=None,
                username=username,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Authentication error occurred"
            )
    
    async def _record_failed_attempt(self, username: str, ip_address: str = None):
        """Record a failed authentication attempt."""
        try:
            current_time = datetime.utcnow()
            self.failed_attempts[username].append(current_time)
            
            # Clean old failed attempts
            cutoff_time = current_time - timedelta(minutes=15)
            self.failed_attempts[username] = [
                attempt for attempt in self.failed_attempts[username]
                if attempt > cutoff_time
            ]
            
            # Check if account should be locked
            if len(self.failed_attempts[username]) >= self.max_failed_attempts:
                lockout_until = current_time + timedelta(seconds=self.lockout_duration)
                self.locked_accounts[username] = lockout_until
                self.logger.warning(f"Account {username} locked due to multiple failed attempts")
            
            self.failed_auths += 1
            
        except Exception as e:
            self.logger.error(f"Error recording failed attempt: {e}")
    
    def _get_user_permissions(self, roles: List[str]) -> List[str]:
        """Get all permissions for a user based on their roles."""
        try:
            permissions = set()
            
            for role_id in roles:
                if role_id in self.roles:
                    role = self.roles[role_id]
                    if role.is_active:
                        # Check for wildcard permissions
                        if '*' in role.permissions:
                            # Super admin - all permissions
                            permissions.update([perm.permission_name for perm in self.permissions.values()])
                        else:
                            # Regular role permissions
                            permissions.update(role.permissions)
            
            return list(permissions)
            
        except Exception as e:
            self.logger.error(f"Error getting user permissions: {e}")
            return []
    
    def _generate_access_token(self, user_id: str, username: str, roles: List[str]) -> str:
        """Generate a JWT access token."""
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'roles': roles,
                'token_type': TokenType.ACCESS_TOKEN.value,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expiry)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            self.logger.error(f"Error generating access token: {e}")
            raise
    
    def _generate_refresh_token(self, user_id: str, username: str) -> str:
        """Generate a JWT refresh token."""
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'token_type': TokenType.REFRESH_TOKEN.value,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expiry)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            self.logger.error(f"Error generating refresh token: {e}")
            raise
    
    async def validate_token(self, token: str) -> AuthResult:
        """Validate a JWT token."""
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check token type
            token_type = payload.get('token_type')
            if token_type != TokenType.ACCESS_TOKEN.value:
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_INVALID,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid token type"
                )
            
            # Check if token is expired
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_EXPIRED,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Token has expired"
                )
            
            # Get user information
            user_id = payload.get('user_id')
            username = payload.get('username')
            roles = payload.get('roles', [])
            
            if not user_id or not username:
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_INVALID,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid token payload"
                )
            
            # Get user permissions
            permissions = self._get_user_permissions(roles)
            
            # Create auth result
            auth_result = AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                user_id=user_id,
                username=username,
                roles=roles,
                permissions=permissions,
                token_info={'token_type': 'Bearer'},
                error_message=None
            )
            
            return auth_result
            
        except jwt.ExpiredSignatureError:
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_EXPIRED,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Token has expired"
            )
        except jwt.InvalidTokenError:
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_INVALID,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Invalid token"
            )
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_INVALID,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Token validation error"
            )
    
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if a user has permission to perform an action on a resource."""
        try:
            # Find user
            user = None
            for user_data in self.users.values():
                if user_data['user_id'] == user_id:
                    user = user_data
                    break
            
            if not user or not user['is_active']:
                return False
            
            # Get user permissions
            roles = user['roles']
            permissions = self._get_user_permissions(roles)
            
            # Check for wildcard permissions
            if '*' in permissions:
                return True
            
            # Check specific permission
            permission_key = f"{resource}_{action}"
            return permission_key in permissions
            
        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False
    
    async def refresh_access_token(self, refresh_token: str) -> AuthResult:
        """Refresh an access token using a refresh token."""
        try:
            # Validate refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check token type
            token_type = payload.get('token_type')
            if token_type != TokenType.REFRESH_TOKEN.value:
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_INVALID,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid refresh token"
                )
            
            # Check if token is expired
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_EXPIRED,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Refresh token has expired"
                )
            
            # Get user information
            user_id = payload.get('user_id')
            username = payload.get('username')
            
            if not user_id or not username:
                return AuthResult(
                    success=False,
                    status=AuthStatus.TOKEN_INVALID,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="Invalid refresh token payload"
                )
            
            # Find user
            user = None
            for user_data in self.users.values():
                if user_data['user_id'] == user_id:
                    user = user_data
                    break
            
            if not user or not user['is_active']:
                return AuthResult(
                    success=False,
                    status=AuthStatus.UNAUTHORIZED,
                    user_id=None,
                    username=None,
                    roles=[],
                    permissions=[],
                    token_info=None,
                    error_message="User not found or inactive"
                )
            
            # Generate new access token
            roles = user['roles']
            permissions = self._get_user_permissions(roles)
            
            new_access_token = self._generate_access_token(user_id, username, roles)
            
            # Create auth result
            auth_result = AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                user_id=user_id,
                username=username,
                roles=roles,
                permissions=permissions,
                token_info={
                    'access_token': new_access_token,
                    'expires_in': self.access_token_expiry,
                    'token_type': 'Bearer'
                },
                error_message=None
            )
            
            return auth_result
            
        except jwt.ExpiredSignatureError:
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_EXPIRED,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_INVALID,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Invalid refresh token"
            )
        except Exception as e:
            self.logger.error(f"Error refreshing access token: {e}")
            return AuthResult(
                success=False,
                status=AuthStatus.TOKEN_INVALID,
                user_id=None,
                username=None,
                roles=[],
                permissions=[],
                token_info=None,
                error_message="Token refresh error"
            )
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired user sessions."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.user_sessions.items():
                    if session.expires_at < current_time:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.user_sessions[session_id]
                
                if expired_sessions:
                    self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning up expired sessions: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_failed_attempts(self):
        """Clean up old failed authentication attempts."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(minutes=15)
                
                # Clean up old failed attempts
                for username in list(self.failed_attempts.keys()):
                    self.failed_attempts[username] = [
                        attempt for attempt in self.failed_attempts[username]
                        if attempt > cutoff_time
                    ]
                    
                    # Remove empty entries
                    if not self.failed_attempts[username]:
                        del self.failed_attempts[username]
                
                # Clean up expired lockouts
                expired_lockouts = [
                    username for username, lockout_time in self.locked_accounts.items()
                    if lockout_time < current_time
                ]
                
                for username in expired_lockouts:
                    del self.locked_accounts[username]
                
                if expired_lockouts:
                    self.logger.info(f"Cleaned up {len(expired_lockouts)} expired lockouts")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning up failed attempts: {e}")
                await asyncio.sleep(300)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_auth_attempts': self.total_auth_attempts,
            'successful_auths': self.successful_auths,
            'failed_auths': self.failed_auths,
            'success_rate': self.successful_auths / self.total_auth_attempts if self.total_auth_attempts > 0 else 0,
            'active_sessions': len(self.user_sessions),
            'locked_accounts': len(self.locked_accounts),
            'total_users': len(self.users),
            'total_roles': len(self.roles),
            'total_permissions': len(self.permissions),
            'token_types_supported': [t.value for t in TokenType],
            'permission_levels_supported': [l.value for l in PermissionLevel]
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'jwt_secret': 'forensic_secure_2024',
        'jwt_algorithm': 'HS256',
        'access_token_expiry': 3600,
        'refresh_token_expiry': 86400 * 7,
        'max_failed_attempts': 5,
        'lockout_duration': 900
    }
    
    # Initialize auth middleware
    auth_middleware = AuthMiddleware(config)
    
    print("AuthMiddleware system initialized successfully!")
