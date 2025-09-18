
from typing import Dict, Any, Set

CARDINALS = ["north","east","south","west"]

def get_available_actions(world, state: Dict[str, Any]) -> Dict[str, Any]:
    loc = world.locations[state["location_id"]]
    moves: Set[str] = set(d for d in CARDINALS if d in loc.exits)
    context = []
    if loc.npcs:
        context.append({"id":"talk","label":"Talk"})
    return {"move": moves, "context": context}
