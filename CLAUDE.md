# CLAUDE.md

Guidance for Claude Code (or any AI assistant) working in this repo. Keep this
file short — link out to existing docs rather than duplicating them.

## What this is

A Streamlit portfolio app deployed to Fly.io as a single Docker container.
Each Streamlit page demos one AI capability — most pages call out to a
managed service or a Cloud Run inference backend. The interesting backend
logic lives in the **Support Agent** page (OpenAI function-calling agent +
PostgreSQL + Qdrant RAG).

For the full picture see [`ARCHITECTURE.md`](ARCHITECTURE.md). For deployment
see [`DEPLOYMENT.md`](DEPLOYMENT.md) / [`QUICKSTART_DEPLOYMENT.md`](QUICKSTART_DEPLOYMENT.md).

## Where the code lives

| Layer | Location |
| --- | --- |
| Streamlit entry point + home page | `app.py` |
| Navigation registration | `nav.py` (`config_navigation`) |
| Sidebar-visible pages | `pages/*.py` |
| Hidden pages (reached via in-app link) | `views/*.py` |
| Agent loop (OpenAI function calling) | `chatbot/agent.py` |
| Agent system prompt | `chatbot/prompts.py` |
| Tool schemas (OpenAI function-call JSON) | `tools/schemas.py` |
| Tool implementations (DB + vector calls) | `tools/implementations.py` |
| PostgreSQL access | `database/db_manager.py` |
| Vector store (Qdrant) | `qdrant/vector_store.py` |
| KB loader (one-shot population) | `qdrant/vector_load_kb.py` |
| Schema + seed data | `database/schema.sql`, `database/*_insert.sql` |

## Page pattern (important)

Every page in `pages/` and `views/` follows the same boilerplate:

```python
import streamlit as st
import nav
from app import home_page

st.set_page_config(...)
nav.config_navigation(home_page)   # registers all pages so navigation works
                                   # regardless of which URL the user enters at
```

`nav.config_navigation` is guarded by a module-level flag so re-entry is a
no-op. If you add a new page, also add an `st.Page(...)` entry inside
`nav.config_navigation` in `nav.py` — Streamlit will otherwise fall back to
alphabetical auto-discovery.

## The Support Agent flow

1. User message → `pages/support_agent.py` → `CustomerSupportAgent.chat()`
2. Agent runs a keyword heuristic (`_detect_likely_tools`) and proactively
   pulls SOPs from Qdrant (`agent-sop-<toolname>` lookups) before the first
   OpenAI call. SOPs are injected as a second system message and cached on
   the agent instance.
3. OpenAI is called with `TOOL_SCHEMAS` (`tools/schemas.py`) and
   `tool_choice="auto"`.
4. For each `tool_call` returned, `ToolImplementations.execute_tool()` is
   dispatched. Most tools touch `DatabaseManager` (Supabase Postgres);
   `search_knowledge_base` (and the SOP lookups) hit Qdrant.
5. Loop runs up to 5 iterations; final assistant message is returned with
   the list of tool calls made.

All DB tables are prefixed `agent_*` — see `database/schema.sql`. Tool names
in `tool_map` (bottom of `tools/implementations.py`) must match
`TOOL_SCHEMAS` entries.

## Environment variables

Required: `OPENAI_API_KEY`, `SUPADATABASE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`.
Per-page: `STABILITY_KEY`, `BRYCEGPT_API_URL`, `BPSIMGCLSS_API_URL`.
Optional: `LOG_LEVEL`, `BPSIMGCLSS_TIMEOUT`.

Note the **unusual name**: the Postgres DSN is `SUPADATABASE_URL`, not the
more conventional `DATABASE_URL`. Don't "fix" this — the deployed Fly
secrets use this name.

## Conventions and gotchas

- **PyTorch isn't in `requirements.txt`** — it's installed CPU-only inside
  the Dockerfile to keep the image small. Local dev: run
  `fix_pytorch_local.ps1` (Windows) or `fix_pytorch_local.sh` (Mac/Linux).
- **The Qdrant collection is owned by `vector_load_kb.py`**, not by
  `VectorStore.__init__`. The init path only verifies and warns; it does not
  create. The embedder is `BAAI/bge-small-en-v1.5` (384-dim) — do not
  hardcode 1536 anywhere.
- **Model training repos live elsewhere.** This repo only renders the demo
  UI and calls remote Cloud Run inference endpoints:
  - Image classifier: <https://github.com/BryceRodgers7/img-classifier-birdplanesuper>
  - Custom GPT: <https://github.com/BryceRodgers7/brycegpt>
- **Cold start UX.** The image-classifier and Voyager-GPT pages share a
  `run_with_cold_start_hint(...)` helper — after `COLD_START_HINT_SEC` (6s)
  they show a "backend may need a cold start" notice while waiting.
- **`models/*.pth` is for reference only.** The deployed classifier
  downloads weights from GCS at startup; nothing in this repo reads the
  `.pth` directly.
- **Pages call `from app import home_page`.** Don't move `home_page` out of
  `app.py` without updating every page in `pages/` and `views/`.

## Running locally

```bash
pip install -r requirements.txt          # or fix_pytorch_local.* first
streamlit run app.py
```

Without `SUPADATABASE_URL`, `DatabaseManager()` raises at construction time —
which means the Support Agent and All Data Views pages will fail on entry.
Other pages should work as long as their own env vars are set.

## Style notes for edits

- Keep page text edits surgical — much of the user-facing copy is hand-tuned
  marketing prose. Don't reflow paragraphs.
- New tools must be registered in three places: `TOOL_SCHEMAS`
  (`tools/schemas.py`), the method body in `tools/implementations.py`, and
  `tool_map` inside `execute_tool`.
- Logger pattern: module-level `logger = logging.getLogger(__name__)`. Root
  level is set in `app.py` from `LOG_LEVEL`.
