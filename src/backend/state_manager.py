
import streamlit as st
from typing import Dict, Any

def init_state(world) -> None:
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
    return {
        "location_id": st.session_state.location_id,
        "inventory": st.session_state.inventory,
        "flags": st.session_state.flags,
        "visited": st.session_state.visited,
    }

def save_state() -> None:
    # TODO: persist to storage adapter
    pass
