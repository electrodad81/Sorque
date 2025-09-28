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
      /* Make ALL secondary buttons fill their column and grow with text */
      .stButton > button[kind="secondary"]{
        width: 100% !important;             
        min-height: 60px !important;        /* was: height: 60px */
        height: auto !important;            /* let it grow when needed */
        white-space: normal !important;     /* allow wrapping */
        overflow-wrap: anywhere;            /* break long words */
        word-break: break-word;             /* cross-browser safety */
        text-align: center !important;
        display: flex !important;
        align-items: center !important;     /* keep vertical centering */
        justify-content: center !important; /* horizontal centering */
        line-height: 1.2 !important;        /* nicer multi-line spacing */
        padding: 10px 14px !important;      /* breathing room for wraps */
        border-radius: 8px !important;
      }

      /* Keep the Look button as a blue outline (primary) */
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

    # ---------- Look (left) | Actions (middle) | Help (right) ----------
    vis = G.visible_interactions()
    A = list(vis)  # stable order

    NUM_COLS = 6  # [Look] [A] [A] [A] [A] [Help]
    MID_SLOTS = NUM_COLS - 2

    def render_actions_row(actions_slice, include_look=False, include_help=False):
        cols = st.columns(NUM_COLS)
        # Left-most: Look (optional, only on first row)
        if include_look:
            with cols[0]:
                if st.button("Look", type="primary", key=f"look_{st.session_state.ui_tick}"):
                    G.look()
                    st.session_state.ui_tick += 1
                    panel_append(G.desc_long(), "body")
                    st.rerun()
        else:
            with cols[0]:
                st.write("")  # keep grid shape

        # Middle: action buttons
        for col, it in zip(cols[1:-1], actions_slice):
            with col:
                if st.button(it.label, key=f"act_{it.id}_{st.session_state.ui_tick}"):
                    before = set(G.inventory)
                    msg, dead = G.do(it.id)
                    after = set(G.inventory)
                    st.session_state.ui_tick += 1

                    if dead:
                        st.session_state.death_msg = msg or "You died."
                        G.restart()
                        st.rerun()

                    # Append authored text and pickup notes
                    if msg:
                        panel_append(msg, "info")
                    for name in sorted(after - before):
                        panel_append(f"**{name.title()} added to inventory.**", "success")

                    # Refresh desc (overrides) after interactions
                    panel_append(G.desc_long(), "body")
                    st.rerun()

        # Fill any unused middle slots to keep width consistent
        empty_slots = MID_SLOTS - len(actions_slice)
        for _ in range(max(0, empty_slots)):
            with cols[-2]:
                st.write("")

        # Right-most: Help (optional, only on first row)
        if include_help:
            with cols[-1]:
                if "read_note" in G.flags:
                    if st.button("Help", key=f"help_{st.session_state.ui_tick}"):
                        st.session_state.ui_tick += 1
                        panel_append(INSTRUCTIONS_MD, "info")
                        st.rerun()
                else:
                    st.button("Help", disabled=True, key="help_placeholder")
        else:
            with cols[-1]:
                st.write("")

    # First row: Look + middle actions + Help
    render_actions_row(A[:MID_SLOTS], include_look=True, include_help=True)

    # Additional rows for overflow actions (no Look/Help on these)
    for i in range(MID_SLOTS, len(A), MID_SLOTS):
        render_actions_row(A[i:i+MID_SLOTS], include_look=False, include_help=False)


# ----- RIGHT: collapsible Inventory -----
with right:
    # Inventory toggle + panel (keep yours)
    st.checkbox("Inventory", key="inv_open")
    if st.session_state.inv_open:
        InventoryPanel(panel_id="inv", height_px=260, border_css="1px solid #333") \
            .render(sorted(G.inventory))

    # Demure spacer between Inventory and Compass   
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ------- Compass under Inventory (2-column grid) -------
    # ------- Compass under Inventory: vertical stack (one button per row) -------
    moves = G.compass()

    def prettify_exit(label: str) -> str:
        t = label.strip()
        tl = t.lower()
        if tl.startswith("to the "): t = t[7:]
        elif tl.startswith("to "):    t = t[3:]
        return t[:1].upper() + t[1:] if t else t

    if moves:
        st.markdown('<div class="compass-vertical">', unsafe_allow_html=True)

        for ex in moves:  # ex is a dict
            to_valid = bool(ex["to"]) and str(ex["to"]) in G.rooms
            disabled = not to_valid
            label = prettify_exit(ex["label"])

            clicked = st.button(
                label,
                key=f"mv_{ex['direction']}_{st.session_state.ui_tick}",
                type="secondary",
                disabled=disabled,
                use_container_width=True,
            )
            if clicked:
                st.session_state.ui_tick += 1

                if not to_valid:
                    panel_append("It doesn't seem to open.", "warning")
                    st.rerun()

                # Locked → show warning in the log, do not move
                if ex["locked"]:
                    locked_line = ex["locked_text"] or "It's stuck. You'll need leverage."
                    panel_append(locked_line, "warning")
                    st.rerun()

                # Detect if this exit was item-gated and the player has that item
                exit_obj = G.room.exits.get(ex["direction"])
                used_item = None
                if exit_obj and getattr(exit_obj, "locked_by_item", None):
                    if exit_obj.locked_by_item in G.inventory:
                        used_item = exit_obj.locked_by_item

                # Move succeeds → append arrival entry (append-only panel)
                G.move(ex["direction"])
                if G.room.name:
                    panel_append(f"**{G.room.name}**", "body")
                panel_append(G.desc_short(), "body")

                if used_item:
                    panel_append(f"You pry the door with the **{used_item}**. It opens.", "success")

                # Victory room?
                if "END_ROOM_IDS" in globals() and G.current_room_id in END_ROOM_IDS:
                    panel_append(G.desc_long(), "body")
                    panel_append("You step into the street and breathe free air. You escaped!", "success")
                    st.session_state.game_over = True
                    st.rerun()

                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


        

# ---------- end of two-column layout ----------

# (Optional) debug
with st.expander("Debug state"):
    st.write({
        "room": G.current_room_id,
        "inventory": sorted(G.inventory),
        "flags": sorted(G.flags),
    })
