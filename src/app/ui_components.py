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
    panel_id: str = "desc"
    height_px: int = 220
    border_css: str = "1px solid #000"
    padding_px: int = 12
    bg_css: str = "var(--background-color, transparent)"
    font_size: Optional[str] = None
    margin_bottom_px: int = 12

    def render(self, messages: list[Union[PanelMessage, str]]) -> None:
        _ensure_css_once()  # keeps layout styles, but colors come inline now

        panel_style = (
            f"height:{self.height_px}px;"
            f"border:{self.border_css};"
            f"padding:{self.padding_px}px;"
            f"overflow-y:auto;"
            f"background:{self.bg_css};"
            f"box-sizing:border-box;"
            f"margin-bottom:{self.margin_bottom_px}px;"
        )
        if self.font_size:
            panel_style += f"font-size:{self.font_size};"

        # Inline color styles (bulletproof against Streamlit CSS quirks)
        style_map = {
            "body":    "padding:0;border:0;background:transparent;",
            "success": "background:#e6f4ea;border:1px solid #c7e8d0;",
            "info":    "background:#e8f0fe;border:1px solid #c8d3ff;",
            "warning": "background:#fff4e5;border:1px solid #ffe2bd;",
            "error":   "background:#fde8e8;border:1px solid #f8c7c7;",
        }

        blocks_html = []
        for raw in (messages or []):
            m = raw if isinstance(raw, PanelMessage) else PanelMessage(str(raw), "info")
            kind = m.kind if m.kind in style_map else "body"
            block_style = f'margin:0 0 .6rem 0;padding:.6rem .75rem;border-radius:.4rem;{style_map[kind]}'
            if kind == "body":  # no extra padding for body text
                block_style = "margin:0 0 .6rem 0;" + style_map[kind]
            blocks_html.append(f'<div style="{block_style}">{_md_min(m.text)}</div>')

        panel_html = f'<div class="desc-panel" id="panel-{self.panel_id}" style="{panel_style}">' \
                    + "".join(blocks_html) + "</div>"
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

