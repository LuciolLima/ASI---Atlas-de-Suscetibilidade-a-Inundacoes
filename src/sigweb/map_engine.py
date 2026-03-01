"""
SISTEMA ASI - MOTOR DE RENDERIZAÇÃO
Versão: 2.8 — MarkerCluster, Escala, Hidrografia, Eventos Históricos, Tooltips
"""

import folium
import streamlit as st
import json
import os
import pandas as pd
from folium.plugins import Fullscreen, HeatMap, MarkerCluster
from src.sigweb import config


# ══════════════════════════════════════════════════════════════
#  CACHE DE ARQUIVOS ESTÁTICOS
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def _load_geojson_cache():
    path = config.PATH_GEOJSON
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"GeoJSON: erro ao ler — {e}")
            return None
    st.caption(f"⚠️ GeoJSON não encontrado: `{path}`")
    return None


@st.cache_data(ttl=3600)
def _load_hidrografia_cache():
    path = config.PATH_HIDROGRAFIA
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Hidrografia: erro ao ler — {e}")
            return None
    return None


# ══════════════════════════════════════════════════════════════
#  RENDER PRINCIPAL
# ══════════════════════════════════════════════════════════════

def render_map(df, conf, df_eventos=None):
    """
    Gera o objeto Folium com todas as camadas configuradas.

    Parâmetros
    ----------
    df          : DataFrame principal (TWI)
    conf        : dict de configuração vindo dos components
    df_eventos  : DataFrame de eventos históricos (opcional, v2.8)
    """

    # ── 1. Centro e Zoom ─────────────────────────────────────
    if not df.empty:
        center = [df['latitude'].mean(), df['longitude'].mean()]
        zoom   = 13 if conf.get('selected_bairro', 'Todos') == "Todos" else 15
    else:
        center = [-8.28, -35.03]
        zoom   = 13

    # ── 2. Tileset ───────────────────────────────────────────
    estilo = conf.get('map_style', 'PADRAO')
    if estilo == "DARK":
        tiles_provider = "CartoDB dark_matter"
    elif estilo == "CLARO":
        tiles_provider = "CartoDB positron"
    else:
        tiles_provider = "OpenStreetMap"

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=tiles_provider,
        control_scale=True,   # barra de escala nativa (canto inferior esquerdo)
        prefer_canvas=True
    )

    Fullscreen(position="topright").add_to(m)

    # ── 3. Malha GeoJSON (Bairros) ───────────────────────────
    if conf.get('show_geojson'):
        geo_data = _load_geojson_cache()
        if geo_data:
            feat = geo_data['features'][0]['properties']
            tooltip_field = 'NM_BAIRRO' if 'NM_BAIRRO' in feat else list(feat.keys())[0]

            folium.GeoJson(
                geo_data,
                name="Malha Territorial (Bairros)",
                style_function=lambda x: {
                    'color':       '#ffffff' if estilo == 'DARK' else '#333333',
                    'weight':      1,
                    'fillOpacity': 0.05
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[tooltip_field],
                    aliases=['Bairro:']
                )
            ).add_to(m)

    # ── 4. Hidrografia (v2.8) ────────────────────────────────
    if conf.get('show_hidrografia'):
        hidro_data = _load_hidrografia_cache()
        if hidro_data:
            props = hidro_data['features'][0]['properties'] if hidro_data.get('features') else {}
            tem_nome = 'nome' in props

            folium.GeoJson(
                hidro_data,
                name="Hidrografia (Rios e Córregos)",
                style_function=lambda x: {
                    'color':   config.COLOR_HIDROGRAFIA,
                    'weight':  2,
                    'opacity': 0.85
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['nome'] if tem_nome else [],
                    aliases=["Curso d'água:"] if tem_nome else []
                )
            ).add_to(m)
        else:
            st.caption("ℹ️ Hidrografia: arquivo `hidrografia_cabo.json` não encontrado em `data/raw/arcmap_exports/`.")

    # ── 5. Heatmap ───────────────────────────────────────────
    if conf.get('show_heatmap') and not df.empty:
        df_heat = df[df['Classe_Risco_Cod'].isin(['CRITICO', 'ALTO'])]
        heat_data = [
            [row['latitude'], row['longitude'], 1]
            for _, row in df_heat.iterrows()
        ]
        HeatMap(
            heat_data,
            name="Mancha de Calor (Risco Elevado)",
            radius=15,
            blur=10,
            min_opacity=0.4,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(m)

    # ── 6. Pontos TWI ────────────────────────────────────────
    if conf.get('show_points') and not df.empty:
        limit = config.MAX_POINTS_DISPLAY if conf.get('selected_bairro', 'Todos') == "Todos" else 10000

        if len(df) > limit:
            subset   = df.sort_values('twi', ascending=False).head(limit)
            omitidos = len(df) - limit
            st.toast(
                f"⚠️ Exibindo os {limit} pontos de maior TWI. "
                f"{omitidos} omitidos — aplique filtro de bairro para ver todos.",
                icon="⚠️"
            )
        else:
            subset = df

        usar_cluster = conf.get('use_cluster', False)

        if usar_cluster:
            # ── MarkerCluster (v2.8) ─────────────────────────
            cluster = MarkerCluster(
                name="Amostras TWI (Agrupado)",
                options={
                    'maxClusterRadius':       40,
                    'disableClusteringAtZoom': 16
                }
            )
            for _, row in subset.iterrows():
                classe = str(row['Classe_Risco_Cod'])
                cor    = config.COLORS.get(classe, '#808080')
                folium.CircleMarker(
                    location     = [row['latitude'], row['longitude']],
                    radius       = 5,
                    color        = cor,
                    fill         = True,
                    fill_color   = cor,
                    fill_opacity = 0.85,
                    weight       = 0,
                    tooltip      = (
                        f"TWI: {row.get('twi', 0):.2f} | "
                        f"{classe} | "
                        f"{row.get('NM_BAIRRO', '')}"
                    )
                ).add_to(cluster)
            cluster.add_to(m)

        else:
            # ── Pontos individuais (modo diagnóstico) ─────────
            point_layer = folium.FeatureGroup(name="Amostras TWI (Pontos)", show=True)
            for _, row in subset.iterrows():
                classe = str(row['Classe_Risco_Cod'])
                cor    = config.COLORS.get(classe, '#808080')
                radius = 6 if classe == 'CRITICO' else 4

                folium.CircleMarker(
                    location     = [row['latitude'], row['longitude']],
                    radius       = radius,
                    color        = cor,
                    fill         = True,
                    fill_color   = cor,
                    fill_opacity = 0.8,
                    weight       = 0,
                    popup        = None,
                    tooltip      = (
                        f"TWI: {row.get('twi', 0):.2f} | "
                        f"{config.CLASS_LABELS.get(classe, classe)} | "
                        f"Bairro: {row.get('NM_BAIRRO', 'N/A')}"
                    )
                ).add_to(point_layer)
            point_layer.add_to(m)

    # ── 7. Eventos Históricos de Inundação (v2.8) ────────────
    if conf.get('show_eventos') and df_eventos is not None and not df_eventos.empty:
        eventos_layer = folium.FeatureGroup(name="Eventos Históricos de Inundação", show=True)

        raio_sev = {'GRAVE': 10, 'MODERADA': 7, 'LEVE': 5, 'NÃO INFORMADA': 5}

        for _, ev in df_eventos.iterrows():
            sev = str(ev.get('severidade', 'NÃO INFORMADA')).upper()
            cor = config.COLORS_EVENTOS.get(sev, '#AAAAAA')
            r   = raio_sev.get(sev, 5)

            data_str = (
                ev['data'].strftime('%d/%m/%Y')
                if 'data' in ev and pd.notna(ev['data']) else 'Data não informada'
            )

            popup_html = f"""
            <div style="font-family:sans-serif;min-width:200px;padding:4px;">
                <b style="color:{cor};">⚠ Evento Registrado — {sev}</b><br><br>
                <b>Data:</b> {data_str}<br>
                <b>Bairro:</b> {ev.get('bairro', 'N/A')}<br>
                <b>Descrição:</b> {ev.get('descricao', 'N/A')}<br><br>
                <small style="color:#999;">Fonte: {ev.get('fonte', 'N/A')}</small>
            </div>
            """

            folium.CircleMarker(
                location     = [ev['latitude'], ev['longitude']],
                radius       = r,
                color        = cor,
                fill         = True,
                fill_color   = cor,
                fill_opacity = 0.9,
                weight       = 2,
                popup        = folium.Popup(popup_html, max_width=300),
                tooltip      = f"Inundação {sev} — {data_str} | {ev.get('bairro','')}"
            ).add_to(eventos_layer)

        eventos_layer.add_to(m)

    # ── 8. Controle de Camadas ───────────────────────────────
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    return m