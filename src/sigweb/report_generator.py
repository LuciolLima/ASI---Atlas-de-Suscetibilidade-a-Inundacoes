"""
SISTEMA ASI - GERADOR DE RELATÓRIOS
Gera diagnósticos textuais baseados em atributos do ponto.
"""

from src.sigweb import config

def generate_technical_report(row):
    """Gera HTML para o painel de detalhes."""
    
    classe = str(row['Classe_Risco_Cod'])
    cor = config.COLORS.get(classe, '#333')
    label = row.get('Classe_Risco_Label', 'Não Classificado')
    
    # Textos de recomendação
    if classe == 'CRITICO':
        rec = "Área de saturação extrema. Requer intervenção de drenagem e restrição construtiva imediata."
    elif classe == 'ALTO':
        rec = "Alto potencial de alagamento. Monitorar em eventos pluviométricos severos."
    elif classe == 'MODERADO':
        rec = "Área de atenção. Verificar sistemas de microdrenagem locais."
    else:
        rec = "Condição hidrológica estável sob parâmetros normais."

    html = f"""
    <div style="border-left: 5px solid {cor}; background: #1f1f1f; padding: 15px; border-radius: 4px;">
        <h3 style="color: {cor}; margin-top: 0; font-family: 'Segoe UI';">{label}</h3>
        <p style="font-size: 0.9em; color: #ccc;">
            <b>Local:</b> {row.get('NM_BAIRRO', 'N/A')}<br>
            <b>Uso do Solo:</b> {row.get('Uso_Solo_Desc', 'N/A')}<br>
            <b>Situação:</b> {row.get('Situacao_Urbana', 'N/A')}
        </p>
        <hr style="border-color: #444;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8em; margin-bottom: 10px;">
            <span>TWI: <b>{row.get('twi', 0):.2f}</b></span>
            <span>Declividade: <b>{row.get('Slope', 0):.2f}°</b></span>
            <span>Altitude: <b>{row.get('mdt_fill_M', 0):.1f}m</b></span>
        </div>
        <div style="background: #2b2b2b; padding: 10px; font-size: 0.85em; color: #ddd; border-radius: 4px;">
            <b>DIAGNÓSTICO TÉCNICO:</b><br>{rec}
        </div>
    </div>
    """
    return html