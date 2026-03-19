import os
import pandas as pd
import streamlit as st

@st.cache_data
def cargar_ipc_empalmadas(dir_path, filename):
    """Carga y procesa el archivo de IPC mensual."""
    file_full_path = os.path.join(dir_path, filename)
    df = pd.read_csv(file_full_path, sep=";", encoding="utf-8")
    
    # Crear columna de fecha
    df["Fecha"] = pd.to_datetime(
        df["Año"].astype(str) + "-" + df["Mes"].astype(str).str.zfill(2) + "-01"
    )
    
    # Limpieza de datos
    df = df.rename(columns={"índice": "IPC"})
    df = df.dropna(subset=["IPC"])
    
    # Conversión numérica robusta
    if df["IPC"].dtype == object:
        df["IPC"] = df["IPC"].str.replace(",", ".").astype(float)
        
    return df[["Fecha", "IPC"]].sort_values("Fecha")

def formatear_csv_uf(df, anio):
    """Procesa un DataFrame individual de UF anual."""
    # Transformar a formato largo (melt)
    df_long = df.melt(id_vars="Día", var_name="Mes", value_name="Valor")

    meses = {
        "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12
    }
    df_long["Mes_num"] = df_long["Mes"].map(meses)

    # Crear fecha completa
    df_long["Fecha"] = pd.to_datetime({
        "year": anio,
        "month": df_long["Mes_num"],
        "day": df_long["Día"]
    }, errors="coerce")

    df_long = df_long.dropna(subset=["Fecha", "Valor"])
    
    # Limpieza de valores numéricos
    if df_long["Valor"].dtype == object:
        # Eliminar puntos de miles y cambiar coma por punto decimal
        df_long["Valor"] = (
            df_long["Valor"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

    return df_long[["Fecha", "Valor"]].set_index("Fecha")["Valor"]

@st.cache_data
def concatenar_datos_uf(dir_path):
    """Lee todos los CSV de UF en la carpeta y los une en un solo DataFrame."""
    archivos = [f for f in os.listdir(dir_path) if f.endswith(".csv")]
    todos_los_datos = []

    for archivo in archivos:
        try:
            anio = int(''.join(filter(str.isdigit, archivo)))
            df = pd.read_csv(os.path.join(dir_path, archivo), sep=";")
            serie_anual = formatear_csv_uf(df, anio)
            todos_los_datos.append(serie_anual)
        except Exception as e:
            st.error(f"Error procesando {archivo}: {e}")
            continue

    if not todos_los_datos:
        return pd.DataFrame()

    df_final = pd.concat(todos_los_datos).sort_index()
    df_final = df_final.to_frame(name="UF").reset_index()
    return df_final

def formatear_numero(valor, decimales=2, porcentaje=False, separador_miles=True):
    """Formatea números al estilo chileno (punto para miles, coma para decimales)."""
    if pd.isna(valor):
        return "—"

    if porcentaje:
        valor *= 100

    formato = "{:,.%df}" % decimales
    resultado = formato.format(valor)
    
    # Intercambiar puntos y comas para formato ES/CL
    # 1,234.56 -> 1.234,56
    resultado = resultado.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{resultado}%" if porcentaje else resultado

def filtrar_periodicidad_anual(data):
    """Filtra solo el primer día de cada año."""
    df = data.copy()
    df['Mes'] = df['Fecha'].dt.month
    df['Dia'] = df['Fecha'].dt.day
    return df[(df['Mes'] == 1) & (df['Dia'] == 1)][["Fecha", data.columns[1]]]

def aplicar_suavizado(df_periodo, metodo, window):
    """Aplica suavizado a la columna de variación porcentual."""
    if metodo == "Ninguno" or window <= 1:
        return df_periodo
        
    df = df_periodo.copy()
    col_var = [c for c in df.columns if "Var_porc" in c][0]
    
    if metodo == "Media móvil":
        df[col_var] = df[col_var].rolling(window=window, center=True).mean()
    elif metodo == "Mediana móvil":
        df[col_var] = df[col_var].rolling(window=window, center=True).median()
        
    return df
