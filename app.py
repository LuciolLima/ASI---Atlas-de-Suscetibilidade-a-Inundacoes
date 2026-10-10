"""SISTEMA ASI - APP PRINCIPAL
Versão: 3.1 — Core Geoespacial (TWI, Mapas, Analytics, Relatórios)
"""

import os
import zipfile

import gdown
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium

from scripts.verify_checksums import verificar_checksums
from src.analysis import analytics
from src.api import (
    fetch_nasa_power_pe_cached,
    fetch_precipitacao_pe_cached,
    fetch_precipitacao_forecast_cached,
    fetch_sidra_consolidado_cached,
    fetch_multi_estacoes_pe_cached,
)
from src.api.charts import render_api_hub_dashboard
from src.core.error_boundary import (
    analytics_error_boundary,
    map_error_boundary,
    report_error_boundary,
)
from src.processing import data_loader
from src.sigweb import components, config, documentation, map_engine, report_generator


@st.cache_resource
def carregar_dados_do_drive():
    """Baixa e extrai dados geoespaciais do GitHub Releases (confiavel, sem auth)."""
    pasta_data = "data"

    if os.path.exists(pasta_data):
        # Verifica integridade dos dados existentes
        if not verificar_checksums():
            st.error("**Falha na verificacao de integridade dos dados**")
            st.error("Os arquivos de dados foram modificados ou corrompidos. Reinicie a aplicacao para re-baixar.")
            st.stop()
        return  # Ja existe e valido, usa cache

    with st.spinner("Baixando dados geoespaciais pre-processados do ASI..."):
        # URL direta do GitHub Releases — CDN global, sem auth, sem limite
        url = "https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes/releases/download/v3.1/data_V3.0-System.zip"

        arquivo_saida = "data_V3.0-System.zip"

        try:
            gdown.download(url, arquivo_saida, quiet=False)

            # Verifica se baixou algo válido
            if not (os.path.exists(arquivo_saida) and os.path.getsize(arquivo_saida) > 1000):
                raise Exception("Arquivo baixado vazio ou inválido")

        except Exception as e:
            st.error(f"""
            **Falha ao baixar dados do GitHub Releases**

            **Erro:** {e}

            **Verifique:**
            1. O release `v3.1` existe e está publicado (não draft)
            2. O asset `data_V3.0-System.zip` está anexado ao release
            3. A URL está correta: {url}
            """)
            st.stop()

        # Descompacta
        try:
            with zipfile.ZipFile(arquivo_saida, 'r') as zip_ref:
                zip_ref.extractall(".")
        except zipfile.BadZipFile:
            st.error("Arquivo ZIP corrompido ou inválido")
            st.stop()
        finally:
            if os.path.exists(arquivo_saida):
                os.remove(arquivo_saida)


# Executa o download e extração dos dados geoespaciais pré-processados do ASI
carregar_dados_do_drive()

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


# Health check endpoint para CI/monitoramento
if st.query_params.get("_health", "") == "1":
    st.json({
        "status": "healthy",
        "version": "3.1",
        "data_loaded": os.path.exists("data")
    })
    st.stop()


def main():
    st.title("ASI | Atlas de Suscetibilidade a Inundações")
    st.markdown(
        "*O Sistema de Informação Geográfica (SIGWeb) ASI utiliza o Topographic Wetness Index (TWI) "
        "para modelar a propensão natural do terreno ao acúmulo hídrico, correlacionando dados "
        "altimétricos e áreas de contribuição de fluxo para identificação de zonas críticas.*"
    )

    # ── CARREGAMENTO DE DADOS ─────────────────────────────────
    df_raw = data_loader.load_geospatial_dataset()
    df_precipitacao = data_loader.load_precipitacao()
    df_eventos_raw = data_loader.load_eventos_inundacao()
    df_defesa_civil = data_loader.load_defesa_civil()

    if df_raw.empty:
        st.warning("Base de dados geoespaciais indisponível.")
        return

    # ── NAVEGAÇÃO / CONFIGURAÇÃO ──────────────────────────────
    conf = components.render_top_navigation(df_raw)
    conf.update(components.render_sidebar())

    # ── PIPELINE DE FILTRAGEM ─────────────────────────────────
    limit_twi = conf.get('twi_threshold', 0.0)
    df_map = df_raw[df_raw['twi'] >= limit_twi].copy()
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

    # ── FILTRO DE EVENTOS POR PERÍODO ─────────────────────────
    df_eventos = df_eventos_raw.copy() if not df_eventos_raw.empty else pd.DataFrame()
    if not df_eventos.empty and conf.get('show_eventos') and 'data' in df_eventos.columns:
        ano_ini = conf.get('ano_inicio', 2000)
        ano_fim = conf.get('ano_fim', 2030)
        df_eventos = df_eventos[
            df_eventos['data'].dt.year.between(ano_ini, ano_fim)
        ]

    if conf.get('block_ui') or conf.get('map_style') in ["NONE", "ERROR"]:
        st.info("Selecione um modelo de base cartográfica no menu superior para iniciar a renderização espacial.")
        return

    # ── EXPORTAÇÃO CSV ────────────────────────────────────────
    if conf.get('export_csv'):
        csv_bytes = df_map.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
        st.download_button(
            label="Clique para baixar o CSV filtrado",
            data=csv_bytes,
            file_name=f"ASI_export_{target_bairro}_TWI{limit_twi:.1f}.csv",
            mime="text/csv"
        )

    # ── SESSÃO 1: MAPA ────────────────────────────────────────
    @map_error_boundary("map")
    def render_map_component():
        m = map_engine.render_map(
            df_map,
            conf,
            df_eventos=df_eventos if conf.get('show_eventos') else None
        )
        return st_folium(
            m,
            height=600,
            use_container_width=True,
            returned_objects=["last_object_clicked"]
        )

    output = render_map_component()

    # ── SESSÃO 2: DIAGNÓSTICO DE PONTO E BUFFER ───────────────
    clicked = output.get("last_object_clicked")
    active_twi_class = None
    cluster_on = conf.get('use_cluster', False)

    if conf.get('inspect_mode') and clicked and not cluster_on:
        st.markdown("---")

        @report_error_boundary("report")
        def render_report_component():
            lat, lon = clicked['lat'], clicked['lng']
            center_point = (lat, lon)

            mask = (
                (abs(df_map['latitude'] - lat) < 0.00001) &
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

                    # ── Gráfico de distribuição de risco no buffer 500m ────────
                    df_nearby_diag = df_map[
                        df_map['latitude'].between(lat - 0.005, lat + 0.005) &
                        df_map['longitude'].between(lon - 0.005, lon + 0.005)
                    ].copy()
                    df_nearby_diag['distancia'] = df_nearby_diag.apply(
                        lambda r: geodesic(center_point, (r['latitude'], r['longitude'])).meters,
                        axis=1
                    )
                    df_nearby_diag = df_nearby_diag[df_nearby_diag['distancia'] <= 500]

                    if not df_nearby_diag.empty:
                        risk_counts = df_nearby_diag['Classe_Risco_Cod'].value_counts()
                        risk_colors = {
                            'CRITICO': '#8B0000',
                            'ALTO': '#FF4500',
                            'MODERADO': '#FFD700',
                            'BAIXO': '#1E90FF',
                            'MUITO_BAIXO': '#ADD8E6',
                        }

                        fig_pie = px.pie(
                            values=risk_counts.values,
                            names=risk_counts.index,
                            title="Distribuição de Risco no Buffer (500m)",
                            color=risk_counts.index,
                            color_discrete_map=risk_colors,
                            hole=0.4,
                        )
                        fig_pie.update_layout(
                            height=250,
                            margin=dict(t=40, b=10, l=10, r=10),
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="IBM Plex Sans", size=11, color="#C8D6E0"),
                        )
                        fig_pie.update_traces(textinfo='label+percent', textfont_size=10)
                        st.plotly_chart(fig_pie, use_container_width=True)

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

                    df_nearby = df_nearby[df_nearby['distancia'] <= 500].sort_values('distancia')

                    st.dataframe(
                        df_nearby[['twi', 'Classe_Risco_Cod', 'NM_BAIRRO', 'distancia']].head(20),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "twi": st.column_config.NumberColumn("TWI", format="%.2f"),
                            "distancia": st.column_config.NumberColumn("Distância (m)", format="%.0f"),
                        }
                    )

                    # Mapa de buffer
                    m_buffer = folium.Map(location=center_point, zoom_start=16, tiles="OpenStreetMap")
                    folium.Circle(
                        location=center_point,
                        radius=500,
                        color="red",
                        fill=True,
                        fill_opacity=0.1,
                        popup="Buffer 500m"
                    ).add_to(m_buffer)
                    folium.Marker(
                        location=center_point,
                        icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
                        popup="Ponto Selecionado"
                    ).add_to(m_buffer)
                    st_folium(m_buffer, height=300, use_container_width=True)
            else:
                st.caption("Amostra vetorial não localizada nos parâmetros atuais.")

        render_report_component()

    # ── LEGENDA ───────────────────────────────────────────────
    components.render_twi_legend(active_class=active_twi_class)

    # ── SESSÃO 3: ANALYTICS GEOESTATÍSTICO ───────────────────
    if conf.get('analytics_mode'):
        st.markdown("---")

        @analytics_error_boundary("composicao")
        def render_analytics_component():
            analytics.render_advanced_dashboard(df_map, conf, df_precipitacao=df_precipitacao)

        render_analytics_component()

    # ── SESSÃO 3b: PRECIPITAÇÃO HISTÓRICA (APAC) ──────────────
    if conf.get('analytics_mode') and not df_precipitacao.empty:
        st.markdown("---")

        @analytics_error_boundary("precipitacao")
        def render_precip_component():
            analytics.render_precipitacao_dashboard(df_precipitacao, conf)

        render_precip_component()

    # ── SESSÃO 3c: DEFESA CIVIL ────────────────────────────────
    if conf.get('analytics_mode') and not df_defesa_civil.empty:
        st.markdown("---")

        @analytics_error_boundary("defesa_civil")
        def render_dc_component():
            analytics.render_defesa_civil_dashboard(df_defesa_civil, conf)

        render_dc_component()

    # ── SESSÃO 3d: RANKING IRA POR BAIRRO ─────────────────────
    if conf.get('ranking_mode'):
        st.markdown("---")

        @analytics_error_boundary("ranking")
        def render_ranking_component():
            df_ranking = data_loader.calcular_indice_risco_bairro(df_map)
            analytics.render_ranking_bairros(df_ranking, conf)

        render_ranking_component()

    # ── SESSÃO 3e: CORRELAÇÃO TWI × DEFESA CIVIL ──────────────
    if conf.get('correlacao_mode') and not df_defesa_civil.empty:
        st.markdown("---")

        @analytics_error_boundary("correlacao")
        def render_correlacao_component():
            df_correlacao = data_loader.correlacionar_datasets(
                df_map,
                df_defesa_civil,
                df_precip=df_precipitacao
            )
            analytics.render_correlacao_dashboard(df_correlacao, conf)

        render_correlacao_component()

    # ── SESSÃO 3f: HUB DE DADOS EXTERNOS (APIs) ────────────────
    if conf.get('api_hub_mode'):
        st.markdown("---")
        render_api_hub_dashboard()

    # ── SESSÃO 6: DOCUMENTAÇÃO TÉCNICA ───────────────────────
    documentation.render_technical_docs()


if __name__ == "__main__":
    main()