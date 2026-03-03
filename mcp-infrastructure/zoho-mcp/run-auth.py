"""
Run Zoho MCP auth with .env loaded from this script's directory.
Use this if "py -m zoho_mcp.auth_cli" says env vars are missing.
"""
import os
import sys

# Force .env to be loaded from this folder (script directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# Now run the real auth CLI
from zoho_mcp.auth_cli import main
sys.exit(main() or 0)
