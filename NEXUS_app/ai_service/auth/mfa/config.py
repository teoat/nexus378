MFA Configuration Module

Configuration settings for Multi-Factor Authentication system

import os

class MFAMethod(Enum):

    TOTP = "totp"
    SMS = "sms"
    HARDWARE = "hardware"
    EMAIL = "email"

class MFALevel(Enum):

    BASIC = "basic"  # Single MFA method
    ENHANCED = "enhanced"  # Two MFA methods
    MAXIMUM = "maximum"  # Three MFA methods

@dataclass
class TOTPConfig:

    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30  # seconds
    window: int = 1  # time window for validation
    issuer: str = "Nexus Platform"
    secret_length: int = 32

@dataclass
class SMSConfig:

    provider: str = "twilio"  # Default SMS provider
    message_template: str = "Your verification code is: {code}"
    code_length: int = 6
    expiration_minutes: int = 10
    max_attempts: int = 3
    cooldown_seconds: int = 60

@dataclass
class HardwareConfig:

    db_connection_string: str = ""
    redis_connection_string: str = ""

    # Logging
    log_level: str = "INFO"
    audit_logging: bool = True

    def __post_init__(self):

    def from_environment(cls) -> "MFAConfig":

        config.enabled = os.getenv("MFA_ENABLED", "true").lower() == "true"
        config.required_for_all_users = (
            os.getenv("MFA_REQUIRED_FOR_ALL", "true").lower() == "true"
        )

        # TOTP settings
        if os.getenv("TOTP_ALGORITHM"):
            config.totp.algorithm = os.getenv("TOTP_ALGORITHM")
        if os.getenv("TOTP_DIGITS"):
            config.totp.digits = int(os.getenv("TOTP_DIGITS"))
        if os.getenv("TOTP_PERIOD"):
            config.totp.period = int(os.getenv("TOTP_PERIOD"))

        # SMS settings
        if os.getenv("SMS_PROVIDER"):
            config.sms.provider = os.getenv("SMS_PROVIDER")
        if os.getenv("SMS_CODE_LENGTH"):
            config.sms.code_length = int(os.getenv("SMS_CODE_LENGTH"))

        # Database connections
        if os.getenv("MFA_DB_CONNECTION"):
            config.db_connection_string = os.getenv("MFA_DB_CONNECTION")
        if os.getenv("MFA_REDIS_CONNECTION"):
            config.redis_connection_string = os.getenv("MFA_REDIS_CONNECTION")

        return config

    def to_dict(self) -> Dict[str, Any]:

            "enabled": self.enabled,
            "required_for_all_users": self.required_for_all_users,
            "methods": [method.value for method in self.methods],
            "default_level": self.default_level.value,
            "totp": {
                "algorithm": self.totp.algorithm,
                "digits": self.totp.digits,
                "period": self.totp.period,
                "window": self.totp.window,
                "issuer": self.totp.issuer,
                "secret_length": self.totp.secret_length,
            },
            "sms": {
                "provider": self.sms.provider,
                "message_template": self.sms.message_template,
                "code_length": self.sms.code_length,
                "expiration_minutes": self.sms.expiration_minutes,
                "max_attempts": self.sms.max_attempts,
                "cooldown_seconds": self.sms.cooldown_seconds,
            },
            "hardware": {
                "supported_types": self.hardware.supported_types or [],
                "challenge_response": self.hardware.challenge_response,
                "timeout_seconds": self.hardware.timeout_seconds,
                "max_retries": self.hardware.max_retries,
            },
            "max_failed_attempts": self.max_failed_attempts,
            "lockout_duration_minutes": self.lockout_duration_minutes,
            "session_timeout_hours": self.session_timeout_hours,
            "log_level": self.log_level,
            "audit_logging": self.audit_logging,
        }

    def validate(self) -> bool:

                assert self.totp.digits in [6, 8], "TOTP digits must be 6 or 8"
                assert self.totp.period >= 15, "TOTP period must be at least 15 seconds"
                assert self.totp.algorithm in [
                    "SHA1",
                    "SHA256",
                    "SHA512",
                ], "Invalid TOTP algorithm"

            # Validate SMS settings
            if MFAMethod.SMS in self.methods:
                assert (
                    self.sms.code_length >= 4
                ), "SMS code length must be at least 4 digits"
                assert (
                    self.sms.expiration_minutes >= 1
                ), "SMS expiration must be at least 1 minute"
                assert self.sms.max_attempts >= 1, "SMS max attempts must be at least 1"

            # Validate general settings
            assert (
                self.max_failed_attempts >= 1
            ), "Max failed attempts must be at least 1"
            assert (
                self.lockout_duration_minutes >= 1
            ), "Lockout duration must be at least 1 minute"
            assert (
                self.session_timeout_hours >= 1
            ), "Session timeout must be at least 1 hour"

            return True

        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False
