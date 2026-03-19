import os
import pandas as pd
import streamlit as st

@st.cache_data
def cargar_ipc_empalmadas(dir_path, filename):
    """
    Carga y procesa el archivo de IPC mensual desde un CSV con formato específico.

    Args:
        dir_path (str): Ruta al directorio que contiene el archivo.
        filename (str): Nombre del archivo CSV.

    Returns:
        pd.DataFrame: DataFrame con columnas ['Fecha', 'IPC'] ordenado por fecha.
    """
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
    """
    Transforma un DataFrame de UF anual (formato ancho con días/meses) a formato largo (serie temporal).

    Args:
        df (pd.DataFrame): DataFrame original cargado del CSV de la UF.
        anio (int): Año al que corresponden los datos.

    Returns:
        pd.Series: Serie temporal con la fecha como índice y el valor de la UF como dato.
    """
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
    """
    Busca y concatena todos los archivos CSV de UF en una carpeta para formar una sola serie histórica.

    Args:
        dir_path (str): Ruta a la carpeta que contiene los archivos CSV anuales de la UF.

    Returns:
        pd.DataFrame: DataFrame unificado con columnas ['Fecha', 'UF'].
    """
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
    """
    Formatea un número según el estándar chileno (punto para miles, coma para decimales).

    Args:
        valor (float): El número a formatear.
        decimales (int): Cantidad de decimales a mostrar.
        porcentaje (bool): Si es True, multiplica por 100 y añade el símbolo '%'.
        separador_miles (bool): Si es True, incluye separador de miles.

    Returns:
        str: El número formateado como cadena de texto.
    """
    if pd.isna(valor):
        return "—"

    if porcentaje:
        valor *= 100

    formato_str = "{:,.%df}" % decimales
    resultado = formato_str.format(valor)
    
    # Intercambiar puntos y comas para formato ES/CL
    # 1,234.56 -> 1.234,56
    resultado = resultado.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{resultado}%" if porcentaje else resultado

def filtrar_periodicidad_anual(data):
    """
    Filtra un DataFrame para mantener únicamente el registro del primer día de cada año.

    Args:
        data (pd.DataFrame): DataFrame con columna 'Fecha'.

    Returns:
        pd.DataFrame: DataFrame filtrado con frecuencia anual.
    """
    df = data.copy()
    df['Mes'] = df['Fecha'].dt.month
    df['Dia'] = df['Fecha'].dt.day
    return df[(df['Mes'] == 1) & (df['Dia'] == 1)][["Fecha", data.columns[1]]]

def aplicar_suavizado(df_periodo, metodo, window):
    """
    Aplica una técnica de suavizado (Media o Mediana móvil) a la serie de variaciones porcentuales.

    Args:
        df_periodo (pd.DataFrame): DataFrame que contiene una columna de variación porcentual.
        metodo (str): Método de suavizado ('Media móvil', 'Mediana móvil' o 'Ninguno').
        window (int): Tamaño de la ventana para el suavizado.

    Returns:
        pd.DataFrame: DataFrame con la serie suavizada.
    """
    if metodo == "Ninguno" or window <= 1:
        return df_periodo
        
    df = df_periodo.copy()
    col_var = [c for c in df.columns if "Var_porc" in c][0]
    
    if metodo == "Media móvil":
        df[col_var] = df[col_var].rolling(window=window, center=True).mean()
    elif metodo == "Mediana móvil":
        df[col_var] = df[col_var].rolling(window=window, center=True).median()
        
    return df
