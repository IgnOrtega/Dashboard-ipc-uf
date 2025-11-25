import plotly.graph_objects as go
import formato


def crear_figura(x_uf,y_uf,name_uf,x_ipc,y_ipc,name_ipc, title_plot, tipo_funcion="1"):

    # Crear figura
    fig = go.Figure()

    
    fig.add_trace(go.Scatter(
        x=x_uf,
        y=y_uf,
        mode='lines',
        name=name_uf
    ))

    fig.add_trace(go.Scatter(
        x=x_ipc,
        y=y_ipc,
        mode='lines',
        name=name_ipc
    ))


    # Configuración del hover vertical
    fig.update_layout(
        hovermode='x unified',   # Hover vertical unificado
        hoverlabel=dict(
            bgcolor="white",     # Fondo del tooltip
            font_size=12,
            font_family="Arial"
        ),
        template='plotly_white', # Tema visual limpio
        title= title_plot
    )
    

    if tipo_funcion=="porc":
        fig.update_yaxes(tickformat=',.2%')    
    else:
        fig.update_yaxes(tickformat=".4~s")
    return fig


def tarjeta_kpi(profit, mom_change,bool_delta=True,porcentaje_profit=False, porcentaje_delta=False,medida_nombre="kpi",label_delta=""):
    # Formateos equivalentes
    _profit = profit
    _change = mom_change
    _sign = "▲" if mom_change >= 0 else "▼"
    _sign_color = "green" if mom_change >= 0 else "red"

    _profit=formato.formatear_numero(_profit, decimales=2, porcentaje=porcentaje_profit, separador_miles=True)
    _change=formato.formatear_numero(_change, decimales=2, porcentaje=porcentaje_delta, separador_miles=True)    
    _profit=_profit.replace(",",":")
    _profit=_profit.replace(".",",")
    _profit=_profit.replace(":",".")

    _change=_change.replace(",",":")
    _change=_change.replace(".",",")
    _change=_change.replace(":",".")

    html_inicio="""
<table style='width:200px; height:150px; border:1px solid; 
            border-color:#d3d3d300; border-radius: 15px;
            background-color:#eff066'>
<tbody>
"""

    medida_principal=f"""
<tr style='border: 0px solid rgba(211, 211, 211, 0)';>
    <td style='width: 2%; border: 0px solid rgba(211, 211, 211, 0);'></td>
    <td style='width: 98%; border: 0px solid rgba(211, 211, 211, 0); color: black'>
        {medida_nombre} &emsp;
        <b> 
            <span style='font-size:30px'>
                {_profit}
            </span> 
        </b>
    </td>
</tr>
"""

    medida_delta=f"""
<tr style='border: 0px solid rgba(211, 211, 211, 0)';>
    <td style='width: 2%; border: 0px solid rgba(211, 211, 211, 0)';></td>
    <td style='width: 98%; border: 0px solid rgba(211, 211, 211, 0)';>
        <span style='color:{_sign_color}; font-size: 18px;"'>
            {_sign}
        </span>
        <b>
            <span style='font-size:14px; color:black'>
                {_change}
            </span>
        </b>
        <span style='font-size:12px; color:black'>&nbsp; {label_delta}</span>
    </td>
</tr>
"""
    html_final="""
</tbody>
</table>
"""
    if bool_delta:
        codigo_html=html_inicio+ medida_principal+medida_delta+html_final
    else:
        codigo_html=html_inicio+ medida_principal +html_final
    return codigo_html


