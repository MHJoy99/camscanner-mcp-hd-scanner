# CamScanner MCP Integration & Architecture Guide

This document provides complete instructions for integrating the **CamScanner Remote Model Context Protocol (MCP)** server with AI agents, developer IDEs, and CLI workflows. It covers remote HTTP streamable protocol mechanics, client configurations, OAuth authentication flows, the `camscanner-cli` utility command reference, and a performance/feature comparison with the included local Python OpenCV batch scanner engine.

---

## Table of Contents

1. [Overview: Remote Streamable HTTP MCP Server](#1-overview-remote-streamable-http-mcp-server)
2. [Client Configuration Blocks](#2-client-configuration-blocks)
   - [Kilo CLI (`kilo.json` / `kilo.jsonc`)](#kilo-cli-kilojson--kilojsonc)
   - [Claude Desktop (`claude_desktop_config.json`)](#claude-desktop-claude_desktop_configjson)
   - [Cursor / VS Code Agent Manager](#cursor--vs-code-agent-manager)
3. [OAuth 2.0 / 2.1 Workflow Instructions](#3-oauth-20--21-workflow-instructions)
4. [`camscanner-cli` Command Reference](#4-camscanner-cli-command-reference)
5. [Architecture Comparison: Remote MCP vs. Local Python Engine](#5-architecture-comparison-remote-mcp-vs-local-python-engine)
6. [Troubleshooting & Best Practices](#6-troubleshooting--best-practices)

---

## 1. Overview: Remote Streamable HTTP MCP Server

CamScanner offers an official, cloud-hosted remote Model Context Protocol (MCP) server accessible at:

```
https://ai-tools.camscanner.com/mcp
```

### Protocol & Transport Mechanics

- **Transport:** HTTP Server-Sent Events (SSE) / Streamable HTTP POST.
- **Protocol Standard:** Anthropic Model Context Protocol (MCP) v1.x specification.
- **Session Lifecycle:** Stateful or stateless session negotiation via HTTP headers (`Authorization: Bearer <TOKEN>`, `Mcp-Session-Id`).
- **Streaming Pipeline:** Tool execution responses (such as multi-page OCR chunking and PDF progress) stream incrementally to prevent client timeouts during multi-gigabyte or high-resolution document processing.
- **Capabilities Provided:**
  - `tools`: Document enhancement, edge correction, Magic Color filtering, optical character recognition (OCR), table extraction, PDF merging, document search.
  - `resources`: Access to synced cloud notebooks, scanned books, folders, and shared document links.
  - `prompts`: Specialized document analysis prompts (receipt categorization, contract legal review, study notes extraction).

---

## 2. Client Configuration Blocks

### Kilo CLI (`kilo.json` / `kilo.jsonc`)

Add the CamScanner remote server definition under the `"mcp"` section of your global (`~/.config/kilo/kilo.jsonc`) or project-level configuration file:

```jsonc
{
  "$schema": "https://kilo.dev/config.schema.json",
  "mcp": {
    "camscanner": {
      "type": "remote",
      "url": "https://ai-tools.camscanner.com/mcp",
      "headers": {
        "Authorization": "Bearer ${CAMSCANNER_ACCESS_TOKEN}",
        "X-Client-Agent": "Kilo-CLI/1.0"
      },
      "timeout": 120000,
      "enabled": true
    }
  },
  "permissions": {
    "camscanner_*": "allow"
  }
}
```

*Note:* When using environmental tokens, set `$env:CAMSCANNER_ACCESS_TOKEN = "<your_token>"` in PowerShell or declare it in your system user environment variables.

---

### Claude Desktop (`claude_desktop_config.json`)

Configure Claude Desktop by editing the configuration file located at:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Because Claude Desktop natively connects to local stdio transports, use an SSE bridge adapter (e.g. `mcp-remote` / `npx -y @modelcontextprotocol/server-sse-client`) or configure the remote endpoint directly:

#### Option A: Using Remote MCP Proxy (Recommended for stdio compatibility)

```json
{
  "mcpServers": {
    "camscanner": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://ai-tools.camscanner.com/mcp",
        "--header",
        "Authorization: Bearer YOUR_CAMSCANNER_ACCESS_TOKEN"
      ],
      "env": {
        "CAMSCANNER_OAUTH_SCOPE": "mcp:tools"
      }
    }
  }
}
```

#### Option B: Direct HTTP Endpoint (Supported in Claude Desktop v0.8+)

```json
{
  "mcpServers": {
    "camscanner": {
      "url": "https://ai-tools.camscanner.com/mcp",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_CAMSCANNER_ACCESS_TOKEN"
      }
    }
  }
}
```

---

### Cursor / VS Code Agent Manager

In Cursor or VS Code with Agent Manager / Roo-Code / Cline extensions, configure the MCP server within the settings interface or in `.vscode/mcp.json`:

#### `.vscode/mcp.json` or Global Settings

```json
{
  "servers": {
    "camscanner-remote": {
      "name": "CamScanner AI Cloud",
      "type": "sse",
      "url": "https://ai-tools.camscanner.com/mcp",
      "headers": {
        "Authorization": "Bearer ${CAMSCANNER_TOKEN}"
      },
      "autoApprove": [
        "image_ocr",
        "doc_search",
        "image_merge_pdf"
      ]
    }
  }
}
```

#### Cursor Settings UI (Manual Setup)
1. Navigate to **Cursor Settings** -> **Features** -> **MCP**.
2. Click **+ Add New MCP Server**.
3. Select type: **SSE / Streamable HTTP**.
4. Set Name: `camscanner`.
5. Set Server URL: `https://ai-tools.camscanner.com/mcp`.
6. Add Header: `Authorization: Bearer <your_access_token>`.
7. Click **Save** and verify the green status indicator.

---

## 3. OAuth 2.0 / 2.1 Workflow Instructions

To invoke CamScanner remote tools, agents and CLI clients authenticate against CamScanner Account Services using the OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange).

### 1. Prerequisite Permissions & Scopes
- Required Scope: `mcp:tools` (Grants permission to execute remote scanner operations, OCR pipelines, and PDF generation).
- Extended Read Scope (Optional): `mcp:docs:read` (Grants permission to query cloud doc search and document metadata).

### 2. Authentication Steps

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as camscanner-cli / Agent
    participant Browser as Web Browser
    participant Auth as CamScanner OAuth Server
    participant MCP as CamScanner MCP (ai-tools.camscanner.com)

    CLI->>CLI: Generate PKCE Code Verifier & Challenge
    CLI->>Browser: Open https://ai-tools.camscanner.com/oauth/authorize
    Note over Browser,Auth: Scope: mcp:tools<br/>Response Type: code<br/>Code Challenge Method: S256
    Browser->>User: Display Login & Consent Screen
    User->>Browser: Approve Access
    Browser->>Auth: Submit Credentials & Consent
    Auth-->>CLI: Redirect to http://127.0.0.1:8765/callback?code=AUTH_CODE
    CLI->>Auth: POST /oauth/token (code, code_verifier, client_id)
    Auth-->>CLI: Return access_token & refresh_token
    CLI->>MCP: Call Tool with Authorization: Bearer <access_token>
    MCP-->>CLI: Streaming Tool Response (JSON-RPC 2.0)
```

### 3. Step-by-Step Browser Sign-In Procedure

1. **Initiate Login:**
   Run the CLI authorization command:
   ```bash
   camscanner-cli auth login --scope mcp:tools
   ```
2. **Interactive Authentication:**
   - A local ephemeral HTTP listener starts on `http://127.0.0.1:8765/callback`.
   - Your default browser automatically opens the CamScanner Authorization Gateway.
   - Sign in via Email, Phone, Apple ID, or Google Account.
3. **Approve Scopes:**
   Confirm access for **Model Context Protocol Engine (`mcp:tools`)**.
4. **Token Persistence:**
   Upon successful redirect, the token is securely written to:
   - **Windows:** `%USERPROFILE%\.camscanner\credentials.json`
   - **Linux/macOS:** `~/.camscanner/credentials.json`
5. **Token Refresh:**
   The client automatically uses the stored `refresh_token` to renew expired access tokens without interrupting your workflow.

---

## 4. `camscanner-cli` Command Reference

The `camscanner-cli` binary provides an interface for humans and AI agents to authenticate, scan, convert, OCR, and query documents.

### Global Options

| Option | Flag | Description |
| :--- | :--- | :--- |
| `--config <path>` | `-c` | Custom path to configuration file |
| `--token <token>` | `-t` | Explicit bearer token override |
| `--verbose` | `-v` | Enable detailed HTTP & RPC debug traces |
| `--format <type>` | `-f` | Output serialization: `json`, `text`, or `markdown` |

---

### Commands

#### 1. `auth login`
Authenticate user session through browser-based OAuth 2.0 PKCE flow.

```bash
# Standard interactive login with mcp:tools scope
camscanner-cli auth login --scope mcp:tools

# Headless / device code mode (for SSH sessions)
camscanner-cli auth login --device-code --scope mcp:tools

# Check status of current authentication credentials
camscanner-cli auth status

# Revoke token and log out
camscanner-cli auth logout
```

#### 2. `image merge-pdf`
Enhance and compile a series of raw images or entire directories into an optimized, high-fidelity PDF document.

```bash
# Merge a folder of images into a single PDF using cloud Magic Color filter
camscanner-cli image merge-pdf \
  --input-dir "D:\Camscanner PDF\PDF 1" \
  --output "D:\Camscanner PDF\output\Merged_Document.pdf" \
  --filter magic-color \
  --page-size auto \
  --quality 95

# Merge specific individual image files with automatic edge correction
camscanner-cli image merge-pdf \
  --files "page1.jpg,page2.jpg,page3.jpg" \
  --output "Compiled.pdf" \
  --auto-crop true \
  --dpi 300
```

*Options for `image merge-pdf`:*
- `--filter`: `original`, `magic-color`, `b&w`, `grayscale`, `super-clean`.
- `--auto-crop`: `true` or `false` (perspective quad warp).
- `--quality`: Compression quality factor `10`–`100` (Default: `95`).
- `--dpi`: Target raster density, e.g., `150`, `300`, `600`.

#### 3. `image ocr`
Extract text, structural formatting, and data tables from images or PDFs via CamScanner Deep Neural OCR.

```bash
# Perform multilingual OCR on a single image and print markdown
camscanner-cli image ocr \
  --input "./samples/raw_photo_01.jpg" \
  --lang auto \
  --format markdown \
  --include-tables

# Extract text from an entire multi-page PDF document into a text file
camscanner-cli image ocr \
  --input "./output/Sample_Document.pdf" \
  --output "./output/Sample_Document_Transcript.md" \
  --detect-orientation \
  --preserve-layout
```

*Options for `image ocr`:*
- `--lang`: Language code (`auto`, `en`, `zh`, `es`, `fr`, `de`, `ja`, `ko`, etc.).
- `--format`: `text`, `markdown`, `json`, `hocr`, `searchable-pdf`.
- `--preserve-layout`: Preserves multi-column layout, headers, and bullet points.
- `--include-tables`: Formats structured financial and scientific tables as Markdown/CSV.

#### 4. `doc search`
Search across indexed CamScanner cloud documents, OCR transcriptions, tags, and notebook content.

```bash
# Full-text semantic search across indexed documents
camscanner-cli doc search "quantum mechanics wave equation"

# Filter search results by creation date and tag
camscanner-cli doc search "invoice 2026" \
  --folder "Receipts" \
  --tag "Business" \
  --limit 10 \
  --format json
```

*Options for `doc search`:*
- `--folder`: Filter search to a specific remote cloud folder.
- `--tag`: Filter results by user tags.
- `--limit`: Maximum number of search hits returned (Default: `20`).
- `--include-snippet`: Include surrounding contextual sentences.

---

## 5. Architecture Comparison: Remote MCP vs. Local Python Engine

This workspace includes an optimized, standalone Python OpenCV processing pipeline located at:
`D:\Camscanner PDF\scripts\batch_scanner.py` (and `scan_to_pdf.py`).

The table below outlines the architectural trade-offs between utilizing the Remote CamScanner MCP service versus running the local Python batch engine:

| Dimension | Remote CamScanner MCP Server (`ai-tools.camscanner.com`) | Local Python Scanner Engine (`scripts/batch_scanner.py`) |
| :--- | :--- | :--- |
| **Execution Environment** | Hosted Cloud / Scalable Distributed Serverless Workers | Local Workstation CPU / GPU (OpenCV + NumPy + Pillow) |
| **Edge Detection & Warp** | Cloud Deep-Learning Edge Model (Tolerates complex clutter, folds, wrinkles) | Canny Edge + Morphological Close + Contour Approximation (`cv2.findContours`) |
| **Color Filtering** | Proprietary Neural Color Balancing & Shadow Eradication | Adaptive Background Normalization (`cv2.dilate` + `medianBlur` + Look-Up Table) |
| **OCR Capabilities** | Integrated Deep Multi-Language OCR, Equation and Table Parser | None (Requires external engine like Tesseract or EasyOCR) |
| **Document Search** | Remote semantic search & cloud notebook vector indexing | Local file system glob search only |
| **Latency / Throughput** | ~500ms–2000ms per page (Network dependent) | ~40ms–150ms per page (Blazing fast local execution) |
| **Network & Privacy** | Requires Internet & OAuth; documents transit to cloud | 100% Offline, Air-gapped, Zero data egress |
| **API Costs / Limits** | Requires CamScanner Pro / API quota subscription | Completely free, unlimited processing, zero quota |
| **Ideal Use Case** | Final cloud archiving, searchable text OCR, agentic chat synthesis | High-volume offline digitizing of camera photo dumps into HD PDFs |

### When to Use Which?

1. **Use Local Python (`batch_scanner.py`) when:**
   - You need to transform dozens or hundreds of high-resolution camera images into clean, shadow-free, high-DPI PDFs rapidly.
   - Working in air-gapped or confidential environments without Internet access.
   - Running automated bulk local build steps or CI/CD pipelines without API costs.

2. **Use Remote CamScanner MCP when:**
   - AI models (Kilo, Claude, Cursor) need on-demand tools to inspect, transcribe, or search document contents.
   - Full-text multi-lingual OCR or structured table extraction is required.
   - Creating cloud-synced, indexed documents accessible across mobile and web interfaces.

---

## 6. Troubleshooting & Best Practices

### Resolving Connection Issues
- **Error `401 Unauthorized`:**
  Run `camscanner-cli auth login --scope mcp:tools` to refresh your expired access token.
- **Connection Timeout / Firewall:**
  Ensure outbound HTTPS traffic to `ai-tools.camscanner.com:443` is permitted. If behind a corporate proxy, export:
  ```bash
  $env:HTTPS_PROXY = "http://proxy.internal:8080"
  ```
- **Stream Interruption:**
  Ensure your client configuration allocates at least `120000ms` (2 minutes) timeout for large PDF OCR transformations.

### Combining Both Engines for Optimal Performance
For large datasets, use the local engine for initial edge detection, shadow whitening, and PDF compilation, then submit the compiled document to the CamScanner MCP endpoint for deep text recognition and indexing:

```powershell
# Step 1: Process local camera captures using Python
python scripts/batch_scanner.py "path/to/raw_photos" "output/Scanned_Document_HD.pdf"

# Step 2: Use CamScanner remote OCR via CLI or Agent
camscanner-cli image ocr --input "output/Scanned_Document_HD.pdf" --format markdown --output "output/Document_Transcript.md"
```
