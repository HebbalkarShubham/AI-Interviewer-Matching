"""
Check Zoho MCP .env: report what is set or missing (no secrets printed).
Run from this folder or: py check-env.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
env_path = os.path.join(SCRIPT_DIR, ".env")

if not os.path.isfile(env_path):
    print("ERROR: .env file not found in", SCRIPT_DIR)
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(env_path)

def ok(name, val):
    return "OK" if (val and str(val).strip() and not str(val).startswith("your_")) else "MISSING/PLACEHOLDER"

client_id   = os.getenv("ZOHO_CLIENT_ID", "")
client_sec  = os.getenv("ZOHO_CLIENT_SECRET", "")
redirect    = os.getenv("ZOHO_REDIRECT_URI", "")
api_domain  = os.getenv("ZOHO_API_DOMAIN", "")
access      = os.getenv("ZOHO_ACCESS_TOKEN", "")
refresh     = os.getenv("ZOHO_REFRESH_TOKEN", "")

print("Zoho MCP .env check (values not printed):")
print("  ZOHO_CLIENT_ID      ", ok("ZOHO_CLIENT_ID", client_id))
print("  ZOHO_CLIENT_SECRET  ", ok("ZOHO_CLIENT_SECRET", client_sec))
print("  ZOHO_REDIRECT_URI   ", ok("ZOHO_REDIRECT_URI", redirect))
print("  ZOHO_API_DOMAIN     ", ok("ZOHO_API_DOMAIN", api_domain))
print("  ZOHO_ACCESS_TOKEN   ", ok("ZOHO_ACCESS_TOKEN", access))
print("  ZOHO_REFRESH_TOKEN  ", ok("ZOHO_REFRESH_TOKEN", refresh))
print()

if not client_id or not client_sec:
    print("Fix: Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET from Zoho API Console.")
    sys.exit(1)
if not refresh and not access:
    print("Fix: Run .\\run-auth.ps1 (or py run-auth.py), complete OAuth, then add the printed")
    print("     ZOHO_ACCESS_TOKEN and ZOHO_REFRESH_TOKEN to .env (two different values).")
    sys.exit(1)
if str(refresh).strip().startswith("your_") or str(access).strip().startswith("your_"):
    print("Fix: Replace placeholder tokens with real values from run-auth.ps1 / run-auth.py.")
    sys.exit(1)

print("Env looks good. Start the server with: .\\run-server.ps1  or  py run-server.py")
sys.exit(0)
