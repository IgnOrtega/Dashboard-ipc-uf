# Dashboard de Comparación UF e IPC 📊

Este proyecto es un dashboard interactivo desarrollado en **Streamlit** que permite visualizar y analizar la evolución histórica de la Unidad de Fomento (UF) y el Índice de Precios al Consumidor (IPC) en Chile.

## Características principales

- **Visualización Comparativa:** Gráficos interactivos (Plotly) que permiten comparar el valor de la UF con el IPC (escalado para facilitar la comparación visual).
- **Métricas Clave (KPIs):** Tarjetas personalizadas que muestran el valor actual de la UF, variaciones mensuales y acumuladas anuales, tanto para UF como para IPC.
- **Análisis de Variaciones:** Herramientas para analizar la variación porcentual con opciones de:
  - Periodicidad (Mensual o Anual).
  - Suavizado de datos (Media móvil o Mediana móvil) con ventana ajustable.
- **Interfaz Adaptativa:** Diseño limpio con tarjetas KPI personalizadas mediante HTML/CSS para una mejor experiencia de usuario.

## Requisitos Técnicos

- **Python:** 3.12.x
- **Dependencias:** Listadas en `requirements.txt` (Streamlit, Pandas, Plotly, Numpy, etc.)

## Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/IgnOrtega/Comparacion-uf-ipc.git
   cd proyecto-6-uf
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

## Estructura del Proyecto

- `app.py`: Punto de entrada principal de la aplicación Streamlit.
- `metricas.py`: Lógica de cálculo de variaciones, promedios y procesamiento de series temporales.
- `figuras.py`: Generación de gráficos Plotly y componentes visuales personalizados (Tarjetas KPI).
- `formato.py`: Funciones de utilidad para carga de datos, limpieza y formateo numérico (estilo chileno).
- `data/`: Directorio que contiene los archivos CSV con datos históricos de IPC y UF.

---
*Desarrollado como parte de una guía práctica de Streamlit.*
