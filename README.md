<div align="center">

# MaaliDost

### Track your money by WhatsApp — text, speak, or snap a receipt, in your own language.

**A "digital Munshi" (bookkeeper) that lives inside WhatsApp. No app to install.**

[![Built with Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-4285F4)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Deployed on Railway](https://img.shields.io/badge/Deployed-Railway-8B5CF6)](https://railway.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## The Problem

Most people never track their spending — not because they don't care, but because every expense app demands the same tedious ritual: install it, tap through menus, fill a form. Roughly **80% of users quit within a week.** And for millions in Pakistan, these apps assume English literacy and a smartphone habit they don't have.

Meanwhile, everyone is already on **WhatsApp** all day.

## The Solution

**MaaliDost** turns expense tracking into a single message. Tell it what you spent the way you'd tell a friend — by text, a voice note, or a photo of a receipt — and it logs it, tracks your budget, and replies **in the same language you used.**

> **You:** *Maine 50 rupay ki chai li*
> **MaaliDost:** ✅ *Likh liya: chai (-50 PKR)* 💰 *Balance: 1,150 PKR*

---

## Features

| Feature | Description |
|---|---|
| 🗣️ **Multimodal input** | Log expenses by **text, voice note, or receipt photo** — all handled natively by one AI model |
| 🌐 **Linguistic mirroring** | Understands **English, Roman Urdu, Urdu (Nastaliq), and Punjabi** — and replies in the *same* language the user used |
| 💰 **Budgets** | Set per-category limits (daily / weekly / monthly), with warnings as you approach them |
| 📊 **Spending queries** | Specific dates, date ranges, and relative periods ("last month", "this week") — totals grouped by category and timeframe |
| ⏰ **Bill reminders** | Set reminders in any language; a daily sweep fires them automatically on the due date |
| 🧾 **Balance checks** | Instant income, expense, and net balance |
| 📋 **Category lookup** | Ask what categories are tracked, independent of anything logged yet |
| ↩️ **Undo last entry** | Mistyped or misspoke? Undo the most recent log and resend it correctly |
| 📄 **Detailed reports** | Export a CSV or PDF with the full transaction history, balance summary, and live budget status — Urdu/Arabic script renders correctly (proper RTL shaping) |
| 🛡️ **Production-grade reliability** | Automatic retries with backoff, duplicate protection, AI-result caching, and dead-letter alerts |

---

## How It Works

A **decoupled two-node architecture** connected by a job queue — so the webhook always responds instantly while the AI does the heavy lifting separately.

WhatsApp user
│
Meta WhatsApp Cloud API
│
┌────▼─────────────────┐
│ INGESTION (FastAPI) │ Verifies webhook, queues job,
│ main.py │ returns 200 OK in <200ms
└────┬─────────────────┘
│
Redis Queue (Upstash)
│
┌────▼─────────────────┐
│ WORKER (ARQ) │ Downloads media → Gemini extracts →
│ processor.py │ writes to DB → replies in user's language
└────┬─────────────────┘
│
Supabase (PostgreSQL)


**Why native multimodal AI?** Instead of chaining a speech-to-text service + an OCR service + a translation service + a parser, a **single Gemini 2.5 Flash call** handles text, audio, and images together. This keeps the cost per logged entry at roughly **0.06 PKR** — cheap enough to offer for free — and handles code-switched speech that transcription services typically mangle.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **AI** | Google Gemini 2.5 Flash (multimodal: text, audio, vision) |
| **Messaging** | Meta WhatsApp Business Cloud API |
| **Web layer** | FastAPI + Uvicorn |
| **Queue** | ARQ over Upstash Redis (TLS) |
| **Database** | Supabase (PostgreSQL) |
| **Hosting** | Railway (web + worker services, 24/7) |
| **PDF/Urdu rendering** | fpdf2 + Amiri (Unicode font) + arabic-reshaper + python-bidi |
| **Language** | Python |

---

## Project Structure

maalidost/
├── main.py # Ingestion node — receives & queues WhatsApp webhooks
├── processor.py # Worker node — the full pipeline + all intent handlers
│ # + reply templates in 4 languages
├── run_worker.py # Worker launcher
├── test_enqueue.py # Test harness (bypasses WhatsApp to test the pipeline)
├── Amiri-Regular.ttf # Unicode font for correct Urdu/Arabic PDF rendering
├── requirements.txt # Python dependencies
├── Procfile # Defines web + worker processes for deployment
└── runtime.txt # Python version


---

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (in a .env file):
#    SUPABASE_URL, SUPABASE_KEY, HISAAB_GEMINI_KEY,
#    WHATSAPP_TOKEN, PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN, REDIS_URL

# 3. Start the worker (processes jobs)
python run_worker.py

# 4. In another terminal, start the web server (receives webhooks)
uvicorn main:app --reload --port 8000

# 5. Test the full pipeline without WhatsApp:
python test_enqueue.py "Maine 50 rupay ki chai li"
```

---

## Intents Understood

`log` · `query` · `balance` · `set_budget` · `get_budget` · `set_reminder` · `list_categories` · `undo_last` · `export` · `help`

The AI maps everyday words to 16 fixed categories — *"chai"* → Food & Dining, *"petrol"* → Transport, *"haircut"* → Personal Care — and can handle **multiple actions in one message**.

---

<div align="center">

*Making financial record-keeping accessible to everyone — in the language they already speak.*

</div>
