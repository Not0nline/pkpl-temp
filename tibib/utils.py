import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from django.conf import settings
import re


def encrypt_and_sign(message):
    # Convert message to bytes
    message_bytes = message.encode('utf-8')

    encrypted_message = settings.RECEIVER_PUBLIC_KEY.encrypt(
        message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Sign the message with the sender's private key
    signature = settings.SENDER_PRIVATE_KEY.sign(
        encrypted_message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return base64.b64encode(encrypted_message).decode(), base64.b64encode(signature).decode()


def decrypt_and_verify(encrypted_message, signature):
    # Decode Base64
    encrypted_message = base64.b64decode(encrypted_message)
    signature = base64.b64decode(signature)

    try:
        settings.SENDER_PUBLIC_KEY.verify(
            signature,
            encrypted_message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Decrypt the message
        decrypted_message = settings.RECEIVER_PRIVATE_KEY.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted_message
    except Exception as e:
        print("Signature verification failed!", e)

import re

def sanitize_input(value, digits_only=False):
    """
    Sanitize input with optional digits-only enforcement
    
    Args:
        value: Input value to sanitize
        digits_only: If True, only allow digits (0-9)
    
    Returns:
        Sanitized string or None if value was None/empty
    """
    if not value:
        return value
        
    if digits_only:
        # Remove all non-digit characters
        return re.sub(r'[^\d]', '', value)
    else:
        # Default sanitization - remove dangerous characters
        return re.sub(r'[<>"\'%;()&+]', '', value).strip()