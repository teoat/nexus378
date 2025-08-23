"""
End-to-End Encryption Service for AI Service
Implements AES-256 encryption with secure key management
"""

import base64
import hashlib
import logging
import os
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class EncryptionService:
    """AES-256 encryption service for sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = (
    master_key or os.environ.get('ENCRYPTION_MASTER_KEY', 'default-key-change-in-production')
)
        self.key_size = 32  # 256 bits
        self.iv_size = 16   # 128 bits
        self.salt_size = 32 # 256 bits
        
    def generate_key(
    self,
    password: str,
    salt: Optional[bytes] = None
)
        """Generate encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(self.salt_size)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_data(self, data: bytes, key: Optional[bytes] = None) -> Dict[str, str]:
        """Encrypt data using AES-256-CBC"""
        if key is None:
            key, salt = self.generate_key(self.master_key)
        else:
            salt = os.urandom(self.salt_size)
        
        # Generate random IV
        iv = os.urandom(self.iv_size)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad data to block size
        padded_data = self._pad_data(data)
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return encrypted data as base64 strings
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }
    
    def decrypt_data(
    self,
    encrypted_data: str,
    iv: str,
    salt: str,
    key: Optional[bytes] = None
)
        """Decrypt data using AES-256-CBC"""
        try:
            # Decode base64 strings
            encrypted_bytes = base64.b64decode(encrypted_data)
            iv_bytes = base64.b64decode(iv)
            salt_bytes = base64.b64decode(salt)
            
            # Generate key
            if key is None:
                key, _ = self.generate_key(self.master_key, salt_bytes)
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv_bytes))
            decryptor = cipher.decryptor()
            
            # Decrypt
            decrypted_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Remove padding
            return self._unpad_data(decrypted_data)
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_file(
    self,
    file_path: str,
    output_path: str,
    key: Optional[bytes] = None
)
        """Encrypt a file and save encrypted version"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_info = self.encrypt_data(data, key)
            
            # Save encrypted data
            with open(output_path, 'w') as f:
                f.write(encrypted_info['encrypted_data'])
            
            return encrypted_info
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(
    self,
    encrypted_file_path: str,
    output_path: str,
    iv: str,
    salt: str,
    key: Optional[bytes] = None
)
        """Decrypt a file and save decrypted version"""
        try:
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_data(encrypted_data, iv, salt, key)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return False
    
    def hash_data(self, data: bytes, algorithm: str = 'sha256') -> str:
        """Generate hash of data for integrity verification"""
        if algorithm == 'sha256':
            hash_obj = hashlib.sha256(data)
        elif algorithm == 'sha512':
            hash_obj = hashlib.sha512(data)
        else:
            raise ValueError("Unsupported hash algorithm")
        
        return hash_obj.hexdigest()
    
    def verify_hash(
    self,
    data: bytes,
    expected_hash: str,
    algorithm: str = 'sha256'
)
        """Verify data integrity using hash"""
        actual_hash = self.hash_data(data, algorithm)
        return actual_hash == expected_hash
    
    def _pad_data(self, data: bytes) -> bytes:
        """Pad data to AES block size"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, data: bytes) -> bytes:
        """Remove padding from data"""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def generate_secure_random(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        return os.urandom(length)
    
    def encrypt_metadata(
    self,
    metadata: Dict[str,
    Any],
    key: Optional[bytes] = None
)
        """Encrypt metadata dictionary"""
        import json
        metadata_json = json.dumps(metadata, sort_keys=True)
        metadata_bytes = metadata_json.encode('utf-8')
        
        return self.encrypt_data(metadata_bytes, key)
    
    def decrypt_metadata(
    self,
    encrypted_info: Dict[str,
    str],
    key: Optional[bytes] = None
)
        """Decrypt metadata dictionary"""
        import json
        
        decrypted_bytes = self.decrypt_data(
            encrypted_info['encrypted_data'],
            encrypted_info['iv'],
            encrypted_info['salt'],
            key
        )
        
        metadata_json = decrypted_bytes.decode('utf-8')
        return json.loads(metadata_json)

# Global encryption service instance
encryption_service = EncryptionService()
