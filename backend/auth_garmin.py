"""Re-authenticate with Garmin Connect and save tokens.

Run once. Tokens last ~6 months, then re-run this script.
"""
import getpass
import os
from pathlib import Path

from garminconnect import Garmin

TOKENDIR = str(Path.home() / ".garminconnect")
os.makedirs(TOKENDIR, exist_ok=True)

print("Garmin Connect re-authentication")
print("=================================")
print(f"Tokens will be saved to: {TOKENDIR}\n")

email = input("Email: ").strip()
password = getpass.getpass("Password (input hidden): ")


def ask_mfa():
    return input("\nMFA code (check your email/phone): ").strip()


print("\nLogging in...")
try:
    client = Garmin(email=email, password=password, prompt_mfa=ask_mfa)
    client.login()
except TypeError:
    client = Garmin(email=email, password=password)
    client.login()

print("Saving tokens...")
client.garth.dump(TOKENDIR)

print(f"\n[OK] Tokens saved to {TOKENDIR}")
print("Restart the backend now:")
print("  1. Close the 'Dashboard Backend' window")
print("  2. Re-run start-dashboard.bat")