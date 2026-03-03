# MCP Infrastructure

This folder contains Docker setup and env examples for **Microsoft 365 MCP** and **Zoho MCP** servers. Your FastAPI backend will connect to these instead of calling Microsoft Graph or Zoho APIs directly.

**Full step-by-step instructions:** [MCP-SETUP-GUIDE.md](./MCP-SETUP-GUIDE.md)

---

## Quick start

### 1. Create env files (required before run)

```powershell
# Microsoft 365 – copy example and add your Azure app credentials
copy ms365-mcp\.env.example ms365-mcp\.env
# Edit ms365-mcp\.env with MS365_MCP_CLIENT_ID, MS365_MCP_CLIENT_SECRET, MS365_MCP_TENANT_ID

# Zoho – copy example and add your Zoho credentials + tokens
copy zoho-mcp\.env.example zoho-mcp\.env
# Edit zoho-mcp\.env with real ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET from Zoho API Console
# Then get tokens: see "Zoho auth (Windows)" below if uvx/pip are not on PATH
```

### 2. Run the servers

**Microsoft 365 (Docker recommended – HTTP):**

```powershell
cd mcp-infrastructure
docker compose up -d ms365-mcp
```

- **Microsoft 365 MCP** will listen at **http://localhost:3000** (MCP endpoint: **http://localhost:3000/mcp**).

**Zoho (no Docker needed – stdio):**

- Your MCP client (e.g. backend or Claude Desktop) **spawns** the Zoho server when needed. Just run it locally: `uvx --from zoho-crm-mcp zoho-mcp` (with `.env` in that directory or env vars set). Docker for Zoho is optional and usually unnecessary.

### 3. Run Microsoft 365 locally (no Docker)

```powershell
npx -y @softeria/ms-365-mcp-server --http 3000 --org-mode
```

**Zoho** is always run locally (or spawned by your MCP client): `uvx --from zoho-crm-mcp zoho-mcp` with your `.env` in place.

### Zoho auth (Windows – when `uvx` or `pip` are not on PATH)

1. Install the package using the Python launcher:
   ```powershell
   py -m pip install zoho-crm-mcp
   ```
2. Put your real **ZOHO_CLIENT_ID** and **ZOHO_CLIENT_SECRET** in `zoho-mcp\.env` (from [Zoho API Console](https://api-console.zoho.com)).
3. From the repo root, run the auth helper (so it finds `.env`):
   ```powershell
   cd mcp-infrastructure\zoho-mcp
   $env:PYTHONIOENCODING = "utf-8"
   py -m zoho_mcp.auth_cli
   ```
   If the script is not found, use the full path to the installed executable:
   ```powershell
   & "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\Scripts\zoho-mcp-auth.exe"
   ```
   (Adjust `pythoncore-3.14-64` if your Python version folder name is different.)
4. Open the URL it prints, sign in with Zoho, then paste the `code` from the redirect URL. Copy the printed `ZOHO_ACCESS_TOKEN` and `ZOHO_REFRESH_TOKEN` into `zoho-mcp\.env`.

To run the Zoho MCP server without uvx (from any directory):
   ```powershell
   cd mcp-infrastructure\zoho-mcp
   .\run-server.ps1
   ```
   Or: `py run-server.py` from inside `zoho-mcp`, or `py -m zoho_mcp.server` after `cd` to `zoho-mcp`.

---

## Testing

- **MS365:** Open or POST to `http://localhost:3000/mcp` with MCP client (e.g. MCP Inspector, or your backend). You must complete device-code login or OAuth first (see guide).
- **Zoho:** Run the server and use an MCP client that spawns it (e.g. Claude Desktop, or a Python MCP client with stdio transport); call a tool like get user info.

See [MCP-SETUP-GUIDE.md](./MCP-SETUP-GUIDE.md) for credential setup (Azure and Zoho) and detailed testing steps.

**Still not able to run a server?** Use the step-by-step guide: [RUN-MCP-SERVERS.md](./RUN-MCP-SERVERS.md). For Zoho, run `py check-env.py` from `zoho-mcp` to see what’s missing in your `.env`.
