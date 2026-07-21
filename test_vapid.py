# test_vapid.py
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

private_key = os.environ.get('VAPID_PRIVATE_KEY')
public_key = os.environ.get('VAPID_PUBLIC_KEY')
email = os.environ.get('VAPID_EMAIL', 'admin@kuravote.com')

print("="*60)
print("VAPID Keys Status")
print("="*60)
print(f"VAPID_PRIVATE_KEY: {'✅ Set' if private_key else '❌ Missing'}")
print(f"VAPID_PUBLIC_KEY: {'✅ Set' if public_key else '❌ Missing'}")
print(f"VAPID_EMAIL: {email}")

if private_key and public_key:
    print("\n✅ All VAPID keys are configured correctly!")
    print(f"Private key length: {len(private_key)} characters")
    print(f"Public key length: {len(public_key)} characters")
else:
    print("\n❌ Some VAPID keys are missing. Please check your .env file.")