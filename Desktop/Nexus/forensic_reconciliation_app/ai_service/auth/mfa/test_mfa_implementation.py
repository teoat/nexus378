#!/usr/bin/env python3
"""
Test script for MFA implementation
Tests TOTP, SMS, and hardware token authentication
"""

import logging
import os
import sys

import asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mfa.mfa_manager import mfa_manager
from mfa.sms_auth import sms_service
from mfa.totp_auth import totp_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_mfa_manager():
    """Test MFA Manager functionality"""
    logger.info("🧪 Testing MFA Manager...")

    try:
        # Setup MFA services
        await mfa_manager.setup_mfa_services()
        logger.info("✅ MFA services setup completed")

        # Test user MFA setup
        user_id = "test_user_001"

        # Enable MFA types for user
        await mfa_manager.enable_mfa_for_user(user_id, mfa_manager.MFAType.TOTP, True)
        await mfa_manager.enable_mfa_for_user(user_id, mfa_manager.MFAType.SMS, True)
        await mfa_manager.enable_mfa_for_user(
            user_id, mfa_manager.MFAType.HARDWARE, True
        )

        logger.info(f"✅ MFA types enabled for user {user_id}")

        # Test MFA challenge creation
        challenge = await mfa_manager.create_mfa_challenge(
            user_id, mfa_manager.MFAType.TOTP
        )
        if challenge:
            logger.info(f"✅ TOTP challenge created: {challenge.id}")
        else:
            logger.error("❌ Failed to create TOTP challenge")
            return False

        # Test SMS challenge creation
        sms_challenge = await mfa_manager.create_mfa_challenge(
            user_id, mfa_manager.MFAType.SMS
        )
        if sms_challenge:
            logger.info(f"✅ SMS challenge created: {sms_challenge.id}")
        else:
            logger.error("❌ Failed to create SMS challenge")
            return False

        # Test hardware challenge creation
        hw_challenge = await mfa_manager.create_mfa_challenge(
            user_id, mfa_manager.MFAType.HARDWARE
        )
        if hw_challenge:
            logger.info(f"✅ Hardware challenge created: {hw_challenge.id}")
        else:
            logger.error("❌ Failed to create hardware challenge")
            return False

        # Test system status
        status = mfa_manager.get_system_status()
        logger.info(f"✅ MFA Manager status: {status}")

        return True

    except Exception as e:
        logger.error(f"❌ MFA Manager test failed: {e}")
        return False


async def test_totp_service():
    """Test TOTP service functionality"""
    logger.info("🧪 Testing TOTP Service...")

    try:
        user_id = "test_user_002"

        # Generate TOTP secret
        secret = totp_service.generate_totp_secret(user_id)
        if secret:
            logger.info(f"✅ TOTP secret generated: {secret[:10]}...")
        else:
            logger.error("❌ Failed to generate TOTP secret")
            return False

        # Generate TOTP code
        code = totp_service.generate_totp_code(user_id)
        if code:
            logger.info(f"✅ TOTP code generated: {code}")
        else:
            logger.error("❌ Failed to generate TOTP code")
            return False

        # Verify TOTP code
        is_valid = totp_service.verify_totp(user_id, code)
        if is_valid:
            logger.info("✅ TOTP code verification successful")
        else:
            logger.error("❌ TOTP code verification failed")
            return False

        # Test invalid code
        is_valid = totp_service.verify_totp(user_id, "000000")
        if not is_valid:
            logger.info("✅ Invalid TOTP code correctly rejected")
        else:
            logger.error("❌ Invalid TOTP code incorrectly accepted")
            return False

        # Get QR code data
        qr_data = totp_service.get_qr_code_data(user_id, "Test Platform")
        if qr_data:
            logger.info(f"✅ QR code data generated: {qr_data[:50]}...")
        else:
            logger.error("❌ Failed to generate QR code data")
            return False

        # Get user status
        status = totp_service.get_user_totp_status(user_id)
        logger.info(f"✅ TOTP user status: {status}")

        return True

    except Exception as e:
        logger.error(f"❌ TOTP service test failed: {e}")
        return False


async def test_sms_service():
    """Test SMS service functionality"""
    logger.info("🧪 Testing SMS Service...")

    try:
        user_id = "test_user_003"
        phone_number = "+1234567890"

        # Generate SMS code
        code_id = await sms_service.generate_sms_code(user_id, phone_number)
        if code_id:
            logger.info(f"✅ SMS code generated: {code_id}")
        else:
            logger.error("❌ Failed to generate SMS code")
            return False

        # Get SMS status
        status = sms_service.get_sms_status(user_id)
        logger.info(f"✅ SMS status: {status}")

        # Test rate limiting (should fail on second attempt)
        second_code_id = await sms_service.generate_sms_code(user_id, phone_number)
        if not second_code_id:
            logger.info("✅ Rate limiting working correctly")
        else:
            logger.warning("⚠️ Rate limiting may not be working")

        # Test system status
        system_status = sms_service.get_system_status()
        logger.info(f"✅ SMS system status: {system_status}")

        return True

    except Exception as e:
        logger.error(f"❌ SMS service test failed: {e}")
        return False


async def test_encryption_service():
    """Test encryption service functionality"""
    logger.info("🧪 Testing Encryption Service...")

    try:
        # Import encryption service
        from encryption_service import encryption_service

        # Generate master key
        master_key_id = encryption_service.generate_master_key()
        if master_key_id:
            logger.info(f"✅ Master key generated: {master_key_id}")
        else:
            logger.error("❌ Failed to generate master key")
            return False

        # Generate user key pair
        user_id = "test_user_004"
        private_key_id, public_key_id = encryption_service.generate_user_key_pair(
            user_id, master_key_id
        )
        if private_key_id and public_key_id:
            logger.info(
                f"✅ User key pair generated: {private_key_id}, {public_key_id}"
            )
        else:
            logger.error("❌ Failed to generate user key pair")
            return False

        # Test data encryption/decryption
        test_data = b"Hello, this is a test message for encryption!"

        # Get master key
        master_key = encryption_service.master_keys[master_key_id]

        # Encrypt data
        iv, ciphertext, tag = encryption_service.encrypt_data(test_data, master_key)
        if iv and ciphertext and tag:
            logger.info("✅ Data encryption successful")
        else:
            logger.error("❌ Data encryption failed")
            return False

        # Decrypt data
        decrypted_data = encryption_service.decrypt_data(
            ciphertext, master_key, iv, tag
        )
        if decrypted_data == test_data:
            logger.info("✅ Data decryption successful")
        else:
            logger.error("❌ Data decryption failed")
            return False

        # Test hash generation
        data_hash = encryption_service.generate_data_hash(test_data)
        if data_hash:
            logger.info(f"✅ Data hash generated: {data_hash[:20]}...")
        else:
            logger.error("❌ Failed to generate data hash")
            return False

        # Test integrity verification
        is_valid = encryption_service.verify_data_integrity(test_data, data_hash)
        if is_valid:
            logger.info("✅ Data integrity verification successful")
        else:
            logger.error("❌ Data integrity verification failed")
            return False

        # Get system status
        status = encryption_service.get_system_status()
        logger.info(f"✅ Encryption system status: {status}")

        return True

    except Exception as e:
        logger.error(f"❌ Encryption service test failed: {e}")
        return False


async def main():
    """Main test function"""
    logger.info("🚀 Starting MFA Implementation Tests")
    logger.info("=" * 60)

    test_results = []

    # Test MFA Manager
    result = await test_mfa_manager()
    test_results.append(("MFA Manager", result))

    # Test TOTP Service
    result = await test_totp_service()
    test_results.append(("TOTP Service", result))

    # Test SMS Service
    result = await test_sms_service()
    test_results.append(("SMS Service", result))

    # Test Encryption Service
    result = await test_encryption_service()
    test_results.append(("Encryption Service", result))

    # Print results
    logger.info("=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info("=" * 60)
    logger.info(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! MFA implementation is working correctly.")
        return True
    else:
        logger.error(
            f"⚠️ {total - passed} tests failed. Please check the implementation.",
        )
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
