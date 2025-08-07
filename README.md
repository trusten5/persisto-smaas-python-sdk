# 🧠 Persisto AI

**Semantic Memory-as-a-Service (SMaaS)** for LLM-powered applications.

> Give your AI agents persistent memory — no vector DB setup, no boilerplate, no drift.

---

## 🧩 What is Persisto?

Persisto is a plug-and-play memory backend for LLM apps, agents, and chatbots. It handles:

* ✅ Memory saving, querying, and deletion
* ✅ OpenAI embedding + `pgvector` similarity search
* ✅ TTL/expiry support for short-lived memory
* ✅ Metadata filtering + structured search
* ✅ Fully working Python SDK with retries, error handling, and test script

Use Persisto to **recall facts, track preferences, or power retrieval-augmented generation (RAG)** — with clean APIs and no infrastructure overhead.

---

## 💡 Why Use Persisto?

LLMs forget. Agents drift. Context disappears.
Persisto solves this with **long-term, queryable memory** that just works:

* 🧠 Save memory chunks by namespace
* 🔍 Retrieve by semantic similarity and metadata filters
* ⏳ Expire memory after N seconds (`ttl_seconds`)
* ⚙️ Use a simple Python SDK or REST API
* 🔐 Scoped by user with API key auth

You focus on building smart apps — Persisto handles memory.

---

## 🔧 Quick Start

### 1. Install the SDK

```bash
pip install persisto-ai
```

> ⚙️ Alternatively, clone the repo and run `python test_sdk.py` after setting your `.env`.

---

### 2. Save a memory

```python
from persisto import PersistoClient

client = PersistoClient(api_key="your-api-key")

client.save(
    namespace="demo-agent",
    content="The user prefers concise summaries.",
    metadata={"source": "profile"}
)
```

---

### 3. Query memory

```python
results = client.query(
    namespace="demo-agent",
    query="How does the user like their output?",
    filters={"source": "profile"}
)

for r in results:
    print(r["content"], r["similarity"])
```

---

## ⚙️ Architecture Overview

```text
sdk/python/persisto/     # Python SDK (retry logic, typed errors)
backend/
├── main.py              # FastAPI app entry
├── routers/memory.py    # REST endpoints: /save, /query, /delete
├── services/            # Embedding, DB, memory logic
├── utils/               # Chunking, auth, helpers
```

---

## ✅ Completed Features (V1.0 + V1.5)

### 🧠 Memory Infrastructure

* `.save()`, `.query()`, `.delete()` APIs
* Text chunking + OpenAI embeddings
* `pgvector` top-k semantic search
* Structured filtering via metadata
* API key–based user isolation

### 🧰 SDK Polish

* Full Python SDK
* Retry logic via `tenacity`
* Typed SDK errors (e.g. `PersistoAuthError`, `PersistoNotFoundError`)
* `.env` support and test suite

### ⏳ TTL / Expiry Support

* `ttl_seconds` in `.save()`
* `expires_at` column in DB
* Expired memories excluded from queries

### 🪪 Query History API

* `/queries/list` endpoint
* `.list_queries()` in SDK
* Filter by namespace and time

---

## 🛣️ Roadmap

### 🔷 V2.0 – Power Tools for Devs *(Next)*

* Retrieval Profiles: `strict`, `fuzzy`, `recency`
* `summarize_old()` — LLM-based memory compression
* JS/TS SDK
* Scoped tokens + project-based auth
* TTL cleanup script (optional)

### 🔶 V3.0 – Persisto Cloud *(Hosted Platform)*

* Hosted dashboard + usage metrics
* Interactive playground
* Org/project system with team access
* API keys + usage billing

### 🔷 V4.0 – The RAG Engine *(Infra Toolkit)*

* Hybrid search (vector + keyword)
* BYO embedder + summarizer
* Declarative config: `persisto.config.json`
* LangChain / LlamaIndex adapters
* GitHub RAG chatbot template

---

## 💼 Use Cases

* Memory for multi-turn AI agents
* Preference recall in LLM copilots
* Long-term document understanding
* Semantic search + RAG pipelines
* Personalization across sessions

---

## 📦 Tech Stack

* Python (FastAPI, Pydantic, Requests)
* Supabase (PostgreSQL + pgvector)
* OpenAI embeddings (`text-embedding-3-small`)
* Tenacity (retry logic)
* dotenv (`.env` config for SDK)
* Future: TS SDK, hosted dashboard, LangChain adapters

---

## 🚀 Vision

> Persisto is building the **Vercel for RAG**
> A fully hosted, developer-first platform to deploy AI memory, retrieval, and context systems — in one line of code.

* No infra setup
* No vector DB config
* Just `.save()` and `.query()` memory — and you're live

---

## 👇 Try It Locally

```bash
# Start backend server
uvicorn backend.main:app --reload

# Run the test script
python test_sdk.py
```

> Configure your `.env` with your API key (from Supabase).

---

## 🧠 Persisto gives your AI a brain.

Build memory-aware agents.
Ship smarter assistants.
Deploy production-ready RAG in minutes.