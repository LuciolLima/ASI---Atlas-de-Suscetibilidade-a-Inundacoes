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
            
            
# ══════════════════════════════════════════════════════════════
#  CORRELAÇÃO CRUZADA TWI × DEFESA CIVIL — v2.9
# ══════════════════════════════════════════════════════════════

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
            'GRAVE':    '#FF1493',
            'MODERADA': '#FF8C00',
            'LEVE':     '#FFD700',
            'SEM_REGISTRO': '#555555'
        }
        
        fig_scatter = px.scatter(
            df_plot,
            x='ira_medio', y='dh_total',
            color='severidade',
            size='_tamanho',
            hover_name='municipio',
            hover_data={
                'twi_medio':        ':.2f',
                'pct_critico_alto': ':.1f',
                'total_pontos_twi': True,
                '_tamanho':         False
            },
            title="IRA Geomorfométrico x Danos Humanos por Município",
            labels={
                'ira_medio': 'IRA Médio (TWI)',
                'dh_total': 'Total de Pesssoas Afetadas (DH)',
                'severidade': 'Severidade (Defesa Civil)',
                'twi_medio': 'TWI Médio',
                'pct_critico_alto': '% Crítico+Alto',
                'total_pontos_twi': 'Pontos TWI'
            },
            color_discrete_map=cores_sev
        )
        fig_scatter.update_layout(template=tema, height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    # ABA 2: Perfil por Município
    with tab2:
        col1, col2, = st.columns(2)
        
        with col1:
            # IRA por município
            df_ira = df_corr.sort_values('ira_medio', ascending=True)
            cores_ira = []
            for val in df_ira['ira_medio']:
                if val >= 4: cores_ira.append(config.COLORS['CRITICO'])
                elif val >= 3: cores_ira.append(config.COLORS['ALTO'])
                elif val >= 2: cores_ira.append(config.COLORS['MODERADO'])
                else: cores_ira.append(config.COLORS['BAIXO'])
                
            fig_ira = go.Figure(go.Bar(
                x=df_ira['ira_medio'],
                y=df_ira['municipio'],
                orientation='h',
                marker_color=cores_ira,
                text=df_ira['ira_medio'].round(2),
                textposition='outside',
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "IRA Médio: %{x:.2f}<br>"
                    "TWI Médio: %{customdata[0]:.2f}<br>"
                    "% Crítico+Alto: %{customdata[1]:.1f}%<br>"
                    "Total Pontos TWI: %{customdata[2]}"
                    "<extra></extra>"
                ),
                customdata=df_ira[['twi_medio', 'pct_critico_alto']].values
            ))
            fig_ira.update_layout(
                template=tema,
                title="IRA Médio por Município",
                xaxis_title="Índice de Risco Agregado (IRA)",
                height=max(300, len(df_ira) * 40),
                margin=dict(l=10, r=60, t=40, b=20)
            )
            st.plotly_chart(fig_ira, use_container_width=True)
            
        with col2:
            # Danos Humanos por município
            df_dh = df_corr.sort_values('dh_total', ascending=True)
            fig_dh = go.Figure(go.Bar(
                x=df_dh['dh_total'],
                y=df_dh['municipio'],
                orientation='h',
                marker_color='#FF8C00',
                text=df_dh['dh_total'].astype(int),
                textposition='outside',
            ))
            fig_dh.update_layout(
                template=tema,
                title="Pessoas Afetadas (DH) por Município",
                xaxis_title="Total de Danos Humanos (DH)",
                height=max(300, len(df_dh) * 40),
                margin=dict(l=10, r=60, t=40, b=20)
            )
            st.plotly_chart(fig_dh, use_container_width=True)
            
    # ABA 3: Tabela Completa
    with tab3:
        cols_exib = [
            'municipio', 'ira_medio', 'twi_medio', 'pct_critico_alto',
            'total_pontos_twi', 'dh_total', 'dm_total', 'severidade'
        ]
        cols_exib = [c for c in cols_exib if c in df_corr.columns]
        
        df_tab = df_corr[cols_exib].copy()
        df_tab.columns = [
            c.replace('_', ' ').replace('ira medio', 'IRA')
            .replace('twi medio', 'TWI Médio')
            .replace('pct critico alto', '% C+A')
            .replace('total pontos twi', 'Pontos TWI')
            .replace('dh total', 'Afetados (DH)')
            .replace('dm total', 'Danos Materiais (DM)')
            .replace('severidade', 'Severidade (DC)')
            for c in cols_exib
        ]
        
        st.dataframe(
            df_tab,
            use_container_width=True,
            hide_index=True,
            height=min(500, len(df_tab) * 40 + 50)
        )
        
        # Destaque do município mais crítico correlacionado
        
        if not df_corr.empty:
            top = df_corr.sort_values('ira_medio', ascending=False).iloc[0]
            cor = config.COLORS.get('CRITICO', '#8B0000') if top['ira_medio'] >= 4 else config.COLORS.get('ALTO', '#FF4500')
            st.markdown(f"""
            <div style="border-left:4px solid {cor}; background:#1f1f1f; padding:10px; border-radius:4px; margin-top:10px;">
                <b style="color:{cor};">⚠ Município de Maior Correlação Crítica</b><br>
                <b>{top['municipio']}</b><br>
                IRA Médio: <b>{top['ira_medio']:.2f}</b> | Pessoas Afetadas (DH): <b>{int(top['dh_total']):,}</b><br>
                Severidade Defesa Civil: <b>{top['severidade']}</b>
            </div>
            """, unsafe_allow_html=True)
            
# ══════════════════════════════════════════════════════════════
#  PRECIPITAÇÃO TEMPO REAL — OPEN-METEO — v2.9
# ══════════════════════════════════════════════════════════════

def render_precipitacao_realtime(df_rt, conf):
    """
    Painel de precipitação em tempo real via Open-Meteo API.
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
        
        # O PULO DO GATO: Converte a coluna 'data' pra datetime64 pra não dar piti no Plotly
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
            x=hoje_ms, # Passando número o Plotly faz a matemática da anotação de boas
            line_dash="dash",
            line_color="#00B4D8",
            annotation_text="Ponto de Inflexão (Hoje)",
            annotation_position="top right"
        )
        
        fig.update_layout(template=tema, height=420)
        st.plotly_chart(fig, use_container_width=True)
        
    # ── ABA 2: Ranking 7 dias ─────────────────────────────────
    with tab2:
        ranking = (
            hist.groupby('estacao')['precipitacao_mm']
            .sum()
            .reset_index()
            .sort_values('precipitacao_mm', ascending=True)
            .rename(columns={'precipitacao_mm': 'acumulado_7d_mm'})
        )

        LIMIAR_ATENCAO = 30.0
        LIMIAR_ALERTA  = 60.0

        cores = []
        for v in ranking['acumulado_7d_mm']:
            if v >= LIMIAR_ALERTA:
                cores.append('#FF1493')   # grave
            elif v >= LIMIAR_ATENCAO:
                cores.append('#FF8C00')   # atenção
            else:
                cores.append('#1E90FF')   # normal

        fig_rank = go.Figure(go.Bar(
            x=ranking['acumulado_7d_mm'],
            y=ranking['estacao'],
            orientation='h',
            marker_color=cores,
            text=ranking['acumulado_7d_mm'].round(1),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Volume Acumulado: %{x:.1f} mm<extra></extra>"
        ))

        fig_rank.add_vline(
            x=LIMIAR_ATENCAO, line_dash="dot",
            line_color="#FF8C00",
            annotation_text=f"Saturação de Atenção ({LIMIAR_ATENCAO}mm)",
            annotation_position="top"
        )
        fig_rank.add_vline(
            x=LIMIAR_ALERTA, line_dash="dot",
            line_color="#FF1493",
            annotation_text=f"Saturação Crítica ({LIMIAR_ALERTA}mm)",
            annotation_position="top"
        )

        fig_rank.update_layout(
            template=tema,
            title="Carga Hidrológica Acumulada por Área (Últimos 7 Dias)",
            xaxis_title="Precipitação Acumulada (mm)",
            height=max(300, len(ranking) * 38),
            margin=dict(l=10, r=80, t=40, b=20)
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    # ── ABA 3: Previsão ───────────────────────────────────────
    with tab3:
        prev_rank = (
            prev.groupby('estacao')['precipitacao_mm']
            .sum()
            .reset_index()
            .sort_values('precipitacao_mm', ascending=False)
            .rename(columns={'precipitacao_mm': 'previsao_7d_mm'})
        )

        fig_prev = px.bar(
            prev_rank,
            x='estacao', y='previsao_7d_mm',
            title="Modelagem de Risco Iminente — Projeção Pluviométrica (Próx. 7 Dias)",
            labels={
                'estacao':       'Estação',
                'previsao_7d_mm':'Estimativa de Precipitação (mm)'
            },
            color='previsao_7d_mm',
            color_continuous_scale='Blues'
        )
        fig_prev.update_layout(template=tema, showlegend=False, height=380)
        st.plotly_chart(fig_prev, use_container_width=True)

    # ── ABA 4: Tabela Completa (NOVO) ─────────────────────────
    with tab4:
        st.markdown("**Matriz Quantitativa de Precipitação (Open-Meteo)**")
        
        df_table = df_rt.copy()
        df_table['data'] = df_table['data'].dt.strftime('%d/%m/%Y')
        df_table.rename(columns={
            'estacao': 'Unidade Estacional',
            'data': 'Data da Coleta/Projeção',
            'precipitacao_mm': 'Volume (mm)',
            'tipo': 'Vetor Analítico'
        }, inplace=True)
        
        # Formata a coluna tipo para ficar com primeira letra maiúscula
        df_table['Vetor Analítico'] = df_table['Vetor Analítico'].str.capitalize()

        st.dataframe(
            df_table[['Unidade Estacional', 'Data da Coleta/Projeção', 'Volume (mm)', 'Vetor Analítico']], 
            use_container_width=True, 
            height=400,
            hide_index=True
        )
        st.caption(
            "Matriz de dados brutos extraídos via API Open-Meteo. A margem de acurácia das previsões está atrelada "
            "à variância estocástica intrínseca aos modelos numéricos de previsão atmosférica."
        )
        
def render_ibge_dashboard(df_sidra):
    """
    Renderiza o dashboard de vulnerabilidade social com dados do IBGE.
    """
    if df_sidra.empty:
        st.error("Falha na aquisição de dados demográficos via API SIDRA.")
        return

    st.markdown("#### Análise de Vulnerabilidade Demográfica (Censo 2022)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Ranking de População por Município em Pernambuco
        fig_pop = px.bar(
            df_sidra.sort_values('populacao_total', ascending=False).head(20),
            x='municipio',
            y='populacao_total',
            title="Top 20 Municípios por População Residente (PE)",
            labels={'municipio': 'Município', 'populacao_total': 'Habitantes'},
            color='populacao_total',
            color_continuous_scale='Greys'
        )
        fig_pop.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pop, use_container_width=True)

    with col2:
        st.markdown("**Estatísticas Descritivas**")
        total_pe = df_sidra['populacao_total'].sum()
        media_pe = df_sidra['populacao_total'].mean()
        
        st.metric("População Total (PE)", f"{total_pe:,}")
        st.metric("Média por Município", f"{int(media_pe):,}")
        
        st.markdown("""
        ---
        **Nota Técnica:** A densidade populacional é um fator multiplicador do risco. 
        Áreas com alto TWI em municípios densamente povoados apresentam 
        maior potencial de danos humanos e materiais.
        """)

# ══════════════════════════════════════════════════════════════
#  HUB DE INTEGRAÇÃO DE DADOS EXTERNOS — v3.0
#  Renderizadores das abas Open-Meteo e IBGE SIDRA.
#  Chamados pelo app.py dentro da Sessão 4 (API Hub).
#  Cache por st.session_state: cada API é consultada uma única
#  vez por sessão, evitando requisições repetidas.
# ══════════════════════════════════════════════════════════════

from src.api import open_meteo as _open_meteo_mod
from src.api import ibge_sidra as _ibge_sidra_mod

_LIMIAR_ATENCAO_MM = 30.0
_LIMIAR_ALERTA_MM  = 60.0

_CORES_VULNERABILIDADE = {
    'CRITICA':  '#8B0000',
    'ALTA':     '#FF4500',
    'MODERADA': '#FFD700',
    'BAIXA':    '#1E90FF',
}


def render_openmeteo_hub(conf: dict, df_precip_csv=None):
    """
    Dashboard completo de monitoramento hidroclimático via API Open-Meteo.
    Cobre série temporal, ranking de saturação, projeção de risco e matriz
    de dados brutos. Utiliza st.session_state para cache inter-aba.
    """
    st.markdown("### Monitoramento Hidroclimático — Nowcasting e Forecasting")
    st.caption(
        "Precipitação diária extraída via API Open-Meteo: histórico dos últimos 7 dias "
        "e projeção para os próximos 7 dias. Dados alimentados por modelos numéricos globais "
        "de previsão do tempo (GFS, ICON, ERA5). Resolução temporal: 24 horas."
    )
    st.info(
        "Estações meteorológicas disponíveis nesta sessão: ARCO VERDE, CABACEIRAS, "
        "CAMPINA GRANDE, CARUARU, JOÃO PESSOA, MONTEIRO, PATOS e SURUBIM. "
        "Mais serão adicionadas em breve. "
        )

    with st.expander("Fundamentação Teórica — Precipitação como Variável de Forçamento Hidroclimático"):
        st.markdown("""
        O monitoramento contínuo da precipitação constitui a principal variável de entrada no
        diagnóstico dinâmico de suscetibilidade a inundações. No modelo TWI, o potencial de
        saturação pedológica é uma função da área de contribuição hídrica e da declividade
        local; porém, a efetivação desse potencial depende diretamente do volume hídrico
        acumulado no perfil de solo antecedente ao evento pluviométrico.

        A API Open-Meteo fornece estimativas de precipitação diária por ponto geográfico, com
        base em reanálises atmosféricas (ERA5) para o período histórico e em modelos de
        previsão numérica de tempo (NWP) para o período de projeção. A integração dessas
        séries temporais ao sistema ASI permite:

        - **Nowcasting**: identificação de acúmulos recentes que possam ter elevado o grau de
          saturação do solo nas zonas de alto TWI mapeadas;
        - **Forecasting**: antecipação de eventos de precipitação intensa, permitindo correlacionar
          a projeção pluviométrica com as áreas de maior convergência hídrica no modelo geomorfométrico;
        - **Análise de limiar crítico**: aplicação dos limiares operacionais de atenção (30 mm/7d)
          e alerta (60 mm/7d) definidos com base em critérios de saturação de bacia hidrográfica.
        """)

    if 'openmeteo_df' not in st.session_state:
        with st.spinner("Consultando API Open-Meteo para estações de Pernambuco..."):
            st.session_state['openmeteo_df'] = _open_meteo_mod.fetch_precipitacao_pe(df_precip_csv)

    df_rt = st.session_state['openmeteo_df']

    if df_rt is None or df_rt.empty:
        st.warning(
            "Não foi possível obter dados da API Open-Meteo neste momento. "
            "Verifique a conectividade de rede ou aguarde e recarregue a aba."
        )
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"
    hist = df_rt[df_rt['tipo'] == 'historico']
    prev = df_rt[df_rt['tipo'] == 'previsao']

    acum_7d     = hist['precipitacao_mm'].sum()
    estacao_top = hist.groupby('estacao')['precipitacao_mm'].sum().idxmax() if not hist.empty else '—'
    max_est_mm  = hist.groupby('estacao')['precipitacao_mm'].sum().max() if not hist.empty else 0.0
    prev_total  = prev['precipitacao_mm'].sum()
    n_alertas   = int(
        (hist.groupby('estacao')['precipitacao_mm'].sum() >= _LIMIAR_ALERTA_MM).sum()
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Carga Hídrica Acumulada (7d)", f"{acum_7d:.1f} mm")
    m2.metric("Epicentro Pluviométrico", estacao_top)
    m3.metric("Acumulado Máximo (Epicentro)", f"{max_est_mm:.1f} mm")
    m4.metric("Projeção Acumulada (Próx. 7d)", f"{prev_total:.1f} mm")
    m5.metric(
        "Estações em Nível de Alerta", n_alertas,
        delta="Risco Elevado" if n_alertas > 0 else "Normal",
        delta_color="inverse" if n_alertas > 0 else "normal"
    )

    st.markdown("---")

    sub1, sub2, sub3, sub4 = st.tabs([
        "Série Temporal de Precipitação",
        "Ranking de Saturação (7 Dias)",
        "Projeção de Risco (Próx. 7 Dias)",
        "Matriz de Dados Brutos"
    ])

    with sub1:
        estacoes = sorted(df_rt['estacao'].unique())
        sel = st.multiselect(
            "Filtrar Estações Meteorológicas",
            options=estacoes,
            default=estacoes[:5],
            key='hub_rt_estacoes'
        )
        df_sel = df_rt[df_rt['estacao'].isin(sel)].copy() if sel else df_rt.copy()
        df_sel['data'] = pd.to_datetime(df_sel['data'])

        fig_ts = px.line(
            df_sel, x='data', y='precipitacao_mm',
            color='estacao', line_dash='tipo', markers=True,
            title="Evolução Pluviométrica Diária — Histórico (ERA5) vs. Previsão (NWP)",
            labels={
                'data': 'Data de Referência',
                'precipitacao_mm': 'Volume Precipitado (mm/dia)',
                'estacao': 'Estação Meteorológica',
                'tipo': 'Vetor Analítico'
            }
        )
        hoje_ms = pd.Timestamp.now().normalize().timestamp() * 1000
        fig_ts.add_vline(
            x=hoje_ms, line_dash="dash", line_color="#00B4D8",
            annotation_text="Data de Referência (Hoje)",
            annotation_position="top right"
        )
        fig_ts.update_layout(template=tema, height=430)
        st.plotly_chart(fig_ts, use_container_width=True)
        st.caption(
            "Linha tracejada: projeção NWP. Linha sólida: reanálise ERA5. "
            "A linha vertical ciana demarca o ponto de inflexão entre dados históricos e projeção."
        )

    with sub2:
        ranking = (
            hist.groupby('estacao')['precipitacao_mm']
            .sum().reset_index()
            .sort_values('precipitacao_mm', ascending=True)
            .rename(columns={'precipitacao_mm': 'acumulado_7d_mm'})
        )
        ranking['classificacao'] = ranking['acumulado_7d_mm'].apply(
            lambda v: 'Saturação Crítica' if v >= _LIMIAR_ALERTA_MM
                      else ('Saturação de Atenção' if v >= _LIMIAR_ATENCAO_MM else 'Normal')
        )
        cores = ranking['acumulado_7d_mm'].apply(
            lambda v: '#FF1493' if v >= _LIMIAR_ALERTA_MM
                      else ('#FF8C00' if v >= _LIMIAR_ATENCAO_MM else '#1E90FF')
        ).tolist()

        fig_rank = go.Figure(go.Bar(
            x=ranking['acumulado_7d_mm'], y=ranking['estacao'],
            orientation='h', marker_color=cores,
            text=ranking['acumulado_7d_mm'].round(1), textposition='outside',
            hovertemplate="<b>%{y}</b><br>Volume Acumulado: %{x:.1f} mm<br>Classificação: %{customdata}<extra></extra>",
            customdata=ranking['classificacao']
        ))
        fig_rank.add_vline(x=_LIMIAR_ATENCAO_MM, line_dash="dot", line_color="#FF8C00",
                           annotation_text=f"Limiar de Atenção ({_LIMIAR_ATENCAO_MM} mm)")
        fig_rank.add_vline(x=_LIMIAR_ALERTA_MM, line_dash="dot", line_color="#FF1493",
                           annotation_text=f"Limiar Crítico ({_LIMIAR_ALERTA_MM} mm)")
        fig_rank.update_layout(
            template=tema,
            title="Carga Hidrológica Acumulada por Estação — Últimos 7 Dias",
            xaxis_title="Precipitação Acumulada (mm)",
            height=max(320, len(ranking) * 38),
            margin=dict(l=10, r=100, t=40, b=20)
        )
        st.plotly_chart(fig_rank, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.info(f"Normal: abaixo de {_LIMIAR_ATENCAO_MM} mm acumulados em 7 dias.")
        c2.warning(f"Atenção: {_LIMIAR_ATENCAO_MM}–{_LIMIAR_ALERTA_MM} mm acumulados.")
        c3.error(f"Crítico: acima de {_LIMIAR_ALERTA_MM} mm — risco de saturação pedológica.")

    with sub3:
        prev_rank = (
            prev.groupby('estacao')['precipitacao_mm']
            .sum().reset_index()
            .sort_values('precipitacao_mm', ascending=False)
            .rename(columns={'precipitacao_mm': 'previsao_7d_mm'})
        )
        fig_prev = px.bar(
            prev_rank, x='estacao', y='previsao_7d_mm',
            title="Estimativa de Precipitação por Estação — Projeção NWP (Próximos 7 Dias)",
            labels={'estacao': 'Estação Meteorológica', 'previsao_7d_mm': 'Precipitação Projetada (mm)'},
            color='previsao_7d_mm', color_continuous_scale='Blues'
        )
        fig_prev.add_hline(y=_LIMIAR_ATENCAO_MM, line_dash="dot", line_color="#FF8C00",
                           annotation_text="Limiar de Atenção")
        fig_prev.add_hline(y=_LIMIAR_ALERTA_MM, line_dash="dot", line_color="#FF1493",
                           annotation_text="Limiar Crítico")
        fig_prev.update_layout(template=tema, showlegend=False, height=400,
                               xaxis_tickangle=-45)
        st.plotly_chart(fig_prev, use_container_width=True)
        st.caption(
            "Projeção gerada por modelos NWP (GFS/ICON). A acurácia decresce progressivamente "
            "com o horizonte de previsão, sendo máxima nos primeiros 3 dias."
        )

        st.markdown("#### Correlação: Acumulado Histórico vs. Projeção")
        merged = pd.merge(
            hist.groupby('estacao')['precipitacao_mm'].sum().reset_index()
                .rename(columns={'precipitacao_mm': 'hist_7d'}),
            prev_rank, on='estacao', how='inner'
        )
        fig_corr_rt = px.scatter(
            merged, x='hist_7d', y='previsao_7d_mm', text='estacao',
            title="Dispersão: Histórico 7d × Projeção 7d por Estação",
            labels={'hist_7d': 'Precipitação Histórica (mm/7d)',
                    'previsao_7d_mm': 'Precipitação Projetada (mm/7d)'}
        )
        fig_corr_rt.update_traces(textposition='top center')
        fig_corr_rt.update_layout(template=tema, height=360)
        st.plotly_chart(fig_corr_rt, use_container_width=True)

    with sub4:
        st.markdown("#### Matriz Quantitativa de Precipitação — Open-Meteo API")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_est = st.multiselect(
                "Filtrar por Estação",
                options=sorted(df_rt['estacao'].unique()),
                default=[],
                key='hub_tabela_estacao'
            )
        with col_f2:
            filtro_vetor = st.selectbox(
                "Filtrar por Vetor Analítico",
                options=['Todos', 'Historico', 'Previsao'],
                key='hub_tabela_vetor'
            )

        df_table = df_rt.copy()
        df_table['data'] = df_table['data'].dt.strftime('%d/%m/%Y')
        df_table['tipo'] = df_table['tipo'].str.capitalize()
        df_table.rename(columns={
            'estacao': 'Estação', 'latitude': 'Latitude', 'longitude': 'Longitude',
            'data': 'Data', 'precipitacao_mm': 'Precipitação (mm)', 'tipo': 'Vetor'
        }, inplace=True)

        df_exib = df_table.copy()
        if filtro_est:
            df_exib = df_exib[df_exib['Estação'].isin(filtro_est)]
        if filtro_vetor != 'Todos':
            df_exib = df_exib[df_exib['Vetor'] == filtro_vetor]

        st.dataframe(
            df_exib[['Estação', 'Latitude', 'Longitude', 'Data', 'Precipitação (mm)', 'Vetor']],
            use_container_width=True, hide_index=True, height=420
        )
        st.caption(
            f"Total de registros exibidos: {len(df_exib)} | "
            "Fonte: Open-Meteo Forecast API (ERA5 + NWP). "
            "Unidade: mm de precipitação acumulada por dia."
        )
        
        col_refresh, _ = st.columns([1, 5])
        with col_refresh:
            if st.button("Atualizar Dados", key="btn_refresh_meteo"):
                if 'openmeteo_df' in st.session_state:
                    del st.session_state['openmeteo_df']
                    st.rerun()


def render_ibge_hub(conf: dict):
    """
    Dashboard completo de vulnerabilidade sociodemográfica via IBGE SIDRA.
    Integra população e saneamento do Censo 2022 em quatro sub-abas analíticas.
    Utiliza st.session_state para cache inter-aba.
    """
    st.markdown("### Diagnóstico de Vulnerabilidade Demográfica — Censo 2022")
    st.caption(
        "Dados extraídos do Sistema IBGE de Recuperação Automática (SIDRA). "
        "Tabelas: 6579 (População Residente) e 9543 (Saneamento Domiciliar). "
        "Recorte territorial: municípios de Pernambuco (código IBGE: 26)."
    )

    with st.expander("Fundamentação Teórica — Vulnerabilidade Social como Amplificador do Risco Geomorfométrico"):
        st.markdown("""
        A suscetibilidade geomorfométrica mensurada pelo TWI representa o potencial físico do
        terreno ao acúmulo hídrico. Contudo, a conversão desse potencial em risco efetivo para
        a população é modulada por fatores socioeconômicos e de infraestrutura. A densidade
        demográfica em zonas de alto TWI amplifica a magnitude dos danos humanos esperados, e
        a ausência de saneamento básico adequado intensifica a vulnerabilidade sanitária pós-evento.

        O índice de cobertura de esgotamento sanitário é utilizado como variável proxy de
        vulnerabilidade estrutural: municípios com alta proporção de domicílios sem coleta de
        esgoto apresentam maior risco de contaminação de corpos hídricos durante eventos de
        inundação, além de menor capacidade de resiliência e recuperação pós-desastre.

        A integração desta camada demográfica ao sistema ASI permite priorizar municípios onde
        o risco geomorfométrico (alto TWI) coincide com alta vulnerabilidade social, gerando
        uma matriz de criticidade composta para suporte à tomada de decisão em políticas
        públicas de proteção e defesa civil.
        """)

    if 'ibge_df' not in st.session_state:
        with st.spinner("Consultando API IBGE SIDRA — Censo Demográfico 2022..."):
            st.session_state['ibge_df'] = _ibge_sidra_mod.fetch_sidra_pe()

    df = st.session_state['ibge_df']

    if df is None or df.empty:
        st.warning(
            "Não foi possível obter dados do IBGE SIDRA neste momento. "
            "Verifique a conectividade ou aguarde e recarregue a aba."
        )
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    total_pop     = int(df['populacao'].sum())
    media_pop     = int(df['populacao'].mean())
    media_san     = df['perc_saneamento_adequado'].mean()
    n_criticos    = int((df['classe_vulnerabilidade'] == 'CRITICA').sum())
    mais_vulneravel = df.sort_values('perc_vulnerabilidade', ascending=False).iloc[0]['municipio']

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("População Total (PE)", f"{total_pop:,}")
    m2.metric("Média por Município", f"{media_pop:,}")
    m3.metric("Cobertura Média de Saneamento", f"{media_san:.1f}%")
    m4.metric(
        "Municípios com Vulnerabilidade Crítica", n_criticos,
        delta="Acima de 60% sem saneamento" if n_criticos > 0 else "Nenhum",
        delta_color="inverse" if n_criticos > 0 else "normal"
    )
    m5.metric("Maior Vulnerabilidade Sanitária", mais_vulneravel)

    st.markdown("---")

    sub1, sub2, sub3, sub4 = st.tabs([
        "Distribuição Populacional",
        "Vulnerabilidade Sanitária",
        "Análise Comparativa",
        "Matriz de Dados Censitários"
    ])

    with sub1:
        col1, col2 = st.columns([2, 1])
        with col1:
            top20 = df.sort_values('populacao', ascending=False).head(20)
            fig_pop = px.bar(
                top20, x='municipio', y='populacao',
                title="Top 20 Municípios por População Residente — Pernambuco (Censo 2022)",
                labels={'municipio': 'Município', 'populacao': 'Habitantes'},
                color='populacao', color_continuous_scale='Blues'
            )
            fig_pop.update_layout(template=tema, xaxis_tickangle=-45,
                                  margin=dict(l=20, r=20, t=40, b=80), height=420)
            st.plotly_chart(fig_pop, use_container_width=True)

        with col2:
            st.markdown("**Distribuição por Faixas Populacionais**")
            bins   = [0, 10_000, 50_000, 100_000, 500_000, float('inf')]
            labels_faixa = ['< 10 mil', '10–50 mil', '50–100 mil', '100–500 mil', '> 500 mil']
            df_faixa = df.copy()
            df_faixa['faixa_pop'] = pd.cut(df_faixa['populacao'], bins=bins, labels=labels_faixa)
            dist = df_faixa['faixa_pop'].value_counts().reset_index()
            dist.columns = ['Faixa', 'Municípios']
            fig_faixa = px.pie(dist, values='Municípios', names='Faixa', hole=0.45,
                               title="Composição por Porte Municipal")
            fig_faixa.update_layout(template=tema, height=320)
            st.plotly_chart(fig_faixa, use_container_width=True)

        st.caption(
            f"Universo amostral: {len(df)} municípios. "
            "Fonte: IBGE, Censo Demográfico 2022, Tabela SIDRA 6579."
        )

    with sub2:
        col1, col2 = st.columns([1.8, 1])
        with col1:
            top_vuln = df.sort_values('perc_vulnerabilidade', ascending=True).tail(25)
            cores_bar = [
                _CORES_VULNERABILIDADE.get(c, '#808080')
                for c in top_vuln['classe_vulnerabilidade']
            ]
            fig_san = go.Figure(go.Bar(
                x=top_vuln['perc_vulnerabilidade'], y=top_vuln['municipio'],
                orientation='h', marker_color=cores_bar,
                text=top_vuln['perc_vulnerabilidade'].round(1).astype(str) + '%',
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>Sem Saneamento: %{x:.1f}%<br>Classe: %{customdata}<extra></extra>",
                customdata=top_vuln['classe_vulnerabilidade']
            ))
            fig_san.add_vline(x=60.0, line_dash="dot", line_color="#8B0000",
                              annotation_text="Limiar Crítico (60%)")
            fig_san.add_vline(x=40.0, line_dash="dot", line_color="#FF4500",
                              annotation_text="Limiar Alto (40%)")
            fig_san.update_layout(
                template=tema,
                title="Top 25 Municípios — Proporção de Domicílios sem Saneamento Adequado",
                xaxis_title="% Domicílios sem Saneamento Adequado",
                height=max(350, len(top_vuln) * 26),
                margin=dict(l=10, r=120, t=40, b=20)
            )
            st.plotly_chart(fig_san, use_container_width=True)

        with col2:
            st.markdown("**Composição por Classe de Vulnerabilidade Sanitária**")
            dist_vuln = df['classe_vulnerabilidade'].value_counts().reset_index()
            dist_vuln.columns = ['Classe', 'Municípios']
            fig_vuln_pie = px.pie(
                dist_vuln, values='Municípios', names='Classe', hole=0.45,
                title="Vulnerabilidade Sanitária — PE",
                color='Classe', color_discrete_map=_CORES_VULNERABILIDADE
            )
            fig_vuln_pie.update_layout(template=tema, height=320)
            st.plotly_chart(fig_vuln_pie, use_container_width=True)

            st.markdown("""
**Critérios de Classificação:**

| Sem saneamento | Classe    |
|----------------|-----------|
| > 60%          | Crítica   |
| 40–60%         | Alta      |
| 20–40%         | Moderada  |
| < 20%          | Baixa     |
""")

    with sub3:
        st.markdown("#### Correlação: Vulnerabilidade Sanitária × Massa Populacional")
        st.caption(
            "Municípios no quadrante superior direito (alta população e baixo saneamento) "
            "apresentam o maior potencial de danos humanos em eventos de inundação."
        )
        fig_scatter_ibge = px.scatter(
            df, x='perc_vulnerabilidade', y='populacao',
            color='classe_vulnerabilidade', size='populacao', size_max=50,
            hover_name='municipio',
            hover_data={'perc_saneamento_adequado': ':.1f',
                        'perc_vulnerabilidade': ':.1f',
                        'populacao': True,
                        'classe_vulnerabilidade': False},
            title="Dispersão: Vulnerabilidade Sanitária × Massa Populacional (PE)",
            labels={
                'perc_vulnerabilidade': '% Domicílios sem Saneamento Adequado',
                'populacao': 'População Residente (hab.)',
                'classe_vulnerabilidade': 'Classe de Vulnerabilidade'
            },
            color_discrete_map=_CORES_VULNERABILIDADE
        )
        fig_scatter_ibge.add_vline(x=40.0, line_dash="dot", line_color="#FF4500",
                                   annotation_text="Limiar Alto")
        fig_scatter_ibge.add_vline(x=60.0, line_dash="dot", line_color="#8B0000",
                                   annotation_text="Limiar Crítico")
        fig_scatter_ibge.update_layout(template=tema, height=470)
        st.plotly_chart(fig_scatter_ibge, use_container_width=True)

        st.markdown("#### Distribuição de Frequência — Cobertura de Saneamento Adequado (%)")
        fig_hist_ibge = px.histogram(
            df, x='perc_saneamento_adequado', nbins=30,
            title="Frequência de Municípios por Faixa de Cobertura Sanitária",
            labels={'perc_saneamento_adequado': 'Cobertura de Saneamento Adequado (%)'},
            color_discrete_sequence=['#2e86c1']
        )
        fig_hist_ibge.update_layout(template=tema, height=320)
        st.plotly_chart(fig_hist_ibge, use_container_width=True)

    with sub4:
        st.markdown("#### Matriz Quantitativa — Dados Censitários por Município (Censo 2022)")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_classe = st.multiselect(
                "Filtrar por Classe de Vulnerabilidade",
                options=['CRITICA', 'ALTA', 'MODERADA', 'BAIXA'],
                default=[],
                key='hub_ibge_classe'
            )
        with col_f2:
            ordenar_por = st.selectbox(
                "Ordenar por",
                options=['Vulnerabilidade (desc)', 'População (desc)',
                         'Saneamento (asc)', 'Município (A-Z)'],
                key='hub_ibge_ordem'
            )

        df_tab = df.copy()
        if filtro_classe:
            df_tab = df_tab[df_tab['classe_vulnerabilidade'].isin(filtro_classe)]
        if ordenar_por == 'Vulnerabilidade (desc)':
            df_tab = df_tab.sort_values('perc_vulnerabilidade', ascending=False)
        elif ordenar_por == 'População (desc)':
            df_tab = df_tab.sort_values('populacao', ascending=False)
        elif ordenar_por == 'Saneamento (asc)':
            df_tab = df_tab.sort_values('perc_saneamento_adequado', ascending=True)
        else:
            df_tab = df_tab.sort_values('municipio', ascending=True)

        df_exib = df_tab[['municipio', 'populacao', 'perc_saneamento_adequado',
                           'perc_vulnerabilidade', 'classe_vulnerabilidade']].copy()
        df_exib.columns = ['Município', 'População (hab.)',
                           'Saneamento Adequado (%)', 'Vulnerabilidade (%)', 'Classe']
        df_exib['Saneamento Adequado (%)'] = df_exib['Saneamento Adequado (%)'].round(1)
        df_exib['Vulnerabilidade (%)']     = df_exib['Vulnerabilidade (%)'].round(1)

        st.dataframe(
            df_exib, use_container_width=True, hide_index=True, height=450
        )
        st.caption(
            f"Registros exibidos: {len(df_exib)} de {len(df)} municípios. "
            "Fonte: IBGE SIDRA — Tabelas 6579 e 9543 | Censo Demográfico 2022."
        )

# ══════════════════════════════════════════════════════════════
#  HUB — ABA 3: NASA POWER
# ══════════════════════════════════════════════════════════════

from src.api import nasa_power as _nasa_power_mod

_LIMIAR_ATENCAO_SOLO   = 0.60
_LIMIAR_SATURACAO_SOLO = 0.80

_CORES_SATURACAO = {
    'CRITICO':   '#8B0000',
    'ATENCAO':   '#FF8C00',
    'NORMAL':    '#1E90FF',
    'SEM DADOS': '#555555',
}


def render_nasa_hub(conf: dict):
    """
    Dashboard de parâmetros agrometeorológicos via NASA POWER API.
    Cobre umidade do solo, precipitação, temperatura, evapotranspiração
    e índice de saturação pedológica para estações de PE.
    Cache por st.session_state — carrega uma única vez por sessão.
    """
    st.markdown("### Parâmetros Agrometeorológicos e Saturação de Solo")
    st.caption(
        "Dados diários extraídos via NASA POWER API (MERRA-2 / MERRA-2 LAND). "
        "Histórico dos últimos 365 dias. Resolução espacial: ~0,5° × 0,625°. "
        "Parâmetros: precipitação, temperatura, umidade relativa, "
        "umidade do solo (superficial, radicular e perfil total) e evapotranspiração."
    )

    with st.expander("Fundamentação Teórica — Umidade do Solo como Variável de Saturação Pedológica"):
        st.markdown("""
        A umidade do solo é a variável de estado mais diretamente relacionada ao potencial
        de saturação pedológica e ao consequente escoamento superficial (Runoff). No contexto
        do modelo TWI, o potencial geomorfométrico de acúmulo hídrico só se converte em risco
        efetivo de inundação quando o perfil de solo já apresenta elevado grau de saturação.

        O NASA POWER disponibiliza três níveis de umidade derivados do modelo MERRA-2 LAND:

        - **GWETTOP** (0–5 cm): camada superficial — responde rapidamente a eventos de chuva,
          indicando saturação imediata e propensão ao escoamento superficial direto;
        - **GWETROOT** (0–100 cm): zona radicular — representa a capacidade de armazenamento
          de médio prazo, determinante para eventos pluviométricos subsequentes;
        - **GWETPROF** (perfil total): integra toda a coluna de solo, refletindo o estado
          hídrico estrutural da bacia.

        O **Índice de Saturação Pedológica (ISP)** calculado pelo ASI é uma média ponderada:
        ISP = 0,4 × GWETTOP + 0,6 × GWETROOT

        Valores de ISP acima de 0,60 indicam atenção hidrológica; acima de 0,80 indicam
        risco crítico de saturação e potencial de escoamento em cadeia em zonas de alto TWI.
        """)

    # ── Carregamento com cache de sessão ─────────────────────
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        if st.button("Atualizar Dados", key="btn_refresh_nasa"):
            if 'nasa_df' in st.session_state:
                del st.session_state['nasa_df']
            st.rerun()

    if 'nasa_df' not in st.session_state:
        with st.spinner("Consultando NASA POWER para estações de Pernambuco (pode levar ~30s)..."):
            st.session_state['nasa_df'] = _nasa_power_mod.fetch_nasa_power_pe()

    df = st.session_state['nasa_df']

    if df is None or df.empty:
        st.warning(
            "Não foi possível obter dados da NASA POWER neste momento. "
            "Verifique a conectividade ou utilize o botão Atualizar Dados."
        )
        return

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    # Janela recente (últimos 30 dias)
    df_rec  = df[df['janela'] == 'recente']
    df_hist = df[df['janela'] == 'historico']

    # ── Métricas de topo ──────────────────────────────────────
    isp_medio   = df_rec['indice_saturacao'].mean()
    isp_max_est = (
        df_rec.groupby('estacao')['indice_saturacao'].mean().idxmax()
        if not df_rec.empty else '—'
    )
    isp_max_val = (
        df_rec.groupby('estacao')['indice_saturacao'].mean().max()
        if not df_rec.empty else 0.0
    )
    n_criticos = int(
        (df_rec.groupby('estacao')['indice_saturacao'].mean() >= _LIMIAR_SATURACAO_SOLO).sum()
    )
    precip_rec  = df_rec['precipitacao_mm'].sum()
    evapo_rec   = df_rec['evapotranspiracao_mm'].sum()
    balanco     = precip_rec - evapo_rec if pd.notna(precip_rec) and pd.notna(evapo_rec) else None

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        "ISP Médio (Últimos 30d)",
        f"{isp_medio:.3f}" if pd.notna(isp_medio) else "—",
        help="Índice de Saturação Pedológica médio de todas as estações."
    )
    m2.metric("Estação Mais Saturada (30d)", isp_max_est)
    m3.metric("ISP Máximo (Epicentro)", f"{isp_max_val:.3f}" if pd.notna(isp_max_val) else "—")
    m4.metric(
        "Estações em Risco Crítico", n_criticos,
        delta="Saturação Crítica" if n_criticos > 0 else "Normal",
        delta_color="inverse" if n_criticos > 0 else "normal"
    )
    m5.metric(
        "Balanço Hídrico (30d)",
        f"{balanco:+.1f} mm" if balanco is not None else "—",
        help="Precipitação acumulada menos evapotranspiração acumulada (mm)."
    )

    st.markdown("---")

    sub1, sub2, sub3, sub4, sub5 = st.tabs([
        "Umidade do Solo",
        "Precipitação e Temperatura",
        "Balanço Hídrico",
        "Índice de Saturação Pedológica",
        "Matriz de Dados Brutos"
    ])

    # ── SUB-ABA 1: Umidade do Solo ────────────────────────────
    with sub1:
        estacoes = sorted(df['estacao'].unique())
        sel_est = st.multiselect(
            "Filtrar Estações",
            options=estacoes,
            default=estacoes[:4],
            key='nasa_est_solo'
        )
        df_sel = df[df['estacao'].isin(sel_est)].copy() if sel_est else df.copy()

        col1, col2 = st.columns(2)
        with col1:
            fig_gwet = px.line(
                df_sel.dropna(subset=['umidade_solo_superficial']),
                x='data', y='umidade_solo_superficial', color='estacao',
                title="Umidade Superficial do Solo — GWETTOP (0–5 cm)",
                labels={
                    'data': 'Data',
                    'umidade_solo_superficial': 'Umidade Superficial (fração)',
                    'estacao': 'Estação'
                }
            )
            fig_gwet.add_hline(
                y=_LIMIAR_ATENCAO_SOLO, line_dash="dot", line_color="#FF8C00",
                annotation_text="Limiar Atenção (0.60)"
            )
            fig_gwet.add_hline(
                y=_LIMIAR_SATURACAO_SOLO, line_dash="dot", line_color="#8B0000",
                annotation_text="Limiar Crítico (0.80)"
            )
            fig_gwet.update_layout(template=tema, height=380)
            st.plotly_chart(fig_gwet, use_container_width=True)

        with col2:
            fig_root = px.line(
                df_sel.dropna(subset=['umidade_solo_radicular']),
                x='data', y='umidade_solo_radicular', color='estacao',
                title="Umidade Zona Radicular — GWETROOT (0–100 cm)",
                labels={
                    'data': 'Data',
                    'umidade_solo_radicular': 'Umidade Radicular (fração)',
                    'estacao': 'Estação'
                }
            )
            fig_root.add_hline(
                y=_LIMIAR_ATENCAO_SOLO, line_dash="dot", line_color="#FF8C00",
                annotation_text="Limiar Atenção (0.60)"
            )
            fig_root.add_hline(
                y=_LIMIAR_SATURACAO_SOLO, line_dash="dot", line_color="#8B0000",
                annotation_text="Limiar Crítico (0.80)"
            )
            fig_root.update_layout(template=tema, height=380)
            st.plotly_chart(fig_root, use_container_width=True)

        # Perfil total de umidade
        fig_prof = px.line(
            df_sel.dropna(subset=['umidade_solo_perfil']),
            x='data', y='umidade_solo_perfil', color='estacao',
            title="Umidade Perfil Total do Solo — GWETPROF (Coluna Completa)",
            labels={
                'data': 'Data',
                'umidade_solo_perfil': 'Umidade Perfil Total (fração)',
                'estacao': 'Estação'
            }
        )
        fig_prof.update_layout(template=tema, height=340)
        st.plotly_chart(fig_prof, use_container_width=True)

        st.caption(
            "Valores em fração volumétrica (0 = solo seco, 1 = solo saturado). "
            "Fonte: NASA MERRA-2 LAND. Resolução: 0,5° × 0,625°."
        )

    # ── SUB-ABA 2: Precipitação e Temperatura ────────────────
    with sub2:
        sel_est2 = st.multiselect(
            "Filtrar Estações",
            options=estacoes,
            default=estacoes[:4],
            key='nasa_est_precip'
        )
        df_sel2 = df[df['estacao'].isin(sel_est2)].copy() if sel_est2 else df.copy()

        col1, col2 = st.columns(2)
        with col1:
            fig_precip = px.bar(
                df_sel2.dropna(subset=['precipitacao_mm']),
                x='data', y='precipitacao_mm', color='estacao',
                title="Precipitação Diária Corrigida — PRECTOTCORR (mm/dia)",
                labels={
                    'data': 'Data',
                    'precipitacao_mm': 'Precipitação (mm/dia)',
                    'estacao': 'Estação'
                },
                barmode='overlay', opacity=0.7
            )
            fig_precip.update_layout(template=tema, height=360)
            st.plotly_chart(fig_precip, use_container_width=True)

        with col2:
            fig_temp = px.line(
                df_sel2.dropna(subset=['temp_media']),
                x='data', y=['temp_max', 'temp_media', 'temp_min'],
                color_discrete_sequence=['#FF4500', '#FFD700', '#1E90FF'],
                facet_col='estacao' if len(sel_est2) <= 2 else None,
                title="Temperatura a 2m — T2M (°C)",
                labels={'data': 'Data', 'value': 'Temperatura (°C)', 'variable': 'Série'}
            )
            fig_temp.update_layout(template=tema, height=360)
            st.plotly_chart(fig_temp, use_container_width=True)

        # Umidade relativa
        fig_rh = px.line(
            df_sel2.dropna(subset=['umidade_relativa']),
            x='data', y='umidade_relativa', color='estacao',
            title="Umidade Relativa do Ar a 2m — RH2M (%)",
            labels={
                'data': 'Data',
                'umidade_relativa': 'Umidade Relativa (%)',
                'estacao': 'Estação'
            }
        )
        fig_rh.update_layout(template=tema, height=320)
        st.plotly_chart(fig_rh, use_container_width=True)

    # ── SUB-ABA 3: Balanço Hídrico ────────────────────────────
    with sub3:
        st.markdown("#### Balanço Hídrico por Estação — Precipitação vs. Evapotranspiração")
        st.caption(
            "O balanço hídrico positivo (Precipitação > Evapotranspiração) indica acúmulo "
            "de água no perfil do solo, aumentando a probabilidade de saturação pedológica "
            "em zonas de alto TWI."
        )

        df_balanco = (
            df.groupby('estacao')[['precipitacao_mm', 'evapotranspiracao_mm']]
            .sum()
            .reset_index()
        )
        df_balanco['balanco_hidrico'] = (
            df_balanco['precipitacao_mm'] - df_balanco['evapotranspiracao_mm']
        )
        df_balanco = df_balanco.sort_values('balanco_hidrico', ascending=True)
        df_balanco['cor'] = df_balanco['balanco_hidrico'].apply(
            lambda v: '#8B0000' if v > 200 else ('#FF8C00' if v > 0 else '#1E90FF')
        )

        col1, col2 = st.columns(2)
        with col1:
            fig_bal = go.Figure(go.Bar(
                x=df_balanco['balanco_hidrico'],
                y=df_balanco['estacao'],
                orientation='h',
                marker_color=df_balanco['cor'],
                text=df_balanco['balanco_hidrico'].round(1),
                textposition='outside',
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Balanço: %{x:.1f} mm<br>"
                    "<extra></extra>"
                )
            ))
            fig_bal.add_vline(x=0, line_dash="solid", line_color="#888888")
            fig_bal.update_layout(
                template=tema,
                title="Balanço Hídrico Anual por Estação (mm)",
                xaxis_title="Precipitação − Evapotranspiração (mm)",
                height=400,
                margin=dict(l=10, r=80, t=40, b=20)
            )
            st.plotly_chart(fig_bal, use_container_width=True)

        with col2:
            fig_bal2 = px.bar(
                df_balanco.melt(
                    id_vars='estacao',
                    value_vars=['precipitacao_mm', 'evapotranspiracao_mm'],
                    var_name='componente',
                    value_name='mm'
                ),
                x='estacao', y='mm', color='componente',
                barmode='group',
                title="Precipitação vs. Evapotranspiração Acumulada (365d)",
                labels={
                    'estacao': 'Estação',
                    'mm': 'Volume Acumulado (mm)',
                    'componente': 'Componente'
                },
                color_discrete_map={
                    'precipitacao_mm':      '#1E90FF',
                    'evapotranspiracao_mm': '#FF8C00'
                }
            )
            fig_bal2.update_layout(
                template=tema, height=400, xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bal2, use_container_width=True)

        # Evapotranspiração temporal
        sel_est3 = st.multiselect(
            "Filtrar Estações",
            options=estacoes,
            default=estacoes[:3],
            key='nasa_est_evapo'
        )
        df_sel3 = df[df['estacao'].isin(sel_est3)].copy() if sel_est3 else df.copy()
        fig_evapo = px.line(
            df_sel3.dropna(subset=['evapotranspiracao_mm']),
            x='data', y='evapotranspiracao_mm', color='estacao',
            title="Evapotranspiração Diária — EVPTRNS (mm/dia)",
            labels={
                'data': 'Data',
                'evapotranspiracao_mm': 'Evapotranspiração (mm/dia)',
                'estacao': 'Estação'
            }
        )
        fig_evapo.update_layout(template=tema, height=320)
        st.plotly_chart(fig_evapo, use_container_width=True)

    # ── SUB-ABA 4: Índice de Saturação Pedológica ─────────────
    with sub4:
        st.markdown("#### Índice de Saturação Pedológica (ISP) por Estação")
        st.caption(
            "ISP = 0,4 × GWETTOP + 0,6 × GWETROOT. "
            "Correlaciona diretamente com o risco de escoamento superficial em zonas de alto TWI."
        )

        # Série temporal do ISP
        sel_est4 = st.multiselect(
            "Filtrar Estações",
            options=estacoes,
            default=estacoes[:5],
            key='nasa_est_isp'
        )
        df_sel4 = df[df['estacao'].isin(sel_est4)].copy() if sel_est4 else df.copy()

        fig_isp = px.line(
            df_sel4.dropna(subset=['indice_saturacao']),
            x='data', y='indice_saturacao', color='estacao',
            title="Evolução do Índice de Saturação Pedológica (ISP) — 365 Dias",
            labels={
                'data': 'Data',
                'indice_saturacao': 'ISP (0–1)',
                'estacao': 'Estação'
            }
        )
        fig_isp.add_hline(
            y=_LIMIAR_ATENCAO_SOLO, line_dash="dot", line_color="#FF8C00",
            annotation_text=f"Atenção (ISP = {_LIMIAR_ATENCAO_SOLO})"
        )
        fig_isp.add_hline(
            y=_LIMIAR_SATURACAO_SOLO, line_dash="dot", line_color="#8B0000",
            annotation_text=f"Crítico (ISP = {_LIMIAR_SATURACAO_SOLO})"
        )
        fig_isp.update_layout(template=tema, height=420)
        st.plotly_chart(fig_isp, use_container_width=True)

        # Ranking de ISP médio (últimos 30 dias)
        st.markdown("#### Ranking de ISP Médio — Últimos 30 Dias")
        isp_rank = (
            df_rec.groupby('estacao')['indice_saturacao']
            .mean()
            .reset_index()
            .sort_values('indice_saturacao', ascending=True)
            .dropna()
        )
        isp_rank['classe'] = isp_rank['indice_saturacao'].apply(
            lambda v: 'CRITICO' if v >= _LIMIAR_SATURACAO_SOLO
                      else ('ATENCAO' if v >= _LIMIAR_ATENCAO_SOLO else 'NORMAL')
        )
        cores_isp = [_CORES_SATURACAO.get(c, '#555') for c in isp_rank['classe']]

        fig_rank_isp = go.Figure(go.Bar(
            x=isp_rank['indice_saturacao'],
            y=isp_rank['estacao'],
            orientation='h',
            marker_color=cores_isp,
            text=isp_rank['indice_saturacao'].round(3),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>ISP Médio: %{x:.3f}<extra></extra>"
        ))
        fig_rank_isp.add_vline(x=_LIMIAR_ATENCAO_SOLO, line_dash="dot", line_color="#FF8C00")
        fig_rank_isp.add_vline(x=_LIMIAR_SATURACAO_SOLO, line_dash="dot", line_color="#8B0000")
        fig_rank_isp.update_layout(
            template=tema,
            title="Ranking de Saturação Pedológica por Estação (Últimos 30 Dias)",
            xaxis_title="ISP Médio (0–1)",
            height=max(300, len(isp_rank) * 38),
            margin=dict(l=10, r=80, t=40, b=20)
        )
        st.plotly_chart(fig_rank_isp, use_container_width=True)

        col_l1, col_l2, col_l3 = st.columns(3)
        col_l1.info(f"Normal: ISP abaixo de {_LIMIAR_ATENCAO_SOLO}")
        col_l2.warning(f"Atenção: ISP entre {_LIMIAR_ATENCAO_SOLO} e {_LIMIAR_SATURACAO_SOLO}")
        col_l3.error(f"Crítico: ISP acima de {_LIMIAR_SATURACAO_SOLO} — risco de escoamento")

    # ── SUB-ABA 5: Matriz de Dados Brutos ─────────────────────
    with sub5:
        st.markdown("#### Matriz Quantitativa — Parâmetros NASA POWER por Estação")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_est5 = st.multiselect(
                "Filtrar por Estação",
                options=estacoes,
                default=[],
                key='nasa_tabela_estacao'
            )
        with col_f2:
            filtro_janela = st.selectbox(
                "Período",
                options=['Todos (365d)', 'Recente (30d)', 'Histórico (365d−30d)'],
                key='nasa_tabela_janela'
            )
        with col_f3:
            filtro_col = st.selectbox(
                "Ordenar por",
                options=['data', 'indice_saturacao', 'precipitacao_mm',
                         'umidade_solo_superficial', 'evapotranspiracao_mm'],
                key='nasa_tabela_ordem'
            )

        df_tab = df.copy()
        if filtro_est5:
            df_tab = df_tab[df_tab['estacao'].isin(filtro_est5)]
        if filtro_janela == 'Recente (30d)':
            df_tab = df_tab[df_tab['janela'] == 'recente']
        elif filtro_janela == 'Histórico (365d−30d)':
            df_tab = df_tab[df_tab['janela'] == 'historico']
        df_tab = df_tab.sort_values(filtro_col, ascending=False)

        cols_exib = ['estacao', 'data', 'precipitacao_mm', 'temp_media',
                     'umidade_relativa', 'umidade_solo_superficial',
                     'umidade_solo_radicular', 'evapotranspiracao_mm',
                     'indice_saturacao', 'classe_saturacao']
        df_exib = df_tab[cols_exib].copy()
        df_exib['data'] = df_exib['data'].dt.strftime('%d/%m/%Y')

        # Arredondamentos
        for col_num in ['precipitacao_mm', 'temp_media', 'umidade_relativa',
                        'umidade_solo_superficial', 'umidade_solo_radicular',
                        'evapotranspiracao_mm', 'indice_saturacao']:
            df_exib[col_num] = pd.to_numeric(df_exib[col_num], errors='coerce').round(3)

        df_exib.columns = [
            'Estação', 'Data', 'Precip. (mm)', 'Temp. Média (°C)',
            'Umid. Relativa (%)', 'GWETTOP', 'GWETROOT',
            'Evapo. (mm)', 'ISP', 'Classe'
        ]

        st.dataframe(df_exib, use_container_width=True, hide_index=True, height=450)
        st.caption(
            f"Registros exibidos: {len(df_exib)} | "
            "Fonte: NASA POWER API — MERRA-2 / MERRA-2 LAND. "
            "Valores -999 substituídos por NaN."
        )