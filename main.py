import streamlit as st
import pandas as pd

# Título y descripción de la aplicación
st.title("Recihome - Análisis de Residuos Domiciliarios")
st.write("Esta aplicación permite analizar datos de residuos para facilitar la toma de decisiones ambientales.")

# Sección para cargar el archivo CSV
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

# Validación y previsualización de datos
if uploaded_file is not None:
    # Cargar datos con manejo de codificación y delimitador adecuado
    try:
        data = pd.read_csv(uploaded_file, encoding='utf-8', delimiter=';')
    except UnicodeDecodeError:
        data = pd.read_csv(uploaded_file, encoding='ISO-8859-1', delimiter=';')

    # Mostrar una vista previa de los datos
    st.subheader("Vista Previa de los Datos Cargados")
    st.write(data.head())

    # Seleccionar columnas relevantes
    if 'REG_NAT' in data.columns and any(col.startswith('QRESIDUOS') for col in data.columns):
        data = data[['REG_NAT'] + [col for col in data.columns if col.startswith('QRESIDUOS')]]
        data = data.melt(id_vars=['REG_NAT'], var_name='tipo_residuo', value_name='cantidad')
        data.dropna(subset=['cantidad'], inplace=True)
        # Verificar que las columnas necesarias están presentes
        if 'REG_NAT' in data.columns and 'tipo_residuo' in data.columns and 'cantidad' in data.columns:
            data.rename(columns={'REG_NAT': 'region'}, inplace=True)

            # Sección de estadísticas generales
            st.sidebar.header("Estadísticas Generales")

            # Calcular medidas de tendencia central
            st.subheader("Medidas de Tendencia Central")
            st.write("**Media:**", data["cantidad"].mean())
            st.write("**Mediana:**", data["cantidad"].median())
            st.write("**Moda:**", data["cantidad"].mode()[0])
            st.write("**Rango:**", data["cantidad"].max() - data["cantidad"].min())

            # Resumen estadístico general
            st.subheader("Resumen Estadístico")
            st.write(data["cantidad"].describe())

            # Filtros de datos
            st.sidebar.subheader("Filtros Interactivos")
            tipo_residuo = st.sidebar.selectbox("Selecciona el tipo de residuo", data["tipo_residuo"].unique())
            region = st.sidebar.selectbox("Selecciona la región", data["region"].unique())

            # Aplicar filtros a los datos
            filtered_data = data[(data["tipo_residuo"] == tipo_residuo) & (data["region"] == region)]

            # Gráficas y visualizaciones
            st.subheader("Visualización de Datos")
              # Gráfica de barras de residuos por región
            st.write("**Cantidad de residuos por región**")
            residuos_por_region = data.groupby("region")["cantidad"].sum()
            st.bar_chart(residuos_por_region)

            # Gráfica de medidas de tendencia central para la región seleccionada
            st.write(f"**Medidas de Tendencia Central para la región '{region}' y residuo '{tipo_residuo}'**")
            tendencia_data = pd.DataFrame({
                "Medida": ["Media", "Mediana", "Moda"],
                "Valor": [filtered_data["cantidad"].mean(),
                          filtered_data["cantidad"].median(),
                          filtered_data["cantidad"].mode()[0] if not filtered_data["cantidad"].mode().empty else 0]
            })
            st.bar_chart(tendencia_data.set_index("Medida"))

            # Gráfica de la región con más residuos para el tipo seleccionado
            st.write(f"**Región con más residuos del tipo '{tipo_residuo}'**")
            residuos_por_tipo_region = data[data["tipo_residuo"] == tipo_residuo].groupby("region")["cantidad"].sum()
            region_max_residuos = residuos_por_tipo_region.idxmax()
            max_residuos = residuos_por_tipo_region.max()
            st.write(f"La región con más residuos del tipo '{tipo_residuo}' es '{region_max_residuos}' con {max_residuos} unidades.")

            # Gráfica comparativa entre tipos de residuos en la región seleccionada
            st.write(f"**Comparación entre tipos de residuos en la región '{region}'**")
            comparacion_residuos = data[data["region"] == region].groupby("tipo_residuo")["cantidad"].sum()
            st.bar_chart(comparacion_residuos)
             # Tabla de datos filtrados
            st.subheader("Datos Filtrados")
            st.write(filtered_data)

            # Opción de descargar resultados en CSV
            st.sidebar.subheader("Descargar Resultados")
            csv = filtered_data.to_csv(index=False)
            st.sidebar.download_button(
                label="Descargar datos filtrados en CSV",
                data=csv,
                file_name="datos_filtrados.csv",
                mime="text/csv"
            )

        else:
            st.error("El archivo cargado no contiene las columnas necesarias ('tipo_residuo', 'region', 'cantidad').")
    else:
        st.error("El archivo no tiene las columnas necesarias para el análisis.")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")




