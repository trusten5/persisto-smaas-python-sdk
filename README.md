````markdown
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
````

This will:

* Automatically chunk the content (if long)
* Embed it with OpenAI
* Store in `memories` table with metadata and namespace

---

### 🔍 Query memory

```bash
curl -X POST http://127.0.0.1:8000/memory/query \
  -H "Content-Type: application/json" \
  -d '{
        "namespace": "demo-agent",
        "query": "How does the user like their output?",
        "filters": { "source": "profile" },
        "top_k": 3
      }'
```

Returns top-k memory chunks by semantic relevance (cosine similarity), filtered by metadata.

---

## 📦 Architecture

```
backend/
├── main.py                # FastAPI app entry
├── db.py                  # DB connection (Supabase + pgvector)
├── routers/
│   └── memory.py          # /memory/save and /memory/query endpoints
├── services/
│   ├── memory_service.py  # Chunk, embed, store, and query memory
│   └── embed_service.py   # OpenAI embedding logic
├── utils/
│   └── chunker.py         # Chunking logic (e.g., split by chars/paras)
```

---

## 🛣️ Roadmap

**V1 (now):**

* [x] Hosted memory API (`save`, `query`)
* [x] OpenAI embedding + pgvector
* [x] Chunking engine
* [x] Metadata tagging & filtering
* [ ] Python & JS SDKs
* [ ] LangChain + OpenAI Assistant templates

**V2:**

* [ ] Summarization & memory condensing
* [ ] Customizable memory lifespan
* [ ] Plug-and-play vector DB switching
* [ ] Personalized scoring logic

**V3:**

* [ ] Memory dashboard (Next.js)
* [ ] Multi-agent collaboration & projects
* [ ] Advanced memory primitives (episodic recall, triggers)
* [ ] Logging & audit analytics

---

## 💡 Use Cases

* Agent memory in multi-turn LLM tools
* User preference recall in AI copilots
* Semantic search in document assistants
* Context persistence across sessions
* Memory for LangChain or OpenAI Assistants

---

## 🧠 Persisto gives your AI a brain.

Build intelligent, context-aware LLM applications — faster and simpler.
Let me know when you want to build the Python SDK and I’ll generate the full working code and test instructions.
```
