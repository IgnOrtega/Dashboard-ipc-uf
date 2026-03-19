import streamlit as st
import metricas
import figuras
import formato 

# --- Configuración de la página ---
st.set_page_config(page_title="Dashboard UF/IPC", page_icon="📊", layout="wide")

# --- 1. Carga de datos con Caché ---
@st.cache_data
def load_data():
    """
    Carga y procesa los datos históricos de IPC y UF desde archivos locales.
    Utiliza el decorador @st.cache_data para evitar procesamientos repetitivos.

    Returns:
        tuple: (uf_diario, uf_mensual, ipc_mensual) DataFrames procesados.
    """
    dir_ipc = "./data/IPC_empalmadas/"
    filename_ipc = "ipc_2009.csv"
    ipc_mensual = formato.cargar_ipc_empalmadas(dir_ipc, filename_ipc)

    dir_uf = "./data/UF/"
    uf_diario = formato.concatenar_datos_uf(dir_uf)
    uf_mensual = metricas.obtener_uf_mensual(uf_diario)
    
    return uf_diario, uf_mensual, ipc_mensual

uf_diario, uf_mensual, ipc_mensual = load_data()

# --- 2. Cálculo de métricas clave ---
valor_uf_hoy = metricas.obtener_valor_uf_hoy(uf_diario)
uf_ultimo_periodo = metricas.obtener_ultimo_valor(uf_mensual)
ipc_ultimo_periodo = metricas.obtener_ultimo_valor(ipc_mensual)

# Asegurar valores numéricos para evitar problemas en el renderizado HTML
uf_ultima_var_mensual = metricas.calcular_variacion_mensual(uf_mensual) or 0.0
ipc_ultima_var_mensual = metricas.calcular_variacion_mensual(ipc_mensual) or 0.0

uf_ultima_var_anual = metricas.calcular_variacion_anual_acumulada(uf_mensual) or 0.0
ipc_ultima_var_anual = metricas.calcular_variacion_anual_acumulada(ipc_mensual) or 0.0

# --- 3. Gestión de Estado de la Sesión ---
DEFAULT_VALUES = {
    "suavizado": "Ninguno",
    "window": 1,
    "periodicidad": "Anual",
}

def initialize_session_state():
    """
    Inicializa las variables de estado de la sesión de Streamlit con valores por defecto.
    """
    for key, val in DEFAULT_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = val

def reset_filters():
    """
    Reinicia los filtros de la aplicación (suavizado, ventana y periodicidad) a sus valores iniciales.
    """
    for key, val in DEFAULT_VALUES.items():
        st.session_state[key] = val

initialize_session_state()

# --- 4. Interfaz Principal ---
st.title("Dashboard Comparación UF e IPC")

# Parte 1: Tarjetas KPI
st.markdown("## Medidas claves de UF e IPC")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    nombre_medida="UF de Hoy"
    code_HTML_figura=figuras.tarjeta_kpi(valor_uf_hoy, 0, bool_delta=False, nombre_medida=nombre_medida)
    st.markdown(code_HTML_figura ,unsafe_allow_html=True)    

with col2:
    code_HTML_figura=figuras.tarjeta_kpi(uf_ultimo_periodo, uf_ultima_var_mensual, 
                                    es_porcentaje_delta=True, nombre_medida="Último Periodo UF", 
                                    etiqueta_delta="Var. Último Mes")

    st.markdown(code_HTML_figura, unsafe_allow_html=True)    

with col3:
    st.markdown(figuras.tarjeta_kpi(uf_ultima_var_anual, 0, bool_delta=False, 
                                    es_porcentaje_valor=True, nombre_medida="Var. Anual Acum. UF"), unsafe_allow_html=True)    

with col4:
    st.markdown(figuras.tarjeta_kpi(ipc_ultimo_periodo, ipc_ultima_var_mensual, 
                                    es_porcentaje_delta=True, nombre_medida="Último Periodo IPC", 
                                    etiqueta_delta="Var. Último Mes"), unsafe_allow_html=True)     

with col5:
    st.markdown(figuras.tarjeta_kpi(ipc_ultima_var_anual, 0, bool_delta=False, 
                                    es_porcentaje_valor=True, nombre_medida="Var. Anual Acum. IPC"), unsafe_allow_html=True)     

# Parte 2: Gráfico de Valores Absolutos
st.markdown("## Comparación entre valor UF y IPC")
st.info("Nota: El IPC se escala por un factor de 1000/3 para facilitar la comparación visual directa con el valor de la UF.")

x_uf = uf_mensual["Fecha"]
y_uf = uf_mensual["UF"]
x_ipc = ipc_mensual["Fecha"]
y_ipc = ipc_mensual["IPC"] * 1000 / 3

fig_valores = figuras.crear_figura_comparativa(
    x_uf, y_uf, "UF", 
    x_ipc, y_ipc, "IPC (escalado)", 
    "Comparación Histórica de Niveles"
)
st.plotly_chart(fig_valores, use_container_width=True)  

# Parte 3: Análisis de Variaciones
st.markdown("## Análisis de Variación Porcentual")
c1, c2, c3, c4 = st.columns([0.5, 1, 1, 1])

with c1:
    st.radio("Periodicidad:", ["Mensual", "Anual"], key="periodicidad")

with c2:
    st.radio("Suavizado:", ["Ninguno", "Media móvil", "Mediana móvil"], key="suavizado")

with c3: 
    st.slider("Ventana de suavizado:", min_value=1, max_value=12, step=1, key="window")

with c4:
    st.markdown("<br>", unsafe_allow_html=True) # Espaciado
    st.button("🔁 Reiniciar Filtros", on_click=reset_filters, type="primary")

# Procesamiento dinámico de variaciones
uf_var_df = metricas.procesar_por_periodicidad(uf_mensual, st.session_state["periodicidad"])
ipc_var_df = metricas.procesar_por_periodicidad(ipc_mensual, st.session_state["periodicidad"])

# Aplicar suavizado si es necesario
uf_var_df = formato.aplicar_suavizado(uf_var_df, st.session_state["suavizado"], st.session_state["window"])
ipc_var_df = formato.aplicar_suavizado(ipc_var_df, st.session_state["suavizado"], st.session_state["window"])

fig_var = figuras.crear_figura_comparativa(
    uf_var_df["Fecha"], uf_var_df["Var_porc_UF"], "Var. UF%", 
    ipc_var_df["Fecha"], ipc_var_df["Var_porc_IPC"], "Var. IPC%", 
    f"Comparación de Variaciones ({st.session_state['periodicidad']})",
    es_porcentaje=True
)
st.plotly_chart(fig_var, use_container_width=True)

st.markdown("---")
