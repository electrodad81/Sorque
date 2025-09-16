"""
Content service for Sorque.

This module provides functions to produce human‑readable descriptions
for locations, NPCs and items. Where possible, these descriptions
delegate to the LLM client to generate atmospheric prose. When the
LLM client is unavailable or returns a stub, the service falls back
to a deterministic description composed from authored metadata.

All functions in this module accept a ``World`` instance rather than
raw YAML structures so that they can look up titles and other
metadata via helper methods. See ``world_loader.py`` for details.
"""

from typing import Dict, Any, List, Optional
from .world_loader import World, Location
from src.adapters.llm_client import complete


def _format_exits(exits: Dict[str, str]) -> str:
    """Return a comma‑separated list of exit directions capitalised."""
    return ", ".join([d.capitalize() for d in exits.keys()]) if exits else "none"


def describe_location(world: World, loc_id: str, state: Dict[str, Any]) -> str:
    """Generate a description for the current location.

    Uses the LLM client to produce a short piece of prose anchored on
    authored facts: the location's title, visible exits, items and
    NPCs. If the LLM client returns its default stub, a simple
    deterministic string is used instead.
    """
    loc: Location = world.locations[loc_id]
    exit_list = _format_exits(loc.exits)
    # Visible items: filter out hidden items
    item_names: List[str] = []
    for itm in loc.items:
        if isinstance(itm, dict):
            if itm.get("hidden"):
                continue
            iid = itm.get("id")
        else:
            iid = itm
        item_def = world.get_item(iid)
        item_names.append(item_def.get("name", iid) if item_def else str(iid))
    item_list = ", ".join(item_names) if item_names else "none"
    # Visible NPCs
    npc_names: List[str] = []
    for npc_id in loc.npcs:
        npc_def = world.get_npc(npc_id)
        npc_names.append(npc_def.get("name", npc_id) if npc_def else npc_id)
    npc_list = ", ".join(npc_names) if npc_names else "no one in particular"
    # Compose a prompt for the LLM. Keep it high level and instruct the
    # model to produce PG‑13 content without explicit mechanics.
    prompt = (
        f"You are narrating a dark fantasy exploration game. The player stands at the location "
        f"called '{loc.title}'. Visible exits are: {exit_list}. The following items can be seen: {item_list}. "
        f"The following characters are present: {npc_list}. Describe the scene in two to three sentences, "
        f"staying in the present tense and using evocative language. Do not mention game mechanics or buttons."
    )
    description = complete(prompt)
    # If the LLM client returns its stub (it starts with 'LLM stub'), fall
    # back to a deterministic description. This ensures a useful output
    # during local development without API access.
    if description.startswith("LLM stub"):
        description = (
            f"You are at **{loc.title}**.\n\n"
            f"Exits: {exit_list}.\n\n"
            f"Items here: {item_list}.\n\n"
            f"You notice {npc_list}."
        )
    return description


def describe_npc(world: World, npc_id: str) -> str:
    """Generate a snippet of dialogue or description for an NPC."""
    npc = world.get_npc(npc_id)
    if not npc:
        return "There is no one here by that name."
    name = npc.get("name", npc_id)
    role = npc.get("role", "")
    goals = npc.get("goals", [])
    goals_text = ", ".join(goals) if goals else "their own mysterious agenda"
    prompt = (
        f"You are improvising first‑person dialogue for a character in a dark fantasy text adventure. "
        f"The character's name is {name}. Their role is {role}. Their goals include {goals_text}. "
        f"They are speaking with the player for the first time. Respond in the character's voice in one or two sentences, "
        f"hinting at their personality without revealing secrets."
    )
    utterance = complete(prompt)
    if utterance.startswith("LLM stub"):
        utterance = f"{name} regards you cautiously but says nothing of consequence."
    return utterance


def describe_item(world: World, item_id: str) -> str:
    """Produce a description for an item when the player inspects or acquires it."""
    item = world.get_item(item_id)
    if not item:
        return f"You examine the {item_id}, but learn nothing unusual."
    name = item.get("name", item_id)
    tags = ", ".join(item.get("tags", [])) if item.get("tags") else ""
    prompt = (
        f"You are describing an item in a dark fantasy exploration game. "
        f"The item is called {name}. It has the following qualities: {tags}. "
        f"Describe it in one or two sentences, using vivid sensory detail."
    )
    desc = complete(prompt)
    if desc.startswith("LLM stub"):
        desc = f"It appears to be a {name}."
    return desc


def get_location_title(world: World, loc_id: str) -> str:
    """Return the title of a location. Wrapper around ``World.title``.

    This helper exists for backwards compatibility with earlier
    versions of the codebase that expected this function in the
    content service. It simply forwards the call to the ``World``
    instance.
    """
    return world.title(loc_id)