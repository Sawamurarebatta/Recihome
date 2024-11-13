import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración inicial de la página
st.set_page_config(page_title="Recihome - Análisis de Residuos Domiciliarios")
st.title("Recihome - Análisis de Residuos Domiciliarios")
st.write("Esta aplicación permite analizar datos de residuos para facilitar la toma de decisiones ambientales.")

# Cargar archivo CSV
st.header("Carga de Datos")
uploaded_file = st.file_uploader("Sube un archivo CSV", type=["csv"])
if uploaded_file is not None:
    # Leer archivo CSV
    data = pd.read_csv(uploaded_file)
    st.write("Vista previa de los datos:")
    st.write(data.head())

    # Validación de columnas necesarias
    columnas_necesarias = ["REGION", "TIPO_RESIDUO", "CANTIDAD"]
    if all(col in data.columns for col in columnas_necesarias):
        # Medidas de tendencia central y estadísticas generales
        st.header("Medidas de Tendencia Central y Datos Generales")
        
        # Calcular estadísticas
        media = data["CANTIDAD"].mean()
        mediana = data["CANTIDAD"].median()
        moda = data["CANTIDAD"].mode().iloc[0] if not data["CANTIDAD"].mode().empty else np.nan
        maximo = data["CANTIDAD"].max()
        minimo = data["CANTIDAD"].min()
        desviacion = data["CANTIDAD"].std()
        
        # Mostrar estadísticas
        st.write("**Resumen Estadístico**")
        st.write(pd.DataFrame({
            "Media": [media],
            "Mediana": [mediana],
            "Moda": [moda],
            "Máximo": [maximo],
            "Mínimo": [minimo],
            "Desviación Estándar": [desviacion]
        }))

        # Filtros interactivos
        st.header("Filtros Interactivos")
        
        tipo_residuo = st.selectbox("Selecciona el tipo de residuo", data["TIPO_RESIDUO"].unique())
        region = st.selectbox("Selecciona la región", data["REGION"].unique())
        
        # Filtrar datos
        data_filtrada = data[(data["TIPO_RESIDUO"] == tipo_residuo) & (data["REGION"] == region)]

        # Gráficas y visualizaciones
        st.header("Gráficas y Visualizaciones")

        # Gráfica de barras de cantidad de residuos por tipo y región
        st.subheader("Cantidad de Residuos por Tipo y Región")
        plt.figure(figsize=(10, 6))
        sns.barplot(data=data, x="REGION", y="CANTIDAD", hue="TIPO_RESIDUO")
        plt.xticks(rotation=45)
        st.pyplot(plt)

        # Gráfica de medidas de tendencia central para el tipo de residuo seleccionado
        st.subheader("Medidas de Tendencia Central")
        plt.figure(figsize=(6, 4))
        sns.boxplot(data=data_filtrada, y="CANTIDAD")
        st.pyplot(plt)

        # Gráfica de la región con más residuos
        st.subheader("Región con Mayor Cantidad de Residuos para el Tipo Seleccionado")
        region_max_residuos = data[data["TIPO_RESIDUO"] == tipo_residuo].groupby("REGION")["CANTIDAD"].sum().idxmax()
        st.write(f"La región con la mayor cantidad de residuos para {tipo_residuo} es: {region_max_residuos}")
        
        # Mostrar estadísticas para los residuos en la región seleccionada
        st.subheader(f"Estadísticas de Residuos en {region}")
        cantidad_region = data[data["REGION"] == region]["CANTIDAD"].sum()
        st.write(f"Cantidad total de residuos en la región {region}: {cantidad_region}")
        
        # Análisis comparativo
        st.header("Análisis Comparativo")

        # Comparación entre regiones
        st.subheader("Comparación entre Regiones")
        plt.figure(figsize=(10, 6))
        sns.barplot(data=data, x="REGION", y="CANTIDAD", hue="TIPO_RESIDUO", estimator=np.sum)
        plt.xticks(rotation=45)
        st.pyplot(plt)

        # Comparación entre tipos de residuos en una misma región
        st.subheader("Comparación entre Tipos de Residuos en la Región Seleccionada")
        data_region = data[data["REGION"] == region]
        plt.figure(figsize=(8, 5))
        sns.barplot(data=data_region, x="TIPO_RESIDUO", y="CANTIDAD", estimator=np.sum)
        st.pyplot(plt)

        # Botón de descarga de resultados
        st.header("Descarga de Resultados")
        if st.button("Descargar Resumen en CSV"):
            resumen_df = pd.DataFrame({
                "Media": [media],
                "Mediana": [mediana],
                "Moda": [moda],
                "Máximo": [maximo],
                "Mínimo": [minimo],
                "Desviación Estándar": [desviacion],
                "Cantidad Total en Región Seleccionada": [cantidad_region]
            })
            resumen_df.to_csv("resumen.csv", index=False)
            st.success("Archivo CSV generado con éxito.")

        # Instrucciones y Ayuda
        st.header("Instrucciones y Ayuda")
        st.write("1. Sube un archivo CSV con las columnas: `REGION`, `TIPO_RESIDUO`, `CANTIDAD`.")
        st.write("2. Usa los filtros para seleccionar el tipo de residuo y la región de interés.")
        st.write("3. Visualiza las gráficas y descarga los resultados si es necesario.")

    else:
        st.error("El archivo CSV no contiene las columnas necesarias: 'REGION', 'TIPO_RESIDUO', 'CANTIDAD'.")

else:
    st.info("Por favor, sube un archivo CSV para comenzar.")



