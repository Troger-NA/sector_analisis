import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px

# Archivo JSON donde almacenaremos los datos
json_file = "marketcap_data.json"

# Definir la URL de la API de CoinGecko
url = "https://api.coingecko.com/api/v3/coins/categories"

def fetch_data():
    """Descarga los datos de la API de CoinGecko"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Error al conectar con la API de CoinGecko")
    return response.json()

def update_json(data):
    """Actualiza el archivo JSON con los datos descargados"""
    today = datetime.now().strftime("%Y-%m-%d")
    new_data = {
        "date": today,
        "categories": [
            {
                "sector": category["name"],
                "market_cap": category["market_cap"],
                "market_cap_change_24h": category["market_cap_change_24h"]
            }
            for category in data
        ]
    }

    # Leer o inicializar el archivo JSON
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Verificar si ya existe una entrada para hoy
    existing_dates = [entry["date"] for entry in existing_data]
    if today in existing_dates:
        # Actualizar los datos del día actual
        for entry in existing_data:
            if entry["date"] == today:
                entry["categories"] = new_data["categories"]
                break
    else:
        # Agregar nuevos datos si no existe entrada para hoy
        existing_data.append(new_data)

    # Guardar datos en el archivo
    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=4)

    print(f"Datos actualizados para la fecha: {today}")

def load_json():
    """Carga el contenido del archivo JSON"""
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            return json.load(file)
    return []

def plot_tendency_all_sectors(df):
    """Grafica todas las tendencias de la variación diaria para todos los sectores"""
    st.write("### Tendencias de la Variación en 24 Horas (Día a Día para Todos los Sectores)")
    fig = px.line(
        df,
        x="Date",
        y="24h Change (%)",
        color="Sector",
        title="Tendencias de la Variación en 24 Horas por Sector",
        labels={"Date": "Fecha", "24h Change (%)": "Cambio 24h (%)", "Sector": "Sector"},
        template="simple_white",
    )
    st.plotly_chart(fig)

# Aplicación Streamlit con pestañas
st.title("Seguimiento de Market Cap por Sector (CoinGecko)")
st.write("Esta aplicación descarga diariamente datos de market cap por sector y los almacena para análisis futuros.")

tab1, tab2, tab3 = st.tabs(["Actualizar y Visualizar Datos", "Gráficos por Sector", "Tendencias Globales 24h"])

with tab1:
    # Botón para actualizar datos
    if st.button("Actualizar datos"):
        try:
            data = fetch_data()
            update_json(data)
            st.success("Datos actualizados exitosamente.")
        except Exception as e:
            st.error(f"Error al actualizar los datos: {e}")

    # Mostrar datos
    data = load_json()
    if not data:
        st.write("No hay datos disponibles aún. Actualiza para descargar datos.")
    else:
        records = []
        for entry in data:
            date = entry["date"]
            for category in entry["categories"]:
                records.append({
                    "Date": date,
                    "Sector": category["sector"],
                    "Market Cap": category["market_cap"],
                    "24h Change (%)": category["market_cap_change_24h"]
                })
        df = pd.DataFrame(records)
        st.dataframe(df)

with tab2:
    # Mostrar gráficos para todos los sectores
    if not data:
        st.write("No hay datos disponibles aún. Actualiza para descargar datos.")
    else:
        # Filtrar los datos del día más reciente
        latest_date = df["Date"].max()
        latest_data = df[df["Date"] == latest_date]
        
        # Gráficos interactivos
        st.write("### Market Cap por Sector (Interactivo)")
        fig = px.scatter(
            latest_data,
            x="Sector",
            y="Market Cap",
            title="Market Cap por Sector",
            labels={"Sector": "Sector", "Market Cap": "Market Cap"},
            template="simple_white",
        )
        st.plotly_chart(fig)

        st.write("### Cambio en las Últimas 24 Horas por Sector (Interactivo)")
        fig = px.scatter(
            latest_data,
            x="Sector",
            y="24h Change (%)",
            title="Cambio en las Últimas 24 Horas por Sector",
            labels={"Sector": "Sector", "24h Change (%)": "Cambio 24h (%)"},
            template="simple_white",
        )
        st.plotly_chart(fig)

with tab3:
    # Mostrar tendencias de variación en 24h día a día para todos los sectores
    if not data:
        st.write("No hay datos disponibles aún. Actualiza para descargar datos.")
    else:
        plot_tendency_all_sectors(df)

