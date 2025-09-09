
from typing import Dict, Any

def get_location_title(world, loc_id: str) -> str:
    return world.title(loc_id)

def describe_location(world, loc_id: str, state: Dict[str, Any]) -> str:
    loc = world.locations[loc_id]
    exits = ", ".join([d.capitalize() for d in loc.exits.keys()]) or "none"
    npc_text = ", ".join(loc.npcs) if loc.npcs else "no one in particular"
    return (
        f"You are at **{loc.title}**.\n\n"
        f"Exits: {exits}. You notice {npc_text}. "
        f"(This is a stub description; LLM output will replace it later.)"
    )
