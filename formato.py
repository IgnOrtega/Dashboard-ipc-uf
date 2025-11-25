
import os
import pandas as pd

def calcular_fecha(row):
    anio=str(row["Año"])
    mes="00"+str(row["Mes"])
    mes=mes[-2:]
    return f'{anio}-{mes}-01'
    

def cargar_ipc_empalmadas(dir, filename):
    df = pd.read_csv(dir + filename,
                    sep=";",          # separador correcto
                    encoding="utf-8" # para tildes
                    )
    cols=df.columns
    df["Periodo"]=df.apply(lambda row: calcular_fecha(row), axis=1)
    df["Periodo"] = pd.to_datetime(df["Periodo"]).dt.to_period("M")
    df=df.rename(mapper={"índice":"IPC"}, axis=1)
    df = df.dropna(subset=["IPC"])
    df=df.loc[:,["Periodo","IPC"]]
    df["IPC"]=df["IPC"].str.replace(",",".").astype("float64")
    df["Fecha"]=df["Periodo"].values.astype("datetime64[M]")
    cols=["Fecha","IPC"]
    df=df.loc[:,cols]
    return df

def formatear_csv(df, AÑO):
    # Reemplazar coma por nada y punto por coma decimal si es necesario
    if 1==0:
        for col in df.columns[1:]:  # excluir "Día"
            df[col] = (
                df[col]
                .astype(str)
                .str.replace('.', '', regex=False)  # eliminar separador de miles
                .str.replace(',', '.', regex=False)  # cambiar coma por punto decimal
                .astype(float)
            )
    # Transformar a formato largo
    df_long = df.melt(id_vars="Día", var_name="Mes", value_name="Valor")


    # Mapear nombres de meses en español a números
    meses = {
        "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12
    }

    df_long["Mes_num"] = df_long["Mes"].map(meses)

    # Crear una columna de fecha completa (usa el año correcto)
    df_long["Fecha"] = pd.to_datetime({
        "year": AÑO,
        "month": df_long["Mes_num"],
        "day": df_long["Día"]
    }, errors="coerce")

    # Eliminar fechas inválidas (por ejemplo, 30-feb)
    df_long = df_long.dropna(subset=["Fecha"])

    # Ordenar por fecha
    df_long = df_long.sort_values("Fecha")

    # Crear la serie de tiempo con frecuencia diaria
    serie = pd.Series(df_long["Valor"].values, index=df_long["Fecha"])
    serie = serie.asfreq("D")
    return serie.str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)


def concadenar_datos_uf(dir):
    # Lista todos los archivos .csv de la carpeta
    archivos = [f for f in os.listdir(dir) if f.endswith(".csv")]

    datos = pd.DataFrame()
    primero = True  # Booleano para identificar la primera iteración

    for archivo in archivos:
        # Extraer el año desde el nombre del archivo (asumiendo formato "UF 2024.csv")
        try:
            AÑO = int(''.join(filter(str.isdigit, archivo)))
        except ValueError:
            print(f"No se pudo extraer el año del archivo: {archivo}")
            continue

        df = pd.read_csv(os.path.join(dir, archivo), sep=";")
        datos_temp = formatear_csv(df, AÑO)

        if primero:
            datos = datos_temp
            primero = False
        else:
            datos = pd.concat([datos, datos_temp], ignore_index=False)

    return datos

def calcular_fecha(row):
    return f"{str(row["Año"])}-{str("00"+str(row["Mes"]))[-2:]}-01"

def cargar_ipc_empalmadas(dir, filename):
    df = pd.read_csv(dir + filename,
                    sep=";",          # separador correcto
                    encoding="utf-8" # para tildes
                    )
    cols=df.columns
    df["Periodo"]=df.apply(lambda row: calcular_fecha(row), axis=1)
    df["Periodo"] = pd.to_datetime(df["Periodo"]).dt.to_period("M")
    df=df.rename(mapper={"índice":"IPC"}, axis=1)
    df = df.dropna(subset=["IPC"])
    df=df.loc[:,["Periodo","IPC"]]
    df["IPC"]=df["IPC"].str.replace(",",".").astype("float64")
    df["Fecha"]=df["Periodo"].values.astype("datetime64[M]")
    cols=["Fecha","IPC"]
    df=df.loc[:,cols]
    return df

def formatear_numero(valor, decimales=2, porcentaje=False, separador_miles=True):
    """
    Formatea un número en formato string.
    
    Parámetros:
        valor (float | int): número a formatear
        decimales (int): cantidad de decimales
        porcentaje (bool): si True, muestra como porcentaje
        separador_miles (bool): si True, usa separador de miles (, o . según locale)
        
    Retorna:
        str: número formateado como texto
    """
    if valor is None:
        return "—"

    try:
        if porcentaje:
            valor *= 100
            formato = f"{{:,.{decimales}f}}%" if separador_miles else f"{{:.{decimales}f}}%"
        else:
            formato = f"{{:,.{decimales}f}}" if separador_miles else f"{{:.{decimales}f}}"
        return formato.format(valor)
    except (ValueError, TypeError):
        return str(valor)
    

def f_periocidad(data):
    obj=list(data.columns)[1]
    data['Mes'] = data['Fecha'].dt.month
    data['day'] = data['Fecha'].dt.day
    cond1=data['day']==1
    cond2=data['Mes']==1
    data=data.loc[cond1 & cond2,:]
    return data.loc[:,["Fecha",obj]]


def suavizamiento_funcion(data_periodo, metodo,window):
    #  Luego de la operacion .rolling(window=window, center=True).mean(), los datos quedan suavizados con la misma media original
    obj=list(data_periodo.columns)[1]
    if metodo=="Media móvil":
        data_periodo[f"Var_porc_{obj}"]=data_periodo[f"Var_porc_{obj}"].rolling(window=window, center=True).mean()
    elif metodo=="Mediana móvil":
        data_periodo[f"Var_porc_{obj}"]=data_periodo[f"Var_porc_{obj}"].rolling(window=window, center=True).median()
    elif metodo=="Ninguno":
        pass
    return data_periodo