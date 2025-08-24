"""
Configuration for the API Gateway
"""

import os
import secrets

# JWT Configuration
# Securely handle JWT_SECRET: require in production, generate random in development
_jwt_secret_env = os.environ.get("JWT_SECRET")
_is_debug = os.environ.get("GATEWAY_DEBUG", "false").lower() == "true"
if _jwt_secret_env:
    JWT_SECRET = _jwt_secret_env
elif _is_debug:
    # Generate a random secret for development if not set
    JWT_SECRET = secrets.token_urlsafe(32)
else:
    raise RuntimeError(
        "JWT_SECRET environment variable must be set in production for security reasons."
    )
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_IN_HOURS = int(os.environ.get("JWT_EXPIRES_IN_HOURS", 24))
JWT_REFRESH_EXPIRES_IN_DAYS = int(os.environ.get("JWT_REFRESH_EXPIRES_IN_DAYS", 7))

# Password Policy
PASSWORD_MIN_LENGTH = int(os.environ.get("PASSWORD_MIN_LENGTH", 12))
PASSWORD_REQUIRE_UPPERCASE = (
    os.environ.get("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
)
PASSWORD_REQUIRE_LOWERCASE = (
    os.environ.get("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
)
PASSWORD_REQUIRE_NUMBERS = (
    os.environ.get("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true"
)
PASSWORD_REQUIRE_SPECIAL_CHARS = (
    os.environ.get("PASSWORD_REQUIRE_SPECIAL_CHARS", "true").lower() == "true"
)

# MFA Configuration
MFA_ENABLED = os.environ.get("MFA_ENABLED", "true").lower() == "true"
MFA_ISSUER = os.environ.get("MFA_ISSUER", "Forensic Reconciliation Platform")

# Session Management
MAX_SESSIONS_PER_USER = int(os.environ.get("MAX_SESSIONS_PER_USER", 5))
SESSION_TIMEOUT_HOURS = int(os.environ.get("SESSION_TIMEOUT_HOURS", 24))

# Rate Limiting Configuration
DEFAULT_MAX_REQUESTS = int(os.environ.get("DEFAULT_MAX_REQUESTS", 100))
DEFAULT_TIME_WINDOW_SECONDS = int(os.environ.get("DEFAULT_TIME_WINDOW_SECONDS", 60))
DEFAULT_BURST_LIMIT = int(os.environ.get("DEFAULT_BURST_LIMIT", 10))
ENABLE_ADAPTIVE_LIMITING = (
    os.environ.get("ENABLE_ADAPTIVE_LIMITING", "true").lower() == "true"
)

# API Gateway Configuration
GATEWAY_HOST = os.environ.get("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.environ.get("GATEWAY_PORT", 8080))
GATEWAY_DEBUG = os.environ.get("GATEWAY_DEBUG", "false").lower() == "true"
MAX_REQUEST_SIZE_MB = int(os.environ.get("MAX_REQUEST_SIZE_MB", 10))


def get_jwt_config():
    """Returns a dictionary with JWT configuration."""
    return {
        "jwt_secret": JWT_SECRET,
        "jwt_algorithm": JWT_ALGORITHM,
        "jwt_expires_in_hours": JWT_EXPIRES_IN_HOURS,
        "jwt_refresh_expires_in_days": JWT_REFRESH_EXPIRES_IN_DAYS,
        "password_min_length": PASSWORD_MIN_LENGTH,
        "password_require_uppercase": PASSWORD_REQUIRE_UPPERCASE,
        "password_require_lowercase": PASSWORD_REQUIRE_LOWERCASE,
        "password_require_numbers": PASSWORD_REQUIRE_NUMBERS,
        "password_require_special_chars": PASSWORD_REQUIRE_SPECIAL_CHARS,
        "mfa_enabled": MFA_ENABLED,
        "mfa_issuer": MFA_ISSUER,
        "max_sessions_per_user": MAX_SESSIONS_PER_USER,
        "session_timeout_hours": SESSION_TIMEOUT_HOURS,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 15,
    }


def get_rate_limiter_config():
    """Returns a dictionary with Rate Limiter configuration."""
    return {
        "default_max_requests": DEFAULT_MAX_REQUESTS,
        "default_time_window": DEFAULT_TIME_WINDOW_SECONDS,
        "default_burst_limit": DEFAULT_BURST_LIMIT,
        "enable_adaptive_limiting": ENABLE_ADAPTIVE_LIMITING,
    }


def get_api_gateway_config():
    """Returns a dictionary with API Gateway configuration."""
    return {
        "host": GATEWAY_HOST,
        "port": GATEWAY_PORT,
        "debug": GATEWAY_DEBUG,
        "max_request_size": MAX_REQUEST_SIZE_MB * 1024 * 1024,
    }
