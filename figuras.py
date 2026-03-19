import plotly.graph_objects as go
import formato

def crear_figura_comparativa(x_uf, y_uf, name_uf, x_ipc, y_ipc, name_ipc, title_plot, es_porcentaje=False):
    """
    Genera un gráfico con fondo neutro adaptativo y barra de herramientas visible.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_uf, y=y_uf, mode='lines', name=name_uf,
        line=dict(width=3, color='#007bff')
    ))

    fig.add_trace(go.Scatter(
        x=x_ipc, y=y_ipc, mode='lines', name=name_ipc,
        line=dict(width=3, color='#ff7f0e')
    ))

    fig.update_layout(
        hovermode='x unified',
        title=dict(
            text=title_plot,
            x=0.02,
            font=dict(size=18)
        ),
        
        # Fondo adaptativo
        paper_bgcolor='rgba(128, 128, 128, 0.12)', 
        plot_bgcolor='rgba(128, 128, 128, 0.05)',
        
        font=dict(family="Source Sans Pro, sans-serif"),
        
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=0.98,
            bgcolor='rgba(0,0,0,0)'
        ),
        
        margin=dict(l=20, r=20, t=60, b=40),
        
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(128, 128, 128, 0.2)',
            linecolor='rgba(128, 128, 128, 0.3)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(128, 128, 128, 0.2)',
            linecolor='rgba(128, 128, 128, 0.3)',
            zeroline=False,
            tickformat=',.2%' if es_porcentaje else ".4~s"
        ),

        # CORRECCIÓN DE BARRA DE HERRAMIENTAS (Modebar):
        # Forzamos un color que sea visible en ambos temas.
        modebar=dict(
            bgcolor='rgba(0,0,0,0)', # Fondo transparente
            color='#888',           # Gris medio para los iconos
            activecolor='#007bff'   # Azul cuando se pasa el mouse
        )
    )
    
    return fig

def tarjeta_kpi(valor_principal, delta, bool_delta=True, es_porcentaje_valor=False, 
                es_porcentaje_delta=False, nombre_medida="KPI", etiqueta_delta=""):
    """
    Genera una tarjeta KPI con fondo neutro adaptativo.
    """
    color_subida = "#28a745"
    color_bajada = "#dc3545"
    
    signo = "▲" if delta >= 0 else "▼"
    color_signo = color_subida if delta >= 0 else color_bajada

    txt_valor = formato.formatear_numero(valor_principal, decimales=2, porcentaje=es_porcentaje_valor)
    txt_delta = formato.formatear_numero(delta, decimales=2, porcentaje=es_porcentaje_delta)

    # Construir el HTML sin indentaciones extra que puedan romper el renderizado de st.markdown
    html_card = (
        f'<div style="padding: 20px; border-radius: 12px; background-color: rgba(128, 128, 128, 0.15); '
        f'border: 1px solid rgba(128, 128, 128, 0.2); font-family: \'Source Sans Pro\', sans-serif; '
        f'min-height: 120px; display: flex; flex-direction: column; justify-content: center; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
        f'<div style="font-size: 0.85rem; font-weight: 500; color: #888; margin-bottom: 5px; '
        f'text-transform: uppercase; letter-spacing: 0.5px;">{nombre_medida}</div>'
        f'<div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 5px; line-height: 1.2;">{txt_valor}</div>'
    )

    if bool_delta:
        html_card += (
            f'<div style="display: flex; align-items: center; gap: 5px; margin-top: auto;">'
            f'<span style="color: {color_signo}; font-size: 1rem;">{signo}</span>'
            f'<span style="font-size: 0.95rem; font-weight: 600; color: {color_signo};">{txt_delta}</span>'
            f'<span style="font-size: 0.75rem; color: #888; margin-left: 2px;">{etiqueta_delta}</span>'
            f'</div>'
        )
    
    html_card += "</div>"
    return html_card
