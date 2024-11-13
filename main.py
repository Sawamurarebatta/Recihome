import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import json
from streamlit_folium import folium_static

# Personalizar la apariencia de Streamlit
st.set_page_config(page_title="Recihome - Análisis de Residuos en Perú", layout="wide")
st.markdown(
    """
    <style>
        .titulo {
            font-size: 2em; font-weight: bold; color: #2E8B57;
        }
        .subtitulo {
            font-size: 1.5em; font-weight: bold; color: #4682B4;
        }
        .texto {
            font-size: 1.1em; color: #333333;
        }
    </style>
    """, unsafe_allow_html=True
)

class DataProcessor:
    def __init__(self, file):
        self.file = file
        self.data = None

    def load_data(self):
        try:
            self.data = pd.read_csv(self.file, delimiter=';', encoding='ISO-8859-1')
        except UnicodeDecodeError:
            self.data = pd.read_csv(self.file, delimiter=';', encoding='ISO-8859-1')
        self.data.columns = self.data.columns.str.upper()
        if len(self.data.columns) > 46:
            self.data = self.data.iloc[:, :46]
        return self.data

    def preprocess_data(self):
        required_column = 'REG_NAT'
        residuos_columns = [col for col in self.data.columns if col.startswith('QRESIDUOS')]

        if required_column in self.data.columns and residuos_columns:
            self.data = self.data[[required_column] + residuos_columns]
            self.data = self.data.melt(id_vars=[required_column], var_name='TIPO_RESIDUO', value_name='CANTIDAD')
            self.data.dropna(subset=['CANTIDAD'], inplace=True)
            self.data.rename(columns={required_column: 'REGION'}, inplace=True)
            return True
        return False

    def filter_data(self, tipo_residuo, region):
        return self.data[(self.data['TIPO_RESIDUO'] == tipo_residuo) & (self.data['REGION'] == region)]

    def calculate_statistics(self):
        return {
            'mean': self.data['CANTIDAD'].mean(),
            'median': self.data['CANTIDAD'].median(),
            'mode': self.data['CANTIDAD'].mode()[0] if not self.data['CANTIDAD'].mode().empty else 0,
            'range': self.data['CANTIDAD'].max() - self.data['CANTIDAD'].min(),
            'description': self.data['CANTIDAD'].describe()
        }

# Streamlit app
st.markdown("<div class='titulo'>Recihome - Análisis de Residuos Domiciliarios en Perú</div>", unsafe_allow_html=True)
st.markdown("<div class='texto'>Esta aplicación permite analizar datos de residuos para facilitar la toma de decisiones ambientales en Perú.</div>", unsafe_allow_html=True)

# Cargar archivo
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file is not None:
    processor = DataProcessor(uploaded_file)
    data = processor.load_data()

    st.markdown("<div class='subtitulo'>Vista Previa de los Datos Cargados</div>", unsafe_allow_html=True)
    st.write(data.head())
   

    if processor.preprocess_data():
        stats = processor.calculate_statistics()

        st.sidebar.header("Estadísticas Generales")
        st.markdown("<div class='subtitulo'>Medidas de Tendencia Central</div>", unsafe_allow_html=True)
        st.write(f"Media: {stats['mean']}")
        st.write(f"Mediana: {stats['median']}")
        st.write(f"Moda: {stats['mode']}")
        st.write(f"Rango: {stats['range']}")

        # Filtros
        st.sidebar.subheader("Filtros Interactivos")
        tipo_residuo = st.sidebar.selectbox("Selecciona el tipo de residuo", processor.data['TIPO_RESIDUO'].unique())
        region = st.sidebar.selectbox("Selecciona la región", processor.data['REGION'].unique())

        filtered_data = processor.filter_data(tipo_residuo, region)

        # Visualizaciones
        st.markdown("<div class='subtitulo'>Visualización de Datos</div>", unsafe_allow_html=True)
        residuos_por_region = processor.data.groupby("REGION")['CANTIDAD'].sum().reset_index()
        fig_bar = px.bar(residuos_por_region, x='REGION', y='CANTIDAD', title="Cantidad de residuos por región")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico interactivo de comparación de residuos por tipo en la región seleccionada
        comparacion_residuos = processor.data[processor.data['REGION'] == region].groupby("TIPO_RESIDUO")['CANTIDAD'].sum().reset_index()
        fig_pie = px.pie(comparacion_residuos, names='TIPO_RESIDUO', values='CANTIDAD', title=f"Comparación entre tipos de residuos en la región {region}")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Cargar el archivo GeoJSON de las regiones de Perú a través de Streamlit file uploader
        st.sidebar.subheader("Carga el archivo GeoJSON de las regiones de Perú")
        uploaded_geojson = st.sidebar.file_uploader("Sube el archivo GeoJSON", type=["geojson"])
        
        if uploaded_geojson is not None:
            geojson_data = json.load(uploaded_geojson)

            # Mapa de Coropletas para mostrar cantidad de residuos por región
            st.markdown("<div class='subtitulo'>Mapa de Residuos por Región</div>", unsafe_allow_html=True)

            # Asegúrate de que los nombres de las regiones en el GeoJSON coincidan con los de tus datos
            residuos_por_region = residuos_por_region.rename(columns={'REGION': 'NOMBDEP'})  # Modificación para coincidir con la clave del GeoJSON

            # Crear el mapa de coropletas
            m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

            folium.Choropleth(
                geo_data=geojson_data,
                name="choropleth",
                data=residuos_por_region,
                columns=['NOMBDEP', 'CANTIDAD'],
                key_on='feature.properties.NOMBDEP',  # Ajuste para coincidir con la clave en el GeoJSON
                fill_color="YlGnBu",  # Puedes elegir el esquema de colores que prefieras
                fill_opacity=20,
                line_opacity=12,
                legend_name="Cantidad de Residuos",
            ).add_to(m)

            folium_static(m)

        st.markdown("<div class='subtitulo'>Datos Filtrados</div>", unsafe_allow_html=True)
        st.write(filtered_data)

        # Descargar los datos filtrados
        st.sidebar.subheader("Descargar Resultados")
        csv = filtered_data.to_csv(index=False)
        st.sidebar.download_button(
            label="Descargar datos filtrados en CSV",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv"
        )
    else:
        st.error("El archivo cargado no contiene las columnas necesarias para el análisis.")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")





