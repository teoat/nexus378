#!/usr/bin/env python3
"""
MFA System Test Script

Comprehensive testing of the Multi-Factor Authentication system including:
- TOTP authentication
- SMS authentication
- Hardware token authentication
- Multi-method authentication
- User setup and management
"""

import logging
import os
import sys
from datetime import datetime

import asyncio

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from config import MFAConfig, MFALevel, MFAMethod
from hardware_auth import (
    HardwareTokenAuthenticator,
    HardwareTokenInfo,
    HardwareTokenType,
)
from mfa_manager import MFAManager
from sms_auth import SMSAuthenticator
from totp_auth import TOTPAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MFASystemTester:
    """Comprehensive MFA system tester"""

    def __init__(self):
        self.config = None
        self.mfa_manager = None
        self.test_results = []

    def setup_config(self):
        """Setup MFA configuration for testing"""
        try:
            logger.info("Setting up MFA configuration...")

            # Create configuration with all methods enabled
            self.config = MFAConfig(
                enabled=True,
                required_for_all_users=True,
                methods=[MFAMethod.TOTP, MFAMethod.SMS, MFAMethod.HARDWARE],
                default_level=MFALevel.ENHANCED,
                max_failed_attempts=3,
                lockout_duration_minutes=5,
                session_timeout_hours=2,
            )

            # Validate configuration
            if not self.config.validate():
                raise ValueError("Invalid MFA configuration")

            logger.info("✅ MFA configuration setup successful")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup MFA configuration: {e}")
            return False

    def setup_mfa_manager(self):
        """Setup MFA manager"""
        try:
            logger.info("Setting up MFA manager...")

            self.mfa_manager = MFAManager(self.config)

            logger.info("✅ MFA manager setup successful")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup MFA manager: {e}")
            return False

    def test_totp_authenticator(self):
        """Test TOTP authenticator functionality"""
        try:
            logger.info("Testing TOTP authenticator...")

            if not self.mfa_manager.totp_auth:
                logger.warning("TOTP authenticator not available")
                return False

            # Test secret generation
            user_id = "test_user_001"
            secret = self.mfa_manager.totp_auth.generate_secret(user_id)
            assert secret and len(secret) >= 16, "Secret generation failed"

            # Test QR code generation
            qr_uri = self.mfa_manager.totp_auth.generate_qr_code(user_id, secret)
            assert qr_uri.startswith("otpauth://totp/"), "QR URI generation failed"

            # Test code generation
            code = self.mfa_manager.totp_auth.generate_code(secret)
            assert (
                code and len(code) == self.config.totp.digits
            ), "Code generation failed"

            # Test code validation
            result = self.mfa_manager.totp_auth.validate_code(secret, code)
            assert result.success, "Code validation failed"

            # Test invalid code
            invalid_result = self.mfa_manager.totp_auth.validate_code(secret, "000000")
            assert not invalid_result.success, "Invalid code should fail validation"

            logger.info("✅ TOTP authenticator tests passed")
            self.test_results.append(("TOTP Authenticator", True, "All tests passed"))
            return True

        except Exception as e:
            logger.error(f"❌ TOTP authenticator tests failed: {e}")
            self.test_results.append(("TOTP Authenticator", False, str(e)))
            return False

    async def test_sms_authenticator(self):
        """Test SMS authenticator functionality"""
        try:
            logger.info("Testing SMS authenticator...")

            if not self.mfa_manager.sms_auth:
                logger.warning("SMS authenticator not available")
                return False

            # Test SMS code sending
            phone_number = "+1234567890"
            user_id = "test_user_001"

            result = await self.mfa_manager.sms_auth.send_code(phone_number, user_id)
            assert result.success, "SMS code sending failed"
            assert result.code, "SMS code not generated"

            # Test code validation
            validation_result = self.mfa_manager.sms_auth.validate_code(
                phone_number, result.code
            )
            assert validation_result.success, "SMS code validation failed"

            # Test invalid code
            invalid_result = self.mfa_manager.sms_auth.validate_code(
                phone_number, "000000"
            )
            assert not invalid_result.success, "Invalid SMS code should fail validation"

            # Test code status
            status = self.mfa_manager.sms_auth.get_code_status(phone_number)
            assert not status[
                "has_active_code"
            ], "Code should be consumed after validation"

            logger.info("✅ SMS authenticator tests passed")
            self.test_results.append(("SMS Authenticator", True, "All tests passed"))
            return True

        except Exception as e:
            logger.error(f"❌ SMS authenticator tests failed: {e}")
            self.test_results.append(("SMS Authenticator", False, str(e)))
            return False

    def test_hardware_authenticator(self):
        """Test hardware token authenticator functionality"""
        try:
            logger.info("Testing hardware token authenticator...")

            if not self.mfa_manager.hardware_auth:
                logger.warning("Hardware token authenticator not available")
                return False

            # Test token registration
            token_info = HardwareTokenInfo(
                token_id="test_token_001",
                token_type=HardwareTokenType.CHALLENGE_RESPONSE,
                user_id="test_user_001",
                name="Test Hardware Token",
                capabilities=["challenge_response"],
            )

            success = self.mfa_manager.hardware_auth.register_token(token_info)
            assert success, "Token registration failed"

            # Test challenge generation
            challenge = self.mfa_manager.hardware_auth.generate_challenge(
                "test_user_001", "test_token_001"
            )
            assert challenge, "Challenge generation failed"

            # Test challenge response validation
            # In real implementation, this would come from the hardware token
            # For testing, we'll simulate the expected response
            expected_response = self.mfa_manager.hardware_auth.tokens[
                "test_token_001"
            ]._generate_expected_response(challenge, "test_user_001")

            result = self.mfa_manager.hardware_auth.validate_challenge_response(
                challenge, expected_response, "test_user_001"
            )
            assert result.success, "Challenge response validation failed"

            # Test invalid response
            invalid_result = self.mfa_manager.hardware_auth.validate_challenge_response(
                challenge, "invalid_response", "test_user_001"
            )
            assert not invalid_result.success, "Invalid response should fail validation"

            logger.info("✅ Hardware token authenticator tests passed")
            self.test_results.append(
                ("Hardware Token Authenticator", True, "All tests passed")
            )
            return True

        except Exception as e:
            logger.error(f"❌ Hardware token authenticator tests failed: {e}")
            self.test_results.append(("Hardware Token Authenticator", False, str(e)))
            return False

    def test_mfa_setup(self):
        """Test MFA setup functionality"""
        try:
            logger.info("Testing MFA setup...")

            user_id = "test_user_002"
            email = "test@example.com"
            phone = "+1234567890"

            # Setup MFA for user
            setup_result = self.mfa_manager.setup_user_mfa(user_id, email, phone)
            assert setup_result.success, "MFA setup failed"
            assert (
                not setup_result.setup_complete
            ), "Setup should not be complete initially"

            # Verify TOTP setup
            if "totp" in setup_result.setup_data["methods"]:
                totp_config = setup_result.setup_data["methods"]["totp"]
                current_code = totp_config["current_code"]

                # Verify TOTP setup
                totp_success = self.mfa_manager.verify_totp_setup(user_id, current_code)
                assert totp_success, "TOTP setup verification failed"

            # Get user status
            status = self.mfa_manager.get_user_mfa_status(user_id)
            assert status is not None, "Failed to get user MFA status"

            logger.info("✅ MFA setup tests passed")
            self.test_results.append(("MFA Setup", True, "All tests passed"))
            return True

        except Exception as e:
            logger.error(f"❌ MFA setup tests failed: {e}")
            self.test_results.append(("MFA Setup", False, str(e)))
            return False

    async def test_mfa_authentication(self):
        """Test MFA authentication functionality"""
        try:
            logger.info("Testing MFA authentication...")

            user_id = "test_user_003"
            email = "test3@example.com"
            phone = "+1234567891"

            # Setup MFA for user
            setup_result = self.mfa_manager.setup_user_mfa(user_id, email, phone)
            assert setup_result.success, "MFA setup failed"

            # Complete TOTP setup
            if "totp" in setup_result.setup_data["methods"]:
                totp_config = setup_result.setup_data["methods"]["totp"]
                current_code = totp_config["current_code"]
                self.mfa_manager.verify_totp_setup(user_id, current_code)

            # Complete SMS setup
            if "sms" in setup_result.setup_data["methods"]:
                # Send SMS code
                sms_result = await self.mfa_manager.sms_auth.send_code(phone, user_id)
                assert sms_result.success, "SMS code sending failed"

                # Verify SMS setup
                sms_success = await self.mfa_manager.verify_sms_setup(
                    user_id, phone, sms_result.code
                )
                assert sms_success, "SMS setup verification failed"

            # Test authentication
            auth_data = {}

            # TOTP authentication
            if "totp" in setup_result.setup_data["methods"]:
                totp_config = setup_result.setup_data["methods"]["totp"]
                secret = totp_config["secret"]
                current_code = self.mfa_manager.totp_auth.generate_code(secret)
                auth_data["totp"] = {"code": current_code}

            # SMS authentication
            if "sms" in setup_result.setup_data["methods"]:
                sms_result = await self.mfa_manager.sms_auth.send_code(phone, user_id)
                auth_data["sms"] = {"code": sms_result.code, "phone": phone}

            # Perform authentication
            auth_result = await self.mfa_manager.authenticate_user(user_id, auth_data)
            assert auth_result.success, "MFA authentication failed"
            assert auth_result.session_token, "Session token not generated"

            # Validate session
            session_data = self.mfa_manager.validate_session(auth_result.session_token)
            assert session_data is not None, "Session validation failed"
            assert session_data["user_id"] == user_id, "Session user ID mismatch"

            logger.info("✅ MFA authentication tests passed")
            self.test_results.append(("MFA Authentication", True, "All tests passed"))
            return True

        except Exception as e:
            logger.error(f"❌ MFA authentication tests failed: {e}")
            self.test_results.append(("MFA Authentication", False, str(e)))
            return False

    async def test_security_features(self):
        """Test security features"""
        try:
            logger.info("Testing security features...")

            # Test session invalidation
            user_id = "test_user_004"
            email = "test4@example.com"

            # Setup MFA
            setup_result = self.mfa_manager.setup_user_mfa(user_id, email)
            assert setup_result.success, "MFA setup failed"

            # Complete TOTP setup
            current_code = None
            if "totp" in setup_result.setup_data["methods"]:
                totp_config = setup_result.setup_data["methods"]["totp"]
                current_code = totp_config["current_code"]
                self.mfa_manager.verify_totp_setup(user_id, current_code)

            # Test authentication
            if current_code:
                auth_data = {"totp": {"code": current_code}}
                auth_result = await self.mfa_manager.authenticate_user(
                    user_id, auth_data
                )
                assert auth_result.success, "Authentication failed"

                # Invalidate session
                session_token = auth_result.session_token
                success = self.mfa_manager.invalidate_session(session_token)
                assert success, "Session invalidation failed"

                # Verify session is invalid
                session_data = self.mfa_manager.validate_session(session_token)
                assert (
                    session_data is None
                ), "Session should be invalid after invalidation"

            logger.info("✅ Security features tests passed")
            self.test_results.append(("Security Features", True, "All tests passed"))
            return True

        except Exception as e:
            logger.error(f"❌ Security features tests failed: {e}")
            self.test_results.append(("Security Features", False, str(e)))
            return False

    async def run_all_tests(self):
        """Run all MFA system tests"""
        logger.info("🚀 Starting MFA System Tests")
        logger.info("=" * 50)

        # Setup phase
        if not self.setup_config():
            logger.error("❌ Configuration setup failed - aborting tests")
            return False

        if not self.setup_mfa_manager():
            logger.error("❌ MFA manager setup failed - aborting tests")
            return False

        # Test phase
        tests = [
            ("TOTP Authenticator", self.test_totp_authenticator),
            ("SMS Authenticator", self.test_sms_authenticator),
            ("Hardware Token Authenticator", self.test_hardware_authenticator),
            ("MFA Setup", self.test_mfa_setup),
            ("MFA Authentication", self.test_mfa_authentication),
            ("Security Features", self.test_security_features),
        ]

        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running {test_name} tests...")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    success = await test_func()
                else:
                    success = test_func()

                if success:
                    logger.info(f"✅ {test_name} tests completed successfully")
                else:
                    logger.error(f"❌ {test_name} tests failed")

            except Exception as e:
                logger.error(f"❌ {test_name} tests failed with exception: {e}")
                self.test_results.append((test_name, False, str(e)))

        # Results summary
        self.print_test_results()

        return True

    def print_test_results(self):
        """Print test results summary"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 MFA SYSTEM TEST RESULTS")
        logger.info("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        logger.info("\nDetailed Results:")
        for test_name, success, message in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {status} - {test_name}: {message}")

        if failed_tests == 0:
            logger.info("\n🎉 All MFA system tests passed successfully!")
        else:
            logger.warning(
                f"\n⚠️  {failed_tests} test(s) failed. Please review the implementation."
            )

        logger.info("=" * 50)


async def main():
    """Main test execution function"""
    try:
        tester = MFASystemTester()
        await tester.run_all_tests()

    except KeyboardInterrupt:
        logger.info("\n⚠️  Tests interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run tests
    asyncio.run(main())
