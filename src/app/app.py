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
/* =========================
   Buttons (primary & secondary)
   ========================= */

/* Primary (Look) — blue outline, full-width, grows with text */
.stButton > button[kind="primary"]{
  width: 100% !important;
  min-height: 60px !important;
  height: auto !important;

  background: transparent !important;
  color: #1a73e8 !important;
  border: 2px solid #1a73e8 !important;
  box-shadow: none !important;

  /* wrapping: no mid-word splits */
  white-space: normal !important;
  word-break: normal !important;
  overflow-wrap: break-word !important;
  word-wrap: break-word !important; /* Safari alias */
  line-height: 1.2 !important;
  padding: 10px 14px !important;
}
.stButton > button[kind="primary"]:hover{ background: rgba(26,115,232,0.08) !important; }
.stButton > button[kind="primary"]:active{ background: rgba(26,115,232,0.16) !important; }

/* Secondary — full-width, grows with text, clean wraps */
.stButton > button[kind="secondary"]{
  width: 100% !important;
  min-height: 60px !important;
  height: auto !important;

  white-space: normal !important;
  word-break: normal !important;        /* ← fixes mid-word splits */
  overflow-wrap: break-word !important; /* only break huge tokens */
  word-wrap: break-word !important;     /* Safari alias */

  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1.2 !important;
  padding: 10px 14px !important;
  border-radius: 8px !important;
}

/* Compass: vertical stack spacing */
.compass-vertical .stButton { margin-bottom: 8px; }

/* =========================
   Right-panel header + divider
   ========================= */

/* Subheader above actions: theme-safe (inherits text color) */
.panel-subhed{
  margin: 0 0 6px;
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: .02em;
  text-transform: uppercase;
  color: inherit !important;     /* <- was hard-coded white */
}

/* Thin divider line that works on light & dark themes */
hr.panel-rule{
  border: none;
  height: 1px;
  margin: 8px 0 0px;
  background: linear-gradient(to right,
              rgba(0,0,0,.06), rgba(0,0,0,.16), rgba(0,0,0,.06));
}
            
/* Room header chip above the story panel */
.room-header-chip{
  background: #e5e7eb !important;   /* neutral gray */
  color: #111 !important;            /* black text */
  padding: 8px 12px;
  border-radius: 1px;
  font-weight: 700;
  font-size: 1.6rem;
  letter-spacing: .01em;
  line-height: 1.25;
  margin: 0 0 8px 0;                 /* space below the chip */
  display: block;                    /* full column width */
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.06); /* subtle edge */
}
            
@media (prefers-color-scheme: dark){
  hr.panel-rule{
    background: linear-gradient(to right,
                rgba(255,255,255,.06), rgba(255,255,255,.22), rgba(255,255,255,.06));
  }
}
</style>
""", unsafe_allow_html=True)


# CSS for room label panel
st.markdown("""
<style>
/* Room header chip inside the description/story panel */
.desc-panel .msg-room{
  background: #e5e7eb !important;   /* neutral gray */
  color: #111111 !important;         /* black text */
  display: inline-block;
  padding: 6px 10px;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: .01em;
  margin: 6px 0 2px;                 /* a little air above the paragraph */
}
</style>
""", unsafe_allow_html=True)

# =========================
# End of game
# =========================

# Default lines used when JSON gives only a cause
DEATH_TEXT = {
    "dog":     "The dog ate your face. You died.",
    "fall":    "You tumble into the dark and stop suddenly. You died.",
    "trap":    "Metal snaps shut around your leg. You died.",
    "generic": "You collapse. Darkness takes you.",
}

# --- Mark death from anywhere in the game/handlers ---
def set_death(cause: str = "generic", msg: Optional[str] = None):
    """Mark player as dead; read by the post-action/post-move guards."""
    G.dead = True
    G.death_cause = cause
    if msg:
        G.death_message = msg

def die(cause: str = "generic", msg: Optional[str] = None):
    """Finalize death with message and freeze UI (same flow as victory)."""
    final = (msg or DEATH_TEXT.get(cause) or DEATH_TEXT["generic"]).strip()
    st.session_state.last_death = {"cause": cause, "message": final}
    end_game(final, level="error")

def end_game(message: str, level: str = "success"):
    """Freeze the game and show a restart affordance, reusing the same path for win/lose."""
    panel_append(message, level)              # final banner line (green for win, red for death)
    st.session_state.game_over = True         # freezes inputs elsewhere
    st.session_state.show_restart = True
    st.rerun()

def restart_game():
    st.session_state.clear()
    st.rerun()

def apply_effect(eff: dict) -> None:
    """Interpret JSON effect objects. Shows only kill_player here; keep your others."""
    if "kill_player" in eff:
        payload = eff["kill_player"]
        cause, msg = "generic", None

        if isinstance(payload, bool):
            if not payload:
                return  # explicit false => no-op
        elif isinstance(payload, str):
            cause = (payload or "generic").strip()
        elif isinstance(payload, dict):
            cause = (payload.get("cause") or "generic").strip()
            msg = (payload.get("message") or payload.get("msg") or "").strip() or None

        set_death(cause, msg)
        return

    # TODO: keep your other effect handlers here (add_item, remove_item, add_flag, etc.)



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
        panel_append(G.room.name, "room")
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
        st.markdown(
            f'<div class="room-header-chip">{G.room.name}</div>',
            unsafe_allow_html=True
        )

    # Fixed, scrollable text window
    DescriptionPanel(
        panel_id="room-desc",
        height_px=560,                 # a little taller looks nice with more width
        border_css="1px solid #333",   # subtle dark border
        bg_css="#111",                 # dark background
        font_size="1.4rem",              # optional bump
        margin_bottom_px=16
    ).render(st.session_state.panel["blocks"])
    
    # --- If over: show Play Again under the panel; else show Look/actions ---
    if st.session_state.get("game_over"):
        st.markdown('<hr class="panel-rule">', unsafe_allow_html=True)
        if st.button("Play again", key="restart_btn", type="primary", use_container_width=True):
            restart_game()
    else:
        # Actions header
        st.markdown('<div class="panel-subhed">Actions you can take:</div>', unsafe_allow_html=True)
        st.markdown('<hr class="panel-rule">', unsafe_allow_html=True)
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
                        msg, dead = G.do(it.id)  # msg may already be a custom death line
                        after = set(G.inventory)
                        st.session_state.ui_tick += 1

                        # If the action resulted in death, use engine-provided message if available
                        if dead or getattr(G, "dead", False) or getattr(G, "hp", 1) <= 0:
                            cause = getattr(G, "death_cause", "generic")
                            # Prefer an explicit engine-set message; otherwise use the action's msg
                            death_msg = getattr(G, "death_message", None) or msg
                            die(cause, death_msg)
                            # die() calls end_game() which appends the line + freezes UI + reruns
                            # so we never reach the normal append code below.

                        # Normal (non-death) path:
                        # Refresh desc (overrides) *first* so authored text ends up on top
                        panel_append(G.desc_long(), "body")

                        # Inventory pickups (if any)
                        for name in sorted(after - before):
                            panel_append(f"**{name.title()} added to inventory.**", "success")

                        # Authored text *last* -> shows at the top in newest-first panel
                        if msg:
                            panel_append(msg, "info")

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


# ----- RIGHT: Directions (compass) above Inventory -----
with right:
    if st.session_state.get("game_over"):
        # When the run is over, don't render compass/inventory
        pass
    else:
        moves = G.compass()

        def prettify_exit(label: str) -> str:
            t = label.strip()
            tl = t.lower()
            if tl.startswith("to the "): t = t[7:]
            elif tl.startswith("to "):    t = t[3:]
            return t[:1].upper() + t[1:] if t else t

        if moves:
            st.markdown('<div class="panel-subhed">Directions you can go</div>', unsafe_allow_html=True)
            st.markdown('<hr class="panel-rule">', unsafe_allow_html=True)

            # Compass: vertical stack of full-width buttons
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
                        panel_append(G.room.name, "room")
                    panel_append(G.desc_short(), "body")

                    if used_item:
                        panel_append(f"You pry the door with the **{used_item}**. It opens.", "success")

                    # ---- Death guard goes HERE ----
                    if getattr(G, "dead", False):
                        cause = getattr(G, "death_cause", "generic")
                        msg   = getattr(G, "death_message", None)
                        die(cause, msg)   # ends the run with the right message (e.g., dog)

                    # Victory room?
                    if "END_ROOM_IDS" in globals() and G.current_room_id in END_ROOM_IDS:
                        panel_append(G.desc_long(), "body")
                        end_game("You step into the street and breathe free air. You escaped!", level="success")

                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Divider + Inventory below the compass
        st.markdown('<hr class="panel-rule">', unsafe_allow_html=True)
        st.checkbox("Inventory", key="inv_open")
        if st.session_state.inv_open:
            InventoryPanel(panel_id="inv", height_px=260, border_css="1px solid #333") \
                .render(sorted(G.inventory))

        

# ---------- end of two-column layout ----------

# (Optional) debug
#with st.expander("Debug state"):
#    st.write({
#        "room": G.current_room_id,
#        "inventory": sorted(G.inventory),
#        "flags": sorted(G.flags),
#    })
