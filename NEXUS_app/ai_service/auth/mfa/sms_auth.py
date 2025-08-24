SMS Authentication Service
Handles SMS-based multi-factor authentication

import asyncio
import logging
import random
import string
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SMSStatus(Enum):
    """SMS verification statusSMS verification status"""

    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"

@dataclass
class SMSCode:
    """SMS verification codeSMS verification code"""

    id: str
    user_id: str
    phone_number: str
    code: str
    created_at: datetime
    expires_at: datetime
    status: SMSStatus
    attempts: int
    max_attempts: int = 3

class SMSService:
    """SMS authentication service implementationSMS authentication service implementation"""

    def __init__(self):
    """__init__ function.__init__ function."""
        self.sms_codes: Dict[str, SMSCode] = {}
        self.sms_config = {
            "code_length": 6,
            "expiry_minutes": 10,
            "max_attempts": 3,
            "resend_cooldown": 60,  # seconds
            "max_codes_per_hour": 5,
        }

        # Mock SMS provider (replace with actual SMS service)
        self.sms_provider = MockSMSProvider()

        logger.info("SMS service initialized")

    async def generate_sms_code(self, user_id: str, phone_number: str) -> Optional[str]:
        """Generate and send SMS verification codeGenerate and send SMS verification code"""
        try:
            # Check rate limiting
            if not self._check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return None

            # Check cooldown period
            if not self._check_cooldown(user_id):
                logger.warning(f"Cooldown period active for user {user_id}")
                return None

            # Generate verification code
            code = self._generate_verification_code()

            # Create SMS code record
            sms_code = SMSCode(
                id=self._generate_code_id(),
                user_id=user_id,
                phone_number=phone_number,
                code=code,
                created_at=datetime.now(),
                expires_at=datetime.now()
                + timedelta(minutes=self.sms_config["expiry_minutes"]),
                status=SMSStatus.PENDING,
                attempts=0,
                max_attempts=self.sms_config["max_attempts"],
            )

            # Store SMS code
            self.sms_codes[sms_code.id] = sms_code

            # Send SMS (async)
            await self._send_sms(phone_number, code)

            logger.info(f"Generated SMS code for user {user_id} to {phone_number}")
            return sms_code.id

        except Exception as e:
            logger.error(f"Failed to generate SMS code: {e}")
            return None

    async def verify_sms_code(self, user_id: str, code: str) -> bool:
        """Verify SMS verification codeVerify SMS verification code"""
        try:
            # Find active SMS code for user
            active_code = self._find_active_code(user_id)
            if not active_code:
                logger.warning(f"No active SMS code found for user {user_id}")
                return False

            # Check if expired
            if datetime.now() > active_code.expires_at:
                active_code.status = SMSStatus.EXPIRED
                logger.warning(f"SMS code expired for user {user_id}")
                return False

            # Check attempts
            if active_code.attempts >= active_code.max_attempts:
                active_code.status = SMSStatus.FAILED
                logger.warning(f"Maximum attempts exceeded for user {user_id}")
                return False

            # Increment attempts
            active_code.attempts += 1

            # Verify code
            if active_code.code == code:
                active_code.status = SMSStatus.VERIFIED
                logger.info(f"SMS code verified for user {user_id}")
                return True
            else:
                if active_code.attempts >= active_code.max_attempts:
                    active_code.status = SMSStatus.FAILED
                    return False
                logger.warning(f"Invalid SMS code for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to verify SMS code: {e}")
            return False

    def _generate_verification_code(self) -> str:
        """Generate random verification codeGenerate random verification code"""
        return "".join(random.choices(string.digits, k=self.sms_config["code_length"]))

    def _generate_code_id(self) -> str:
        """Generate unique code IDGenerate unique code ID"""
        import uuid

        return str(uuid.uuid4())

    def _find_active_code(self, user_id: str) -> Optional[SMSCode]:
        """Find active SMS code for userFind active SMS code for user"""
        for code in self.sms_codes.values():
            if (
                code.user_id == user_id
                and code.status == SMSStatus.PENDING
                and datetime.now() <= code.expires_at
            ):
                return code
        return None

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limitCheck if user has exceeded rate limit"""
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)

        # Count codes generated in last hour
        codes_count = sum(
            1
            for code in self.sms_codes.values()
            if code.user_id == user_id and code.created_at >= hour_ago
        )

        return codes_count < self.sms_config["max_codes_per_hour"]

    def _check_cooldown(self, user_id: str) -> bool:
        """Check if user is in cooldown periodCheck if user is in cooldown period"""
        current_time = datetime.now()
        cooldown_ago = current_time - timedelta(
            seconds=self.sms_config["resend_cooldown"]
        )

        # Check if last code was sent within cooldown period
        for code in self.sms_codes.values():
            if code.user_id == user_id and code.created_at >= cooldown_ago:
                return False

        return True

    async def _send_sms(self, phone_number: str, code: str):
        """Send SMS with verification codeSend SMS with verification code"""
        try:
            # Use mock SMS provider for development
            await self.sms_provider.send_sms(
                phone_number, f"Your verification code is: {code}"
            )
            logger.info(f"SMS sent to {phone_number}")

        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise

    async def resend_sms_code(self, user_id: str) -> Optional[str]:
        """Resend SMS verification codeResend SMS verification code"""
        try:
            # Find last active code
            last_code = None
            for code in self.sms_codes.values():
                if code.user_id == user_id:
                    if not last_code or code.created_at > last_code.created_at:
                        last_code = code

            if not last_code:
                logger.warning(f"No previous SMS code found for user {user_id}")
                return None

            # Check cooldown
            if not self._check_cooldown(user_id):
                logger.warning(f"Cooldown period active for user {user_id}")
                return None

            # Generate new code
            return await self.generate_sms_code(user_id, last_code.phone_number)

        except Exception as e:
            logger.error(f"Failed to resend SMS code: {e}")
            return None

    def get_sms_status(self, user_id: str) -> Dict[str, any]:
        """Get SMS status for userGet SMS status for user"""
        try:
            active_code = self._find_active_code(user_id)
            if not active_code:
                return {"status": "no_active_code"}

            return {
                "status": active_code.status.value,
                "phone_number": active_code.phone_number,
                "expires_at": active_code.expires_at.isoformat(),
                "attempts": active_code.attempts,
                "max_attempts": active_code.max_attempts,
            }

        except Exception as e:
            logger.error(f"Failed to get SMS status: {e}")
            return {"status": "error", "error": str(e)}

    async def cleanup_expired_codes(self):
        """Remove expired SMS codesRemove expired SMS codes"""
        try:
            current_time = datetime.now()
            expired_ids = [
                code_id
                for code_id, code in self.sms_codes.items()
                if current_time > code.expires_at
            ]

            for code_id in expired_ids:
                del self.sms_codes[code_id]

            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired SMS codes")

        except Exception as e:
            logger.error(f"Failed to cleanup expired SMS codes: {e}")

    def update_sms_config(self, **kwargs):
        """Update SMS configurationUpdate SMS configuration"""
        try:
            for key, value in kwargs.items():
                if key in self.sms_config:
                    self.sms_config[key] = value
                    logger.info(f"Updated SMS config: {key} = {value}")
                else:
                    logger.warning(f"Unknown SMS config key: {key}")

        except Exception as e:
            logger.error(f"Failed to update SMS config: {e}")

    def get_system_status(self) -> Dict[str, any]:
        """Get SMS service statusGet SMS service status"""
        return {
            "total_codes": len(self.sms_codes),
            "active_codes": len(
                [c for c in self.sms_codes.values() if c.status == SMSStatus.PENDING]
            ),
            "config": self.sms_config,
            "status": "active",
        }

class MockSMSProvider:
    """Mock SMS provider for development/testingMock SMS provider for development/testing"""

    async def send_sms(self, phone_number: str, message: str):
        """Mock SMS sendingMock SMS sending"""
        # Simulate SMS sending delay
        await asyncio.sleep(0.1)

        # Log the SMS (in production, this would send actual SMS)
        logger.info(f"[MOCK SMS] To: {phone_number}, Message: {message}")

        # Simulate 95% success rate
        if random.random() < 0.95:
            return True
        else:
            raise Exception("Mock SMS delivery failed")

# Global SMS service instance
sms_service = SMSService()
