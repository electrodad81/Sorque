# --- path bootstrap so "backend" is importable when running src/app/app.py ---
import sys
from pathlib import Path
from typing import Optional
import streamlit as st
st.set_page_config(page_title="Sorque", layout="wide")

THIS_FILE = Path(__file__).resolve()
SRC_DIR   = THIS_FILE.parents[1]      # .../src
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))  # make 'backend' a top-level package

# now import the OO engine
from backend.oo_loader import new_game_from_path
from backend.oo import Game

from app.ui_components import DescriptionPanel, PanelMessage, InventoryPanel

APP_MAX_WIDTH = 1000  # tweak to taste (e.g., 1000–1300)

st.markdown(f"""
<style>
  /* Cap & center the whole app content. Use both selectors and !important to win. */
  .block-container {{
    max-width: {APP_MAX_WIDTH}px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }}
  [data-testid="block-container"] {{
    max-width: {APP_MAX_WIDTH}px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }}
</style>
""", unsafe_allow_html=True)


# Rooms that should end the game when entered
END_ROOM_IDS = {"5"}  # your Street room id

INSTRUCTIONS_MD = (
    "**Welcome to Sorque**\n"
    "- Click **Look** to reveal more detail in a room.\n"
    "- Use the **compass** to move.\n"
    "- **Actions** appear contextually under the room panel.\n"
    "- Jammed doors may need items (try the **hatchet**).\n"
    "- In the basement, **petting the dog will kill you**.\n"
    "- The **hatchet** can be found outside.\n"
    "- Step **outside** to escape.\n\n"
    "Good luck."
)

# one-time default
if "game_over" not in st.session_state:
    st.session_state.game_over = False

st.markdown(
    """
    <style>
      /* make primary buttons just a bit taller for prominence */
      .stButton > button[kind="primary"] { padding: 0.6rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
      /* Make ONLY primary buttons (we use it for Look) a blue outline */
      .stButton > button[kind="primary"]{
        background: transparent !important;
        color: #1a73e8 !important;                 /* Google-ish blue */
        border: 2px solid #1a73e8 !important;
        box-shadow: none !important;
      }
      .stButton > button[kind="primary"]:hover{
        background: rgba(26,115,232,0.08) !important;
      }
      .stButton > button[kind="primary"]:active{
        background: rgba(26,115,232,0.16) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
  /* Primary (Look) — blue outline, full width, fixed height */
  .stButton > button[kind="primary"]{
    background: transparent !important;
    color: #1a73e8 !important;
    border: 2px solid #1a73e8 !important;
    box-shadow: none !important;
    width: 100% !important;         /* NEW */
    height: 60px !important;        /* NEW: match secondary buttons */
  }
  .stButton > button[kind="primary"]:hover{ background: rgba(26,115,232,0.08) !important; }
  .stButton > button[kind="primary"]:active{ background: rgba(26,115,232,0.16) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
      /* Make ALL secondary buttons equal size & fill their column */
      .stButton > button[kind="secondary"]{
        width: 100% !important;             /* span the st.columns cell */
        height: 60px !important;            /* fixed height (tweak if you like) */
        white-space: normal !important;     /* allow wrapping for long labels */
        text-align: center !important;
        display: flex !important;
        align-items: center !important;     /* vertical center */
        justify-content: center !important; /* horizontal center */
        line-height: 1.15 !important;
        border-radius: 8px !important;
      }
      /* Keep the Look button as a blue outline (primary) — already added earlier */
      .stButton > button[kind="primary"]{
        background: transparent !important;
        color: #1a73e8 !important;
        border: 2px solid #1a73e8 !important;
        box-shadow: none !important;
      }
      .stButton > button[kind="primary"]:hover{
        background: rgba(26,115,232,0.08) !important;
      }
      .stButton > button[kind="primary"]:active{
        background: rgba(26,115,232,0.16) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- tiny panel helpers ----------
# --- panel helpers (append-only log) ---
def panel_init(initial_text: str):
    """Create the log once at app start; do NOT clear on room changes."""
    if "panel" not in st.session_state:
        st.session_state.panel = {"blocks": [PanelMessage(initial_text, "body")]}

MAX_LOG_BLOCKS = 300  # keep memory sane; tweak to taste

def panel_set_body(html: str):
    st.session_state.panel["blocks"] = [PanelMessage(html, "body")]

def panel_append(text: str, kind: str = "body"):
    st.session_state.panel["blocks"].append(PanelMessage(text, kind))  # type: ignore[arg-type]
    # trim oldest if too long
    if len(st.session_state.panel["blocks"]) > MAX_LOG_BLOCKS:
        st.session_state.panel["blocks"] = st.session_state.panel["blocks"][-MAX_LOG_BLOCKS:]

def panel_divider():
    panel_append("— — —", "body")  # simple visual break in the log

ROOT_DIR  = THIS_FILE.parents[2]   # project root (…/Sorque/)
WORLD_PATH = ROOT_DIR / "data" / "worlds" / "house_start.json"

# ---------- session/bootstrap ----------
if "ui_tick" not in st.session_state:
    st.session_state.ui_tick = 0
# old CSS key cleanup (safe no-op if absent)
st.session_state.pop("_ui_desc_panel_css_loaded", None)

G: Optional[Game] = st.session_state.get("game")
if G is None:
    try:
        st.session_state.game = new_game_from_path(str(WORLD_PATH))
        G = st.session_state.game
    except Exception as e:
        st.error(f"Failed to load world: {e}")
        st.stop()

# --- append-only seed + death handling ---
panel_init(G.desc_short())  # seed the log once with the starting room short

death_msg = st.session_state.pop("death_msg", None)
if death_msg:
    # append the death line first, then remind the player where they are
    panel_append(death_msg, "error")
    if G.room.name:
        panel_append(f"**{G.room.name}**")
    panel_append(G.desc_short())

# Inventory toggle state
if "inv_open" not in st.session_state:
    st.session_state.inv_open = True  # start open


# =========================
# TWO-COLUMN LAYOUT
# =========================
left, right = st.columns([3, 1], gap="large")  # wider story area

# ----- LEFT: header + fixed text window + controls -----
with left:
    # Header ABOVE the window
    if G.room.name:
        st.subheader(G.room.name)

    # Fixed, scrollable text window
    DescriptionPanel(
        panel_id="room-desc",
        height_px=560,                 # a little taller looks nice with more width
        border_css="1px solid #333",   # subtle dark border
        bg_css="#111",                 # dark background
        font_size="1rem",              # optional bump
        margin_bottom_px=16
    ).render(st.session_state.panel["blocks"])
    
    # >>> ADD THE GAME-OVER CHECK RIGHT HERE <<<
    if st.session_state.game_over:
        if st.button("Play again", type="primary"):
            G.restart()
            st.session_state.game_over = False
            st.session_state.panel = {"blocks": []}   # fresh log
            panel_init(G.desc_short())                # seed with start-room short
            st.rerun()
        st.stop()  # prevents Look/Compass/Actions from rendering below

    # ---------- Look (left) + Help (far right) ----------
    c1, c2, c3, c4 = st.columns(4)

    # Leftmost: Look (primary, blue outline & fixed size via CSS)
    with c1:
        if st.button("Look", type="primary", key=f"look_{st.session_state.ui_tick}"):
            G.look()  # reveals flags for the room
            st.session_state.ui_tick += 1
            panel_append(G.desc_long(), "body")   # <-- append, don't replace
            st.rerun()

    # Middle columns are spacers (keep row shape consistent)
    with c2: st.write("")
    with c3: st.write("")

    # Far right: Help (only after note is read)
    with c4:
        if "read_note" in G.flags:
            if st.button("Help", key=f"help_{st.session_state.ui_tick}"):
                st.session_state.ui_tick += 1
                panel_append(INSTRUCTIONS_MD, "info")
                st.rerun()
        else:
            # Optional: keep button footprint without action (disabled placeholder)
            st.button("Help", disabled=True, key="help_placeholder")


    cols = st.columns(4)
    for i, ex in enumerate(G.compass()):
        col = cols[i % 4]
        to_valid = bool(ex["to"]) and str(ex["to"]) in G.rooms
        disabled = not to_valid

        if col.button(ex["label"], disabled=disabled, key=f"mv_{ex['direction']}_{st.session_state.ui_tick}"):
            st.session_state.ui_tick += 1

            if not to_valid:
                st.session_state.panel["blocks"].append(PanelMessage("It doesn't seem to open.", "warning"))
                st.rerun()

            if ex["locked"]:
                locked_line = ex["locked_text"] or "It's stuck. You'll need leverage."
                st.session_state.panel["blocks"].append(PanelMessage(locked_line, "warning"))
                st.rerun()

            # --- NEW: detect if this exit is item-gated and you have that item
            exit_obj = G.room.exits.get(ex["direction"])
            used_item = None
            if exit_obj and getattr(exit_obj, "locked_by_item", None):
                if exit_obj.locked_by_item in G.inventory:
                    used_item = exit_obj.locked_by_item  # e.g., "hatchet"

            # Move succeeds -> append arrival entry
            G.move(ex["direction"])
            # optional separator line:
            # panel_append("— — —")
            if G.room.name:
                panel_append(f"**{G.room.name}**", "body")
            panel_append(G.desc_short(), "body")

            # --- NEW: if you used an item to get through, show a green success line
            if used_item:
                st.session_state.panel["blocks"].append(
                    PanelMessage(f"You pry the door with the **{used_item}**. It opens.", "success")
                )

            # If this is a win room, show victory & end the session UI (keep your existing block if present)
            if "END_ROOM_IDS" in globals() and G.current_room_id in END_ROOM_IDS:
                panel_append(G.desc_long(), "body")
                panel_append("You step into the street and breathe free air. You escaped!", "success")
                st.session_state.game_over = True
                st.rerun()

            st.rerun()



    # ---------- Interactions ----------
    vis = G.visible_interactions()
    if vis:
        st.markdown("### Actions")
    for it in vis:
        if st.button(it.label, key=f"act_{it.id}_{st.session_state.ui_tick}"):
            before = set(G.inventory)
            msg, dead = G.do(it.id)
            after = set(G.inventory)
            st.session_state.ui_tick += 1

            if dead:
                st.session_state.death_msg = msg or "You died."
                G.restart()
                st.rerun()

            # Append room long desc (reflect overrides)
            panel_append(G.desc_long(), "body")
            # Append interaction text
            if msg:
                panel_append(msg, "info")

            # Append pickups
            for name in sorted(after - before):
                panel_append(f"**{name.title()}** added to inventory.", "success")

            st.rerun()

# ----- RIGHT: collapsible Inventory -----
with right:
    st.checkbox("Inventory", key="inv_open")
    if st.session_state.inv_open:
        InventoryPanel(panel_id="inv", height_px=220, border_css="1px solid #000") \
            .render(sorted(G.inventory))

# (Optional) debug
with st.expander("Debug state"):
    st.write({
        "room": G.current_room_id,
        "inventory": sorted(G.inventory),
        "flags": sorted(G.flags),
    })
