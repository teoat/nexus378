"""
AES-256 Encryption Core - Advanced Encryption System

This module implements the AES256EncryptionCore class that provides
comprehensive AES-256 encryption, decryption, and key management
capabilities for the forensic platform.
"""

import asyncio
import logging
import os
import base64
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union, bytes
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey, InvalidTag
import secrets

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class EncryptionMode(Enum):
    """AES encryption modes."""
    CBC = "cbc"                                    # Cipher Block Chaining
    GCM = "gcm"                                    # Galois/Counter Mode
    CTR = "ctr"                                    # Counter Mode
    XTS = "xts"                                    # XEX-based tweaked-codebook mode


class KeyDerivationFunction(Enum):
    """Key derivation functions."""
    PBKDF2 = "pbkdf2"                             # Password-Based Key Derivation Function 2
    SCRYPT = "scrypt"                              # Memory-hard key derivation
    HKDF = "hkdf"                                  # HMAC-based Key Derivation Function
    ARGON2 = "argon2"                              # Memory-hard key derivation (if available)


class EncryptionAlgorithm(Enum):
    """Encryption algorithms."""
    AES_256 = "aes_256"                           # AES-256
    AES_192 = "aes_192"                           # AES-192
    AES_128 = "aes_128"                           # AES-128


@dataclass
class EncryptionKey:
    """Encryption key with metadata."""
    
    id: str
    key_data: bytes
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime] = None
    key_type: str = "symmetric"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()


@dataclass
class EncryptedData:
    """Encrypted data with metadata."""
    
    ciphertext: bytes
    iv: bytes
    tag: Optional[bytes] = None
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    mode: EncryptionMode = EncryptionMode.GCM
    key_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AES256EncryptionCore:
    """
    Comprehensive AES-256 encryption core system.
    
    The AES256EncryptionCore is responsible for:
    - AES-256 encryption and decryption
    - Multiple encryption modes (CBC, GCM, CTR, XTS)
    - Secure key derivation and management
    - Data integrity verification
    - Performance optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the AES256EncryptionCore."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.default_algorithm = EncryptionAlgorithm.AES_256
        self.default_mode = EncryptionMode.GCM
        self.key_size = 32  # 256 bits
        self.iv_size = 16   # 128 bits
        self.block_size = 16  # AES block size
        
        # Security settings
        self.min_key_length = config.get('min_key_length', 32)
        self.max_key_length = config.get('max_key_length', 64)
        self.key_derivation_iterations = config.get('key_derivation_iterations', 100000)
        self.salt_size = config.get('salt_size', 32)
        
        # Key management
        self.active_keys: Dict[str, EncryptionKey] = {}
        self.key_cache: Dict[str, bytes] = {}
        
        # Performance tracking
        self.total_encryptions = 0
        self.total_decryptions = 0
        self.average_encryption_time = 0.0
        self.average_decryption_time = 0.0
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("AES256EncryptionCore initialized successfully")
    
    async def start(self):
        """Start the AES256EncryptionCore."""
        self.logger.info("Starting AES256EncryptionCore...")
        
        # Initialize encryption components
        await self._initialize_encryption_components()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_keys())
        asyncio.create_task(self._update_performance_metrics())
        
        self.logger.info("AES256EncryptionCore started successfully")
    
    async def stop(self):
        """Stop the AES256EncryptionCore."""
        self.logger.info("Stopping AES256EncryptionCore...")
        self.logger.info("AES256EncryptionCore stopped")
    
    async def generate_key(self, algorithm: EncryptionAlgorithm = None, 
                          key_type: str = "symmetric") -> EncryptionKey:
        """Generate a new encryption key."""
        try:
            if not algorithm:
                algorithm = self.default_algorithm
            
            # Generate random key
            key_data = secrets.token_bytes(self.key_size)
            
            # Create key object
            key_id = f"key_{datetime.utcnow().timestamp()}_{secrets.token_hex(8)}"
            key = EncryptionKey(
                id=key_id,
                key_data=key_data,
                algorithm=algorithm,
                created_at=datetime.utcnow(),
                key_type=key_type
            )
            
            # Store key
            self.active_keys[key_id] = key
            self.key_cache[key_id] = key_data
            
            self.logger.info(f"Generated new key: {key_id} ({algorithm.value})")
            
            return key
            
        except Exception as e:
            self.logger.error(f"Error generating key: {e}")
            raise
    
    async def derive_key_from_password(self, password: str, salt: bytes = None,
                                     kdf: KeyDerivationFunction = KeyDerivationFunction.PBKDF2) -> EncryptionKey:
        """Derive encryption key from password."""
        try:
            if not salt:
                salt = secrets.token_bytes(self.salt_size)
            
            # Convert password to bytes
            password_bytes = password.encode('utf-8')
            
            # Derive key using specified KDF
            if kdf == KeyDerivationFunction.PBKDF2:
                key_data = self._derive_key_pbkdf2(password_bytes, salt)
            elif kdf == KeyDerivationFunction.SCRYPT:
                key_data = self._derive_key_scrypt(password_bytes, salt)
            elif kdf == KeyDerivationFunction.HKDF:
                key_data = self._derive_key_hkdf(password_bytes, salt)
            else:
                raise ValueError(f"Unsupported KDF: {kdf}")
            
            # Create key object
            key_id = f"derived_key_{datetime.utcnow().timestamp()}_{secrets.token_hex(8)}"
            key = EncryptionKey(
                id=key_id,
                key_data=key_data,
                algorithm=self.default_algorithm,
                created_at=datetime.utcnow(),
                key_type="derived",
                metadata={'kdf': kdf.value, 'salt': base64.b64encode(salt).decode()}
            )
            
            # Store key
            self.active_keys[key_id] = key
            self.key_cache[key_id] = key_data
            
            self.logger.info(f"Derived key from password: {key_id} ({kdf.value})")
            
            return key
            
        except Exception as e:
            self.logger.error(f"Error deriving key from password: {e}")
            raise
    
    def _derive_key_pbkdf2(self, password: bytes, salt: bytes) -> bytes:
        """Derive key using PBKDF2."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_size,
                salt=salt,
                iterations=self.key_derivation_iterations,
                backend=default_backend()
            )
            
            key = kdf.derive(password)
            return key
            
        except Exception as e:
            self.logger.error(f"Error in PBKDF2 key derivation: {e}")
            raise
    
    def _derive_key_scrypt(self, password: bytes, salt: bytes) -> bytes:
        """Derive key using Scrypt."""
        try:
            kdf = Scrypt(
                salt=salt,
                length=self.key_size,
                n=2**14,  # CPU cost
                r=8,      # Memory cost
                p=1,      # Parallelization cost
                backend=default_backend()
            )
            
            key = kdf.derive(password)
            return key
            
        except Exception as e:
            self.logger.error(f"Error in Scrypt key derivation: {e}")
            raise
    
    def _derive_key_hkdf(self, password: bytes, salt: bytes) -> bytes:
        """Derive key using HKDF."""
        try:
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=self.key_size,
                salt=salt,
                info=b'forensic_platform_key',
                backend=default_backend()
            )
            
            key = kdf.derive(password)
            return key
            
        except Exception as e:
            self.logger.error(f"Error in HKDF key derivation: {e}")
            raise
    
    async def encrypt_data(self, data: Union[str, bytes], 
                          key: Union[EncryptionKey, str, bytes],
                          mode: EncryptionMode = None,
                          algorithm: EncryptionAlgorithm = None) -> EncryptedData:
        """Encrypt data using AES."""
        try:
            start_time = datetime.utcnow()
            
            # Convert data to bytes
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Get key
            if isinstance(key, str):
                if key in self.active_keys:
                    key_obj = self.active_keys[key]
                    key_data = self.key_cache[key]
                else:
                    raise ValueError(f"Key not found: {key}")
            elif isinstance(key, EncryptionKey):
                key_obj = key
                key_data = key.key_data
            elif isinstance(key, bytes):
                key_obj = EncryptionKey(
                    id="temp_key",
                    key_data=key,
                    algorithm=algorithm or self.default_algorithm,
                    created_at=datetime.utcnow()
                )
                key_data = key
            else:
                raise ValueError("Invalid key type")
            
            # Use defaults if not specified
            if not mode:
                mode = self.default_mode
            if not algorithm:
                algorithm = key_obj.algorithm
            
            # Generate IV
            iv = secrets.token_bytes(self.iv_size)
            
            # Encrypt data
            if mode == EncryptionMode.GCM:
                ciphertext, tag = self._encrypt_gcm(data_bytes, key_data, iv)
            elif mode == EncryptionMode.CBC:
                ciphertext = self._encrypt_cbc(data_bytes, key_data, iv)
                tag = None
            elif mode == EncryptionMode.CTR:
                ciphertext = self._encrypt_ctr(data_bytes, key_data, iv)
                tag = None
            elif mode == EncryptionMode.XTS:
                ciphertext = self._encrypt_xts(data_bytes, key_data, iv)
                tag = None
            else:
                raise ValueError(f"Unsupported encryption mode: {mode}")
            
            # Create encrypted data object
            encrypted_data = EncryptedData(
                ciphertext=ciphertext,
                iv=iv,
                tag=tag,
                algorithm=algorithm,
                mode=mode,
                key_id=key_obj.id if hasattr(key_obj, 'id') else None
            )
            
            # Update statistics
            self.total_encryptions += 1
            
            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_encryption_time(processing_time)
            
            self.logger.info(f"Encrypted data: {len(data_bytes)} bytes using {mode.value}")
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise
    
    def _encrypt_gcm(self, data: bytes, key: bytes, iv: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-GCM."""
        try:
            # Pad data to block size
            padded_data = self._pad_data(data)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Get tag
            tag = encryptor.tag
            
            return ciphertext, tag
            
        except Exception as e:
            self.logger.error(f"Error in GCM encryption: {e}")
            raise
    
    def _encrypt_cbc(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt data using AES-CBC."""
        try:
            # Pad data to block size
            padded_data = self._pad_data(data)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            return ciphertext
            
        except Exception as e:
            self.logger.error(f"Error in CBC encryption: {e}")
            raise
    
    def _encrypt_ctr(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt data using AES-CTR."""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CTR(iv),
                backend=default_backend()
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            return ciphertext
            
        except Exception as e:
            self.logger.error(f"Error in CTR encryption: {e}")
            raise
    
    def _encrypt_xts(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt data using AES-XTS."""
        try:
            # XTS requires data to be multiple of block size
            if len(data) % self.block_size != 0:
                raise ValueError("Data length must be multiple of block size for XTS mode")
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.XTS(iv),
                backend=default_backend()
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            return ciphertext
            
        except Exception as e:
            self.logger.error(f"Error in XTS encryption: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: EncryptedData,
                          key: Union[EncryptionKey, str, bytes]) -> bytes:
        """Decrypt data using AES."""
        try:
            start_time = datetime.utcnow()
            
            # Get key
            if isinstance(key, str):
                if key in self.active_keys:
                    key_obj = self.active_keys[key]
                    key_data = self.key_cache[key]
                else:
                    raise ValueError(f"Key not found: {key}")
            elif isinstance(key, EncryptionKey):
                key_obj = key
                key_data = key.key_data
            elif isinstance(key, bytes):
                key_data = key
            else:
                raise ValueError("Invalid key type")
            
            # Decrypt data
            if encrypted_data.mode == EncryptionMode.GCM:
                decrypted_data = self._decrypt_gcm(
                    encrypted_data.ciphertext,
                    key_data,
                    encrypted_data.iv,
                    encrypted_data.tag
                )
            elif encrypted_data.mode == EncryptionMode.CBC:
                decrypted_data = self._decrypt_cbc(
                    encrypted_data.ciphertext,
                    key_data,
                    encrypted_data.iv
                )
            elif encrypted_data.mode == EncryptionMode.CTR:
                decrypted_data = self._decrypt_ctr(
                    encrypted_data.ciphertext,
                    key_data,
                    encrypted_data.iv
                )
            elif encrypted_data.mode == EncryptionMode.XTS:
                decrypted_data = self._decrypt_xts(
                    encrypted_data.ciphertext,
                    key_data,
                    encrypted_data.iv
                )
            else:
                raise ValueError(f"Unsupported decryption mode: {encrypted_data.mode}")
            
            # Remove padding
            unpadded_data = self._unpad_data(decrypted_data)
            
            # Update statistics
            self.total_decryptions += 1
            
            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_decryption_time(processing_time)
            
            self.logger.info(f"Decrypted data: {len(unpadded_data)} bytes using {encrypted_data.mode.value}")
            
            return unpadded_data
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    def _decrypt_gcm(self, ciphertext: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes:
        """Decrypt data using AES-GCM."""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error in GCM decryption: {e}")
            raise
    
    def _decrypt_cbc(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-CBC."""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error in CBC decryption: {e}")
            raise
    
    def _decrypt_ctr(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-CTR."""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CTR(iv),
                backend=default_backend()
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error in CTR decryption: {e}")
            raise
    
    def _decrypt_xts(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-XTS."""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.XTS(iv),
                backend=default_backend()
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error in XTS decryption: {e}")
            raise
    
    def _pad_data(self, data: bytes) -> bytes:
        """Pad data to block size using PKCS7."""
        try:
            padding_length = self.block_size - (len(data) % self.block_size)
            padding = bytes([padding_length] * padding_length)
            return data + padding
            
        except Exception as e:
            self.logger.error(f"Error padding data: {e}")
            raise
    
    def _unpad_data(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        try:
            if len(data) == 0:
                return data
            
            padding_length = data[-1]
            if padding_length > self.block_size:
                raise ValueError("Invalid padding")
            
            return data[:-padding_length]
            
        except Exception as e:
            self.logger.error(f"Error unpadding data: {e}")
            raise
    
    async def verify_data_integrity(self, data: bytes, key: bytes, signature: bytes) -> bool:
        """Verify data integrity using HMAC."""
        try:
            # Calculate HMAC
            h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
            h.update(data)
            expected_signature = h.finalize()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying data integrity: {e}")
            return False
    
    async def generate_data_signature(self, data: bytes, key: bytes) -> bytes:
        """Generate HMAC signature for data."""
        try:
            h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
            h.update(data)
            signature = h.finalize()
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Error generating data signature: {e}")
            raise
    
    async def _initialize_encryption_components(self):
        """Initialize encryption components."""
        try:
            # Verify cryptography backend
            backend = default_backend()
            self.logger.info(f"Using cryptography backend: {backend}")
            
            # Test key generation
            test_key = secrets.token_bytes(self.key_size)
            self.logger.info(f"Test key generation successful: {len(test_key)} bytes")
            
            self.logger.info("Encryption components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption components: {e}")
    
    async def _cleanup_expired_keys(self):
        """Clean up expired encryption keys."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key_id, key in self.active_keys.items():
                    if key.expires_at and key.expires_at < current_time:
                        expired_keys.append(key_id)
                
                # Remove expired keys
                for key_id in expired_keys:
                    del self.active_keys[key_id]
                    if key_id in self.key_cache:
                        del self.key_cache[key_id]
                
                if expired_keys:
                    self.logger.info(f"Cleaned up {len(expired_keys)} expired keys")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up expired keys: {e}")
                await asyncio.sleep(3600)
    
    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # This would calculate performance metrics
                # For now, just log current stats
                self.logger.debug(f"Performance metrics - Encryptions: {self.total_encryptions}, Decryptions: {self.total_decryptions}")
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(3600)
    
    def _update_average_encryption_time(self, new_time: float):
        """Update average encryption time."""
        self.average_encryption_time = (
            (self.average_encryption_time * self.total_encryptions + new_time) /
            (self.total_encryptions + 1)
        )
    
    def _update_average_decryption_time(self, new_time: float):
        """Update average decryption time."""
        self.average_decryption_time = (
            (self.average_decryption_time * self.total_decryptions + new_time) /
            (self.total_decryptions + 1)
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_encryptions': self.total_encryptions,
            'total_decryptions': self.total_decryptions,
            'average_encryption_time': self.average_encryption_time,
            'average_decryption_time': self.average_decryption_time,
            'active_keys': len(self.active_keys),
            'supported_modes': [mode.value for mode in EncryptionMode],
            'supported_algorithms': [algo.value for algo in EncryptionAlgorithm],
            'supported_kdfs': [kdf.value for kdf in KeyDerivationFunction]
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'min_key_length': 32,
        'max_key_length': 64,
        'key_derivation_iterations': 100000,
        'salt_size': 32
    }
    
    # Initialize encryption core
    encryption_core = AES256EncryptionCore(config)
    
    print("AES256EncryptionCore system initialized successfully!")
