"""SISTEMA ASI — VISUALIZAÇÕES PARA APIs EXTERNAS
Versão: 1.0 — Gráficos Plotly profissionais para Open-Meteo, NASA POWER, IBGE SIDRA
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional

from src.sigweb import config
from src.core.error_boundary import analytics_error_boundary


# ════════════════════════════════════════════════════════════════════════════════
# PALETA DE CORES ASI
# ════════════════════════════════════════════════════════════════════════════════

ASI_COLORS = {
    'primary': '#2E86C1',
    'secondary': '#00B4D8',
    'critical': '#8B0000',
    'high': '#FF4500',
    'moderate': '#FFD700',
    'low': '#1E90FF',
    'very_low': '#ADD8E6',
    'background': '#080C10',
    'surface': '#0D1219',
    'border': '#1C2A38',
    'border_hi': '#2E4A64',
    'text': '#C8D6E0',
    'text_dim': '#5A7A8A',
    'success': '#2ECC71',
    'warning': '#F39C12',
}

# Sequências de cores para gráficos categóricos
RISK_COLOR_SEQ = ['#8B0000', '#FF4500', '#FFD700', '#1E90FF', '#ADD8E6']
API_COLOR_SEQ = ['#2E86C1', '#00B4D8', '#E74C3C', '#F39C12', '#2ECC71', '#9B59B6']


# ════════════════════════════════════════════════════════════════════════════════
# LAYOUT BASE PARA GRÁFICOS
# ════════════════════════════════════════════════════════════════════════════════

def get_asi_layout(title: str = "", height: int = 400, **kwargs) -> Dict[str, Any]:
    """Retorna layout padrão ASI para gráficos Plotly."""
    layout = {
        'title': {
            'text': title,
            'font': {'family': 'IBM Plex Sans', 'size': 14, 'color': ASI_COLORS['text']},
            'x': 0.02,
        },
        'paper_bgcolor': ASI_COLORS['background'],
        'plot_bgcolor': ASI_COLORS['surface'],
        'font': {'family': 'IBM Plex Sans', 'color': ASI_COLORS['text'], 'size': 11},
        'height': height,
        'margin': {'l': 60, 'r': 30, 't': 50, 'b': 50},
        'xaxis': {
            'gridcolor': ASI_COLORS['border'],
            'zerolinecolor': ASI_COLORS['border'],
            'linecolor': ASI_COLORS['border_hi'],
            'title_font': {'family': 'IBM Plex Mono', 'size': 11, 'color': ASI_COLORS['text_dim']},
            'tickfont': {'family': 'IBM Plex Mono', 'size': 10, 'color': ASI_COLORS['text_dim']},
        },
        'yaxis': {
            'gridcolor': ASI_COLORS['border'],
            'zerolinecolor': ASI_COLORS['border'],
            'linecolor': ASI_COLORS['border_hi'],
            'title_font': {'family': 'IBM Plex Mono', 'size': 11, 'color': ASI_COLORS['text_dim']},
            'tickfont': {'family': 'IBM Plex Mono', 'size': 10, 'color': ASI_COLORS['text_dim']},
        },
        'legend': {
            'bgcolor': 'rgba(13,18,25,0.8)',
            'bordercolor': ASI_COLORS['border'],
            'borderwidth': 1,
            'font': {'family': 'IBM Plex Sans', 'size': 10, 'color': ASI_COLORS['text']},
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.15,
            'xanchor': 'center',
            'x': 0.5,
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': ASI_COLORS['surface'],
            'bordercolor': ASI_COLORS['border'],
            'font': {'family': 'IBM Plex Sans', 'size': 11},
        },
    }
    layout.update(kwargs)
    return layout


def apply_asi_style(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    """Aplica estilo ASI a uma figura existente."""
    fig.update_layout(get_asi_layout(title, height))
    return fig


# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICOS OPEN-METEO
# ════════════════════════════════════════════════════════════════════════════════

def plot_open_meteo_precipitation(df: pd.DataFrame, station: str = "ESTAÇÃO", 
                                   forecast_df: pd.DataFrame | None = None) -> go.Figure:
    """Gráfico de precipitação histórica + previsão."""
    fig = go.Figure()
    
    # Histórico - barras
    if not df.empty and 'precipitacao_mm' in df.columns:
        fig.add_trace(go.Bar(
            x=df['data'],
            y=df['precipitacao_mm'],
            name='Precipitação (Histórico)',
            marker_color='rgba(46, 134, 193, 0.6)',
            marker_line=dict(color=ASI_COLORS['primary'], width=0.5),
            hovertemplate='%{x|%d/%m/%Y %H:%M}<br>Precipitação: %{y:.1f} mm<extra></extra>',
        ))
    
    # Previsão - linha + área
    if forecast_df is not None and not forecast_df.empty and 'precipitacao_mm' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=forecast_df['data'],
            y=forecast_df['precipitacao_mm'],
            mode='lines+markers',
            name='Previsão',
            line=dict(color=ASI_COLORS['warning'], width=2, dash='dot'),
            marker=dict(size=5, color=ASI_COLORS['warning']),
            fill='tozeroy',
            fillcolor='rgba(243, 156, 18, 0.15)',
            hovertemplate='%{x|%d/%m/%Y %H:%M}<br>Previsto: %{y:.1f} mm<extra></extra>',
        ))
        
        # Probabilidade de precipitação se disponível
        if 'probabilidade_precipitacao_pct' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['data'],
                y=forecast_df['probabilidade_precipitacao_pct'],
                mode='lines',
                name='Prob. Precip. (%)',
                line=dict(color='rgba(243, 156, 18, 0.5)', width=1, dash='dash'),
                yaxis='y2',
                hovertemplate='%{x|%d/%m/%Y %H:%M}<br>Prob: %{y:.0f}%<extra></extra>',
            ))
    
    fig.update_layout(
        get_asi_layout(
            f"🌧️ Precipitação — {station}",
            height=450,
            yaxis_title="Precipitação (mm)",
            yaxis2=dict(
                title="Probabilidade (%)",
                overlaying='y',
                side='right',
                range=[0, 100],
                showgrid=False,
                tickfont=dict(family='IBM Plex Mono', size=10, color=ASI_COLORS['text_dim']),
                title_font=dict(family='IBM Plex Mono', size=11, color=ASI_COLORS['text_dim']),
            ),
        )
    )
    return fig


def plot_open_meteo_temperature(df: pd.DataFrame, station: str = "ESTAÇÃO",
                                 forecast_df: pd.DataFrame | None = None) -> go.Figure:
    """Gráfico de temperatura (min/max/média) com banda de variação."""
    fig = go.Figure()
    
    # Histórico
    if not df.empty:
        if 'temperatura_2m_max' in df.columns and 'temperatura_2m_min' in df.columns:
            # Banda min-max
            fig.add_trace(go.Scatter(
                x=pd.concat([df['data'], df['data'][::-1]]),
                y=pd.concat([df['temperatura_2m_max'], df['temperatura_2m_min'][::-1]]),
                fill='toself',
                fillcolor='rgba(46, 134, 193, 0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Faixa Min-Max (Histórico)',
                hoverinfo='skip',
                showlegend=True,
            ))
        
        if 'temperatura_2m_max' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df['temperatura_2m_max'],
                mode='lines', name='Máxima (Histórico)',
                line=dict(color=ASI_COLORS['high'], width=1.5),
                hovertemplate='%{x|%d/%m/%Y}<br>Máx: %{y:.1f}°C<extra></extra>',
            ))
        if 'temperatura_2m_min' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df['temperatura_2m_min'],
                mode='lines', name='Mínima (Histórico)',
                line=dict(color=ASI_COLORS['low'], width=1.5),
                hovertemplate='%{x|%d/%m/%Y}<br>Mín: %{y:.1f}°C<extra></extra>',
            ))
        if 'temperatura_2m' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df['temperatura_2m'],
                mode='lines', name='Média (Histórico)',
                line=dict(color=ASI_COLORS['primary'], width=2),
                hovertemplate='%{x|%d/%m/%Y}<br>Média: %{y:.1f}°C<extra></extra>',
            ))
    
    # Previsão
    if forecast_df is not None and not forecast_df.empty:
        if 'temperatura_2m_max' in forecast_df.columns and 'temperatura_2m_min' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=pd.concat([forecast_df['data'], forecast_df['data'][::-1]]),
                y=pd.concat([forecast_df['temperatura_2m_max'], forecast_df['temperatura_2m_min'][::-1]]),
                fill='toself',
                fillcolor='rgba(243, 156, 18, 0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Faixa Min-Max (Previsão)',
                hoverinfo='skip',
                showlegend=True,
            ))
        if 'temperatura_2m_max' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['data'], y=forecast_df['temperatura_2m_max'],
                mode='lines+markers', name='Máxima (Previsão)',
                line=dict(color=ASI_COLORS['high'], width=2, dash='dot'),
                marker=dict(size=4, symbol='diamond'),
                hovertemplate='%{x|%d/%m/%Y}<br>Máx Prevista: %{y:.1f}°C<extra></extra>',
            ))
        if 'temperatura_2m_min' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['data'], y=forecast_df['temperatura_2m_min'],
                mode='lines+markers', name='Mínima (Previsão)',
                line=dict(color=ASI_COLORS['low'], width=2, dash='dot'),
                marker=dict(size=4, symbol='diamond'),
                hovertemplate='%{x|%d/%m/%Y}<br>Mín Prevista: %{y:.1f}°C<extra></extra>',
            ))
    
    fig.update_layout(
        get_asi_layout(
            f"🌡️ Temperatura — {station}",
            height=400,
            yaxis_title="Temperatura (°C)",
        )
    )
    return fig


def plot_open_meteo_multi_station(df: pd.DataFrame) -> go.Figure:
    """Gráfico comparativo multi-estação (precipitação acumulada + temperatura média)."""
    if df.empty or 'estacao' not in df.columns:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Precipitação Total por Estação', 'Temperatura Média por Estação'),
        vertical_spacing=0.12,
        specs=[[{"type": "bar"}], [{"type": "box"}]],
    )
    
    stations = sorted(df['estacao'].unique())
    colors = API_COLOR_SEQ[:len(stations)]
    
    # Precipitação total por estação
    precip_totals = df.groupby('estacao')['precipitacao_mm'].sum().reset_index()
    for i, station in enumerate(stations):
        station_data = precip_totals[precip_totals['estacao'] == station]
        if not station_data.empty:
            fig.add_trace(go.Bar(
                x=[station_data['estacao'].iloc[0]],
                y=[station_data['precipitacao_mm'].iloc[0]],
                name=station,
                marker_color=colors[i % len(colors)],
                showlegend=True,
                hovertemplate=f'{station}<br>Total: %{{y:.1f}} mm<extra></extra>',
            ), row=1, col=1)
    
    # Box plot de temperatura por estação
    if 'temperatura_2m_max' in df.columns:
        for i, station in enumerate(stations):
            station_df = df[df['estacao'] == station]
            if not station_df.empty and 'temperatura_2m_max' in station_df.columns:
                fig.add_trace(go.Box(
                    y=station_df['temperatura_2m_max'],
                    name=station,
                    marker_color=colors[i % len(colors)],
                    showlegend=False,
                    boxpoints='outliers',
                    hovertemplate=f'{station}<br>Temp: %{{y:.1f}}°C<extra></extra>',
                ), row=2, col=1)
    
    fig.update_layout(
        get_asi_layout("📊 Comparativo Multi-Estações", height=550),
        barmode='group',
        showlegend=True,
    )
    fig.update_xaxes(title_text="", row=1, col=1)
    fig.update_yaxes(title_text="Precipitação Total (mm)", row=1, col=1)
    fig.update_yaxes(title_text="Temp. Máxima (°C)", row=2, col=1)
    return fig


# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICOS NASA POWER
# ════════════════════════════════════════════════════════════════════════════════

def plot_nasa_power_overview(df: pd.DataFrame, station: str = "ESTAÇÃO") -> go.Figure:
    """Dashboard 2x2 com os principais indicadores NASA POWER."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '☀️ Radiação Solar (GHI / Céu Limpo)', 
            '💧 Umidade do Solo (3 Camadas)',
            '🌡️ Temperatura (Máx / Mín / Média)',
            '🌧️ Precipitação vs Evapotranspiração'
        ),
        vertical_spacing=0.1,
        horizontal_spacing=0.08,
    )
    
    # 1. Radiação Solar
    if 'rad_solar_todo_céu_kwh_m2_dia' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['data'], y=df['rad_solar_todo_céu_kwh_m2_dia'],
            mode='lines', name='GHI (Todo Céu)',
            line=dict(color=ASI_COLORS['warning'], width=1.5),
            fill='tozeroy', fillcolor='rgba(243, 156, 18, 0.1)',
        ), row=1, col=1)
    if 'rad_solar_céu_limpo_kwh_m2_dia' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['data'], y=df['rad_solar_céu_limpo_kwh_m2_dia'],
            mode='lines', name='Céu Limpo',
            line=dict(color=ASI_COLORS['primary'], width=1, dash='dot'),
        ), row=1, col=1)
    
    # 2. Umidade do Solo (3 camadas)
    soil_cols = {
        'umidade_solo_superficial': ('0-5 cm', ASI_COLORS['critical']),
        'umidade_solo_radicular': ('0-100 cm', ASI_COLORS['high']),
        'umidade_solo_perfil': ('Perfil Total', ASI_COLORS['moderate']),
    }
    for col, (label, color) in soil_cols.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df[col],
                mode='lines', name=f'Umidade {label}',
                line=dict(color=color, width=1.5),
            ), row=1, col=2)
    # Linha de saturação crítica
    fig.add_hline(y=0.85, line_dash="dash", line_color=ASI_COLORS['critical'], 
                  line_width=1, annotation_text="Saturação Crítica (0.85)",
                  row=1, col=2)
    
    # 3. Temperatura
    temp_cols = {
        't2m_max': ('Máxima', ASI_COLORS['high']),
        't2m_media': ('Média', ASI_COLORS['primary']),
        't2m_min': ('Mínima', ASI_COLORS['low']),
    }
    for col, (label, color) in temp_cols.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df[col],
                mode='lines', name=f'T {label}',
                line=dict(color=color, width=1.5),
            ), row=2, col=1)
    
    # 4. Precipitação vs ET0
    if 'precipitacao_mm' in df.columns:
        fig.add_trace(go.Bar(
            x=df['data'], y=df['precipitacao_mm'],
            name='Precipitação (P)',
            marker_color='rgba(46, 134, 193, 0.6)',
        ), row=2, col=2)
    if 'et0_fao_evapotranspiracao_mm' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['data'], y=df['et0_fao_evapotranspiracao_mm'],
            mode='lines+markers', name='ET₀',
            line=dict(color=ASI_COLORS['warning'], width=2, dash='dot'),
            marker=dict(size=3),
        ), row=2, col=2)
    
    fig.update_layout(
        get_asi_layout(f"🛰️ NASA POWER — {station}", height=600),
        barmode='overlay',
    )
    fig.update_yaxes(title_text="Radiação (kWh/m²/dia)", row=1, col=1)
    fig.update_yaxes(title_text="Umidade (0-1)", row=1, col=2)
    fig.update_yaxes(title_text="Temperatura (°C)", row=2, col=1)
    fig.update_yaxes(title_text="mm/dia", row=2, col=2)
    return fig


def plot_nasa_power_soil_moisture(df: pd.DataFrame, station: str = "ESTAÇÃO") -> go.Figure:
    """Gráfico dedicado à umidade do solo com zonas de risco."""
    fig = go.Figure()
    
    # Zonas de risco como background
    fig.add_hrect(y0=0.85, y1=1.0, fillcolor=ASI_COLORS['critical'], opacity=0.1,
                  annotation_text="CRÍTICO (>0.85)", annotation_position="left")
    fig.add_hrect(y0=0.70, y1=0.85, fillcolor=ASI_COLORS['high'], opacity=0.1,
                  annotation_text="ATENÇÃO (0.70-0.85)", annotation_position="left")
    fig.add_hrect(y0=0.30, y1=0.70, fillcolor=ASI_COLORS['moderate'], opacity=0.05,
                  annotation_text="NORMAL (0.30-0.70)", annotation_position="left")
    fig.add_hrect(y0=0, y1=0.30, fillcolor=ASI_COLORS['low'], opacity=0.1,
                  annotation_text="SECO (<0.30)", annotation_position="left")
    
    soil_cols = {
        'umidade_solo_superficial': ('Superficial (0-5 cm)', ASI_COLORS['critical']),
        'umidade_solo_radicular': ('Radicular (0-100 cm)', ASI_COLORS['high']),
        'umidade_solo_perfil': ('Perfil Total', ASI_COLORS['moderate']),
    }
    
    for col, (label, color) in soil_cols.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['data'], y=df[col],
                mode='lines', name=label,
                line=dict(color=color, width=2),
                hovertemplate=f'{label}<br>%{{x|%d/%m/%Y}}<br>Umidade: %{{y:.2f}}<extra></extra>',
            ))
    
    # Média móvel 7 dias para tendência
    if 'umidade_solo_superficial' in df.columns:
        df_smooth = df.copy()
        df_smooth['ma7'] = df_smooth['umidade_solo_superficial'].rolling(7, center=True).mean()
        fig.add_trace(go.Scatter(
            x=df_smooth['data'], y=df_smooth['ma7'],
            mode='lines', name='Média Móvel 7d (Superficial)',
            line=dict(color=ASI_COLORS['secondary'], width=2, dash='dash'),
            hovertemplate='MM7 Superficial<br>%{x|%d/%m/%Y}: %{y:.2f}<extra></extra>',
        ))
    
    fig.update_layout(
        get_asi_layout(f"💧 Umidade do Solo (NASA POWER) — {station}", height=400,
                       yaxis_title="Umidade Volumétrica (0-1)",
                       yaxis=dict(range=[0, 1.05])),
    )
    return fig


def plot_nasa_power_water_balance(df: pd.DataFrame, station: str = "ESTAÇÃO") -> go.Figure:
    """Balanço hídrico: P - ET₀ - ΔUmidade."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Balanço Hídrico Diário (P - ET₀)', 'Déficit/Excedente Acumulado'),
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4],
    )
    
    if not all(c in df.columns for c in ['precipitacao_mm', 'et0_fao_evapotranspiracao_mm']):
        return fig
    
    # Balanço diário
    balance = df['precipitacao_mm'] - df['et0_fao_evapotranspiracao_mm']
    
    # Barras coloridas por sinal
    colors = [ASI_COLORS['success'] if b >= 0 else ASI_COLORS['critical'] for b in balance]
    
    fig.add_trace(go.Bar(
        x=df['data'], y=balance,
        name='Balanço (P - ET₀)',
        marker_color=colors,
        hovertemplate='%{x|%d/%m/%Y}<br>Balanço: %{y:.1f} mm<extra></extra>',
    ), row=1, col=1)
    
    # Linha zero
    fig.add_hline(y=0, line_dash="dash", line_color=ASI_COLORS['text_dim'], row=1, col=1)
    
    # Linhas de P e ET0
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['precipitacao_mm'],
        mode='lines', name='Precipitação (P)',
        line=dict(color=ASI_COLORS['primary'], width=1.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['et0_fao_evapotranspiracao_mm'],
        mode='lines', name='ET₀',
        line=dict(color=ASI_COLORS['warning'], width=1.5, dash='dot'),
    ), row=1, col=1)
    
    # Acumulado
    cumulative = balance.cumsum()
    colors_cum = [ASI_COLORS['success'] if c >= 0 else ASI_COLORS['critical'] for c in cumulative]
    fig.add_trace(go.Bar(
        x=df['data'], y=cumulative,
        name='Acumulado',
        marker_color=colors_cum,
        hovertemplate='%{x|%d/%m/%Y}<br>Acumulado: %{y:.1f} mm<extra></extra>',
    ), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color=ASI_COLORS['text_dim'], row=2, col=1)
    
    fig.update_layout(
        get_asi_layout(f"⚖️ Balanço Hídrico (NASA POWER) — {station}", height=500),
        barmode='overlay',
    )
    fig.update_yaxes(title_text="Balanço Diário (mm)", row=1, col=1)
    fig.update_yaxes(title_text="Acumulado (mm)", row=2, col=1)
    return fig


# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICOS IBGE SIDRA
# ════════════════════════════════════════════════════════════════════════════════

def plot_ibge_sidra_population(df: pd.DataFrame) -> go.Figure:
    """Gráfico de população por município (top 15)."""
    if df.empty or 'populacao_total' not in df.columns:
        return go.Figure()
    
    df_top = df.nlargest(15, 'populacao_total').sort_values('populacao_total')
    
    fig = go.Figure(go.Bar(
        x=df_top['populacao_total'] / 1000,
        y=df_top['municipio'],
        orientation='h',
        marker_color=ASI_COLORS['primary'],
        hovertemplate='%{y}<br>População: %{x:,.0f} mil<extra></extra>',
    ))
    
    fig.update_layout(
        get_asi_layout("👥 Top 15 Municípios — População (Censo 2022)", height=500),
        xaxis_title="População (mil habitantes)",
        yaxis={'categoryorder': 'total ascending'},
    )
    return fig


def plot_ibge_sidra_sanitation(df: pd.DataFrame) -> go.Figure:
    """Gráfico de saneamento adequado (%) - scatter population vs saneamento."""
    if df.empty or 'perc_saneamento_adequado' not in df.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    # Colorir por classe de vulnerabilidade se disponível
    if 'classe_vulnerabilidade' in df.columns:
        color_map = {
            'CRITICA': ASI_COLORS['critical'],
            'ALTA': ASI_COLORS['high'],
            'MODERADA': ASI_COLORS['moderate'],
            'BAIXA': ASI_COLORS['low'],
            'SEM DADOS': ASI_COLORS['text_dim'],
        }
        colors = df['classe_vulnerabilidade'].map(color_map).fillna(ASI_COLORS['text_dim'])
    else:
        colors = ASI_COLORS['primary']
    
    fig.add_trace(go.Scatter(
        x=df['populacao_total'] / 1000,
        y=df['perc_saneamento_adequado'],
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='rgba(255,255,255,0.3)'),
            opacity=0.8,
        ),
        text=df['municipio'],
        hovertemplate='<b>%{text}</b><br>Pop: %{x:,.0f} mil<br>Saneamento: %{y:.1f}%<extra></extra>',
    ))
    
    # Linha de referência 80%
    fig.add_hline(y=80, line_dash="dash", line_color=ASI_COLORS['success'],
                  annotation_text="Meta Saneamento Adequado (80%)", annotation_position="left")
    
    fig.update_layout(
        get_asi_layout("🚿 Saneamento vs População (IBGE SIDRA)", height=500),
        xaxis_title="População (mil hab)",
        yaxis_title="% Saneamento Adequado",
        yaxis=dict(range=[0, 105]),
    )
    return fig


def plot_ibge_sidra_vulnerability(df: pd.DataFrame) -> go.Figure:
    """Gráfico de vulnerabilidade por município."""
    if df.empty or 'classe_vulnerabilidade' not in df.columns:
        return go.Figure()
    
    order = ['CRITICA', 'ALTA', 'MODERADA', 'BAIXA', 'SEM DADOS']
    df['classe_vulnerabilidade'] = pd.Categorical(df['classe_vulnerabilidade'], categories=order, ordered=True)
    df_sorted = df.sort_values('classe_vulnerabilidade')
    
    color_map = {
        'CRITICA': ASI_COLORS['critical'],
        'ALTA': ASI_COLORS['high'],
        'MODERADA': ASI_COLORS['moderate'],
        'BAIXA': ASI_COLORS['low'],
        'SEM DADOS': ASI_COLORS['text_dim'],
    }
    
    fig = go.Figure(go.Bar(
        y=df_sorted['municipio'],
        x=df_sorted['perc_vulnerabilidade'],
        orientation='h',
        marker_color=[color_map[c] for c in df_sorted['classe_vulnerabilidade']],
        hovertemplate='<b>%{y}</b><br>Vulnerabilidade: %{x:.1f}%<extra></extra>',
    ))
    
    fig.update_layout(
        get_asi_layout("⚠️ Vulnerabilidade Social por Município (IBGE SIDRA)", height=600),
        xaxis_title="Índice de Vulnerabilidade (%)",
        xaxis=dict(range=[0, 105]),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════════
# RENDERIZADOR DO API HUB
# ════════════════════════════════════════════════════════════════════════════════

def render_api_hub_dashboard() -> None:
    """Renderiza o dashboard completo do Hub de Dados Externos."""
    from src.api.open_meteo import (
        fetch_precipitacao_pe_cached,
        fetch_precipitacao_forecast_cached,
        fetch_multi_estacoes_pe_cached,
    )
    from src.api.nasa_power import (
        fetch_nasa_power_pe_cached,
        fetch_nasa_power_historico_cached,
    )
    from src.api.ibge_sidra import fetch_sidra_consolidado_cached
    from src.core.error_boundary import analytics_error_boundary
    
    st.markdown("## 🌐 Hub de Dados Externos — Visualizações")
    
    # Tabs para cada API
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌤️ Open-Meteo", 
        "🛰️ NASA POWER", 
        "📊 IBGE SIDRA", 
        "🔄 Comparativo"
    ])
    
    with tab1:
        _render_open_meteo_tab()
    
    with tab2:
        _render_nasa_power_tab()
    
    with tab3:
        _render_ibge_sidra_tab()
    
    with tab4:
        _render_comparativo_tab()


@analytics_error_boundary("Erro ao carregar Open-Meteo")
def _render_open_meteo_tab() -> None:
    from src.api.open_meteo import (
        fetch_precipitacao_pe_cached,
        fetch_precipitacao_forecast_cached,
        fetch_multi_estacoes_pe_cached,
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        station = st.selectbox(
            "Estação",
            ["RECIFE", "CABO_DE_SANTO_AGOSTINHO", "JABOATAO_DOS_GUARARAPES", 
             "OLINDA", "PAULISTA", "CARUARU", "PETROLINA", "GARANHUNS"],
            key="om_station"
        )
    with col2:
        days_back = st.slider("Dias históricos", 7, 90, 30, key="om_days")
    
    # Carrega dados
    with st.spinner("Carregando Open-Meteo..."):
        hist = fetch_precipitacao_pe_cached(station, days_back)
        forecast = fetch_precipitacao_forecast_cached(station, 7)
        multi = fetch_multi_estacoes_pe_cached(days_back=days_back)
    
    # Gráfico Precipitação
    if hist.success and hist.data is not None:
        fig = plot_open_meteo_precipitation(hist.data, station, 
                                            forecast.data if forecast.success else None)
        st.plotly_chart(fig, use_container_width=True)
    
    # Temperatura
    col1, col2 = st.columns(2)
    with col1:
        if hist.success and hist.data is not None:
            fig_temp = plot_open_meteo_temperature(hist.data, station,
                                                   forecast.data if forecast.success else None)
            st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        if multi.success and multi.data is not None:
            fig_multi = plot_open_meteo_multi_station(multi.data)
            st.plotly_chart(fig_multi, use_container_width=True)
    
    # Métricas rápidas
    if hist.success and hist.data is not None:
        df = hist.data
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📍 Estação", station)
        col2.metric("🌧️ Precip Total", f"{df['precipitacao_mm'].sum():.1f} mm")
        col3.metric("🌡️ Temp Média", f"{df.get('temperatura_2m_media', pd.Series([0])).mean():.1f}°C")
        col4.metric("📊 Registros", len(df))


@analytics_error_boundary("Erro ao carregar NASA POWER")
def _render_nasa_power_tab() -> None:
    from src.api.nasa_power import (
        fetch_nasa_power_pe_cached,
        fetch_nasa_power_historico_cached,
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        station = st.selectbox(
            "Estação",
            ["RECIFE", "CABO_DE_SANTO_AGOSTINHO", "JABOATAO_DOS_GUARARAPES",
             "OLINDA", "PAULISTA", "CARUARU", "PETROLINA", "GARANHUNS"],
            key="np_station"
        )
    with col2:
        years = st.slider("Anos de histórico", 1, 10, 2, key="np_years")
    
    with st.spinner("Carregando NASA POWER..."):
        recent = fetch_nasa_power_pe_cached(station, 30)
        historico = fetch_nasa_power_historico_cached(station, years)
    
    # Overview 2x2
    if recent.success and recent.data is not None:
        fig_overview = plot_nasa_power_overview(recent.data, station)
        st.plotly_chart(fig_overview, use_container_width=True)
    
    # Solo
    col1, col2 = st.columns(2)
    with col1:
        if recent.success and recent.data is not None:
            fig_soil = plot_nasa_power_soil_moisture(recent.data, station)
            st.plotly_chart(fig_soil, use_container_width=True)
    
    with col2:
        if recent.success and recent.data is not None:
            fig_water = plot_nasa_power_water_balance(recent.data, station)
            st.plotly_chart(fig_water, use_container_width=True)
    
    # Histórico longo
    if historico.success and historico.data is not None:
        st.markdown("### 📈 Histórico Longo (Anos)")
        df_hist = historico.data
        fig_hist = make_subplots(rows=2, cols=1, subplot_titles=('Precipitação Anual', 'Temp Média Anual'))
        
        annual_precip = df_hist.groupby(df_hist['data'].dt.year)['precipitacao_mm'].sum()
        fig_hist.add_trace(go.Bar(x=annual_precip.index, y=annual_precip.values, name='Precipitação'), row=1, col=1)
        
        annual_temp = df_hist.groupby(df_hist['data'].dt.year)['t2m_media'].mean()
        fig_hist.add_trace(go.Scatter(x=annual_temp.index, y=annual_temp.values, mode='lines+markers', name='Temp Média', line=dict(color=ASI_COLORS['warning'])), row=2, col=1)
        
        fig_hist.update_layout(get_asi_layout(f"📈 Histórico {years} Anos — {station}", height=500))
        st.plotly_chart(fig_hist, use_container_width=True)


@analytics_error_boundary("Erro ao carregar IBGE SIDRA")
def _render_ibge_sidra_tab() -> None:
    from src.api.ibge_sidra import fetch_sidra_consolidado_cached
    
    with st.spinner("Carregando IBGE SIDRA..."):
        consolidated = fetch_sidra_consolidado_cached()
    
    if consolidated.success and consolidated.data is not None:
        df = consolidated.data
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏙️ Municípios", len(df))
        col2.metric("👥 Pop Total", f"{df['populacao_total'].sum():,.0f}")
        col3.metric("🚿 Saneamento Médio", f"{df['perc_saneamento_adequado'].mean():.1f}%")
        col4.metric("⚠️ Vuln. Média", f"{df['perc_vulnerabilidade'].mean():.1f}%")
        
        # Gráficos
        tab1, tab2, tab3 = st.tabs(["👥 População", "🚿 Saneamento", "⚠️ Vulnerabilidade"])
        
        with tab1:
            fig_pop = plot_ibge_sidra_population(df)
            st.plotly_chart(fig_pop, use_container_width=True)
        
        with tab2:
            fig_san = plot_ibge_sidra_sanitation(df)
            st.plotly_chart(fig_san, use_container_width=True)
        
        with tab3:
            fig_vuln = plot_ibge_sidra_vulnerability(df)
            st.plotly_chart(fig_vuln, use_container_width=True)
        
        # Tabela
        st.markdown("### 📋 Dados Consolidados")
        st.dataframe(
            df[['municipio', 'populacao_total', 'perc_saneamento_adequado', 'perc_vulnerabilidade', 'classe_vulnerabilidade']],
            use_container_width=True,
            column_config={
                'municipio': 'Município',
                'populacao_total': st.column_config.NumberColumn('População', format="%d"),
                'perc_saneamento_adequado': st.column_config.NumberColumn('Saneamento (%)', format="%.1f"),
                'perc_vulnerabilidade': st.column_config.NumberColumn('Vulnerabilidade (%)', format="%.1f"),
                'classe_vulnerabilidade': 'Classe',
            },
        )
    else:
        st.error(f"Falha ao carregar IBGE SIDRA: {consolidated.error}")
        st.info("A API do IBGE SIDRA pode estar temporariamente indisponível (503). Tente novamente mais tarde.")


@analytics_error_boundary("Erro no comparativo")
def _render_comparativo_tab() -> None:
    st.markdown("### 🔄 Comparativo Multi-Fonte")
    st.info("Esta seção combina dados de múltiplas fontes para análise integrada.")
    
    # Placeholder para futuro desenvolvimento
    st.markdown("""
    **Em desenvolvimento:**
    - Correlação TWI × Precipitação (Open-Meteo/NASA)
    - Vulnerabilidade Social × Risco Hidrológico
    - Série temporal unificada multi-fonte
    - Alertas baseados em múltiplos indicadores
    """)


# ════════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Open-Meteo
    'plot_open_meteo_precipitation',
    'plot_open_meteo_temperature',
    'plot_open_meteo_multi_station',
    # NASA POWER
    'plot_nasa_power_overview',
    'plot_nasa_power_soil_moisture',
    'plot_nasa_power_water_balance',
    # IBGE SIDRA
    'plot_ibge_sidra_population',
    'plot_ibge_sidra_sanitation',
    'plot_ibge_sidra_vulnerability',
    # Hub
    'render_api_hub_dashboard',
    # Utils
    'get_asi_layout',
    'apply_asi_style',
    'ASI_COLORS',
]