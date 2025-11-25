import numpy as np
import pandas as pd
import formato


def obtener_valor_uf_hoy(datos):
    fecha_hoy=np.datetime64('today')
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
    obj=list(data_mensual.columns)[1]
    periodo_actual=data_mensual.sort_values(by="Fecha", ascending=False).iloc[0,1]
    
    fecha_hoy=np.datetime64('today')
    anio=fecha_hoy.astype('datetime64[Y]')
    fecha_inicial=np.datetime64(f"{anio}-01-01")
    primer_periodo=data_mensual.loc[data_mensual["Fecha"]==fecha_inicial,obj].values[0]
    
    return (periodo_actual-primer_periodo)/primer_periodo


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