# Local LLM Configuration - Voice Fingerprinting

**Updated:** 2026-02-19

---

## Selected Model for Voice Fingerprinting Research

**Model:** `ollama/deepseek-r1:14b`  
**Reason:** Superior reasoning capabilities, shows chain-of-thought thinking  
**Cron Job:** 9e880e1b-1dd7-4b8e-9f89-1e747d806edc  
**Timeout:** 900 seconds (15 minutes)  

---

## Why DeepSeek-R1?

**Advantages:**
- **Reasoning visibility:** Shows step-by-step thinking process
- **Deep analysis:** Better for evaluating technical papers and tools
- **LaTeX support:** Formats math and technical content nicely
- **9GB size:** Good balance of capability vs resource usage

**Trade-offs:**
- **Slower:** ~2-3 minute response time vs 30 seconds for smaller models
- **Memory:** Uses ~10GB RAM when loaded
- **Not for quick tasks:** Overkill for simple lookups

---

## Available Models (All Tested ✅)

| Model | Size | Best For | Speed | Status |
|-------|------|----------|-------|--------|
| gemma3:4b | 3.3GB | Quick tasks, heartbeats | ⚡ Fast (~5s) | ✅ Tested |
| llama3.1:8b | 4.9GB | General purpose | 🚀 Good (~30s) | ✅ Tested |
| **gemma3:12b** | **8.1GB** | **Balanced daily work** | **🚀 Good (~69s)** | **✅ Tested & Configured** |
| **deepseek-r1:14b** | 9.0GB | **Research, reasoning** | 🧠 Deep (~2-3min) | ✅ Tested |
| qwen2.5:14b | 9.0GB | Multilingual, coding | 🚀 Good (~2min) | ✅ Tested |
| phi4:14b | 9.1GB | Microsoft ecosystem | 🧠 Smart (~2min) | ✅ Tested |
| gemma3:27b | 17GB | Maximum capability | 🐢 Heavy (~90s+) | ✅ Tested |

---

## Auth Configuration

All Ollama models configured in:
`/Users/mctoon/.openclaw/agents/main/agent/auth-profiles.json`

Profiles:
- `ollama:default` - General Ollama access
- `ollama:gemma3-12b` - gemma3:12b specific

API Key: `ollama-local` (any value works for local Ollama)

---

## Daily Research Workflow

**Schedule:** 9:00 AM CT daily  
**Model:** deepseek-r1:14b  
**Task:** Find new voice transcription + speaker ID research  
**Output:** Document in daily-notes/YYYY-MM-DD.md

The model will provide detailed analysis of:
- GitHub repositories
- Research papers
- Technical architectures
- Mac M2 compatibility assessments

---

*Model selection optimized for research quality over speed*
