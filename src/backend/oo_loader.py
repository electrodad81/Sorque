from __future__ import annotations
from typing import Dict, Any, List, Set
import json
from .oo import Room, Exit, Interaction, Game, DescOverride

def _to_interactions(raw_list):
    out = []
    for idata in (raw_list or []):
        out.append(
            Interaction(
                id=str(idata.get("id")),
                label=str(idata.get("label", "Interact")),
                text=idata.get("text"),
                once=bool(idata.get("once", False)),
                visible_if_flags=_to_set(idata.get("visible_if_flags")),
                visible_if_not_flags=_to_set(idata.get("visible_if_not_flags")),
                visible_if_items=_to_set(idata.get("visible_if_items")),
                visible_if_not_items=_to_set(idata.get("visible_if_not_items")),
                effects=list(idata.get("effects") or []),
                sort=int(idata.get("sort", 0)),
            )
        )
    return out

def _to_set(v: Any) -> Set[str]:
    if not v:
        return set()
    if isinstance(v, list):
        return set(str(x) for x in v)
    return {str(v)}

def _to_overrides(raw_list):
    out = []
    for ov in (raw_list or []):
        out.append(DescOverride(
            short=ov.get("short"),
            long=ov.get("long"),
            visible_if_flags=_to_set(ov.get("visible_if_flags")),
            visible_if_not_flags=_to_set(ov.get("visible_if_not_flags")),
            visible_if_items=_to_set(ov.get("visible_if_items")),
            visible_if_not_items=_to_set(ov.get("visible_if_not_items")),
            priority=int(ov.get("priority", 0)),  # NEW
        ))
    return out

def load_rooms(world: Dict[str, Any]) -> Dict[str, Room]:
    """Build Room objects (exits, interactions, desc overrides) from world JSON."""
    rooms: Dict[str, Room] = {}

    raw_rooms = world.get("rooms") or {}
    for rid, rdata in raw_rooms.items():
        # Exits
        exits: Dict[str, Exit] = {}
        for direction, edata in (rdata.get("exits") or {}).items():
            exits[direction] = Exit(
                direction=direction,
                to_room=str(edata.get("to")),
                locked_by_item=edata.get("locked_by_item"),
                locked_by_flag=edata.get("locked_by_flag"),
                locked_text=edata.get("locked_text"),
                label=edata.get("label"),
            )

        # Interactions (now via helper)
        interactions: List[Interaction] = _to_interactions(rdata.get("interactions"))

        # Description overrides
        desc_overrides: List[DescOverride] = _to_overrides(rdata.get("desc_overrides"))

        # Room
        room = Room(
            id=str(rdata.get("id", rid)),
            name=rdata.get("name"),
            desc_short=rdata.get("desc_short", ""),
            desc_long=rdata.get("desc_long", ""),
            exits=exits,
            interactions=interactions,
            on_look_add_flags=_to_set(rdata.get("on_look_add_flags")),
            desc_overrides=desc_overrides,
        )
        rooms[room.id] = room

    return rooms


def _resolve_start_room(world: Dict[str, Any], rooms: Dict[str, Room]) -> str:
    candidates = [
        world.get("start_room"),
        world.get("start"),
        world.get("startRoom"),
        (world.get("meta") or {}).get("start_room"),
        (world.get("meta") or {}).get("start_room_id"),
    ]
    for c in candidates:
        if c is not None and str(c) in rooms:
            return str(c)
    if rooms:
        return next(iter(rooms.keys()))
    raise ValueError("World JSON has no rooms; cannot determine start_room.")

def new_game_from_path(json_path: str) -> Game:
    with open(json_path, "r", encoding="utf-8") as f:
        world = json.load(f)
    rooms = load_rooms(world)
    start = _resolve_start_room(world, rooms)

    global_interactions = _to_interactions(world.get("global_interactions"))

    return Game(rooms=rooms, start_room_id=start, global_interactions=global_interactions)
