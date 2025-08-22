"""
End-to-End Encryption Service
Implements AES-256 encryption with secure key management
"""

import logging
import os
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets

logger = logging.getLogger(__name__)


class EncryptionService:
    """End-to-end encryption service implementation"""
    
    def __init__(self):
        self.encryption_config = {
            "algorithm": "AES-256-GCM",
            "key_length": 32,  # 256 bits
            "salt_length": 16,
            "iv_length": 12,
            "tag_length": 16,
            "pbkdf2_iterations": 100000
        }
        
        # Key storage (in production, use secure key management service)
        self.master_keys: Dict[str, bytes] = {}
        self.user_keys: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Encryption service initialized")
    
    def generate_master_key(self) -> str:
        """Generate a new master encryption key"""
        try:
            # Generate cryptographically secure random key
            master_key = secrets.token_bytes(self.encryption_config["key_length"])
            
            # Generate key ID
            key_id = self._generate_key_id()
            
            # Store master key
            self.master_keys[key_id] = master_key
            
            logger.info(f"Generated master encryption key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"Failed to generate master key: {e}")
            raise
    
    def generate_user_key_pair(self, user_id: str, master_key_id: str) -> Tuple[str, str]:
        """Generate RSA key pair for user"""
        try:
            # Get master key
            master_key = self.master_keys.get(master_key_id)
            if not master_key:
                raise ValueError(f"Master key {master_key_id} not found")
            
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(master_key)
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Generate key IDs
            private_key_id = self._generate_key_id()
            public_key_id = self._generate_key_id()
            
            # Store user keys
            self.user_keys[user_id] = {
                "private_key_id": private_key_id,
                "public_key_id": public_key_id,
                "private_key": private_pem,
                "public_key": public_pem,
                "master_key_id": master_key_id,
                "created_at": datetime.now()
            }
            
            logger.info(f"Generated key pair for user {user_id}")
            return private_key_id, public_key_id
            
        except Exception as e:
            logger.error(f"Failed to generate user key pair: {e}")
            raise
    
    def encrypt_data(self, data: bytes, encryption_key: bytes, 
                    associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes, bytes]:
        """Encrypt data using AES-256-GCM"""
        try:
            # Generate random IV
            iv = os.urandom(self.encryption_config["iv_length"])
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(encryption_key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Add associated data if provided
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # Encrypt data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Get authentication tag
            tag = encryptor.tag
            
            logger.debug(f"Data encrypted successfully (size: {len(data)} bytes)")
            return iv, ciphertext, tag
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes, encryption_key: bytes, iv: bytes, 
                    tag: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt data using AES-256-GCM"""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(encryption_key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Add associated data if provided
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            # Decrypt data
            plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            logger.debug(f"Data decrypted successfully (size: {len(plaintext)} bytes)")
            return plaintext
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2"""
        try:
            if salt is None:
                salt = os.urandom(self.encryption_config["salt_length"])
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.encryption_config["key_length"],
                salt=salt,
                iterations=self.encryption_config["pbkdf2_iterations"],
                backend=default_backend()
            )
            
            key = kdf.derive(password.encode('utf-8'))
            
            logger.debug("Key derived from password successfully")
            return key, salt
            
        except Exception as e:
            logger.error(f"Failed to derive key from password: {e}")
            raise
    
    def encrypt_file(self, file_path: str, encryption_key: bytes, 
                    output_path: Optional[str] = None) -> str:
        """Encrypt a file using AES-256-GCM"""
        try:
            if output_path is None:
                output_path = file_path + ".encrypted"
            
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            iv, ciphertext, tag = self.encrypt_data(data, encryption_key)
            
            # Write encrypted file
            with open(output_path, 'wb') as f:
                f.write(iv)
                f.write(tag)
                f.write(ciphertext)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to encrypt file {file_path}: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, encryption_key: bytes, 
                    output_path: Optional[str] = None) -> str:
        """Decrypt a file using AES-256-GCM"""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            
            # Read encrypted file
            with open(encrypted_file_path, 'rb') as f:
                iv = f.read(self.encryption_config["iv_length"])
                tag = f.read(self.encryption_config["tag_length"])
                ciphertext = f.read()
            
            # Decrypt data
            plaintext = self.decrypt_data(ciphertext, encryption_key, iv, tag)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to decrypt file {encrypted_file_path}: {e}")
            raise
    
    def generate_data_hash(self, data: bytes, algorithm: str = "SHA256") -> str:
        """Generate hash of data for integrity verification"""
        try:
            if algorithm.upper() == "SHA256":
                hash_obj = hashlib.sha256()
            elif algorithm.upper() == "SHA512":
                hash_obj = hashlib.sha512()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            hash_obj.update(data)
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to generate hash: {e}")
            raise
    
    def verify_data_integrity(self, data: bytes, expected_hash: str, 
                             algorithm: str = "SHA256") -> bool:
        """Verify data integrity using hash"""
        try:
            actual_hash = self.generate_data_hash(data, algorithm)
            return hmac.compare_digest(actual_hash, expected_hash)
            
        except Exception as e:
            logger.error(f"Failed to verify data integrity: {e}")
            return False
    
    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_user_public_key(self, user_id: str) -> Optional[bytes]:
        """Get user's public key"""
        user_key_info = self.user_keys.get(user_id)
        if user_key_info:
            return user_key_info["public_key"]
        return None
    
    def revoke_user_keys(self, user_id: str) -> bool:
        """Revoke user's encryption keys"""
        try:
            if user_id in self.user_keys:
                del self.user_keys[user_id]
                logger.info(f"Encryption keys revoked for user {user_id}")
                return True
            else:
                logger.warning(f"No encryption keys found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to revoke user keys: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get encryption service status"""
        return {
            "master_keys": len(self.master_keys),
            "user_keys": len(self.user_keys),
            "algorithm": self.encryption_config["algorithm"],
            "key_length": self.encryption_config["key_length"],
            "status": "active"
        }


# Global encryption service instance
encryption_service = EncryptionService()
