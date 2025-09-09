import streamlit as st

# added to help visualize the columns
def css_debug():
    st.markdown("""
    <style>
        :root{
        --panel-h: 320px;   /* ← one place to control total panel height */
        --cell: 64px;      /* size of each compass cell */
        --pad-gap: 2px;    /* spacing between cells */
        }
                
      .demo-box{
        height: var(--panel-h);         
        box-sizing: border-box;
        border: 2px solid #111;        /* clear divider */
        background: #fafafa;           /* base background */
        display: flex; align-items: center; justify-content: center;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
        font-weight: 700;
      }
      .demo-left  { 
                background:#e3f2fd; 
                }  /* light blue */
      .demo-main  { 
                background:#fff3e0;
                border-left: 6px solid #000;  /* thick black separator */
                 }  /* light orange */
      .demo-right { 
                background:#e8f5e9; 
                }  /* light green */

    /* Column 2: a vertical stack = header (fixed) + body (fills the rest) */    
    .main-panel {
    display: flex;
    flex-direction: column;            
    /* set a demo height so you can see the split clearly;
    tweak this up/down as you like, or remove for natural height */
    height: var(--panel-h);
    box-sizing: border-box;
    }

    /* Header bar */   
    .main-header {
    background: #c0c0c0;   /* light gray bar */
    color: #000;
    padding: 8px 12px;
    border: 2px solid #111;
    border-bottom:0;         /* merges with body border to look like one frame */
    display: flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
    font-weight: 700;
    font-family: ui-monospace, Menlo, Consolas, "Courier New", monospace;
    }
    .main-header .title{ font-weight:700; }
    .main-header .meta { opacity:0.9; }
                
    /* 3-part layout across the bar */
    .page-status .row{
    display:flex;
    align-items:center;
    justify-content:space-between;  /* left | center | right */
    gap:12px;
    }
    .page-status .left,
    .page-status .center{
    font-weight:700;
    }       
                
    /* Pad Area: compass grid */
    .pad-panel{
    height: var(--panel-h);
    box-sizing: border-box;
    border: 2px solid #111;
    background: #000; color: #fff;
    padding: 6px;
    display: flex; align-items: center; justify-content: center;
    }

:root{
  --left-side-pad: 12px;
  --left-bottom-gap: 12px;   /* small gap between buttons and the mid divider */
}

/* Whole left column frame */
.left-panel{
  height: var(--panel-h);
  border: 2px solid #111;
  background:#000;
  box-sizing: border-box;
  display:flex;
  flex-direction: column;    /* stack two rows */
}

/* Two halves */
.left-top, .left-bottom{
  flex: 1 1 50%;             /* 50/50 split; change ratios below if desired */
  display:flex;              /* so we can position content inside each half */
}

/* Put the grid at the BOTTOM of the top half, centered horizontally */
.left-top{
  align-items: flex-end;      /* vertical bottom (cross axis) */
  justify-content: center;    /* horizontal center (main axis) */
  /*padding: 0 var(--left-side-pad) var(--left-bottom-gap);*/
}

/* Placeholder for the second half (centered for now) */
.left-bottom{
  align-items: center;
  justify-content: center;
  padding: var(--left-side-pad);
  color:#bbb;
  font-family: ui-monospace, Menlo, Consolas, "Courier New", monospace;
}
                
/* 2×2 grid */
.util-grid{
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 5px; /*var(--util-gap); */            /* <-- gap between tiles */
  width: 100%;
  max-width: 340px;                 /* keeps buttons away from the panel edge on wide screens */
  box-sizing: border-box;
  margin: 0 auto;                   /* keep grid centered */
}

/* tiles */
.util-btn{
    display: flex; align-items: center; justify-content: center;
    text-align: center;
    line-height: 1;
  width: 100%;
  height: 52px;
  background: #000;
  color: #fff;
  border: 2px solid #fff;
  border-radius: 4px;
  font-family: ui-monospace, Menlo, Consolas, "Courier New", monospace;
  font-weight: 700;
  letter-spacing: .5px;
  text-decoration: none;
  user-select: none;
}
.util-btn:hover{ background:#111; }

                         
    /*-------------------*/    
    /* Main content area */ 
    /*-------------------*/    
    .main-body {
    flex: 1;                /* take the remaining height */
    overflow:auto;
    background: #fffdf7;    /* subtle off-white so you can see the region */
    border: 2px solid #111; /* matches header sides/bottom */
    padding: 12px;
    display: flex; align-items: center; justify-content: center; 
    font-family: ui-monospace, Menlo, Consolas, "Courier New", monospace;
    }
                
    /* Center the whole app and limit its width */
    .main .block-container{
    max-width: 1200px; 
    margin: 8px auto 0;  /* center horizontally */
    }
    /*.main-header { outline: 3px dashed #c33; } */  /* temporary debug */
    /* .main-body   { outline: 3px dashed #39c; } */ /* temporary debug */

    /* Page header bar */
    .page-status{
    background:#cfcfcf;      /* light gray */
    color:#000;
    border:2px solid #111;
    padding:6px 10px;
    margin-bottom:10px;      /* space below the bar */
    font-family: ui-monospace, Menlo, Consolas, "Courier New", monospace;
    }       

/* === Right column compass panel (anchor-based, robust) ===
   Target: the 3rd column in the columns row that follows #row-anchor. */

/* Make the entire right column look like the black framed panel */
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3) {
  border: 2px solid #111;
  background: #000;
  color: #fff;
  padding: 6px;
  box-sizing: border-box;
}

/* Stretch the right column’s inner vertical block to fixed height and center contents */
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3)
  > div {
  height: var(--panel-h);
  display: flex;
  align-items: center;     /* center the 3×3 cluster vertically */
  justify-content: center; /* and horizontally */
}

/* Gaps between the three columns in each row, and space between rows */
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3)
  [data-testid="stHorizontalBlock"]{
  gap: var(--pad-gap) !important;   /* horizontal gap inside the 3×3 */
  margin: 0 0 var(--pad-gap) 0;     /* vertical gap between the three rows */
}

/* Make Streamlit buttons look like tiles (override Emotion with !important) */
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3)
  .stButton > button{
  width: 100% !important;
  height: var(--cell) !important;
  background: #fff !important;
  color: #000 !important;
  border: 2px solid #fff !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  font-weight: 700 !important;
  letter-spacing: .5px !important;
}
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3)
  .stButton > button:hover{
  background: #f7f7f7 !important;
}

/* Corner placeholders (top-left, top-right, bottom-left, bottom-right) */
#row-anchor ~ div[data-testid="stHorizontalBlock"]
  > div[data-testid="column"]:nth-of-type(3)
  .pad-spacer{
  height: var(--cell);
  border: 2px dashed #888;
  background: #eee;
  box-sizing: border-box;
}

    </style>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="UI Workshop", layout="wide")
css_debug()

st.title("UI Workshop — Step 1: Three Columns")

st.markdown("""
<div class="page-status">
  <div class="row">
    <div class="left">Location</div>
    <div class="center">Your Game</div>
    <div class="right">Moves: 0</div>
  </div>
</div>
""", unsafe_allow_html=True)

# This is where columns are defined
st.markdown('<div id="row-anchor"></div>', unsafe_allow_html=True)

# 3 columns: Left sidebar (1), Primary (2), Secondary (1)
col_left, col_main, col_right = st.columns([1, 2, 1], gap="small")

with col_left:
    st.markdown(
        '''
<div class="left-panel">
  <div class="left-top">
    <div class="util-grid">
      <div class="util-btn">Inventory</div>
      <div class="util-btn">Journal</div>
      <div class="util-btn">Log</div>
      <div class="util-btn">Settings</div>
    </div>
  </div>
  <div class="left-bottom">
    <!-- second row content goes here later -->
    (empty)
  </div>
</div>
        ''',
        unsafe_allow_html=True
    )


with col_main:
    st.markdown("""
      <div class="main-panel">
        <div class="main-header">
          <span class="title">Primary Screen</span>
          <span class="meta">Moves: 0</span>
        </div>
        <div class="main-body">
          (Main content area)
        </div>
      </div>
    """, unsafe_allow_html=True)

with col_right:
    # Anchor that our CSS will use to find the *next* container
    st.markdown('<div id="compass-scope"></div>', unsafe_allow_html=True)

    # This container will become the black panel via CSS
    with st.container():
        # Row 1:  _   N   _
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: st.markdown('<div class="pad-spacer"></div>', unsafe_allow_html=True)
        with r1c2: st.button("N", key="btnN")
        with r1c3: st.markdown('<div class="pad-spacer"></div>', unsafe_allow_html=True)

        # Row 2:  W  Look  E
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: st.button("W", key="btnW")
        with r2c2: st.button("Look", key="btnLook")
        with r2c3: st.button("E", key="btnE")

        # Row 3:  _   S   _
        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1: st.markdown('<div class="pad-spacer"></div>', unsafe_allow_html=True)
        with r3c2: st.button("S", key="btnS")
        with r3c3: st.markdown('<div class="pad-spacer"></div>', unsafe_allow_html=True)



