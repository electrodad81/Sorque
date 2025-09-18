"""
Action routing for Sorque.

The action router consumes high‑level player actions and mutates the
global Streamlit session state accordingly. It appends log entries to
the transcript and invokes appropriate content generation functions.

This version extends the original router with new action types:

* ``talk`` – talk to a specific NPC at the current location. Requires
  ``npc_id``.
* ``inspect`` – inspect an item at the current location without
  picking it up. Requires ``item_id``.
* ``take`` – pick up an item. Requires ``item_id``. The item is
  removed from the location and added to the player's inventory.

Any unrecognised action type will result in a simple placeholder
message. If an action refers to an NPC or item that is not present,
the router will log an appropriate message.
"""

import streamlit as st
from typing import Dict, Any
from .state_manager import get_state
from .content_service import (
    describe_location,
    describe_npc,
    describe_item,
)


def _append(line: str = "") -> None:
    """Append a single line to the session transcript."""
    log = st.session_state.get("log", [])
    log.append(line)
    # Trim the log to the most recent 400 entries
    if len(log) > 400:
        log[:] = log[-400:]
    st.session_state.log = log


def _append_block(*lines: str) -> None:
    """Append a block of lines separated by a blank line."""
    for ln in lines:
        _append(ln)
    _append("")  # blank line between blocks


def handle_action(world, state: Dict[str, Any], action: Dict[str, Any]) -> None:
    """Dispatch a player action and update state/log accordingly."""
    t = action.get("type")

    # Movement actions
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
        return

    # Look action refreshes the description of the current location
    if t == "look":
        st.session_state.moves += 1
        _append("> look")
        desc = describe_location(world, state["location_id"], state)
        st.session_state.last_description = desc
        _append_block(world.title(state["location_id"]), desc)
        return

    # Talk action for NPC interaction
    if t == "talk":
        npc_id = action.get("npc_id")
        # Log the attempted action
        if npc_id:
            npc_def = world.get_npc(npc_id)
            label = npc_def.get("name", npc_id) if npc_def else npc_id
            _append(f"> talk to {label}")
        else:
            _append("> talk")
        st.session_state.moves += 1
        # Verify the NPC is present at the current location
        loc = world.locations[state["location_id"]]
        if not npc_id or npc_id not in loc.npcs:
            _append_block("There is no one by that name here.")
            return
        dialogue = describe_npc(world, npc_id)
        st.session_state.last_description = dialogue
        _append_block(dialogue)
        return

    # Inspect an item without picking it up
    if t == "inspect":
        item_id = action.get("item_id")
        if item_id:
            item_def = world.get_item(item_id)
            label = item_def.get("name", item_id) if item_def else item_id
            _append(f"> inspect {label}")
        else:
            _append("> inspect")
        st.session_state.moves += 1
        loc = world.locations[state["location_id"]]
        # Determine if the item exists at the location and is visible
        visible_ids = []
        for itm in loc.items:
            iid = None
            if isinstance(itm, dict):
                if itm.get("hidden"):
                    continue
                iid = itm.get("id")
            else:
                iid = itm
            if iid:
                visible_ids.append(iid)
        if not item_id or item_id not in visible_ids:
            _append_block("You don't see that item here.")
            return
        desc = describe_item(world, item_id)
        st.session_state.last_description = desc
        _append_block(desc)
        return

    # Take an item – add to inventory and remove from the location
    if t == "take":
        item_id = action.get("item_id")
        if item_id:
            item_def = world.get_item(item_id)
            label = item_def.get("name", item_id) if item_def else item_id
            _append(f"> take {label}")
        else:
            _append("> take")
        st.session_state.moves += 1
        loc = world.locations[state["location_id"]]
        # Find the target item in the location list
        idx_to_remove = None
        visible_id_list: List[str] = []
        for idx, itm in enumerate(loc.items):
            iid = None
            if isinstance(itm, dict):
                if itm.get("hidden"):
                    continue
                iid = itm.get("id")
            else:
                iid = itm
            if iid:
                visible_id_list.append(iid)
            if iid == item_id:
                idx_to_remove = idx
        if not item_id or item_id not in visible_id_list or idx_to_remove is None:
            _append_block("You can't take that; it's not here.")
            return
        # Remove from location and add to inventory
        removed = loc.items.pop(idx_to_remove)
        # Normalise id for inventory storage
        iid = removed.get("id") if isinstance(removed, dict) else removed
        # Initialise inventory list if necessary
        inv = st.session_state.get("inventory", [])
        inv.append(iid)
        st.session_state.inventory = inv
        desc = describe_item(world, iid)
        st.session_state.last_description = desc
        _append_block(f"You take the {label}.", desc)
        return

    # Inventory listing
    if t == "inventory":
        _append("> inventory")
        inv = state.get("inventory", [])
        if inv:
            for iid in inv:
                item_def = world.get_item(iid)
                name = item_def.get("name", iid) if item_def else iid
                _append(f"- {name}")
        else:
            _append("(empty)")
        _append("")
        return

    # Fallback
    _append_block(f"Action '{t}' not implemented yet.")