"""
SISTEMA ASI - ANALYTICS
Versão: 2.8 — Ranking de Bairros, Precipitação e Dispersão Aprimorada
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.sigweb import config


# ════════════════════════════════════════════════════════════════════════════════
#  CONSTANTES
# ════════════════════════════════════════════════════════════════════════════════

_LIMIAR_ATENCAO_MM = 30.0
_LIMIAR_ALERTA_MM  = 60.0

_LIMIAR_ATENCAO_SOLO   = 0.60
_LIMIAR_SATURACAO_SOLO = 0.80

_CORES_VULNERABILIDADE = {
    'CRITICA': '#8B0000',
    'ALTA':    '#FF4500',
    'MODERADA':'#FF8C00',
    'BAIXA':   '#32CD32',
    'SEM DADOS':'#555555'
}

_CORES_SATURACAO = {
    'CRITICO':  '#8B0000',
    'ATENCAO':  '#FF8C00',
    'NORMAL':   '#1E90FF',
    'SEM DADOS':'#555555',
}


# ════════════════════════════════════════════════════════════════════════════════
#  DASHBOARD GEOESTATÍSTICO AVANÇADO — v2.8
# ════════════════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════════════════
#  RANKING DE RISCO POR BAIRRO — v2.8
# ════════════════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════════════════
#  PRECIPITAÇÃO HISTÓRICA — v2.8
# ════════════════════════════════════════════════════════════════════════════════

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
        if 'precipitacao_mm' in df_precip.columns:
            stats = df_precip['precipitacao_mm'].describe()
            st.dataframe(stats.to_frame().T, use_container_width=True)

            # Boxplot por estação
            if 'estacao' in df_precip.columns:
                fig_box = px.box(
                    df_precip.dropna(subset=['precipitacao_mm']),
                    x='estacao', y='precipitacao_mm',
                    color='estacao',
                    title="Distribuição de Precipitação por Estação",
                    labels={'estacao': 'Estação', 'precipitacao_mm': 'Precipitação (mm)'}
                )
                fig_box.update_layout(template=tema)
                st.plotly_chart(fig_box, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
#  DEFESA CIVIL PE — DASHBOARD — v2.8
# ════════════════════════════════════════════════════════════════════════════════

def render_defesa_civil_dashboard(df_dc, conf):
    """Painel Defesa Civil PE 2024-2026 — Danos humanos e materiais por município."""
    if df_dc is None or df_dc.empty:
        st.info(
            "Dados da Defesa Civil não disponíveis. "
            "Adicione `data/raw/events/defesacivil_pe_consolidado.csv`."
        )
        return

    st.markdown("### Painel Defesa Civil PE 2024–2026")
    st.caption("Fonte: SEPDEC / Defesa Civil PE — Consolidação de danos humanos e materiais por município.")

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    # Métricas totais
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Óbitos", int(df_dc['dh_obitos'].sum()) if 'dh_obitos' in df_dc.columns else 0)
    m2.metric("Total Desabrigados", int(df_dc['dh_desabrigados'].sum()) if 'dh_desabrigados' in df_dc.columns else 0)
    m3.metric("Total Desalojados", int(df_dc['dh_desalojados'].sum()) if 'dh_desalojados' in df_dc.columns else 0)
    m4.metric("Total Feridos", int(df_dc['dh_feridos'].sum()) if 'dh_feridos' in df_dc.columns else 0)

    # Ranking de municípios mais afetados
    st.markdown("#### Top 10 Municípios — Danos Humanos (DH Total)")
    if 'dh_total' in df_dc.columns:
        top_dh = df_dc.nlargest(10, 'dh_total')[['municipio', 'dh_total', 'severidade']].copy()
        fig = px.bar(
            top_dh,
            x='dh_total', y='municipio',
            orientation='h',
            color='severidade',
            color_discrete_map={
                'GRAVE': '#FF1493',
                'MODERADA': '#FF8C00',
                'LEVE': '#32CD32',
                'SEM_REGISTRO': '#808080'
            },
            title="Municípios com Maior Impacto Humano",
            labels={'dh_total': 'Danos Humanos Totais', 'municipio': 'Município'}
        )
        fig.update_layout(template=tema, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Ranking de danos materiais
    st.markdown("#### Top 10 Municípios — Danos Materiais (DM Total)")
    if 'dm_total' in df_dc.columns:
        top_dm = df_dc.nlargest(10, 'dm_total')[['municipio', 'dm_total', 'severidade']].copy()
        fig = px.bar(
            top_dm,
            x='dm_total', y='municipio',
            orientation='h',
            color='severidade',
            color_discrete_map={
                'GRAVE': '#FF1493',
                'MODERADA': '#FF8C00',
                'LEVE': '#32CD32',
                'SEM_REGISTRO': '#808080'
            },
            title="Municípios com Maior Prejuízo Material",
            labels={'dm_total': 'Danos Materiais Totais', 'municipio': 'Município'}
        )
        fig.update_layout(template=tema, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Tabela completa
    with st.expander("Tabela Completa — Dados por Município", expanded=False):
        df_display = df_dc.copy()
        # Selecionar colunas relevantes
        cols = ['municipio', 'severidade', 'dh_total', 'dm_total']
        if 'dh_obitos' in df_display.columns:
            cols += ['dh_obitos', 'dh_desabrigados', 'dh_desalojados', 'dh_feridos']
        if 'dm_estradas' in df_display.columns:
            cols += ['dm_estradas', 'dm_comercial', 'dm_residencial', 'dm_outros']
        st.dataframe(df_display[cols].sort_values('dh_total', ascending=False), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
#  CORRELAÇÃO CRUZADA TWI × DEFESA CIVIL — v2.9
# ════════════════════════════════════════════════════════════════════════════════

def render_correlacao_dashboard(df_corr, conf):
    """
    Painel de Correlação cruzada entre datasets df_corr vem de data_loader.correlacionar_datasets()
    """
    if df_corr is None or df_corr.empty:
        st.info(
            "Dados insuficientes para análise de correlação cruzada. "
            "Certifique-se de que ambos os datasets (TWI e Defesa Civil) estejam carregados e processados."
        )
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    st.markdown("### Correlação de Risco - TWI x Defesa Civil PE")
    st.caption(
        "Cruzamento por Município entre o índice de risco geomorfomético (TWI/IRA) e os registros de danos da Defesa Civil PE (SEPDEC 2024-2026)."
    )

    # Metricas de topo
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Municípios Cruzados", len(df_corr))
    m2.metric("IRA Médio Geral", f"{df_corr['ira_medio'].mean():.2f}")
    m3.metric("Total Afetados (DH)", f"{int(df_corr['dh_total'].sum()):,}")
    m4.metric("Total Danos (DM)", f"{int(df_corr['dm_total'].sum()):,}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "IRA x Danos Humanos",
        "Perfil por Município",
        "Tabela Completa"
    ])

    # ABA 1: IRA x Danos Humanos
    with tab1:
        df_plot = df_corr[df_corr['dh_total'] >= 0].copy()
        df_plot['_tamanho'] = (df_plot['dh_total'] + 1).clip(upper=500)

        # Cor Baseada na Severidade da Defesa Civil
        cores_sev = {
            'GRAVE': '#FF1493',
            'MODERADA': '#FF8C00',
            'LEVE': '#32CD32',
            'SEM_REGISTRO': '#808080'
        }

        fig_scatter = px.scatter(
            df_plot,
            x='ira_medio', y='dh_total',
            color='severidade',
            size='_tamanho',
            hover_name='municipio',
            hover_data={
                'twi_medio': ':.2f',
                'pct_critico_alto': ':.1f',
                'total_pontos_twi': True,
                '_tamanho': False
            },
            title="IRA Geomorfométrico x Danos Humanos por Município",
            labels={
                'ira_medio': 'IRA Médio (TWI)',
                'dh_total': 'Total de Pessoas Afetadas (DH)',
                'severidade': 'Severidade (Defesa Civil)',
                'twi_medio': 'TWI Médio',
            },
            color_discrete_map=cores_sev
        )
        fig_scatter.update_layout(template=tema, height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ABA 2: Perfil por Município
    with tab2:
        st.markdown("#### Perfil dos Municípios Cruzados")
        st.dataframe(df_corr[['municipio', 'ira_medio', 'twi_medio', 'pct_critico_alto', 'dh_total', 'dm_total', 'severidade']], use_container_width=True)

        # Gráfico de barras empilhadas se houver dados suficientes
        if len(df_corr) >= 2:
            fig_bar = px.bar(
                df_corr,
                x='municipio',
                y=['ira_medio', 'twi_medio'],
                barmode='group',
                title="IRA Médio e TWI Médio — Municípios Cruzados",
                labels={'value': 'Índice', 'municipio': 'Município', 'variable': 'Indicador'}
            )
            fig_bar.update_layout(template=tema, xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

    # ABA 3: Tabela Completa
    with tab3:
        st.markdown("#### Dados Completos da Correlação")
        df_display = df_corr.copy()
        for col in ['ira_medio', 'twi_medio', 'precip_media_mm', 'pct_critico_alto']:
            if col in df_display.columns:
                df_display[col] = df_display[col].round(2)
        st.dataframe(df_display, use_container_width=True, height=400)


# ════════════════════════════════════════════════════════════════════════════════
#  PRECIPITAÇÃO TEMPO REAL — OPEN-METEO — v2.9
# ════════════════════════════════════════════════════════════════════════════════

def render_precipitacao_realtime(df_rt, conf):
    """Painel de precipitação em tempo real via Open-Meteo API.
    df_rt vem de data_loader.load_precipitacao_realtime()
    """
    if df_rt is None or df_rt.empty:
        st.info("Dados de precipitação em tempo real indisponíveis no momento.")
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    st.markdown("### Monitoramento Hidroclimático — Nowcasting & Forecasting (Open-Meteo)")
    st.caption(
        "Modelagem meteorológica diária das estações de Pernambuco (Histórico de 7 dias e Projeção de 7 dias). "
        "Base de dados alimentada por modelos numéricos globais de previsão do tempo."
    )

    # ── Descrição Acadêmica / Técnica ─────────────────────────
    st.success(
        "**Fundamentação Teórica:** O monitoramento contínuo da precipitação atua como a principal variável "
        "de forçamento hidroclimático no sistema ASI. A saturação do perfil pedológico e a consequente "
        "resposta de escoamento superficial (Runoff) em zonas de alto TWI dependem de forma direta do "
        "volume hídrico acumulado antecedentemente e da intensidade pluviométrica projetada."
    )

    # ── Métricas de topo ─────────────────────────────────────
    hist = df_rt[df_rt['tipo'] == 'historico']
    prev = df_rt[df_rt['tipo'] == 'previsao']

    acum_7d    = hist['precipitacao_mm'].sum()
    estacao_top = (
        hist.groupby('estacao')['precipitacao_mm'].sum()
        .idxmax() if not hist.empty else '—'
    )
    max_estacao = (
        hist.groupby('estacao')['precipitacao_mm'].sum().max()
        if not hist.empty else 0
    )
    prev_total = prev['precipitacao_mm'].sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Carga Hídrica 7d (Geral)", f"{acum_7d:.1f} mm")
    m2.metric("Epicentro Pluviométrico",     estacao_top)
    m3.metric("Acumulado Máximo (Epicentro)",     f"{max_estacao:.1f} mm")
    m4.metric("Projeção Global (Próx. 7d)",          f"{prev_total:.1f} mm")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Série Temporal de Eventos",
        "Ranking de Saturação (7 Dias)",
        "Projeção de Risco (Próx. 7 Dias)",
        "Matriz de Dados Meteorológicos"
    ])

    # ── ABA 1: Série temporal ─────────────────────────────────
    with tab1:
        estacoes = sorted(df_rt['estacao'].unique())
        sel = st.multiselect(
            "Filtrar Estações Meteorológicas",
            options=estacoes,
            default=estacoes[:4],
            key='rt_estacoes'
        )

        # Filtra e cria uma cópia pra gente poder alterar o tipo da coluna em paz
        df_sel = df_rt[df_rt['estacao'].isin(sel)].copy() if sel else df_rt.copy()

        # O PULOPS: Converte a coluna 'data' pra datetime64 pra não dar piti no Plotly
        df_sel['data'] = pd.to_datetime(df_sel['data'])

        fig = px.line(
            df_sel,
            x='data', y='precipitacao_mm',
            color='estacao',
            line_dash='tipo',
            markers=True,
            title="Evolução Pluviométrica Diária — Histórico vs. Previsão",
            labels={
                'data':            'Data de Referência',
                'precipitacao_mm': 'Volume Precipitado (mm)',
                'estacao':         'Estação Monitorada',
                'tipo':            'Vetor Analítico'
            }
        )

        # Pega a data de hoje e converte pra milissegundos
        hoje_ms = pd.Timestamp.now().normalize().timestamp() * 1000

        fig.add_vline(
            x=hoje_ms,
            line_dash="dash",
            line_color="#FFD700",
            annotation_text="HOJE",
            annotation_position="top left"
        )
        fig.update_layout(template=tema, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # ── ABA 2: Ranking de Saturação ───────────────────────────
    with tab2:
        st.markdown("#### Ranking de Estações — Acúmulo nos Últimos 7 Dias")
        ranking_7d = (
            hist.groupby('estacao')['precipitacao_mm']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={'precipitacao_mm': 'acumulado_7d_mm'})
        )
        ranking_7d['acumulado_7d_mm'] = ranking_7d['acumulado_7d_mm'].round(1)

        fig_bar = px.bar(
            ranking_7d,
            x='acumulado_7d_mm', y='estacao',
            orientation='h',
            color='acumulado_7d_mm',
            color_continuous_scale='Blues',
            title="Volume Acumulado por Estação (Últimos 7 Dias)",
            labels={'acumulado_7d_mm': 'Acumulado (mm)', 'estacao': 'Estação'}
        )
        fig_bar.update_layout(template=tema, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── ABA 3: Projeção de Risco ──────────────────────────────
    with tab3:
        st.markdown("#### Projeção de Risco Hidrológico (Próximos 7 Dias)")
        if not prev.empty:
            projecao = (
                prev.groupby('estacao')['precipitacao_mm']
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .rename(columns={'precipitacao_mm': 'projetado_7d_mm'})
            )
            projecao['projetado_7d_mm'] = projecao['projetado_7d_mm'].round(1)

            fig_proj = px.bar(
                projecao,
                x='projetado_7d_mm', y='estacao',
                orientation='h',
                color='projetado_7d_mm',
                color_continuous_scale='Reds',
                title="Volume Projetado por Estação (Próximos 7 Dias)",
                labels={'projetado_7d_mm': 'Projeção (mm)', 'estacao': 'Estação'}
            )
            fig_proj.update_layout(template=tema, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_proj, use_container_width=True)

    # ── ABA 4: Matriz ─────────────────────────────────────────
    with tab4:
        st.markdown("#### Tabela Detalhada — Dados Meteorológicos")
        df_show = df_rt.copy()
        df_show['data'] = pd.to_datetime(df_show['data']).dt.strftime('%d/%m/%Y')
        df_show['precipitacao_mm'] = df_show['precipitacao_mm'].round(1)
        st.dataframe(df_show.sort_values(['estacao', 'data']), use_container_width=True)