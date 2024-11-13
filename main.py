import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Análisis de Composición Anual de Residuos Domiciliarios (2019-2022)")

# Subir archivo CSV desde la computadora
uploaded_file = st.file_uploader("Sube el archivo CSV", type="csv")

if uploaded_file is not None:
    # Leer el archivo CSV subido
    try:
        data = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        # Si utf-8 falla, intenta con latin-1
        data = pd.read_csv(uploaded_file, encoding='latin-1')

    # Renombrar las columnas para simplificar su uso en el código, si es necesario
    data.rename(columns={
        'REG_NAT': 'Region',
        'DEPARTAMENTO ': 'Departamento',
        'PROVINCIA': 'Provincia',
        'DISTRITO': 'Distrito',
        'QRESIDUOS_DOM': 'Tipo_de_Residuo',  # Cambia esto según corresponda
        'QRESIDUOS_DOM': 'Cantidad'  # Cambia esto según corresponda
    }, inplace=True)

    # Mostrar los primeros registros para vista previa
    st.subheader("Vista previa de los datos")
    st.write(data.head())

    # Medidas de tendencia central y datos generales
    st.subheader("Medidas de Tendencia Central")
    st.write(data.describe())

    # Opciones para seleccionar tipo de residuo y región
    tipo_residuo = st.selectbox("Seleccione el tipo de residuo:", data['Tipo_de_Residuo'].dropna().unique())
    region = st.selectbox("Seleccione la región:", data['Region'].dropna().unique())

    # Mostrar la región con más residuos para el tipo seleccionado
    st.subheader(f"Región con más {tipo_residuo}")
    region_mas_residuos = (
        data[data['Tipo_de_Residuo'] == tipo_residuo]
        .groupby('Region')['Cantidad']
        .sum()
        .idxmax()
    )
    cantidad_maxima = (
        data[data['Tipo_de_Residuo'] == tipo_residuo]
        .groupby('Region')['Cantidad']
        .sum()
        .max()
    )
    st.write(f"La región con más {tipo_residuo} es {region_mas_residuos} con una cantidad de {cantidad_maxima} toneladas.")

    # Mostrar estadísticas para los residuos en la región seleccionada
    st.subheader(f"Estadísticas de residuos en la región {region}")
    data_region = data[data['Region'] == region]
    st.write(data_region.describe())
else:
    st.warning("Por favor, sube un archivo CSV para analizar.")

