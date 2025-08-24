Key Management Service for AI Service
Handles encryption key generation, storage, and rotation

import base64
import hashlib
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

@dataclass
class EncryptionKey:

            raise ValueError("AES key size must be 128, 192, or 256 bits")
        
        # Generate random key
        key_data = secrets.token_bytes(key_size // 8)
        key_id = self._generate_key_id(key_data, 'aes')
        
        # Create key object
        key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            key_type=f'aes-{key_size}',
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.key_rotation_interval,
            metadata={'algorithm': 'AES', 'mode': 'CBC'}
        )
        
        # Store key
        self.active_keys[key_id] = key
        self._save_key(key)
        
        logger.info(f"Generated new AES-{key_size} key: {key_id}")
        
        return key_id, key_data
    
    def generate_rsa_key_pair(self, key_size: int = 2048) -> Tuple[str, bytes, bytes]:

            raise ValueError("RSA key size must be 1024, 2048, or 4096 bits")
        
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Generate key ID
            key_id = self._generate_key_id(public_pem, 'rsa')
            
            # Create key object
            key = EncryptionKey(
                key_id=key_id,
                key_data=private_pem,
                key_type=f'rsa-{key_size}',
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + self.key_rotation_interval,
                metadata={
                    'algorithm': 'RSA',
                    'public_key': public_pem.decode('utf-8'),
                    'key_size': str(key_size)
                }
            )
            
            # Store key
            self.active_keys[key_id] = key
            self._save_key(key)
            
            logger.info(f"Generated new RSA-{key_size} key pair: {key_id}")
            
            return key_id, private_pem, public_pem
            
        except ImportError:
            logger.error("cryptography library not available for RSA key generation")
            raise
    
    def generate_hmac_key(self, key_size: int = 256) -> Tuple[str, bytes]:

            raise ValueError("HMAC key size must be 128, 256, or 512 bits")
        
        # Generate random key
        key_data = secrets.token_bytes(key_size // 8)
        key_id = self._generate_key_id(key_data, 'hmac')
        
        # Create key object
        key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            key_type=f'hmac-{key_size}',
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.key_rotation_interval,
            metadata={'algorithm': 'HMAC', 'hash': 'SHA256'}
        )
        
        # Store key
        self.active_keys[key_id] = key
        self._save_key(key)
        
        logger.info(f"Generated new HMAC-{key_size} key: {key_id}")
        
        return key_id, key_data
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:

            logger.warning(f"Key {key_id} has expired")
            return None
        
        # Increment usage count
        key.usage_count += 1
        
        return key
    
    def rotate_key(self, key_id: str) -> Optional[str]:

            logger.error(f"Unknown key type: {old_key.key_type}")
            return None
        
        logger.info(f"Rotated key {key_id} to {new_key_id}")
        
        return new_key_id
    
    def revoke_key(self, key_id: str) -> bool:

        key_file_path = os.path.join(self.key_storage_path, f"{key_id}.key")
        if os.path.exists(key_file_path):
            os.remove(key_file_path)
        
        logger.info(f"Revoked key: {key_id}")
        
        return True
    
    def list_keys(
    self,
    key_type: Optional[str] = None,
    active_only: bool = True
)

        combined = f"{key_type}-{timestamp}-{key_hash[:8].hex()}"
        
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _save_key(self, key: EncryptionKey):

            key_file_path = os.path.join(self.key_storage_path, f"{key.key_id}.key")
            
            # Convert key data to base64 for storage
            key_data_b64 = base64.b64encode(key.key_data).decode('utf-8')
            
            # Create key metadata
            key_metadata = {
                'key_id': key.key_id,
                'key_type': key.key_type,
                'key_data': key_data_b64,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
                'usage_count': key.usage_count,
                'metadata': key.metadata or {}
            }
            
            # Save to file
            import json
            with open(key_file_path, 'w') as f:
                json.dump(key_metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save key {key.key_id}: {e}")
    
    def _load_keys(self):

            logger.error(f"Failed to load keys: {e}")

# Global key management service instance
key_management_service = KeyManagementService()
