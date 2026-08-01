"""Python wrapper para componente React AsiMap (Deck.gl + MapLibre).

Integra o componente React buildado via Vite com Streamlit via st.components.v1.html.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import re
from pathlib import Path
import pyarrow as pa
import pyarrow.ipc as ipc


# Diretório do build React (commitado no repo)
COMPONENT_DIR = Path(__file__).parent.parent.parent / "streamlit_components" / "asi_map"


def _read_component_html() -> str:
    """Lê HTML template do build React."""
    html_file = COMPONENT_DIR / "AsiMap.html"
    if not html_file.exists():
        return _fallback_html()
    return html_file.read_text(encoding="utf-8")


def _fallback_html() -> str:
    """HTML de fallback quando build não existe."""
    return """
    <div style="
        width:100%;height:100%;
        display:flex;align-items:center;justify-content:center;
        background:#0d1219;color:#5a7a8a;font-family:monospace;
    ">
      AsiMap component não buildado.<br>
      <code>cd src/sigweb/map && npm run build</code>
    </div>
    """


def _serialize_arrow(df) -> str:
    """Polars DataFrame → Arrow IPC base64."""
    table = pa.Table.from_pandas(df.to_pandas())
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return base64.b64encode(sink.getvalue().to_pybytes()).decode()


def render_deck_gl_map(
    twi_df,                    # Polars DataFrame
    events_df=None,            # Polars DataFrame (opcional)
    conf: dict = None,         # config do sidebar
    highlight_point: dict = None,
    key: str = "asi_deck_gl",
    height: int = 600,
) -> dict:
    """
    Renderiza componente AsiMap React.
    Retorna dict com last_object_clicked, bbox_selected, viewState.
    """
    conf = conf or {}

    # Serializa dados TWI para Arrow IPC base64
    twi_data = _serialize_arrow(twi_df.select([
        "latitude", "longitude", "twi", "Classe_Risco_Cod", "NM_BAIRRO"
    ]))

    # Props para o componente React
    props = {
        "data": twi_data,
        "dataFormat": "arrow",
        "initialViewState": {
            "longitude": conf.get("map_center_lon", -35.03),
            "latitude": conf.get("map_center_lat", -8.28),
            "zoom": conf.get("map_zoom", 13),
            "pitch": conf.get("map_pitch", 0),
            "bearing": conf.get("map_bearing", 0),
        },
        "highlightPoint": highlight_point,
        "layers": {
            "points": conf.get("show_points", True),
            "hexagon": conf.get("show_hexagon", False),
            "heatmap": conf.get("show_heatmap", False),
            "bairros": conf.get("show_geojson", False),
            "hidro": conf.get("show_hidrografia", False),
        },
        "mapStyle": conf.get("map_style", "dark").lower(),
    }

    # Lê template HTML
    html = _read_component_html()

    # Substitui placeholder por props JSON
    html = re.sub(
        r'__ASI_MAP_PROPS__',
        json.dumps(props),
        html
    )

    # Renderiza componente
    result = components.html(html, height=height, scrolling=False)

    # Parse retorno (salvo no session_state pelo postMessage do React)
    return st.session_state.get(f"{key}_result", {
        "last_object_clicked": None,
        "bbox_selected": None,
        "viewState": None,
    })