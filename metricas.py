import numpy as np
import pandas as pd
import formato

def obtener_valor_uf_hoy(datos):
    """
    Obtiene el valor de la UF para el día de hoy, o el último dato disponible en el dataset.

    Args:
        datos (pd.DataFrame): DataFrame con columnas ['Fecha', 'UF'].

    Returns:
        float: El valor de la UF correspondiente a la fecha buscada.
    """
    # Usar Timestamp para consistencia
    fecha_hoy = pd.Timestamp.today().normalize()
    fecha_max = datos["Fecha"].max()
    
    fecha_busqueda = min(fecha_hoy, fecha_max)
    valor = datos.loc[datos["Fecha"] == fecha_busqueda, "UF"]
    
    if valor.empty:
        return datos.sort_values("Fecha").iloc[-1]["UF"]
    return valor.values[0]

def obtener_uf_mensual(datos):
    """
    Extrae los registros correspondientes al primer día de cada mes para generar una serie mensual.

    Args:
        datos (pd.DataFrame): DataFrame con datos diarios de la UF.

    Returns:
        pd.DataFrame: DataFrame filtrado con un registro por mes.
    """
    df = datos.copy()
    # Aseguramos que sea el primer día del mes real
    df["Es_Primero"] = df["Fecha"].dt.is_month_start
    df_mensual = df[df["Es_Primero"]].drop(columns=["Es_Primero"])
    return df_mensual.sort_values("Fecha")

def obtener_ultimo_valor(df):
    """
    Retorna el valor más reciente de la serie de datos.

    Args:
        df (pd.DataFrame): DataFrame ordenable por fecha. Se asume que la segunda columna contiene los valores.

    Returns:
        float: El último valor numérico de la serie.
    """
    return df.sort_values("Fecha", ascending=True).iloc[-1, 1]

def calcular_variacion_mensual(df):
    """
    Calcula la variación porcentual entre el último periodo y el periodo inmediatamente anterior.

    Args:
        df (pd.DataFrame): DataFrame con la serie temporal.

    Returns:
        float: Variación porcentual (ej: 0.01 para 1%).
    """
    ultimos = df.sort_values("Fecha", ascending=True).iloc[-2:, 1].values
    if len(ultimos) < 2:
        return 0.0
    return (ultimos[1] - ultimos[0]) / ultimos[0]

def calcular_variacion_anual_acumulada(df):
    """
    Calcula la variación acumulada desde el 1 de enero del año del último dato disponible.

    Args:
        df (pd.DataFrame): DataFrame con la serie temporal.

    Returns:
        float: Variación porcentual acumulada en el año.
    """
    col_valor = df.columns[1]
    df_sorted = df.sort_values("Fecha")
    
    ultimo_dato = df_sorted.iloc[-1]
    valor_actual = ultimo_dato[col_valor]
    anio_actual = ultimo_dato["Fecha"].year
    
    fecha_inicial_anio = pd.Timestamp(year=anio_actual, month=1, day=1)
    
    filtro_inicio = df_sorted[df_sorted["Fecha"] == fecha_inicial_anio]
    
    if filtro_inicio.empty:
        # Si no hay dato exacto del 1 de enero, usar el primero disponible del año
        valor_inicial = df_sorted[df_sorted["Fecha"].dt.year == anio_actual].iloc[0][col_valor]
    else:
        valor_inicial = filtro_inicio.iloc[0][col_valor]
        
    return (valor_actual - valor_inicial) / valor_inicial

def calcular_variacion_serie(df):
    """
    Genera una nueva columna en el DataFrame con la variación porcentual punto a punto.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        pd.DataFrame: DataFrame con una columna adicional 'Var_porc_[NombreCol]'.
    """
    df_new = df.sort_values("Fecha").copy()
    valores = df_new.iloc[:, 1].values
    
    variaciones = np.full(len(valores), np.nan)
    variaciones[1:] = (valores[1:] - valores[:-1]) / valores[:-1]
    
    nombre_col = f"Var_porc_{df_new.columns[1]}"
    df_new[nombre_col] = variaciones
    return df_new.reset_index(drop=True)

def procesar_por_periodicidad(df_mensual, periodicidad):
    """
    Ajusta la frecuencia de la serie (Mensual o Anual) y calcula sus variaciones correspondientes.

    Args:
        df_mensual (pd.DataFrame): Serie de datos con frecuencia mensual.
        periodicidad (str): 'Mensual' o 'Anual'.

    Returns:
        pd.DataFrame: Serie procesada con las variaciones calculadas.
    """
    if periodicidad == "Anual":
        df_periodo = formato.filtrar_periodicidad_anual(df_mensual)
    else:
        df_periodo = df_mensual.copy()
        
    return calcular_variacion_serie(df_periodo)
