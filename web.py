# generate_keys_manual.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Convert to base64
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Get base64url encoded keys (without padding)
private_b64 = base64.urlsafe_b64encode(private_pem).decode('utf-8').rstrip('=')
public_b64 = base64.urlsafe_b64encode(public_pem).decode('utf-8').rstrip('=')

print("="*60)
print("VAPID KEYS - Add these to your environment variables")
print("="*60)
print(f"VAPID_PRIVATE_KEY={private_b64}")
print(f"VAPID_PUBLIC_KEY={public_b64}")
print("="*60)
print("\nNote: The private key must be kept secret!")
