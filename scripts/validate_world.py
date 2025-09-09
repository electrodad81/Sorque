
"""Basic world validation script (skeleton).

Run:
    python scripts/validate_world.py
"""
from pathlib import Path
import sys
import yaml

BASE = Path(__file__).resolve().parents[1]

def main() -> int:
    locs = yaml.safe_load((BASE / "world" / "graph" / "locations.yaml").read_text(encoding="utf-8")) or []
    edges = yaml.safe_load((BASE / "world" / "graph" / "edges.yaml").read_text(encoding="utf-8")) or []
    ids = {l["id"] for l in locs}
    ok = True

    for e in edges:
        if e["from"] not in ids:
            print(f"[ERR] edge.from '{e['from']}' not found")
            ok = False
        if e["to"] not in ids:
            print(f"[ERR] edge.to '{e['to']}' not found")
            ok = False
        if e.get("dir") not in {"north","south","east","west","up","down"}:
            print(f"[ERR] invalid dir '{e.get('dir')}' in edge {e}")
            ok = False

    # Check that exits in locations match edges (soft check)
    for l in locs:
        for d, to in (l.get("exits") or {}).items():
            if not any(e for e in edges if e["from"] == l["id"] and e["to"] == to and e["dir"] == d):
                print(f"[WARN] location {l['id']} exit '{d}' -> '{to}' has no matching edge")
    print("Validation complete.", "OK" if ok else "FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
