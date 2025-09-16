"""
Session state management for Sorque.

This module wraps Streamlit's session_state to initialise and access
persistent state across reruns. The ``init_state`` function seeds
default values when the app is first loaded. ``get_state`` returns
only the values that are needed by the action router and other
components.
"""

import streamlit as st
from typing import Dict, Any


def init_state(world) -> None:
    """Initialise Streamlit session state keys if they are missing."""
    if "location_id" not in st.session_state:
        first = next(iter(world.locations.keys()))
        st.session_state.location_id = first
        st.session_state.inventory = []
        st.session_state.flags = set()
        st.session_state.visited = {first}
        st.session_state.last_description = ""
        st.session_state.moves = 0
        st.session_state.log = []


def get_state() -> Dict[str, Any]:
    """Return a shallow copy of the player's current state."""
    return {
        "location_id": st.session_state.location_id,
        "inventory": st.session_state.inventory,
        "flags": st.session_state.flags,
        "visited": st.session_state.visited,
    }


def save_state() -> None:
    """Placeholder for persistence backends. Not yet implemented."""
    pass