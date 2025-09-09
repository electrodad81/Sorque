import streamlit as st
from typing import Dict, Any
from .state_manager import get_state
from .content_service import describe_location

def _append(line: str = "") -> None:
    log = st.session_state.get("log", [])
    log.append(line)
    if len(log) > 400:
        log[:] = log[-400:]
    st.session_state.log = log

def _append_block(*lines: str) -> None:
    for ln in lines:
        _append(ln)
    _append("")  # blank line between blocks

def handle_action(world, state: Dict[str, Any], action: Dict[str, Any]) -> None:
    t = action.get("type")

    if t == "move":
        direction = action.get("dir")
        dest = world.neighbor(state["location_id"], direction)
        _append(f"> go {direction}")
        if dest:
            st.session_state.location_id = dest
            st.session_state.visited.add(dest)
            st.session_state.moves += 1
            desc = describe_location(world, dest, get_state())
            st.session_state.last_description = desc
            _append_block(world.title(dest), desc)
        else:
            _append_block("You can't go that way.")

    elif t == "look":
        st.session_state.moves += 1
        _append("> look")
        desc = describe_location(world, state["location_id"], state)
        st.session_state.last_description = desc
        _append_block(world.title(state["location_id"]), desc)

    elif t == "talk":
        st.session_state.moves += 1
        _append("> talk")
        st.session_state.last_description = "You strike up a conversation. (Dialog system stub)"
        _append_block(st.session_state.last_description)

    elif t == "inventory":
        _append("> inventory")
        inv = state.get("inventory", [])
        if inv:
            for item in inv:
                _append(f"- {item}")
        else:
            _append("(empty)")
        _append("")

    else:
        _append_block(f"Action '{t}' not implemented yet.")
