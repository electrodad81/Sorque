# src/backend/oo.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any

# -----------------------------
# Core data structures
# -----------------------------

@dataclass
class Exit:
    """A directional exit from a room.

    Attributes:
        direction: canonical direction key (e.g., 'north', 'south', 'up', etc.)
        to_room: target room id
        locked_by_item: optional item name required in inventory to pass
        locked_by_flag: optional flag name that must be present to pass
        locked_text: message if locked (default falls back to a generic one)
        label: optional UI label (defaults to title-cased direction)
    """
    direction: str
    to_room: str
    locked_by_item: Optional[str] = None
    locked_by_flag: Optional[str] = None
    locked_text: Optional[str] = None
    label: Optional[str] = None

    def is_locked(self, inventory: Set[str], flags: Set[str]) -> bool:
        if self.locked_by_item and self.locked_by_item not in inventory:
            return True
        if self.locked_by_flag and self.locked_by_flag not in flags:
            return True
        return False

    def display_label(self) -> str:
        return self.label or self.direction.title()


@dataclass
class Interaction:
    """An authored interaction available in a room.

    Interactions are intentionally *authored-only* — no LLM paths.
    Visibility and behavior are controlled by flags/items.

    JSON fields this class understands (all optional except id & label):
      - id: stable id used for state (e.g., 'look_glint', 'take_hatchet')
      - label: UI text for the button
      - text: response text when performed (optional)
      - once: if True, auto-hides after first use (via flag 'done:<id>')
      - visible_if_flags: list of flags required for visibility
      - visible_if_not_flags: list of flags that must be absent for visibility
      - visible_if_items: list of items required in inventory for visibility
      - visible_if_not_items: list of items that must be *not* in inventory
      - effects: list of effect dicts, in order. Supported effect keys:
           {"add_flag": str}
           {"remove_flag": str}
           {"add_item": str}
           {"remove_item": str}
           {"set_room": str}
           {"kill_player": True, "message": Optional[str]}
      - sort: optional int to control ordering in UI
    """
    id: str
    label: str
    text: Optional[str] = None
    once: bool = False
    visible_if_flags: Set[str] = field(default_factory=set)
    visible_if_not_flags: Set[str] = field(default_factory=set)
    visible_if_items: Set[str] = field(default_factory=set)
    visible_if_not_items: Set[str] = field(default_factory=set)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    sort: int = 0

    def _done_flag(self) -> str:
        return f"done:{self.id}"

    def is_visible(self, game: "Game") -> bool:
        # once-only interactions disappear after completion
        if self.once and self._done_flag() in game.flags:
            return False
        if any(f not in game.flags for f in self.visible_if_flags):
            return False
        if any(f in game.flags for f in self.visible_if_not_flags):
            return False
        if any(i not in game.inventory for i in self.visible_if_items):
            return False
        if any(i in game.inventory for i in self.visible_if_not_items):
            return False
        return True

    def perform(self, game: "Game") -> Tuple[str, bool]:
        """Applies effects and returns (message, dead?)."""
        out_lines: List[str] = []
        if self.text:
            out_lines.append(self.text)
        dead = False

        for eff in self.effects:
            if "add_flag" in eff:
                game.flags.add(eff["add_flag"])
            if "remove_flag" in eff:
                game.flags.discard(eff["remove_flag"])
            if "add_item" in eff:
                game.inventory.add(eff["add_item"])
            if "remove_item" in eff:
                game.inventory.discard(eff["remove_item"])
            if "set_room" in eff:
                target = eff["set_room"]
                if target in game.rooms:
                    game.current_room_id = target
            if eff.get("kill_player"):
                dead = True
                msg = eff.get("message")
                if msg:
                    out_lines.append(msg)

        if self.once:
            game.flags.add(self._done_flag())

        return ("\n".join(out_lines).strip(), dead)


@dataclass
class Room:
    id: str
    name: Optional[str] = None
    desc_short: str = ""
    desc_long: str = ""
    exits: Dict[str, Exit] = field(default_factory=dict)
    interactions: List[Interaction] = field(default_factory=list)
    on_look_add_flags: Set[str] = field(default_factory=set)
    desc_overrides: List[DescOverride] = field(default_factory=list)  # <— NEW

    def render_desc(self, game: "Game", long: bool = False) -> str:
        # First matching override wins
        for ov in self.desc_overrides:
            if ov.is_visible(game):
                txt = (ov.long if long else ov.short)
                if txt:  # allow partial overrides
                    return txt
        return self.desc_long if long else self.desc_short
    
@dataclass
class DescOverride:
    short: Optional[str] = None
    long: Optional[str] = None
    visible_if_flags: Set[str] = field(default_factory=set)
    visible_if_not_flags: Set[str] = field(default_factory=set)
    visible_if_items: Set[str] = field(default_factory=set)
    visible_if_not_items: Set[str] = field(default_factory=set)

    def is_visible(self, game: "Game") -> bool:
        if any(f not in game.flags for f in self.visible_if_flags): return False
        if any(f in game.flags for f in self.visible_if_not_flags): return False
        if any(i not in game.inventory for i in self.visible_if_items): return False
        if any(i in game.inventory for i in self.visible_if_not_items): return False
        return True

# -----------------------------
# Game state & API
# -----------------------------

class Game:
    """Runtime container for world + player state.

    This engine is deterministic and derived entirely from authored data.
    """

    def __init__(self, rooms: Dict[str, Room], start_room_id: str):
        if start_room_id not in rooms:
            raise ValueError(f"start_room '{start_room_id}' not in rooms")
        self.rooms: Dict[str, Room] = rooms
        self.start_room_id: str = start_room_id
        self.current_room_id: str = start_room_id
        self.flags: Set[str] = set()
        self.inventory: Set[str] = set()
        self.dead: bool = False
        self.last_message: str = ""

    # ---------- derived helpers ----------
    @property
    def room(self) -> Room:
        return self.rooms[self.current_room_id]

    def compass(self) -> List[Dict[str, Any]]:
        """Return UI-friendly exit info with lock status."""
        data = []
        for direction, ex in self.room.exits.items():
            locked = ex.is_locked(self.inventory, self.flags)
            data.append({
                "direction": direction,
                "label": ex.display_label(),
                "to": ex.to_room,
                "locked": locked,
                "locked_text": ex.locked_text or "It's stuck. You'll need something to pry it open.",
            })
        # Stable order by common compass ordering
        order = {k: i for i, k in enumerate([
            "north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest",
            "up", "down", "in", "out"
        ])}
        data.sort(key=lambda d: order.get(d["direction"], 999))
        return data

    def visible_interactions(self) -> List[Interaction]:
        vis = [it for it in self.room.interactions if it.is_visible(self)]
        vis.sort(key=lambda it: (it.sort, it.label))
        return vis

    # ---------- player verbs ----------
    def look(self) -> str:
        # Looking reveals authored flags (e.g., saw_glint)
        for f in self.room.on_look_add_flags:
            self.flags.add(f)
        self.last_message = self.desc_long()   # <-- was: self.room.desc_long
        return self.last_message

    def move(self, direction: str) -> str:
        ex = self.room.exits.get(direction)
        if not ex:
            self.last_message = "You can't go that way."
            return self.last_message
        if ex.is_locked(self.inventory, self.flags):
            self.last_message = ex.locked_text or "It's stuck. You can't force it."
            return self.last_message
        self.current_room_id = ex.to_room
        self.last_message = self.desc_short()
        return self.last_message

    def do(self, interaction_id: str) -> Tuple[str, bool]:
        it = next((i for i in self.room.interactions if i.id == interaction_id), None)
        if not it or not it.is_visible(self):
            self.last_message = "Nothing happens."
            return self.last_message, False
        msg, dead = it.perform(self)
        self.dead = dead
        if not msg:
            # Default to the room short desc so UI always has feedback
            msg = self.desc_short()
        self.last_message = msg
        return msg, dead

    # ---------- lifecycle ----------
    def restart(self) -> None:
        """Clean restart after death or manual reset."""
        self.current_room_id = self.start_room_id
        self.flags.clear()
        self.inventory.clear()
        self.dead = False
        self.last_message = self.room.desc_short

    # ---------- (de)serialization ----------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_room_id": self.start_room_id,
            "current_room_id": self.current_room_id,
            "flags": sorted(self.flags),
            "inventory": sorted(self.inventory),
            "dead": self.dead,
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.current_room_id = data.get("current_room_id", self.start_room_id)
        self.flags = set(data.get("flags", []))
        self.inventory = set(data.get("inventory", []))
        self.dead = bool(data.get("dead", False))
        # last_message is ephemeral/UI-only; do not restore
    
    def desc_short(self) -> str:
        return self.room.render_desc(self, long=False)

    def desc_long(self) -> str:
        return self.room.render_desc(self, long=True)