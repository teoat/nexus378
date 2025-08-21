"""
Key Management Service for AI Service
Handles encryption key generation, storage, and rotation
"""

import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class EncryptionKey:
    """Encryption key data structure"""
    key_id: str
    key_data: bytes
    key_type: str  # 'aes-256', 'rsa-2048', 'hmac'
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool = True
    usage_count: int = 0
    metadata: Dict[str, str] = None

class KeyManagementService:
    """Service for managing encryption keys"""
    
    def __init__(self, key_storage_path: Optional[str] = None):
        self.key_storage_path = key_storage_path or os.path.join(os.getcwd(), 'keys')
        self.active_keys: Dict[str, EncryptionKey] = {}
        self.key_rotation_interval = timedelta(days=90)  # 90 days
        self.max_key_age = timedelta(days=365)  # 1 year
        
        # Ensure key storage directory exists
        os.makedirs(self.key_storage_path, exist_ok=True)
        
        # Load existing keys
        self._load_keys()
    
    def generate_aes_key(self, key_size: int = 256) -> Tuple[str, bytes]:
        """Generate a new AES key"""
        if key_size not in [128, 192, 256]:
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
        """Generate a new RSA key pair"""
        if key_size not in [1024, 2048, 4096]:
            raise ValueError("RSA key size must be 1024, 2048, or 4096 bits")
        
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
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
        """Generate a new HMAC key"""
        if key_size not in [128, 256, 512]:
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
        """Get an encryption key by ID"""
        if key_id not in self.active_keys:
            return None
        
        key = self.active_keys[key_id]
        
        # Check if key is expired
        if key.expires_at and datetime.utcnow() > key.expires_at:
            logger.warning(f"Key {key_id} has expired")
            return None
        
        # Increment usage count
        key.usage_count += 1
        
        return key
    
    def rotate_key(self, key_id: str) -> Optional[str]:
        """Rotate an existing key"""
        if key_id not in self.active_keys:
            return None
        
        old_key = self.active_keys[key_id]
        
        # Deactivate old key
        old_key.is_active = False
        
        # Generate new key of same type
        if old_key.key_type.startswith('aes'):
            new_key_id, _ = self.generate_aes_key(int(old_key.key_type.split('-')[1]))
        elif old_key.key_type.startswith('rsa'):
            new_key_id, _, _ = self.generate_rsa_key_pair(int(old_key.key_type.split('-')[1]))
        elif old_key.key_type.startswith('hmac'):
            new_key_id, _ = self.generate_hmac_key(int(old_key.key_type.split('-')[1]))
        else:
            logger.error(f"Unknown key type: {old_key.key_type}")
            return None
        
        logger.info(f"Rotated key {key_id} to {new_key_id}")
        
        return new_key_id
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an encryption key"""
        if key_id not in self.active_keys:
            return False
        
        key = self.active_keys[key_id]
        key.is_active = False
        
        # Remove from active keys
        del self.active_keys[key_id]
        
        # Delete key file
        key_file_path = os.path.join(self.key_storage_path, f"{key_id}.key")
        if os.path.exists(key_file_path):
            os.remove(key_file_path)
        
        logger.info(f"Revoked key: {key_id}")
        
        return True
    
    def list_keys(self, key_type: Optional[str] = None, active_only: bool = True) -> List[Dict]:
        """List all keys with optional filtering"""
        keys = []
        
        for key in self.active_keys.values():
            if key_type and not key.key_type.startswith(key_type):
                continue
            
            if active_only and not key.is_active:
                continue
            
            keys.append({
                'key_id': key.key_id,
                'key_type': key.key_type,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
                'usage_count': key.usage_count,
                'metadata': key.metadata
            })
        
        return keys
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys"""
        now = datetime.utcnow()
        expired_keys = []
        
        for key_id, key in self.active_keys.items():
            if key.expires_at and now > key.expires_at:
                expired_keys.append(key_id)
        
        for key_id in expired_keys:
            self.revoke_key(key_id)
        
        return len(expired_keys)
    
    def _generate_key_id(self, key_data: bytes, key_type: str) -> str:
        """Generate a unique key ID"""
        # Create hash of key data
        key_hash = hashlib.sha256(key_data).digest()
        
        # Combine with key type and timestamp
        timestamp = str(int(datetime.utcnow().timestamp()))
        combined = f"{key_type}-{timestamp}-{key_hash[:8].hex()}"
        
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _save_key(self, key: EncryptionKey):
        """Save key to storage"""
        try:
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
        """Load keys from storage"""
        try:
            for filename in os.listdir(self.key_storage_path):
                if not filename.endswith('.key'):
                    continue
                
                key_file_path = os.path.join(self.key_storage_path, filename)
                
                with open(key_file_path, 'r') as f:
                    import json
                    key_data = json.load(f)
                
                # Recreate key object
                key = EncryptionKey(
                    key_id=key_data['key_id'],
                    key_data=base64.b64decode(key_data['key_data']),
                    key_type=key_data['key_type'],
                    created_at=datetime.fromisoformat(key_data['created_at']),
                    expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data['expires_at'] else None,
                    is_active=key_data['is_active'],
                    usage_count=key_data['usage_count'],
                    metadata=key_data.get('metadata', {})
                )
                
                # Only load active keys
                if key.is_active:
                    self.active_keys[key.key_id] = key
                    
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")

# Global key management service instance
key_management_service = KeyManagementService()
