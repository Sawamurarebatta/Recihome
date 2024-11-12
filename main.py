import streamlit as st
import pandas as pd

# URL del archivo CSV en GitHub (en formato "raw")
url_csv = "https://raw.githubusercontent.com/Sawamurarebatta/Recihome/main/D.%20Composición%20Anual%20de%20residuos%20domiciliarios_Distrital_2019_2022.csv"

# Leer el archivo CSV directamente desde la URL especificando la codificación
try:
    data = pd.read_csv(url_csv, encoding='utf-8')
except UnicodeDecodeError:
    # Si utf-8 falla, intenta con latin-1
    data = pd.read_csv(url_csv, encoding='latin-1')

# Título de la aplicación
st.title("Análisis de Composición Anual de Residuos Domiciliarios (2019-2022)")

# Mostrar los primeros registros para vista previa
st.subheader("Vista previa de los datos")
st.write(data.head())

# Medidas de tendencia central y datos generales
st.subheader("Medidas de Tendencia Central")
st.write(data.describe())

# Opciones para seleccionar tipo de residuo y región
tipo_residuo = st.selectbox("Seleccione el tipo de residuo:", data['Tipo_de_Residuo'].unique())
region = st.selectbox("Seleccione la región:", data['Region'].unique())

# Mostrar la región con más residuos para el tipo seleccionado
st.subheader(f"Región con más {tipo_residuo}")
region_mas_residuos = data[data['Tipo_de_Residuo'] == tipo_residuo].groupby('Region')['Cantidad'].sum().idxmax()
cantidad_maxima = data[data['Tipo_de_Residuo'] == tipo_residuo].groupby('Region')['Cantidad'].sum().max()
st.write(f"La región con más {tipo_residuo} es {region_mas_residuos} con una cantidad de {cantidad_maxima} toneladas.")

# Mostrar estadísticas para los residuos en la región seleccionada
st.subheader(f"Estadísticas de residuos en la región {region}")
data_region = data[data['Region'] == region]
st.write(data_region.describe())
