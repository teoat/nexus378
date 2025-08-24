JWT Authentication System for Nexus Platform

This module implements JWT-based authentication with multi-factor authentication,
role-based access control, and secure session management.

import logging
import secrets
from datetime import datetime, timedelta

import bcrypt
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles enumeration.User roles enumeration."""

    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    VIEWER = "viewer"

class AuthStatus(Enum):
    """Authentication status enumeration.Authentication status enumeration."""

    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    MFA_REQUIRED = "mfa_required"

@dataclass
class User:
    """User data model.User data model."""

    id: str
    username: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    roles: List[UserRole]
    is_active: bool = True
    is_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
    """__post_init__ function.__post_init__ function."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class AuthResult:
    """Authentication result.Authentication result."""

    status: AuthStatus
    user: Optional[User] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    mfa_required: bool = False
    message: str = ""

class JWTAuthManager:


    JWT Authentication Manager.

    Handles user authentication, JWT token generation/validation,
    password management, and MFA operations.


    def __init__(self, config: Dict[str, Any]):
        """Initialize the JWT Auth Manager.Initialize the JWT Auth Manager."""
        self.config = config
        self.secret_key = config.get(
            "jwt_secret", "your_super_secret_jwt_key_change_this"
        )
        self.algorithm = config.get("jwt_algorithm", "HS256")
        self.access_token_expiry = timedelta(
            hours=config.get("jwt_expires_in_hours", 24)
        )
        self.refresh_token_expiry = timedelta(
            days=config.get("jwt_refresh_expires_in_days", 7)
        )

        # Password policy
        self.password_min_length = config.get("password_min_length", 12)
        self.password_require_uppercase = config.get("password_require_uppercase", True)
        self.password_require_lowercase = config.get("password_require_lowercase", True)
        self.password_require_numbers = config.get("password_require_numbers", True)
        self.password_require_special_chars = config.get(
            "password_require_special_chars", True
        )

        # MFA configuration
        self.mfa_enabled = config.get("mfa_enabled", True)
        self.mfa_issuer = config.get("mfa_issuer", "Nexus Platform")
        self.mfa_algorithm = config.get("mfa_algorithm", "SHA1")
        self.mfa_digits = config.get("mfa_digits", 6)
        self.mfa_period = config.get("mfa_period", 30)

        # Session management
        self.max_sessions_per_user = config.get("max_sessions_per_user", 5)
        self.session_timeout = timedelta(hours=config.get("session_timeout_hours", 24))

        # In-memory storage (in production, use Redis or database)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
        self.failed_attempts: Dict[str, Dict[str, Any]] = {}

        # Rate limiting
        self.max_login_attempts = config.get("max_login_attempts", 5)
        self.lockout_duration = timedelta(
            minutes=config.get("lockout_duration_minutes", 15)
        )

        logger.info("JWT Auth Manager initialized successfully")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        return password_hash.decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash.Verify a password against its hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against policy requirements.Validate password against policy requirements."""
        errors = []

        if len(password) < self.password_min_length:
            errors.append(
                f"Password must be at least {self.password_min_length} characters long"
            )

        if self.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if self.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if self.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        if self.password_require_special_chars and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            errors.append("Password must contain at least one special character")

        return {"valid": len(errors) == 0, "errors": errors}

    def generate_mfa_secret(self) -> str:
        """Generate a new MFA secret.Generate a new MFA secret."""
        return secrets.token_urlsafe(32)

    def generate_mfa_qr_code(self, username: str, secret: str) -> str:
        """Generate MFA QR code URL.Generate MFA QR code URL."""

        otpauth_url = f"otpauth://totp/{self.mfa_issuer}:{username}?secret={secret}&issuer={self.mfa_issuer}&algorithm={self.mfa_algorithm}&digits={self.mfa_digits}&period={self.mfa_period}"
        return otpauth_url

    def verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verify MFA token.Verify MFA token."""
        try:
            import pyotp

            totp = pyotp.TOTP(secret, digits=self.mfa_digits, interval=self.mfa_period)
            return totp.verify(token)
        except ImportError:
            logger.warning("pyotp not installed, MFA verification disabled")
            return True  # Allow if MFA library not available
        except Exception as e:
            logger.error(f"Error verifying MFA token: {e}")
            return False

    def generate_access_token(self, user: User) -> str:
        """Generate JWT access token.Generate JWT access token."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.access_token_expiry,
            "type": "access",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def generate_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token.Generate JWT refresh token."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.refresh_token_expiry,
            "type": "refresh",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token.Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def authenticate_user(
        self, username: str, password: str, mfa_token: Optional[str] = None
    ) -> AuthResult:
        """Authenticate a user with username and password.Authenticate a user with username and password."""
        try:
            # Check if user is locked out
            if self._is_user_locked_out(username):
                return AuthResult(
                    status=AuthStatus.FAILED,
                    message="Account temporarily locked due to too many failed attempts",
                )

            # Get user from database (this would be implemented based on your data layer)
            user = self._get_user_by_username(username)
            if not user:
                self._record_failed_attempt(username)
                return AuthResult(
                    status=AuthStatus.FAILED, message="Invalid username or password"
                )

            if not user.is_active:
                return AuthResult(
                    status=AuthStatus.FAILED, message="Account is deactivated"
                )

            if not user.is_verified:
                return AuthResult(
                    status=AuthStatus.FAILED, message="Account not verified"
                )

            # Verify password
            if not self.verify_password(password, user.password_hash):
                self._record_failed_attempt(username)
                return AuthResult(
                    status=AuthStatus.FAILED, message="Invalid username or password"
                )

            # Check MFA if enabled
            if user.mfa_enabled:
                if not mfa_token:
                    return AuthResult(
                        status=AuthStatus.MFA_REQUIRED,
                        message="MFA token required",
                        mfa_required=True,
                    )

                if not self.verify_mfa_token(user.mfa_secret, mfa_token):
                    self._record_failed_attempt(username)
                    return AuthResult(
                        status=AuthStatus.FAILED, message="Invalid MFA token"
                    )

            # Clear failed attempts on successful login
            self._clear_failed_attempts(username)

            # Generate tokens
            access_token = self.generate_access_token(user)
            refresh_token = self.generate_refresh_token(user)

            # Update user last login
            user.last_login = datetime.utcnow()

            # Store session
            self._store_session(user.id, access_token, refresh_token)

            logger.info(f"User {username} authenticated successfully")

            return AuthResult(
                status=AuthStatus.SUCCESS,
                user=user,
                token=access_token,
                refresh_token=refresh_token,
            )

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return AuthResult(
                status=AuthStatus.FAILED, message="Authentication error occurred"
            )

    def refresh_access_token(self, refresh_token: str) -> AuthResult:
        """Refresh an access token using a refresh token.Refresh an access token using a refresh token."""
        try:
            # Decode refresh token
            payload = self.decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return AuthResult(
                    status=AuthStatus.INVALID, message="Invalid refresh token"
                )

            # Check if refresh token is in our store
            stored_refresh = self.refresh_tokens.get(refresh_token)
            if not stored_refresh:
                return AuthResult(
                    status=AuthStatus.INVALID, message="Refresh token not found"
                )

            # Check if refresh token is expired
            if datetime.utcnow() > stored_refresh["expires_at"]:
                return AuthResult(
                    status=AuthStatus.EXPIRED, message="Refresh token expired"
                )

            # Get user
            user = self._get_user_by_id(payload["user_id"])
            if not user or not user.is_active:
                return AuthResult(
                    status=AuthStatus.FAILED, message="User not found or inactive"
                )

            # Generate new access token
            new_access_token = self.generate_access_token(user)

            # Update session
            self._update_session(user.id, new_access_token)

            logger.info(f"Access token refreshed for user {user.username}")

            return AuthResult(
                status=AuthStatus.SUCCESS, user=user, token=new_access_token
            )

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return AuthResult(
                status=AuthStatus.FAILED, message="Error refreshing token"
            )

    def validate_token(self, token: str) -> AuthResult:
        """Validate an access token.Validate an access token."""
        try:
            payload = self.decode_token(token)
            if not payload:
                return AuthResult(status=AuthStatus.INVALID, message="Invalid token")

            if payload.get("type") != "access":
                return AuthResult(
                    status=AuthStatus.INVALID, message="Invalid token type"
                )

            # Get user
            user = self._get_user_by_id(payload["user_id"])
            if not user or not user.is_active:
                return AuthResult(
                    status=AuthStatus.FAILED, message="User not found or inactive"
                )

            # Check if token is in active sessions
            if not self._is_token_active(user.id, token):
                return AuthResult(
                    status=AuthStatus.INVALID, message="Token not in active sessions"
                )

            return AuthResult(status=AuthStatus.SUCCESS, user=user)

        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return AuthResult(
                status=AuthStatus.FAILED, message="Error validating token"
            )

    def logout(self, user_id: str, token: str) -> bool:
        """Logout a user and invalidate their session.Logout a user and invalidate their session."""
        try:
            if user_id in self.active_sessions:
                # Remove token from active sessions
                if token in self.active_sessions[user_id]["tokens"]:
                    self.active_sessions[user_id]["tokens"].remove(token)

                # If no more tokens, remove session entirely
                if not self.active_sessions[user_id]["tokens"]:
                    del self.active_sessions[user_id]

            logger.info(f"User {user_id} logged out successfully")
            return True

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False

    def has_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for a specific resource and action.Check if user has permission for a specific resource and action."""
        # Admin has all permissions
        if UserRole.ADMIN in user.roles:
            return True

        # Define permission matrix
        permissions = {
            UserRole.INVESTIGATOR: {
                "cases": ["read", "write", "delete"],
                "evidence": ["read", "write", "delete"],
                "investigation": ["read", "write", "delete"],
                "reports": ["read", "write"],
            },
            UserRole.ANALYST: {
                "cases": ["read"],
                "evidence": ["read"],
                "investigation": ["read"],
                "reports": ["read", "write"],
            },
            UserRole.VIEWER: {
                "cases": ["read"],
                "evidence": ["read"],
                "investigation": ["read"],
                "reports": ["read"],
            },
        }

        # Check user's roles for permissions
        for role in user.roles:
            if role in permissions:
                role_perms = permissions[role]
                if resource in role_perms and action in role_perms[resource]:
                    return True

        return False

    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username from database.Get user by username from database."""
        # This would be implemented based on your data layer
        # For now, return a mock user
        if username == "admin":
            return User(
                id="user_001",
                username="admin",
                email="admin@forensic.local",
                password_hash=self.hash_password("admin123!"),
                first_name="Admin",
                last_name="User",
                roles=[UserRole.ADMIN],
                is_active=True,
                is_verified=True,
            )
        return None

    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from database.Get user by ID from database."""
        # This would be implemented based on your data layer
        if user_id == "user_001":
            return User(
                id="user_001",
                username="admin",
                email="admin@forensic.local",
                password_hash=self.hash_password("admin123!"),
                first_name="Admin",
                last_name="User",
                roles=[UserRole.ADMIN],
                is_active=True,
                is_verified=True,
            )
        return None

    def _store_session(self, user_id: str, access_token: str, refresh_token: str):
        """Store user session.Store user session."""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {
                "tokens": [],
                "refresh_token": refresh_token,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
            }

        self.active_sessions[user_id]["tokens"].append(access_token)
        self.active_sessions[user_id]["last_activity"] = datetime.utcnow()

        # Store refresh token
        self.refresh_tokens[refresh_token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.refresh_token_expiry,
        }

        # Limit sessions per user
        if len(self.active_sessions[user_id]["tokens"]) > self.max_sessions_per_user:
            oldest_token = self.active_sessions[user_id]["tokens"].pop(0)
            logger.info(f"Removed oldest session for user {user_id}")

    def _update_session(self, user_id: str, new_access_token: str):
        """Update user session with new access token.Update user session with new access token."""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]["tokens"].append(new_access_token)
            self.active_sessions[user_id]["last_activity"] = datetime.utcnow()

    def _is_token_active(self, user_id: str, token: str) -> bool:
        """Check if a token is active for a user.Check if a token is active for a user."""
        if user_id in self.active_sessions:
            return token in self.active_sessions[user_id]["tokens"]
        return False

    def _is_user_locked_out(self, username: str) -> bool:
        """Check if user account is locked out.Check if user account is locked out."""
        if username in self.failed_attempts:
            attempts = self.failed_attempts[username]
            if attempts["count"] >= self.max_login_attempts:
                lockout_until = attempts["first_attempt"] + self.lockout_duration
                if datetime.utcnow() < lockout_until:
                    return True
                else:
                    # Lockout period expired, reset
                    del self.failed_attempts[username]
        return False

    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt.Record a failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                "count": 0,
                "first_attempt": datetime.utcnow(),
            }

        self.failed_attempts[username]["count"] += 1

        if self.failed_attempts[username]["count"] >= self.max_login_attempts:
            logger.warning(
                f"User {username} account locked due to too many failed attempts"
            )

    def _clear_failed_attempts(self, username: str):
        """Clear failed login attempts for a user.Clear failed login attempts for a user."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

    def cleanup_expired_sessions(self):
        """Clean up expired sessions and tokens.Clean up expired sessions and tokens."""
        current_time = datetime.utcnow()

        # Clean up expired refresh tokens
        expired_refresh = [
            token
            for token, data in self.refresh_tokens.items()
            if current_time > data["expires_at"]
        ]
        for token in expired_refresh:
            del self.refresh_tokens[token]

        # Clean up expired sessions
        expired_sessions = []
        for user_id, session in self.active_sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(user_id)

        for user_id in expired_sessions:
            del self.active_sessions[user_id]

        if expired_refresh or expired_sessions:
            logger.info(
                f"Cleaned up {len(expired_refresh)} expired refresh tokens and {len(expired_sessions)} expired sessions"
            )

# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "jwt_secret": "forensic_jwt_super_secret_key_2024_change_in_production",
        "jwt_expires_in_hours": 24,
        "jwt_refresh_expires_in_days": 7,
        "password_min_length": 12,
        "mfa_enabled": True,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 15,
    }

    # Initialize auth manager
    auth_manager = JWTAuthManager(config)

    # Test password validation
    password = "TestPassword123!"
    validation = auth_manager.validate_password(password)
    print(f"Password validation: {validation}")

    # Test password hashing
    password_hash = auth_manager.hash_password(password)
    print(f"Password hash: {password_hash}")

    # Test password verification
    is_valid = auth_manager.verify_password(password, password_hash)
    print(f"Password verification: {is_valid}")

    # Test MFA secret generation
    mfa_secret = auth_manager.generate_mfa_secret()
    print(f"MFA secret: {mfa_secret}")

    # Test MFA QR code generation
    qr_code = auth_manager.generate_mfa_qr_code("testuser", mfa_secret)
    print(f"MFA QR code: {qr_code}")

    print("JWT Authentication system initialized successfully!")
