import streamlit as st
import metricas
import figuras
import formato 




#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----
#-----                      Cargar datos 
#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----
dir="./data/IPC_empalmadas/"
filename="ipc_2009.csv"
ipc_mensual=formato.cargar_ipc_empalmadas(dir, filename)

dir = "./data/UF/"
uf_diario=formato.concadenar_datos_uf(dir)
uf_diario=uf_diario.dropna()
uf_diario=uf_diario.reset_index()
cols=uf_diario.columns
dict_name={cols[1]:"UF"}
uf_diario=uf_diario.rename(mapper=dict_name, axis=1)
uf_mensual=metricas.obtener_uf_por_periodo(uf_diario)                  # Obtener UF por periodos mensuales


# Valores tarjetas kpi
valor_uf_hoy=metricas.obtener_valor_uf_hoy(uf_diario)                  # Obtener Valor de UF de Hoy

uf_ultimo_periodo=metricas.obtener_ultimo_periodo(uf_mensual)          # Obtener valor UF ultimo periodo
ipc_ultimo_periodo=metricas.obtener_ultimo_periodo(ipc_mensual)        # Obtener valor IPC ultimo periodo

uf_ultima_var_mensual=metricas.obtener_ultima_var_mensual(uf_mensual)  # 
ipc_ultima_var_mensual=metricas.obtener_ultima_var_mensual(ipc_mensual)

uf_ultima_var_anual=metricas.obtener_var_accum(uf_mensual)
ipc_ultima_var_anual=metricas.obtener_var_accum(ipc_mensual)


#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----
#-----                      Inicio Dashboard
#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----
# Definir valores por defecto del widget del gráfico 2.
DEFAULT_VALUES = {
    "suavizado": "Ninguno",  # Valor predeterminado para el radio button
    "window": 1,             # Valor predeterminado para el slider
    "periocidad": "Anual",             
}
# --- 2. Funciones de Estado y Reset ---
def initialize_session_state():
    """Inicializa el estado de sesión con los valores predeterminados si no existen."""
    for key, default_value in DEFAULT_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def reset_filters():
    """Función que sobrescribe los valores del estado de sesión con los predeterminados.
    
    Esta función se asigna al argumento 'on_click' del botón Reset.
    """
    for key, default_value in DEFAULT_VALUES.items():
        st.session_state[key] = default_value

# Inicializamos el estado ANTES de que se ejecuten los widgets
initialize_session_state()

# --- Configuración de la página ---
st.set_page_config(page_title="Dashboard UF/IPC", page_icon="📊", layout="wide")

st.title("Dashboard Comparación UF e IPC")



# Parte 1: target card
st.markdown("## Medidas claves de UF e IPC")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1,1,1])  # col2 será el doble de ancho que col1 y col3
with col1:
    medida_nombre="UF de Hoy"
    code_html=figuras.tarjeta_kpi(valor_uf_hoy, valor_uf_hoy,bool_delta=False, medida_nombre=medida_nombre)
    st.markdown(code_html,unsafe_allow_html=True)    

with col2:
    medida_nombre="Último Periodo UF"
    code_html=figuras.tarjeta_kpi(uf_ultimo_periodo, uf_ultima_var_mensual, porcentaje_profit=False, porcentaje_delta=True,medida_nombre=medida_nombre, label_delta="Var. Último Mes.")
    st.markdown(code_html,unsafe_allow_html=True)    

with col3:
    medida_nombre="Var. Anual Acum. UF"        
    code_html=figuras.tarjeta_kpi(uf_ultima_var_anual, uf_ultima_var_anual,porcentaje_profit=True,bool_delta=False,medida_nombre=medida_nombre)
    st.markdown(code_html,unsafe_allow_html=True)    

with col4:
    medida_nombre="Último Periodo IPC"
    code_html=figuras.tarjeta_kpi(ipc_ultimo_periodo, ipc_ultima_var_mensual,porcentaje_profit=False,porcentaje_delta=True,medida_nombre=medida_nombre, label_delta="Var. Último Mes.")
    st.markdown(code_html,unsafe_allow_html=True)     

with col5:
    medida_nombre="Var. Anual Acum. IPC"        
    code_html=figuras.tarjeta_kpi(ipc_ultima_var_anual, ipc_ultima_var_anual,porcentaje_profit=True,medida_nombre=medida_nombre,bool_delta=False)
    st.markdown(code_html,unsafe_allow_html=True)     



# Parte 2: Grafica UF e IPC
st.markdown("## Comparación entre valor UF y IPC")

x_uf=uf_mensual["Fecha"]
y_uf=uf_mensual["UF"]
name_uf="UF"
x_ipc=ipc_mensual["Fecha"]
y_ipc=ipc_mensual["IPC"]*1_000/3
name_ipc="IPC x1000 /3"
title_plot="Comparación UF v/s IPC"
fig=figuras.crear_figura(x_uf,y_uf,name_uf,x_ipc,y_ipc,name_ipc, title_plot)
st.plotly_chart(fig, use_container_width=True)  


# Parte 3: Grafica Var. UF e IPC
st.markdown("## Comparación entre variación valor UF y IPC")
col1, col2, col3, col4 = st.columns([0.5,1, 1, 1])

with col1:
    # Radio Button vinculado a st.session_state["suavizado"]
    periocidad = st.radio(
        "Periocidad:",
        ["Mensual", "Anual"],
        horizontal=False,
        key="periocidad"
    )

with col2:
    suavizado = st.radio(
        "Aplicar suavizado:",
        ["Ninguno", "Media móvil", "Mediana móvil"],
        horizontal=False,
        key="suavizado"
    )

with col3: 
    window = st.slider(
        "Tamaño de ventana de suavizado:",
        min_value=1,
        max_value=10,
        step=1,
        key="window" 
    )

# --- Botón de reset (Soft Reset) ---
with col4:
    # Usamos on_click para ejecutar la función de reseteo, que cambiará los valores en st.session_state
    st.button(
        "🔁 Reiniciar Filtros",
        on_click=reset_filters,
        type="primary"
    )

uf_periodo=metricas.var_por_periodo(uf_mensual,periocidad)   # Cambio de periocidad 
ipc_periodo=metricas.var_por_periodo(ipc_mensual,periocidad) # Cambio de periocidad

uf_periodo=formato.suavizamiento_funcion(uf_periodo, suavizado,window)   # Suavizamiento
ipc_periodo=formato.suavizamiento_funcion(ipc_periodo, suavizado,window) # Suavizamiento

x_uf=uf_periodo["Fecha"]
x_ipc=ipc_periodo["Fecha"]

y_uf=uf_periodo["Var_porc_UF"]
y_ipc=ipc_periodo["Var_porc_IPC"]

name_uf="Var. UF%"
name_ipc="Var. IPC%"
title_plot="Comparación Variación UF v/s IPC"
fig=figuras.crear_figura(x_uf,y_uf,name_uf,x_ipc,y_ipc,name_ipc, title_plot, tipo_funcion="porc")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")



