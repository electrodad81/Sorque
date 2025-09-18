"""
Streamlit application entry point for Sorque.

This module defines the layout of the user interface and ties
together the world loader, state management and action routing. The
UI consists of a status bar at the top, a transcript console on the
left and a keypad on the right. Additional interactive buttons for
NPCs and items appear below the compass when available.

The overall layout and styling are preserved from the original
skeleton. Only the addition of interaction buttons in the right panel
changes the visual elements on the screen. New buttons are created
dynamically based on the current location's items and NPCs.
"""

from base64 import b64encode
import sys
from html import escape
from pathlib import Path
import streamlit as st

from typing import Dict, Any, List

# Path shim so 'from src....' works when running 'streamlit run src/app/app.py'
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backend.world_loader import World
from src.backend.state_manager import init_state, get_state
from src.backend.action_router import handle_action
from src.backend.content_service import describe_location  # type: ignore

BASE_DIR = Path(__file__).resolve().parents[2]


@st.cache_resource
def load_world() -> World:
    """Load the game world from YAML files on disk."""
    return World.from_files(
        BASE_DIR / "world" / "graph" / "locations.yaml",
        BASE_DIR / "world" / "graph" / "edges.yaml",
        BASE_DIR / "world" / "npcs.yaml",
        BASE_DIR / "world" / "items.yaml",
    )


def inject_css() -> None:
    """Inject custom CSS styles into the Streamlit app."""
    st.markdown(
        """

/* Hide sidebar + narrow, centered page */
section[data-testid="stSidebar"] { display:none; }
.main .block-container {
  max-width: 840px; width: 90vw; margin: 8px auto 0 auto;
}

/* Status bar */
.sq-status{
  background:#c0c0c0; color:#000; padding:6px 10px; border-radius:0; margin-bottom:8px;
  font-family: Consolas, "Courier New", ui-monospace, monospace; font-size:15px;
  border:1px solid #888;
}
.sq-status .row { display:flex; align-items:center; justify-content:space-between; }
.sq-status .left,.sq-status .center{ font-weight:700; }

/* Two columns, no gutters */
div[data-testid="stHorizontalBlock"] { gap:0 !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  padding-left:0 !important; padding-right:0 !important;
}

/* LEFT: transcript — keep the vertical white separator on the right edge */
.sq-left{
  background:#000; color:#d7d7d7; line-height:1.35;
  font-family: Consolas, "Courier New", ui-monospace, monospace;
  height:480px; overflow-y:auto; padding:6px 8px;
  border:2px solid #fff; border-right:2px solid #fff;   /* separator */
}
.sq-left pre{ margin:0; white-space:pre-wrap; }

/* RIGHT: no background box, just buttons sitting on the page */
#kp-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
  padding:0 8px 0 16px !important;
}
/* Square, modern buttons: black bg, white outline, white text */
div.stButton > button{
  width:100%;
  background:#000 !important; color:#fff !important;
  border:2px solid #fff !important; border-radius:0 !important;
  box-shadow:none !important; padding:8px 0 !important;
  font-weight:600; letter-spacing:0.5px;
}
div.stButton > button:hover{ background:#111 !important; }
div.stButton > button:disabled{ color:#666 !important; border-color:#444 !important; }

        """,
        unsafe_allow_html=True,
    )


def use_apple2_font() -> None:
    """Embed the Apple II font and apply it across the UI."""
    font_path = BASE_DIR / "assets" / "fonts" / "PrintChar21.ttf"  # adjust if necessary
    try:
        with open(font_path, "rb") as f:
            b64 = b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"""

@font-face {{
  font-family: 'Apple2';
  src: url(data:font/ttf;base64,{b64}) format('truetype');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}}

/* Use the font in our app (status bar, console text, keypad buttons) */
.sq-status,
.sq-left, .sq-left pre,
#sq-console-row + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child,
#sq-console-row + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child div.stButton > button {{
  font-family: 'Apple2', Consolas, "Courier New", ui-monospace, monospace !important;
  font-size: 16px;
  letter-spacing: 0.02em;
  -webkit-font-smoothing: none;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeSpeed;
}}

    """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        # In case the font file is missing, silently continue using default fonts
        pass


def render_status_bar(world: World, state: Dict[str, Any]) -> None:
    """Render the top status bar showing the location title and other info."""
    location_name = world.title(state["location_id"])
    moves = st.session_state.get("moves", 0)
    st.markdown(
        f"""


{escape(location_name)} 
Sorque 
Moves: {moves} 


        """,
        unsafe_allow_html=True,
    )


def seed_transcript(world: World, state: Dict[str, Any]) -> None:
    """Populate the transcript on first render."""
    if not st.session_state.get("log"):
        loc_title = world.title(state["location_id"])
        desc = describe_location(world, state["location_id"], state)
        st.session_state.last_description = desc
        st.session_state.log = [loc_title, desc, ""]


def render_console(world: World, state: Dict[str, Any]) -> None:
    """Render the main console consisting of transcript and keypad."""
    # Anchor so CSS can reliably target this specific columns row
    st.markdown(' ', unsafe_allow_html=True, key="sq-console-row")
    # Two columns: left (text) and right (buttons only)
    left_col, right_col = st.columns([2.8, 1.0], gap="small")
    # LEFT: transcript
    with left_col:
        seed_transcript(world, state)
        text = "\n".join(st.session_state.get("log", []))
        st.markdown(f' {escape(text)} ', unsafe_allow_html=True)
    # RIGHT: keypad and interactions
    with right_col:
        exits = world.locations[state["location_id"]].exits
        # Movement callback
        def mv(dir_key: str) -> None:
            handle_action(world, state, {"type": "move", "dir": dir_key})
        # Compass
        c1a, c1b, c1c = st.columns([1, 1, 1])  # N
        with c1b:
            st.button("Go North", key="pad_N", disabled=("north" not in exits), on_click=mv, kwargs={"dir_key": "north"})
        c2a, c2b, c2c = st.columns(3)  # W L E
        with c2a:
            st.button("Go West", key="pad_W", disabled=("west" not in exits), on_click=mv, kwargs={"dir_key": "west"})
        with c2b:
            st.button("Look", key="pad_L", on_click=lambda: handle_action(world, state, {"type": "look"}))
        with c2c:
            st.button("Go East", key="pad_E", disabled=("east" not in exits), on_click=mv, kwargs={"dir_key": "east"})
        c3a, c3b, c3c = st.columns([1, 1, 1])  # S
        with c3b:
            st.button("Go South", key="pad_S", disabled=("south" not in exits), on_click=mv, kwargs={"dir_key": "south"})
        # Auxiliary buttons
        c4a, c4b, c4c, c4d = st.columns(4)  # m j inv ✱
        with c4a:
            st.button("Map", key="pad_m", help="Map", on_click=lambda: st.session_state.__setitem__("active_panel", "map"))
        with c4b:
            st.button("Journal", key="pad_j", help="Journal", on_click=lambda: st.session_state.__setitem__("active_panel", "journal"))
        with c4c:
            st.button("Inventory", key="pad_inv", help="Inventory", on_click=lambda: handle_action(world, state, {"type": "inventory"}))
        with c4d:
            st.button("Settings", key="pad_settings", help="Settings", on_click=lambda: st.session_state.__setitem__("active_panel", "settings"))
        # Interaction buttons: NPCs and items
        loc = world.locations[state["location_id"]]
        # NPC interactions
        for npc_id in loc.npcs:
            npc_def = world.get_npc(npc_id)
            label = npc_def.get("name", npc_id) if npc_def else npc_id
            st.button(
                f"Talk to {label}",
                key=f"npc_{npc_id}",
                on_click=lambda npc_id=npc_id: handle_action(world, state, {"type": "talk", "npc_id": npc_id}),
            )
        # Item interactions – show only non‑hidden items
        for itm in loc.items:
            # skip hidden items
            if isinstance(itm, dict) and itm.get("hidden"):
                continue
            iid = itm.get("id") if isinstance(itm, dict) else itm
            item_def = world.get_item(iid)
            name = item_def.get("name", iid) if item_def else iid
            # Provide both inspect and take actions; for now we only implement 'take'
            st.button(
                f"Take {name}",
                key=f"take_{iid}",
                on_click=lambda iid=iid: handle_action(world, state, {"type": "take", "item_id": iid}),
            )


def render_panels(world: World, state: Dict[str, Any]) -> None:
    """Render side panels such as map, journal and settings."""
    panel = st.session_state.get("active_panel")
    if not panel:
        return
    st.markdown("---")
    if panel == "map":
        # Show adjacency list of exits
        rows: List[str] = []
        for loc in world.locations.values():
            for d, to in (loc.exits or {}).items():
                rows.append(f"{loc.id:<18} {d:>5} → {to}")
        content = "\n".join(rows) or "(no exits)"
        st.markdown("**Map (adjacency)** — press the button again to close")
        st.code(content)
    elif panel == "journal":
        log = st.session_state.get("log", [])
        tail = "\n".join(log[-40:]) if log else "(empty)"
        st.markdown("**Journal (recent transcript)**")
        st.code(tail)
    elif panel == "settings":
        st.markdown("**Settings**")
        st.checkbox("Typewriter effect (placeholder)", value=False, key="typewriter")
        st.checkbox("PG-13 content filter (always on in MVP)", value=True, disabled=True, key="pg13")
    # Close panel button
    st.button("Close panel", on_click=lambda: st.session_state.__setitem__("active_panel", None))


def main() -> None:
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Sorque", page_icon="🕯️", layout="wide", initial_sidebar_state="collapsed")
    inject_css()
    use_apple2_font()
    world = load_world()
    init_state(world)
    state = get_state()
    render_status_bar(world, state)
    render_console(world, state)
    render_panels(world, state)


if __name__ == "__main__":
    main()