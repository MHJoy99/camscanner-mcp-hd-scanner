# Promotion Kit: CamScanner MCP & HD Auto-Scanner 🚀

This promotion kit contains ready-to-post announcements, launch copy, and promotional threads tailored for major developer communities, social platforms, and AI forums.

---

## 1. Show HN (Hacker News) 🟠

**Title:**  
Show HN: CamScanner MCP – 100% free local document scanner without watermarks

**Link/Text:**  
https://github.com/MHJoy99/camscanner-mcp-hd-scanner

**Submission Body:**  
Hey HN,

Like many of you, I've used CamScanner for years to quickly snap notes and physical documents with my phone. But their free tier has gotten increasingly frustrating: compressed resolution, severe batch page limits, and an intrusive "Scanned with CamScanner" watermark on every exported PDF (unless you pay $49.99/year for Premium).

So we built an open-source solution that does two things:

1. **Local OpenCV/Python Engine (Zero Watermark, 300 DPI HD):**
   - Implements the "Magic Color" filter locally: uses morphological dilation and spatial median filtering to isolate uneven lighting and ambient phone shadows.
   - Normalizes background to crisp white (`#FFFFFF`) while deepening ink and boosting contrast (+420%).
   - Applies an adaptive unsharp mask for mathematical formulas and fine handwriting.
   - Batches unlimited mobile photos into a single high-definition 300 DPI PDF in seconds without leaving your computer.

2. **Official CamScanner Model Context Protocol (MCP) Integration:**
   - Full MCP bridge connecting Claude Desktop, Kilo CLI, and Cursor to CamScanner's remote Streamable HTTP server (`https://ai-tools.camscanner.com/mcp`) for cloud OCR, layout parsing, and document translation directly inside AI agent workflows.

Repo: https://github.com/MHJoy99/camscanner-mcp-hd-scanner  
License: MIT

Would love to hear your thoughts and feedback!

---

## 2. Reddit (r/Python, r/MachineLearning, r/opensource, r/ClaudeAI) 🔴

**Post Title:**  
I open-sourced a free CamScanner alternative in Python + MCP server integration (no watermarks, 300 DPI HD)

**Body:**  
Tired of paying $49.99/year for CamScanner Premium just to remove the watermark and export in HD?

I built **camscanner-mcp-hd-scanner**:
👉 https://github.com/MHJoy99/camscanner-mcp-hd-scanner

### What it does:
- **Zero Watermark:** 100% clean PDF exports.
- **Magic Color Algorithm:** Uses OpenCV to subtract phone shadows, whiten yellowed paper background to pure `#FFFFFF`, and sharpen fine ink/formulas.
- **Batch Processing:** Drop 20, 50, or 100+ raw mobile photos in a folder and get an organized multi-page 300 DPI PDF in ~3 seconds.
- **Model Context Protocol (MCP):** Comes pre-configured for AI agents (Claude Desktop, Kilo, Cursor) to automate document conversion and OCR through standard tool calls.

Star the repo if you find it useful!

---

## 3. Twitter / X Thread 🐦

**Tweet 1:**  
Tired of the "Scanned with CamScanner" watermark and $50/yr subscription? 📄

We just open-sourced CamScanner MCP & HD Auto-Scanner:
✨ 100% Free & Local
✨ Zero Watermarks Forever
✨ Lossless 300 DPI Multi-Page PDF
✨ Model Context Protocol (MCP) native for AI agents

🔗 https://github.com/MHJoy99/camscanner-mcp-hd-scanner

**Tweet 2:**  
How does the local Magic Color filter work?
1. Detects paper boundaries & warps perspective flat.
2. Estimates ambient phone shadows via morphological dilation.
3. Whitens paper background to pure #FFFFFF while darkening ink.
4. Applies an unsharp mask for razor-sharp math formulas & handwriting.

**Tweet 3:**  
It also connects directly to @AnthropicAI Claude Desktop, Kilo CLI, and Cursor via MCP for automated document OCR and cloud translation in your terminal.

Check it out on GitHub:
https://github.com/MHJoy99/camscanner-mcp-hd-scanner ⭐

---

## 4. Product Hunt / Indie Hackers Quick Pitch 🚀

**Tagline:**  
Lossless HD document scanner without watermarks, powered by Python & MCP.

**Description:**  
Turn your mobile photos into crisp, professional 300 DPI PDFs without watermarks or subscription paywalls. Features automatic shadow removal, perspective cropping, and native Model Context Protocol (MCP) integration for AI agents.
