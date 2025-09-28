from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal, Union
import html, re
import streamlit as st

Kind = Literal["body", "success", "info", "warning", "error"]

@dataclass
class PanelMessage:
    text: str
    kind: Kind = "body"
    id: Optional[str] = None

def _md_min(s: str) -> str:
    """Very small Markdown -> HTML: bold/italic + line breaks. Escapes HTML first."""
    s = html.escape(s)               # escape any raw HTML
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)  # **bold**
    s = re.sub(r"__(.+?)__", r"<strong>\1</strong>", s)      # __bold__
    s = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"<em>\1</em>", s) # *italic*
    s = re.sub(r"_(.+?)_", r"<em>\1</em>", s)                # _italic_
    s = s.replace("\n", "<br/>")
    return s

@dataclass
class DescriptionPanel:
    """Fixed-size panel that renders a stack of messages with colored backgrounds."""
    fade_span: int = 16          # number of newest blocks that fade from 1.0 → fade_min_opacity
    fade_min_opacity: float = 0.05
    panel_id: str = "desc"
    height_px: int = 220
    border_css: str = "1px solid #333"            # darker border
    padding_px: int = 24
    bg_css: str = "#111"                          # DARK background
    font_size: Optional[int] = 50
    margin_bottom_px: int = 16
    text_color: str = "#f5f5f5"                   # LIGHT body text

    def render(self, messages: list[Union[PanelMessage, str]]) -> None:
        _ensure_css_once()  # layout styles; colors are inline below

        panel_style = (
            f"height:{self.height_px}px;"
            f"border:{self.border_css};"
            f"padding:{self.padding_px}px;"
            f"overflow-y:auto;"
            f"background:{self.bg_css};"
            f"box-sizing:border-box;"
            f"margin-bottom:{self.margin_bottom_px}px;"
            f"color:{self.text_color};"
        )
        if self.font_size:
            panel_style += f"font-size:{self.font_size};"

        # Inline color styles (block chrome). Text color is inherited from panel unless overridden.
        #style_map = {
        #    "body":    "padding:0;border:0;background:transparent;color:inherit;",
        #    "success": "background:#e6f4ea;border:1px solid #c7e8d0;color:#111;",
        #    "info":    "background:#e8f0fe;border:1px solid #c8d3ff;color:#111;",
        #    "warning": "background:#fff4e5;border:1px solid #ffe2bd;color:#111;",
        #    "error":   "background:#fde8e8;border:1px solid #f8c7c7;color:#111;",
        #}

        style_map = {
            "body":    "padding:0;border:0;background:transparent;color:inherit;",
            "success": "background:#111;border:0px solid #15FF00;color:#15FF00;",
            "info":    "background:#111;border:0px solid #00FFEA;color:#00FFEA;",
            "warning": "background:#111;border:0px solid #FF0015;color:#FF0015;",
            "error":   "background:#111;border:0px solid #EE4B2B;color:#EE4B2B;",
        }

        # Newest-first: reverse the list so latest message renders at the top
        data = list(messages or [])
        data.reverse()

        # Compute per-block opacity: newest = 1.0, then linearly down to fade_min_opacity over fade_span items
        blocks_html: list[str] = []
        span = max(1, int(self.fade_span))
        min_op = max(0.0, min(1.0, float(self.fade_min_opacity)))

        for idx, raw in enumerate(data):
            m = raw if isinstance(raw, PanelMessage) else PanelMessage(str(raw), "info")
            kind = m.kind if m.kind in style_map else "body"

            # opacity factor by age
            t = min(idx / span, 1.0)                # 0 .. 1 across the span
            opacity = (1.0 - t) * (1.0 - min_op) + min_op  # lerp to min opacity

            block_style = (
                "margin:0 0 .6rem 0;"
                "padding:.6rem .75rem;"
                "border-radius:.4rem;"
                f"{style_map[kind]}"
                f"opacity:{opacity};"
            )
            if kind == "body":  # no extra padding for room prose
                block_style = "margin:0 0 .6rem 0;" + style_map[kind] + f"opacity:{opacity};"

            blocks_html.append(f'<div style="{block_style}">{_md_min(m.text)}</div>')

        panel_id = f"panel-{self.panel_id}"
        panel_html = (
            f'<div class="desc-panel" id="{panel_id}" style="{panel_style}">'
            + "".join(blocks_html)
            + "</div>"
        )
        st.markdown(panel_html, unsafe_allow_html=True)

@dataclass
class InventoryPanel:
    panel_id: str = "inv"
    height_px: int = 220
    border_css: str = "1px solid #000"
    padding_px: int = 12
    bg_css: str = "var(--background-color, transparent)"

    def render(self, items: List[str]) -> None:
        # inline styles (bulletproof across themes/containers)
        box = (
            f"height:{self.height_px}px;"
            f"border:{self.border_css};"
            f"padding:{self.padding_px}px;"
            f"overflow-y:auto;"
            f"background:{self.bg_css};"
            f"box-sizing:border-box;"
        )
        if not items:
            html = f'<div style="{box}"><em>Inventory is empty.</em></div>'
        else:
            lis = "".join(f"<li>{_md_min(i)}</li>" for i in items)
            html = f'<div style="{box}"><ul style="margin:0 0 0 1.1rem;">{lis}</ul></div>'
        st.markdown(html, unsafe_allow_html=True)

def _ensure_css_once():
    # bump the key to force a one-time refresh of styles
    if st.session_state.get("_ui_desc_panel_css_v2"):
        return
    st.session_state["_ui_desc_panel_css_v2"] = True
    st.markdown(
        """
        <style>
            .desc-panel { line-height: 1.35; }
            .desc-panel .msg { margin: 0 0 .6rem 0; padding: .6rem .75rem; border-radius: .4rem; }
            .desc-panel .msg-body { padding: 0; border-radius: 0; background: transparent; border: 0; }
            .desc-panel .msg-success { background: #e6f4ea !important; border: 1px solid #c7e8d0 !important; }
            .desc-panel .msg-info    { background: #e8f0fe !important; border: 1px solid #c8d3ff !important; }
            .desc-panel .msg-warning { background: #fff4e5 !important; border: 1px solid #ffe2bd !important; }
            .desc-panel .msg-error   { background: #fde8e8 !important; border: 1px solid #f8c7c7 !important; }
            .desc-panel p { margin: 0 0 .6rem 0; }
            .desc-panel strong, .desc-panel b { font-weight: 600; }
            .desc-panel em, .desc-panel i { font-style: italic; }
        </style>
        """,
        unsafe_allow_html=True,
    )

