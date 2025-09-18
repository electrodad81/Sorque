
# --- Path shim so 'from src....' works when running 'streamlit run src/app/app.py'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from pathlib import Path
from src.backend.world_loader import World

BASE_DIR = Path(__file__).resolve().parents[3]

@st.cache_resource
def load_world():
    return World.from_files(
        BASE_DIR / "world" / "graph" / "locations.yaml",
        BASE_DIR / "world" / "graph" / "edges.yaml",
        BASE_DIR / "world" / "npcs.yaml",
        BASE_DIR / "world" / "items.yaml",
    )

st.set_page_config(page_title="Map — Sorque", page_icon="🗺️", layout="wide")
world = load_world()

st.title("World Map (Adjacency)")
rows = []
for loc in world.locations.values():
    for d, to in (loc.exits or {}).items():
        rows.append({"from": loc.id, "dir": d, "to": to})
df = pd.DataFrame(rows, columns=["from","dir","to"])
st.dataframe(df, use_container_width=True)
st.caption("Simple adjacency view. A visual map can be added later.")
