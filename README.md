
# Sorque

A Zork-like, button-driven adventure on a premade graph. Prose is LLM-generated (later) and grounded by authored world data. Romance is PG-13 with consent and fade-to-black. (Image generation currently excluded.)

## Status
This is a **code skeleton** to help you spin up the repo quickly.

## Quickstart
```bash
# 1) optional: create a venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) install deps
pip install -r requirements.txt

# 3) run the app
streamlit run src/app/app.py
```

The app will load the authored world from `world/` and let you move between nodes using the compass.
The LLM pipeline is stubbed for now; descriptions are generated from authored data.

## Project Layout
- `world/` — authored map, items, NPCs, quests, lore (YAML).
- `schemas/` — JSON schemas for world validation.
- `src/backend/` — logic stubs (action routing, rules, world loading, content service).
- `src/app/` — Streamlit UI pages.
- `prompts/` — prompt templates (not yet wired).
- `docs/` — design/architecture notes.
- `scripts/` — helpers (validation).

## Roadmap
- Wire LLM client in `src/adapters/llm_client.py` using `OPENAI_API_KEY`.
- Add persistence in `src/adapters/storage.py` (SQLite/Postgres).
- Expand world content and quests.
