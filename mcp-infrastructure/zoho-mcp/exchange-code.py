"""
Exchange Zoho authorization code for access & refresh tokens using the CORRECT accounts server.
Use this when run-auth.ps1 says "Token generation successful!" but prints blank ZOHO_ACCESS_TOKEN/ZOHO_REFRESH_TOKEN
(e.g. because you use Zoho India and the default script uses accounts.zoho.com).
"""
import os
import sys
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

client_id = os.getenv("ZOHO_CLIENT_ID")
client_secret = os.getenv("ZOHO_CLIENT_SECRET")
redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "http://localhost:8080/callback")

# Use ZOHO_ACCOUNTS_URL for token exchange. For Zoho India use https://accounts.zoho.in
# (Your redirect had accounts-server=https://accounts.zoho.in)
accounts_url = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com").rstrip("/")
token_url = f"{accounts_url}/oauth/v2/token"

if not client_id or not client_secret:
    print("ERROR: Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET in .env")
    sys.exit(1)

if len(sys.argv) > 1 and sys.argv[1].strip():
    code = sys.argv[1].strip()
else:
    # Print auth URL for Zoho India so user can get a new code (previous code may be one-time use)
    from urllib.parse import urlencode
    auth_params = {
        "scope": os.getenv("ZOHO_SCOPE", "ZohoCRM.modules.ALL,ZohoCRM.users.READ"),
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
    }
    auth_url = f"{accounts_url}/oauth/v2/auth?{urlencode(auth_params)}"
    print("Open this URL in your browser (Zoho India), sign in, then copy the 'code' from the redirect URL:\n")
    print(auth_url)
    print("\nThen run: py exchange-code.py <paste_the_code_here>")
    print("Or paste the code below:\n")
    code = input("Authorization code: ").strip()
if not code:
    print("No code provided.")
    sys.exit(1)

print(f"Exchanging code with {token_url} ...")
resp = requests.post(token_url, data={
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "code": code,
})

if resp.status_code != 200:
    print(f"Token exchange failed ({resp.status_code}): {resp.text}")
    sys.exit(1)

data = resp.json()
if "error" in data:
    print(f"Error from Zoho: {data.get('error')} - {data.get('description', data.get('error_description', ''))}")
    sys.exit(1)

access = data.get("access_token", "")
refresh = data.get("refresh_token", "")

if not access and not refresh:
    print("Zoho did not return access_token or refresh_token. Response:", data)
    sys.exit(1)

print("\nToken generation successful! Add these lines to your .env file:\n")
print(f"ZOHO_ACCESS_TOKEN={access}")
print(f"ZOHO_REFRESH_TOKEN={refresh}")
print("\nThen run: .\\run-server.ps1")
sys.exit(0)
