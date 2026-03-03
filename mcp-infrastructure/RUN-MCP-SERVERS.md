# How to run the MCP servers

Follow these steps in order. If something fails, use the checklist at the bottom.

---

## 1. Zoho MCP server

### Step 1.1 – Install (once)

In PowerShell:

```powershell
py -m pip install zoho-crm-mcp
```

### Step 1.2 – Check your .env

From the project root:

```powershell
cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure\zoho-mcp
py check-env.py
```

- If it says **MISSING/PLACEHOLDER** for `ZOHO_ACCESS_TOKEN` or `ZOHO_REFRESH_TOKEN`, you need to get real tokens (Step 1.3).
- If it says **Env looks good**, go to Step 1.4.

### Step 1.3 – Get Zoho tokens (if needed)

1. Make sure `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` in `zoho-mcp\.env` are from [Zoho API Console](https://api-console.zoho.com) (Server-based app, redirect `http://localhost:8080/callback`).
2. Run the auth helper:

   ```powershell
   cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure\zoho-mcp
   .\run-auth.ps1
   ```

3. Open the URL it prints → sign in with Zoho (use an account that is part of a **Zoho CRM organization**) → after redirect, copy the `code` from the URL and paste it when asked.
4. The script will print two lines. Put the **first** value into `ZOHO_ACCESS_TOKEN` and the **second** into `ZOHO_REFRESH_TOKEN` in `zoho-mcp\.env` (two different values).

### Step 1.4 – Start the Zoho MCP server

```powershell
cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure\zoho-mcp
.\run-server.ps1
```

You should see something like:

- `Fetching user information...`
- `✓ Authenticated as: Your Name (your@email.com)`
- `Starting Zoho CRM MCP Server in STDIO mode...`
- `Server ready for MCP client connections.`

The process will stay running and talk over stdin/stdout. Your MCP client (e.g. Claude Desktop, or your backend) should start this process and connect to it.

---

## 2. Microsoft 365 MCP server

### Option A – Run with Node (no Docker)

1. Install **Node.js 20+** from [nodejs.org](https://nodejs.org) if you don’t have it.
2. Create `mcp-infrastructure\ms365-mcp\.env` from `.env.example` and set:
   - `MS365_MCP_CLIENT_ID` (Azure app Client ID)
   - `MS365_MCP_CLIENT_SECRET` (Azure app Client secret)
   - `MS365_MCP_TENANT_ID` (e.g. `common` or your tenant ID)
3. From any directory:

   ```powershell
   npx -y @softeria/ms-365-mcp-server --http 3000 --org-mode
   ```

4. First run may ask you to log in (device code). Follow the URL it prints.
5. When it’s running, the MCP endpoint is **http://localhost:3000/mcp**.

### Option B – Run with Docker

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Create `mcp-infrastructure\ms365-mcp\.env` (same variables as above).
3. From the repo:

   ```powershell
   cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure
   docker compose up -d ms365-mcp
   ```

4. MCP endpoint: **http://localhost:3000/mcp**.

---

## 3. Test that they are working

### Test Zoho MCP server

1. Start the server:
   ```powershell
   cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure\zoho-mcp
   .\run-server.ps1
   ```
2. You should see (within a few seconds):
   - `Fetching user information...`
   - `✓ Authenticated as: Your Name (your@email.com)`
   - `Starting Zoho CRM MCP Server in STDIO mode...`
   - `Server ready for MCP client connections.`
3. If you see that, the server is working. It will wait for MCP messages on stdin. Stop it with Ctrl+C.
4. To test from an MCP client: use Claude Desktop (or another client) and add the Zoho server with command `py` and args `run-server.py` (with cwd set to `zoho-mcp`), or use a small script that spawns the server and sends a tool list request.

### Test Microsoft 365 MCP server (HTTP)

1. Start the server (Docker or local):
   ```powershell
   # Docker
   cd c:\Shubham\AI\AI-Interviewer-Matching\mcp-infrastructure
   docker compose up -d ms365-mcp

   # Or local (separate terminal)
   npx -y @softeria/ms-365-mcp-server --http 3000 --org-mode
   ```
2. If using Docker, do device-code login once (see MCP-SETUP-GUIDE.md) or ensure `.env` has valid tokens.
3. Send an MCP **initialize** request to check the endpoint responds:
   ```powershell
   $body = '{"jsonrpc":"2.0","id":"test-1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
   Invoke-RestMethod -Uri "http://localhost:3000/mcp" -Method Post -Body $body -ContentType "application/json" -Headers @{ Accept = "application/json, text/event-stream" }
   ```
   You should get a JSON response with `result` (server capabilities, version). If you see that, the server is working.
4. Optional: use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) or another MCP client, connect to `http://localhost:3000/mcp`, and list/call tools.

### Quick checklist

| Server   | How to test |
|----------|-------------|
| **Zoho** | Run `.\run-server.ps1` → expect `✓ Authenticated as:` and `Server ready`. |
| **MS365** | Run server, then `Invoke-RestMethod` to `http://localhost:3000/mcp` with the JSON above → expect a JSON `result`. |

---

## 4. If something doesn’t work

### Zoho: “Missing tokens” or “Authentication Error”

- Run `py check-env.py` from `mcp-infrastructure\zoho-mcp`. Fix any **MISSING/PLACEHOLDER**.
- Ensure you did **not** put the same value in both `ZOHO_ACCESS_TOKEN` and `ZOHO_REFRESH_TOKEN`. They must be the two different values printed by `run-auth.ps1`.
- If your Zoho account is not part of a CRM org, OAuth will deny CRM access. Use an account that has Zoho CRM (trial or paid).

### Zoho: “Authentication test failed” / “tokens may have expired”

- In `zoho-mcp\.env`, clear `ZOHO_ACCESS_TOKEN` (leave it empty or delete the line), keep `ZOHO_REFRESH_TOKEN`, then run `.\run-server.ps1` again.
- If it still fails, run `.\run-auth.ps1` again and put the **new** access and refresh tokens into `.env`.

### Microsoft 365: “npx not recognized”

- Install Node.js from [nodejs.org](https://nodejs.org) and restart the terminal (or use Docker as in Option B).

### Microsoft 365: Docker “compose” or “up” fails

- Make sure Docker Desktop is running and you’re in `mcp-infrastructure` when running `docker compose up -d ms365-mcp`.
- If `docker-compose.yml` is missing, see `MCP-SETUP-GUIDE.md` for manual Docker run commands.

### Both: “py not recognized”

- Install Python from [python.org](https://www.python.org/downloads/) and ensure “Add Python to PATH” is checked. Restart the terminal. Use `py` (Windows launcher) or `python` from the folder that contains your Python install.
