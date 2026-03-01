"""
SISTEMA ASI - APP PRINCIPAL
Versão: 2.8 — Precipitação, Eventos Históricos, Ranking por Bairro,
              MarkerCluster, Escala, Exportação CSV
"""

import streamlit as st
from streamlit_folium import st_folium
from geopy.distance import geodesic
import plotly.express as px
import pandas as pd

from src.sigweb import config, components, map_engine, report_generator, documentation
from src.processing import data_loader
from src.analysis import analytics

st.set_page_config(
    page_title=config.PAGE_TITLE,
    layout=config.PAGE_LAYOUT,
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
        .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("ASI | Atlas de Suscetibilidade a Inundações")
    st.markdown(
        "*O Sistema de Informação Geográfica (SIGWeb) ASI utiliza o Topographic Wetness Index (TWI) "
        "para modelar a propensão natural do terreno ao acúmulo hídrico, correlacionando dados "
        "altimétricos e áreas de contribuição de fluxo para identificação de zonas críticas.*"
    )

    # ── CARREGAMENTO DE DADOS ─────────────────────────────────
    df_raw          = data_loader.load_geospatial_dataset()
    df_precipitacao = data_loader.load_precipitacao()
    df_eventos_raw  = data_loader.load_eventos_inundacao()
    df_defesa_civil = data_loader.load_defesa_civil()        # v2.8 — consolidado

    if df_raw.empty:
        st.warning("Base de dados geoespaciais indisponível.")
        return

    # ── NAVEGAÇÃO / CONFIGURAÇÃO ──────────────────────────────
    conf = components.render_top_navigation(df_raw)

    # ── PIPELINE DE FILTRAGEM ─────────────────────────────────
    limit_twi     = conf.get('twi_threshold', 0.0)
    df_map        = df_raw[df_raw['twi'] >= limit_twi].copy()
    target_bairro = conf.get('selected_bairro', 'Todos')

    if target_bairro != "Todos":
        if 'NM_BAIRRO' in df_map.columns:
            df_map = df_map[df_map['NM_BAIRRO'] == target_bairro]
        elif 'LAYER' in df_map.columns:
            df_map = df_map[df_map['LAYER'] == target_bairro]

    if limit_twi > 0 or target_bairro != "Todos":
        st.caption(
            f"Amostragem ativa: {len(df_map)} vetores processados "
            f"(Unidade: {target_bairro} | TWI >= {limit_twi:.2f})"
        )

    # ── FILTRO DE EVENTOS POR PERÍODO (v2.8) ─────────────────
    df_eventos = df_eventos_raw.copy() if not df_eventos_raw.empty else pd.DataFrame()
    if not df_eventos.empty and conf.get('show_eventos') and 'data' in df_eventos.columns:
        ano_ini = conf.get('ano_inicio', 2000)
        ano_fim = conf.get('ano_fim',    2030)
        df_eventos = df_eventos[
            df_eventos['data'].dt.year.between(ano_ini, ano_fim)
        ]

    if conf.get('block_ui') or conf.get('map_style') in ["NONE", "ERROR"]:
        st.info("Selecione um modelo de base cartográfica no menu superior para iniciar a renderização espacial.")
        return

    # ── EXPORTAÇÃO CSV (v2.8) ─────────────────────────────────
    if conf.get('export_csv'):
        csv_bytes = df_map.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
        st.download_button(
            label="💾 Clique para baixar o CSV filtrado",
            data=csv_bytes,
            file_name=f"ASI_export_{target_bairro}_TWI{limit_twi:.1f}.csv",
            mime="text/csv"
        )

    # ── SESSÃO 1: MAPA ────────────────────────────────────────
    m = map_engine.render_map(
        df_map,
        conf,
        df_eventos=df_eventos if conf.get('show_eventos') else None
    )

    output = st_folium(
        m,
        height=600,
        use_container_width=True,
        returned_objects=["last_object_clicked"]
    )

    # ── SESSÃO 2: DIAGNÓSTICO DE PONTO E BUFFER ───────────────
    clicked          = output.get("last_object_clicked")
    active_twi_class = None

    cluster_on = conf.get('use_cluster', False)

    if conf.get('inspect_mode') and clicked and not cluster_on:
        st.markdown("---")
        lat, lon     = clicked['lat'], clicked['lng']
        center_point = (lat, lon)

        mask = (
            (abs(df_map['latitude']  - lat) < 0.00001) &
            (abs(df_map['longitude'] - lon) < 0.00001)
        )
        foco = df_map[mask]

        if not foco.empty:
            col_diag, col_buffer = st.columns([1.5, 1])

            with col_diag:
                st.subheader("Diagnóstico Vetorial Selecionado")
                st.markdown(
                    report_generator.generate_technical_report(foco.iloc[0]),
                    unsafe_allow_html=True
                )
                active_twi_class = str(foco.iloc[0]['Classe_Risco_Cod'])

                if conf.get('tech_mode'):
                    st.info(
                        f"**Nota Geomorfométrica:** A amostra apresenta TWI de "
                        f"{foco.iloc[0]['twi']:.2f}, em área classificada como "
                        f"{foco.iloc[0].get('Uso_Solo_Desc', 'não especificada')}. "
                        "Indica tendência de convergência de fluxo superficial."
                    )

            with col_buffer:
                st.subheader("Análise de Adjacência (Raio 500m)")

                df_nearby = df_map[
                    df_map['latitude'].between(lat - 0.005, lat + 0.005) &
                    df_map['longitude'].between(lon - 0.005, lon + 0.005)
                ].copy()

                df_nearby['distancia'] = df_nearby.apply(
                    lambda r: geodesic(center_point, (r['latitude'], r['longitude'])).meters,
                    axis=1
                )
                df_radius = df_nearby[df_nearby['distancia'] <= 500]
                total_pontos   = len(df_radius)
                criticos_altos = len(df_radius[df_radius['Classe_Risco_Cod'].isin(['CRITICO', 'ALTO'])])
                seguros        = total_pontos - criticos_altos

                st.metric("Pontos no Raio (500m)", total_pontos)
                st.metric(
                    "Focos Críticos/Altos", criticos_altos,
                    delta="Risco" if criticos_altos > 0 else "Estável",
                    delta_color="inverse" if criticos_altos > 0 else "normal"
                )

                if criticos_altos == 0:
                    st.success("Zona Estável: Nenhum ponto de risco elevado detectado no entorno.")
                elif 1 <= criticos_altos <= 5:
                    st.warning(f"Atenção: {criticos_altos} foco(s) de risco indicam possibilidade de saturação localizada.")
                else:
                    st.error(f"Alerta Máximo: {criticos_altos} pontos de alto risco sugerem perigo de transbordamento em cadeia.")

                if total_pontos > 0:
                    df_pie = pd.DataFrame({
                        'Status':     ['Risco (Crítico/Alto)', 'Seguro (Moderado/Baixo)'],
                        'Quantidade': [criticos_altos, seguros]
                    })
                    fig = px.pie(
                        df_pie, values='Quantidade', names='Status', hole=0.5,
                        color='Status',
                        color_discrete_map={
                            'Risco (Crítico/Alto)':      '#FF4500',
                            'Seguro (Moderado/Baixo)':   '#1E90FF'
                        }
                    )
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=200, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # v2.8 — Eventos históricos próximos ao ponto clicado
                if not df_eventos.empty and 'latitude' in df_eventos.columns:
                    ev_prox = df_eventos[
                        df_eventos['latitude'].between(lat - 0.005, lat + 0.005) &
                        df_eventos['longitude'].between(lon - 0.005, lon + 0.005)
                    ]
                    if not ev_prox.empty:
                        st.markdown("---")
                        st.markdown(f"**📍 {len(ev_prox)} evento(s) histórico(s) registrado(s) nesta proximidade:**")
                        for _, ev in ev_prox.iterrows():
                            sev = str(ev.get('severidade', 'N/A'))
                            cor = config.COLORS_EVENTOS.get(sev, '#AAAAAA')
                            data_str = (
                                ev['data'].strftime('%d/%m/%Y')
                                if 'data' in ev and pd.notna(ev['data']) else '—'
                            )
                            st.markdown(
                                f"<span style='color:{cor}; font-weight:bold;'>⚠ {sev}</span> "
                                f"— {data_str} | {ev.get('bairro','N/A')} "
                                f"| {ev.get('descricao','—')}",
                                unsafe_allow_html=True
                            )

        else:
            st.caption("Amostra vetorial não localizada nos parâmetros atuais.")

    # ── LEGENDA ───────────────────────────────────────────────
    components.render_twi_legend(active_class=active_twi_class)

    # ── SESSÃO 3: ANALYTICS ───────────────────────────────────
    if conf.get('analytics_mode'):
        st.markdown("---")
        analytics.render_advanced_dashboard(df_map, conf, df_precipitacao=df_precipitacao)

    # ── SESSÃO 3b: PRECIPITAÇÃO (v2.8) ────────────────────────
    if conf.get('analytics_mode') and not df_precipitacao.empty:
        st.markdown("---")
        analytics.render_precipitacao_dashboard(df_precipitacao, conf)

    # ── SESSÃO 3c: DEFESA CIVIL (v2.8) ────────────────────────
    if conf.get('analytics_mode') and not df_defesa_civil.empty:
        st.markdown("---")
        analytics.render_defesa_civil_dashboard(df_defesa_civil, conf)

    # ── SESSÃO 3d: RANKING POR BAIRRO (v2.8) ─────────────────
    if conf.get('ranking_mode'):
        st.markdown("---")
        df_ranking = data_loader.calcular_indice_risco_bairro(df_map)
        analytics.render_ranking_bairros(df_ranking, conf)

    # ── SESSÃO 4: DOCUMENTAÇÃO ────────────────────────────────
    documentation.render_technical_docs()


if __name__ == "__main__":
    main()