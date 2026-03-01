# CLAUDE.md

## Project Context
Sorque is a Zork-like text adventure game built with React + Vite (JavaScript).

## Stack
- **React 19** + **Vite 6** — SPA, no routing, no SSR
- **No additional runtime deps** — useState + custom hook for state, plain CSS, JSON world data
- World data lives in `public/worlds/*.json`, served as static files
- LLM integration is stubbed (`src/services/llm.js`)

## Architecture
- `src/engine/` — ES6 classes: Game, Room, Exit, Interaction, DescOverride, WorldLoader
- `src/hooks/useGame.js` — custom hook owning Game instance, message log, tick counter
- `src/components/` — GameLayout, StoryPanel, ActionBar, CompassPanel, InventoryPanel, DeathOverlay, RoomHeader
- `src/services/` — persistence (localStorage), llm (stub)
- `src/constants.js` — compass ordering, color map, help text, death text

## Conventions
- Use ES modules (import/export)
- Keep the project runnable with `npm install && npm start`
- Game mutates in place; a `tick` counter in useGame forces re-renders
- All content is authored JSON — mini-markdown rendered via dangerouslySetInnerHTML is safe

## Legacy Python (can be removed)
- `src/backend/` — original Python engine (oo.py, oo_loader.py)
- `src/app/` — original Streamlit UI (app.py, ui_components.py)
- `requirements.txt`, `.streamlit/`, `venv/`
