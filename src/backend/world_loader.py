
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import yaml

DIRS = ["north","east","south","west","up","down"]

@dataclass
class Location:
    id: str
    title: str
    exits: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    items: List[dict] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    lore_refs: List[str] = field(default_factory=list)

@dataclass
class World:
    locations: Dict[str, Location]
    edges: List[dict]

    @classmethod
    def from_files(cls, loc_path: Path, edge_path: Path, npcs_path: Optional[Path]=None, items_path: Optional[Path]=None):
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
        with open(edge_path, "r", encoding="utf-8") as f:
            edges = yaml.safe_load(f) or []
        return cls(locations=locations, edges=edges)

    def neighbor(self, loc_id: str, direction: str) -> Optional[str]:
        loc = self.locations.get(loc_id)
        if not loc:
            return None
        return loc.exits.get(direction)

    def title(self, loc_id: str) -> str:
        return self.locations.get(loc_id, Location(id=loc_id, title=loc_id)).title
