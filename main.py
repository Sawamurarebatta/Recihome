import streamlit as st
import pandas as pd

class DataProcessor:
    def __init__(self, file):
        self.file = file
        self.data = None

    def load_data(self):
        try:
            self.data = pd.read_csv(self.file, encoding='utf-8', delimiter=';')
        except UnicodeDecodeError:
            self.data = pd.read_csv(self.file, encoding='ISO-8859-1', delimiter=';')
        return self.data

    def preprocess_data(self):
        if 'REG_NAT' in self.data.columns and any(col.startswith('QRESIDUOS') for col in self.data.columns):
            self.data = self.data[['REG_NAT'] + [col for col in self.data.columns if col.startswith('QRESIDUOS')]]
            self.data = self.data.melt(id_vars=['REG_NAT'], var_name='tipo_residuo', value_name='cantidad')
            self.data.dropna(subset=['cantidad'], inplace=True)
            self.data.rename(columns={'REG_NAT': 'region'}, inplace=True)
            return True
        return False

    def filter_data(self, tipo_residuo, region):
        return self.data[(self.data['tipo_residuo'] == tipo_residuo) & (self.data['region'] == region)]

    def calculate_statistics(self):
        return {
            'mean': self.data['cantidad'].mean(),
            'median': self.data['cantidad'].median(),
            'mode': self.data['cantidad'].mode()[0] if not self.data['cantidad'].mode().empty else 0,
            'range': self.data['cantidad'].max() - self.data['cantidad'].min(),
            'description': self.data['cantidad'].describe()
        }

    def sum_by_region(self, year):
        columns = [col for col in self.data.columns if f'{year}' in col]
        if columns:
            return self.data.groupby('region')[columns].sum().reset_index()
        return None

# Streamlit app
st.title("Recihome - Análisis de Residuos Domiciliarios")
st.write("Esta aplicación permite analizar datos de residuos para facilitar la toma de decisiones ambientales.")

# Cargar archivo
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file is not None:
    processor = DataProcessor(uploaded_file)
    data = processor.load_data()

    st.subheader("Vista Previa de los Datos Cargados")
    st.write(data.head())

    if processor.preprocess_data():
        stats = processor.calculate_statistics()

        st.sidebar.header("Estadísticas Generales")
        st.subheader("Medidas de Tendencia Central")
        st.write("*Media:*", stats['mean'])
        st.write("*Mediana:*", stats['median'])
        st.write("*Moda:*", stats['mode'])
        st.write("*Rango:*", stats['range'])

        st.subheader("Resumen Estadístico")
        st.write(stats['description'])

        # Filtros
        st.sidebar.subheader("Filtros Interactivos")
        tipo_residuo = st.sidebar.selectbox("Selecciona el tipo de residuo", data['tipo_residuo'].unique())
        region = st.sidebar.selectbox("Selecciona la región", data['region'].unique())

        filtered_data = processor.filter_data(tipo_residuo, region)

        # Visualizaciones
        st.subheader("Visualización de Datos")
        st.write("*Cantidad de residuos por región*")
        residuos_por_region = data.groupby("region")['cantidad'].sum()
        st.bar_chart(residuos_por_region)

        st.write(f"*Medidas de Tendencia Central para la región '{region}' y residuo '{tipo_residuo}'*")
        tendencia_data = pd.DataFrame({
            "Medida": ["Media", "Mediana", "Moda"],
            "Valor": [
                filtered_data['cantidad'].mean(),
                filtered_data['cantidad'].median(),
                filtered_data['cantidad'].mode()[0] if not filtered_data['cantidad'].mode().empty else 0
            ]
        })
        st.bar_chart(tendencia_data.set_index("Medida"))

        st.write(f"*Región con más residuos del tipo '{tipo_residuo}'*")
        residuos_por_tipo_region = data[data['tipo_residuo'] == tipo_residuo].groupby("region")['cantidad'].sum()
        region_max_residuos = residuos_por_tipo_region.idxmax()
        max_residuos = residuos_por_tipo_region.max()
        st.write(f"La región con más residuos del tipo '{tipo_residuo}' es '{region_max_residuos}' con {max_residuos} unidades.")

        st.write(f"*Comparación entre tipos de residuos en la región '{region}'*")
        comparacion_residuos = data[data['region'] == region].groupby("tipo_residuo")['cantidad'].sum()
        st.bar_chart(comparacion_residuos)

        st.subheader("Datos Filtrados")
        st.write(filtered_data)

        st.sidebar.subheader("Descargar Resultados")
        csv = filtered_data.to_csv(index=False)
        st.sidebar.download_button(
            label="Descargar datos filtrados en CSV",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv"
        )

        # Suma de residuos por región en 2019
        st.subheader("Suma de residuos por región en 2019")
        suma_2019 = processor.sum_by_region(2019)
        if suma_2019 is not None:
            st.write(suma_2019)
            st.bar_chart(suma_2019.set_index('region'))
        else:
            st.write("No se encontraron datos de 2019.")
    else:
        st.error("El archivo cargado no contiene las columnas necesarias para el análisis.")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")


