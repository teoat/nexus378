import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# For simplicity, we use a fixed key here.
# In a real application, this should be a securely managed secret.
ENCRYPTION_KEY = (
    b"_Y\x99\x1d\xf2\x0b\x8av\xe6\xc2\x08\x05\xbf\xc1\x80\x90"
    b"\x91\x9a\x9d\x16\xf0\x01\x14\x81\xf5\x0c\x91\x9b\x87\x9e\x8d\x8b"
)


def encrypt(data: str, key: bytes) -> str:
    """Encrypts data using AES-256-GCM."""
    iv = os.urandom(12)
    encryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv), backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(data.encode("utf-8")) + encryptor.finalize()
    return base64.b64encode(iv + encryptor.tag + ciphertext).decode("utf-8")


def decrypt(encrypted_data: str, key: bytes) -> str:
    """Decrypts data using AES-256-GCM."""
    data = base64.b64decode(encrypted_data.encode("utf-8"))
    iv = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]

    decryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
    ).decryptor()

    return (decryptor.update(ciphertext) + decryptor.finalize()).decode("utf-8")
