"""
Run Zoho MCP server with .env loaded from this script's directory.
Use this so the server finds .env no matter where you start it from.
"""
import os
import sys

# Force .env to be loaded from this folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# Run the Zoho MCP server
from zoho_mcp.server import main
sys.exit(main() or 0)
