# 🧠 Persisto AI

**Semantic Memory-as-a-Service (SMaaS)** for LLM applications — built to give your AI apps long-term memory out of the box.

---

## 🧩 What Is Persisto?

Persisto AI is a developer-first memory backend for AI agents, chatbots, and LLM-powered tools. It provides:

- Persistent memory storage via `save()`
- Fast semantic retrieval via `query()`
- Built-in text chunking, OpenAI embeddings, and pgvector
- Metadata filters for structured retrieval
- Modular, production-grade architecture (FastAPI + Supabase)

It abstracts away vector DBs, embedding calls, and memory logic — so you can focus on building intelligent apps, not infrastructure.

---

## 💡 Why Use Persisto?

LLMs forget. Agents drift. Context disappears.

Persisto solves this by acting as a **long-term memory layer** for AI workflows:

- 🧠 Recall facts, past interactions, or user preferences
- 🔍 Retrieve relevant memories using natural language queries
- ⚙️ Attach metadata (timestamps, sources, tags) for smarter filtering
- 🪄 Plug into any AI app — no infrastructure or setup required

---

## 🚀 Current Feature Set (v0.1)

| Feature             | Description                                                      |
|---------------------|------------------------------------------------------------------|
| ✅ Save API          | `POST /memory/save` with `namespace`, `content`, and `metadata` |
| ✅ Query API         | `POST /memory/query` with `namespace`, `query`, and filters     |
| ✅ Embedding Engine  | Uses OpenAI `text-embedding-3-small`                            |
| ✅ Vector Search     | Postgres + `pgvector` similarity ranking                        |
| ✅ Chunking Engine   | Naive character-based chunking (modularized)                    |
| ✅ Metadata Filters  | JSONB-based filtering on metadata keys                          |

---

## 🛠️ How to Use

### 🧪 Save a memory

```bash
curl -X POST http://127.0.0.1:8000/memory/save \
  -H "Content-Type: application/json" \
  -d '{
        "namespace": "demo-agent",
        "content": "The user prefers concise, structured summaries.",
        "metadata": { "source": "profile", "user_id": "abc123" }
      }'
