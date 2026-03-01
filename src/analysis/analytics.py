"""
SISTEMA ASI - ANALYTICS
Versão: 2.8 — Ranking de Bairros, Precipitação e Dispersão Aprimorada
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.sigweb import config


def render_advanced_dashboard(df, conf, df_precipitacao=None):
    if df.empty:
        st.info("Aguardando carregamento de dados espaciais.")
        return

    st.markdown("### Análise Geoestatística de Área")

    tab1, tab2, tab3 = st.tabs([
        "Composição Proporcional",
        "Distribuição de Frequência",
        "Matriz de Uso do Solo"
    ])

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    # ── ABA 1: Composição ─────────────────────────────────────
    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            df_pie = df['Classe_Risco_Cod'].value_counts().reset_index()
            df_pie.columns = ['Classe', 'Quantidade']

            fig_pie = px.pie(
                df_pie,
                values='Quantidade',
                names='Classe',
                title="Composição Proporcional de Suscetibilidade",
                color='Classe',
                color_discrete_map=config.COLORS,
                hole=0.4
            )
            fig_pie.update_layout(template=tema)
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            if conf.get('tech_mode'):
                st.success(
                    "**Fundamentação Teórica:** A segmentação amostral é estruturada mediante os "
                    "limiares hidrogeológicos estabelecidos para o TWI. Amostragens designadas como "
                    "'Críticas' ou 'Altas' corroboram para áreas de convergência hídrica, denotando "
                    "elevada suscetibilidade à saturação pedológica."
                )
            else:
                st.info("Habilite 'Exibir Fundamentação Teórica' para visualização do descritivo técnico.")

    # ── ABA 2: Frequência ─────────────────────────────────────
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            fig_hist = px.histogram(
                df, x="twi", nbins=40,
                title="Frequência Estatística (TWI)",
                color_discrete_sequence=['#1E90FF']
            )
            fig_hist.update_layout(template=tema)
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            fig_scatter = px.scatter(
                df, x="longitude", y="twi", color="Classe_Risco_Cod",
                title="Dispersão Espacial vs Saturação",
                color_discrete_map=config.COLORS,
                hover_data=['NM_BAIRRO'] if 'NM_BAIRRO' in df.columns else None
            )
            fig_scatter.update_layout(template=tema)
            st.plotly_chart(fig_scatter, use_container_width=True)

        if conf.get('tech_mode'):
            st.success(
                "**Fundamentação Teórica:** A distribuição de frequência consolida o comportamento "
                "hidrológico da região em análise. A assimetria à direita na distribuição do TWI "
                "sinaliza predominância de áreas secas com zonas restritas de saturação extrema."
            )

    # ── ABA 3: Uso do Solo ────────────────────────────────────
    with tab3:
        if 'Uso_Solo_Desc' in df.columns:
            df_grp = df.groupby(['Uso_Solo_Desc', 'Classe_Risco_Cod']).size().reset_index(name='Contagem')

            fig_bar = px.bar(
                df_grp, y="Uso_Solo_Desc", x="Contagem", color="Classe_Risco_Cod",
                orientation='h',
                title="Correlação: Vulnerabilidade vs Cobertura Pedológica",
                color_discrete_map=config.COLORS
            )
            fig_bar.update_layout(template=tema, barmode='stack')
            st.plotly_chart(fig_bar, use_container_width=True)

            if conf.get('tech_mode'):
                st.success(
                    "**Fundamentação Teórica:** A matriz de correlação evidencia o risco inerente à "
                    "ocupação antrópica em zonas de alta convergência hídrica, servindo como embasamento "
                    "empírico para o planejamento do ordenamento territorial."
                )


# ══════════════════════════════════════════════════════════════
#  RANKING DE RISCO POR BAIRRO — v2.8
# ══════════════════════════════════════════════════════════════

def render_ranking_bairros(df_ranking, conf):
    """
    Exibe o ranking de Índice de Risco Agregado (IRA) por bairro.
    df_ranking vem de data_loader.calcular_indice_risco_bairro()
    """
    if df_ranking is None or df_ranking.empty:
        st.info("Dados insuficientes para gerar o ranking de bairros.")
        return

    st.markdown("### Ranking de Risco por Bairro — Índice de Risco Agregado (IRA)")
    st.caption(
        "O IRA é calculado como média ponderada das classes de risco dos pontos TWI de cada bairro. "
        "Pesos: Crítico=5 | Alto=4 | Moderado=3 | Baixo=2 | Muito Baixo=1"
    )

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    col_graf, col_tab = st.columns([1.6, 1])

    with col_graf:
        # Cores do gráfico baseadas na classe dominante
        cores_barras = [
            config.COLORS.get(str(c), '#808080')
            for c in df_ranking['classe_dominante']
        ]

        fig = go.Figure(go.Bar(
            x=df_ranking['ira'],
            y=df_ranking['NM_BAIRRO'],
            orientation='h',
            marker_color=cores_barras,
            text=df_ranking['ira'].round(2),
            textposition='outside',
            hovertemplate=(
                "<b>%{y}</b><br>"
                "IRA: %{x:.2f}<br>"
                "Total de Pontos: %{customdata[0]}<br>"
                "Pontos Críticos: %{customdata[1]}<br>"
                "% Crítico+Alto: %{customdata[2]}%"
                "<extra></extra>"
            ),
            customdata=df_ranking[['total_pontos', 'criticos', 'pct_critico_alto']].values
        ))

        fig.update_layout(
            template=tema,
            title="IRA por Bairro (ordenado por criticidade)",
            xaxis_title="Índice de Risco Agregado",
            yaxis=dict(autorange="reversed"),
            height=max(350, len(df_ranking) * 28),
            margin=dict(l=10, r=60, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_tab:
        st.markdown("**Tabela de Ranking**")

        # Formata tabela para exibição
        df_exib = df_ranking[['NM_BAIRRO', 'ira', 'total_pontos', 'criticos', 'pct_critico_alto', 'classe_dominante']].copy()
        df_exib.columns = ['Bairro', 'IRA', 'Pontos', 'Críticos', '% C+A', 'Classe Dom.']
        df_exib['IRA'] = df_exib['IRA'].round(2)
        df_exib['% C+A'] = df_exib['% C+A'].astype(str) + '%'

        st.dataframe(
            df_exib,
            use_container_width=True,
            hide_index=True,
            height=min(500, len(df_exib) * 36 + 40)
        )

        # Destaque do bairro mais crítico
        top = df_ranking.iloc[0]
        cor_top = config.COLORS.get(str(top['classe_dominante']), '#FF4500')
        st.markdown(f"""
        <div style="border-left:4px solid {cor_top}; background:#1f1f1f; padding:10px; border-radius:4px; margin-top:10px;">
            <b style="color:{cor_top};">⚠ Bairro de Maior Criticidade</b><br>
            <b>{top['NM_BAIRRO']}</b><br>
            IRA: <b>{top['ira']:.2f}</b> | Pontos críticos: <b>{int(top['criticos'])}</b><br>
            {top['pct_critico_alto']}% dos vetores classificados como Alto ou Crítico
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PRECIPITAÇÃO HISTÓRICA — v2.8
# ══════════════════════════════════════════════════════════════

def render_precipitacao_dashboard(df_precip, conf):
    """
    Painel de série histórica de precipitação (dados APAC).
    df_precip vem de data_loader.load_precipitacao()
    """
    if df_precip is None or df_precip.empty:
        st.info(
            "Dados de precipitação não disponíveis. "
            "Adicione o arquivo `data/raw/apac_exports/precipitacao_pernambuco.csv` para ativar este painel."
        )
        return

    st.markdown("### Série Histórica de Precipitação (INMET/APAC)")

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    col1, col2 = st.columns(2)

    with col1:
        if 'data' in df_precip.columns and 'precipitacao_mm' in df_precip.columns:
            df_ts = df_precip.dropna(subset=['data', 'precipitacao_mm'])
            color_col = 'estacao' if 'estacao' in df_ts.columns else None
            fig_line = px.line(
                df_ts.sort_values('data'),
                x='data', y='precipitacao_mm',
                color=color_col,
                title="Precipitação Histórica por Estação (mm)",
                labels={'precipitacao_mm': 'Precipitação (mm)', 'data': 'Data'}
            )
            fig_line.update_layout(template=tema)
            st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        if 'data' in df_precip.columns:
            df_mensal = df_precip.copy()
            df_mensal['mes'] = df_mensal['data'].dt.month
            df_mensal['mes_nome'] = df_mensal['data'].dt.strftime('%b')
            df_mes_agg = df_mensal.groupby(['mes', 'mes_nome'])['precipitacao_mm'].mean().reset_index()
            df_mes_agg = df_mes_agg.sort_values('mes')
            fig_bar = px.bar(
                df_mes_agg, x='mes_nome', y='precipitacao_mm',
                title="Precipitação Média por Mês",
                labels={'precipitacao_mm': 'Média (mm)', 'mes_nome': 'Mês'},
                color='precipitacao_mm',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(template=tema, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    if 'precipitacao_mm' in df_precip.columns:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Máxima Registrada",  f"{df_precip['precipitacao_mm'].max():.1f} mm")
        m2.metric("Média Histórica",     f"{df_precip['precipitacao_mm'].mean():.1f} mm")
        m3.metric("Mediana",             f"{df_precip['precipitacao_mm'].median():.1f} mm")
        m4.metric("Total de Registros",  f"{len(df_precip):,}")


# ══════════════════════════════════════════════════════════════
#  DEFESA CIVIL PE — PAINEL COMPLETO — v2.8
# ══════════════════════════════════════════════════════════════

def render_defesa_civil_dashboard(df_dc, conf):
    """
    Painel analítico completo com danos humanos e materiais
    por município — fonte: Defesa Civil PE / SEPDEC.
    df_dc vem de data_loader.load_defesa_civil()
    """
    if df_dc is None or df_dc.empty:
        st.info(
            "Dados da Defesa Civil não disponíveis. "
            "Adicione `data/raw/eventos/defesacivil_pe_consolidado.csv` para ativar este painel."
        )
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    # Filtra apenas municípios com alguma ocorrência
    df = df_dc[df_dc['severidade'] != 'SEM_REGISTRO'].copy()

    st.markdown("### Painel de Desastres — Defesa Civil PE (2024–2026)")
    st.caption(f"Fonte: Secretaria Executiva de Proteção e Defesa Civil de Pernambuco — SEPDEC | {len(df)} municípios afetados")

    # ── Métricas de topo ────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Municípios Afetados", len(df))
    m2.metric("Óbitos",              int(df['dh_obitos'].sum()))
    m3.metric("Desabrigados",        f"{int(df['dh_desabrigados'].sum()):,}")
    m4.metric("Desalojados",         f"{int(df['dh_desalojados'].sum()):,}")
    m5.metric("Imóveis Danificados", f"{int(df['dm_total'].sum()):,}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "Danos Humanos por Município",
        "Danos Materiais por Município",
        "Distribuição e Severidade"
    ])

    # ── ABA 1: Danos Humanos ─────────────────────────────────
    with tab1:
        col_graf, col_tab = st.columns([1.6, 1])

        with col_graf:
            df_hum = df[df['dh_total'] > 0].sort_values('dh_total', ascending=True).tail(20)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=df_hum['municipio'], x=df_hum['dh_desalojados'],
                name='Desalojados', orientation='h', marker_color='#FF8C00'
            ))
            fig.add_trace(go.Bar(
                y=df_hum['municipio'], x=df_hum['dh_desabrigados'],
                name='Desabrigados', orientation='h', marker_color='#FF1493'
            ))
            fig.add_trace(go.Bar(
                y=df_hum['municipio'], x=df_hum['dh_feridos'],
                name='Feridos', orientation='h', marker_color='#FFD700'
            ))
            fig.add_trace(go.Bar(
                y=df_hum['municipio'], x=df_hum['dh_obitos'],
                name='Óbitos', orientation='h', marker_color='#8B0000'
            ))
            fig.update_layout(
                template=tema,
                barmode='stack',
                title="Top 20 Municípios — Danos Humanos",
                xaxis_title="Pessoas Afetadas",
                height=500,
                margin=dict(l=10, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tab:
            st.markdown("**Tabela Completa — Danos Humanos**")
            df_exib = df[df['dh_total'] > 0][[
                'municipio','severidade','dh_obitos',
                'dh_desabrigados','dh_desalojados','dh_feridos','dh_total'
            ]].copy()
            df_exib.columns = ['Município','Severidade','Óbitos','Desabrigados','Desalojados','Feridos','Total']
            df_exib = df_exib.sort_values('Total', ascending=False).reset_index(drop=True)
            st.dataframe(df_exib, use_container_width=True, hide_index=True, height=480)

    # ── ABA 2: Danos Materiais ───────────────────────────────
    with tab2:
        col_graf, col_tab = st.columns([1.6, 1])

        with col_graf:
            df_mat = df[df['dm_total'] > 0].sort_values('dm_total', ascending=True).tail(20)

            fig2 = go.Figure()
            for col, nome, cor in [
                ('dm_residencial',  'Residencial',  '#1E90FF'),
                ('dm_comercial',    'Comercial',    '#FFD700'),
                ('dm_estradas',     'Estradas',     '#FF8C00'),
                ('dm_p_publico',    'P. Público',   '#9370DB'),
                ('dm_outros',       'Outros',       '#808080'),
            ]:
                if col in df_mat.columns:
                    fig2.add_trace(go.Bar(
                        y=df_mat['municipio'], x=df_mat[col],
                        name=nome, orientation='h', marker_color=cor
                    ))

            fig2.update_layout(
                template=tema,
                barmode='stack',
                title="Top 20 Municípios — Danos Materiais",
                xaxis_title="Unidades Danificadas",
                height=500,
                margin=dict(l=10, r=20, t=40, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col_tab:
            st.markdown("**Tabela Completa — Danos Materiais**")
            df_mat_tab = df[df['dm_total'] > 0][[
                'municipio','dm_total','dm_residencial',
                'dm_comercial','dm_estradas','dm_p_publico','dm_outros'
            ]].copy()
            df_mat_tab.columns = ['Município','Total','Residencial','Comercial','Estradas','P.Público','Outros']
            df_mat_tab = df_mat_tab.sort_values('Total', ascending=False).reset_index(drop=True)
            st.dataframe(df_mat_tab, use_container_width=True, hide_index=True, height=480)

    # ── ABA 3: Distribuição e Severidade ─────────────────────
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            df_sev = df['severidade'].value_counts().reset_index()
            df_sev.columns = ['Severidade', 'Municípios']
            cores_sev = {
                'GRAVE':    '#FF1493',
                'MODERADA': '#FF8C00',
                'LEVE':     '#FFD700'
            }
            fig_pie = px.pie(
                df_sev, values='Municípios', names='Severidade',
                title="Distribuição por Severidade",
                color='Severidade',
                color_discrete_map=cores_sev,
                hole=0.4
            )
            fig_pie.update_layout(template=tema)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Correlação danos humanos x materiais
            df_corr = df[(df['dh_total'] > 0) | (df['dm_total'] > 0)].copy()
            # dh_total como tamanho do ponto (registros não está no CSV)
            df_corr['_tamanho'] = (df_corr['dh_total'] + 1).clip(upper=500)
            fig_scatter = px.scatter(
                df_corr,
                x='dh_total', y='dm_total',
                color='severidade',
                size='_tamanho',
                hover_name='municipio',
                title="Correlação: Danos Humanos × Materiais",
                labels={
                    'dh_total':  'Total Danos Humanos',
                    'dm_total':  'Total Danos Materiais',
                    'severidade':'Severidade'
                },
                color_discrete_map={
                    'GRAVE':    '#FF1493',
                    'MODERADA': '#FF8C00',
                    'LEVE':     '#FFD700'
                }
            )
            fig_scatter.update_layout(template=tema)
            st.plotly_chart(fig_scatter, use_container_width=True)