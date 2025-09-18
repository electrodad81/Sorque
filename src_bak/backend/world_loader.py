"""
World loader for Sorque.

This module defines data structures for the game world and a helper to
load authored data from YAML files. In addition to the original
location and edge handling, this version also supports loading NPC and
item definitions. These definitions are stored on the ``World``
instance so that other parts of the game (the UI and action router)
can look up human‑readable names and metadata when presenting
interactive options or resolving actions.

The ``Location`` dataclass mirrors the structure of the YAML
``locations.yaml`` file. Each location lists its exits by direction,
any tags for filtering/behaviour, a list of items (by id with
additional flags such as ``hidden``), and a list of NPC ids that are
currently present.

The optional ``npc_defs`` and ``item_defs`` dictionaries hold
authoritative definitions for NPCs and items keyed by id. See
``world/npcs.yaml`` and ``world/items.yaml`` for examples.

Adding new keys to these definitions is non‑breaking: unknown keys
will simply be stored as part of the resulting dictionary. Consumers
should treat these structures as opaque metadata bundles.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

# A canonical ordering of movement directions. The UI uses this to
# determine which compass buttons to enable/disable.
DIRS = ["north", "east", "south", "west", "up", "down"]


@dataclass
class Location:
    """Represents a single node in the world graph."""

    id: str
    title: str
    exits: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    items: List[Any] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    lore_refs: List[str] = field(default_factory=list)


@dataclass
class World:
    """Holds the entire authored world including locations, edges, and definitions."""

    locations: Dict[str, Location]
    edges: List[dict]
    npc_defs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    item_defs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_files(
        cls,
        loc_path: Path,
        edge_path: Path,
        npcs_path: Optional[Path] = None,
        items_path: Optional[Path] = None,
    ) -> "World":
        """Load locations, edges, NPCs and items from YAML files.

        ``loc_path`` and ``edge_path`` are required. ``npcs_path`` and
        ``items_path`` are optional; if provided they will be loaded
        into ``npc_defs`` and ``item_defs`` respectively.
        """
        # Load locations
        with open(loc_path, "r", encoding="utf-8") as f:
            locs_raw = yaml.safe_load(f) or []
        locations: Dict[str, Location] = {}
        for l in locs_raw:
            locations[l["id"]] = Location(
                id=l["id"],
                title=l.get("title", l["id"]),
                exits=l.get("exits", {}),
                tags=l.get("tags", []),
                items=l.get("items", []),
                npcs=l.get("npcs", []),
                lore_refs=l.get("lore_refs", []),
            )

        # Load directed edges. These are kept separate to allow for
        # traversability rules (e.g. locking) in the future.
        with open(edge_path, "r", encoding="utf-8") as f:
            edges = yaml.safe_load(f) or []

        # Load NPC definitions
        npc_defs: Dict[str, Dict[str, Any]] = {}
        if npcs_path and Path(npcs_path).exists():
            with open(npcs_path, "r", encoding="utf-8") as f:
                npcs_raw = yaml.safe_load(f) or []
            for n in npcs_raw:
                if not isinstance(n, dict) or "id" not in n:
                    continue
                # Copy all fields verbatim so that arbitrary keys are preserved
                npc_defs[n["id"]] = dict(n)

        # Load item definitions
        item_defs: Dict[str, Dict[str, Any]] = {}
        if items_path and Path(items_path).exists():
            with open(items_path, "r", encoding="utf-8") as f:
                items_raw = yaml.safe_load(f) or []
            for i in items_raw:
                if not isinstance(i, dict) or "id" not in i:
                    continue
                item_defs[i["id"]] = dict(i)

        return cls(locations=locations, edges=edges, npc_defs=npc_defs, item_defs=item_defs)

    def neighbor(self, loc_id: str, direction: str) -> Optional[str]:
        """Return the location id in the given direction, if any."""
        loc = self.locations.get(loc_id)
        if not loc:
            return None
        return loc.exits.get(direction)

    def title(self, loc_id: str) -> str:
        """Return the human‑readable title for a location id."""
        return self.locations.get(loc_id, Location(id=loc_id, title=loc_id)).title

    def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Lookup an NPC definition by id."""
        return self.npc_defs.get(npc_id)

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Lookup an item definition by id."""
        return self.item_defs.get(item_id)