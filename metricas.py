import numpy as np
import pandas as pd
import formato


def obtener_valor_uf_hoy(datos):
    fecha_hoy=np.datetime64('today')
    
    if fecha_hoy>=max(datos.reset_index()["Fecha"]):
        fecha_hoy=max(datos.reset_index()["Fecha"])

    valor_uf_hoy=datos.loc[datos["Fecha"]==fecha_hoy,"UF"].values[0]
    return valor_uf_hoy


def obtener_uf_por_periodo(datos):
    datos["primer_dia_mes"]=datos['Fecha'] + pd.offsets.MonthBegin(0)
    cond=datos["primer_dia_mes"]==datos['Fecha']
    datos_por_periodo=datos.loc[cond,:]
    datos_por_periodo=datos_por_periodo.drop(columns=["primer_dia_mes"])
    return datos_por_periodo

def obtener_ultimo_periodo(data_mensual):
    return data_mensual.sort_values(by="Fecha", ascending=False).iloc[0,1]

def obtener_ultima_var_mensual(uf_mensual):
    periodo_actual=uf_mensual.sort_values(by="Fecha", ascending=False).iloc[0,1]
    periodo_anterior=uf_mensual.sort_values(by="Fecha", ascending=False).iloc[1,1]
    return (periodo_actual-periodo_anterior)/periodo_anterior

def obtener_var_accum(data_mensual):
    obj = data_mensual.columns[1]

    data_mensual["Fecha"] = pd.to_datetime(data_mensual["Fecha"]) # Asegurar que Fecha sea datetime64[ns]

    
    periodo_actual = (  data_mensual
                        .sort_values(by="Fecha", ascending=False)
                        .iloc[0][obj] )

    fecha_max = data_mensual["Fecha"].max()
    fecha_hoy = pd.Timestamp.today().normalize()

    if fecha_hoy > fecha_max:
        fecha_hoy = fecha_max
    anio = fecha_hoy.year

    fecha_inicial = pd.Timestamp(year=anio, month=1, day=1)  # Fecha inicial del año

    # Primer valor del año
    primer_periodo = (  data_mensual
                        .loc[data_mensual["Fecha"] == fecha_inicial, obj]
                        .iloc[0] )

    return (periodo_actual - primer_periodo) / primer_periodo

def obtener_var_periodo(data_por_periodo):
    metrica_valores = data_por_periodo.iloc[:, 1].values

    var_porc_periodo = np.empty(len(metrica_valores))  # crea un array del mismo largo
    var_porc_periodo[0] = np.nan
    var_porc_periodo[1:] =  (metrica_valores[1:] - metrica_valores[:-1]) / metrica_valores[:-1]
    obj=list(data_por_periodo.columns)[1]
    
    data_por_periodo[f"Var_porc_{obj}"] = var_porc_periodo
    
    return data_por_periodo.reset_index(drop=True)


def var_por_periodo(data_periodo,periocidad):
    
    if periocidad=="Anual":
        data_periodo=formato.f_periocidad(data_periodo)
    return obtener_var_periodo(data_periodo)