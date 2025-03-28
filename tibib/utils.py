import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

AES_KEY = base64.b64decode(os.getenv("AES_KEY"))
AES_IV = base64.b64decode(os.getenv("AES_IV"))

def encode_value(value):
    """
    Encrypts a single value using AES.
    """
    padder = padding.PKCS7(128).padder()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()

    # Convert value to string and pad it
    value_str = str(value)
    padded_data = padder.update(value_str.encode('utf-8')) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data.hex()  # Convert bytes to hex string