import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import pandas as pd
from pyspark.sql import SparkSession
import plotly.express as px
from math import isnan
import json
import os
from datetime import datetime

# --------------------------------- py's functions --------------------------------------------------

from utils import (
    create_spider_chart,
    load_filtered_data,
    display_general_stats,
    display_instructions,
    format_market_value,


)

from config import (
    save_configuration,
    load_configuration,
    get_user_configurations,
)

# --------------------------------- Initialization --------------------------------------------------

# Page configuration
st.set_page_config(
    page_title="Footballytics App",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Folder to store configurations
CONFIG_FOLDER = "./configs"

# CSS styles
st.markdown("""
<style>
body {
    background-color: #ffffff;
}

.stApp {
    background-color: #ffffff;
}

.stDataFrame {
    background-color: #ffffff;
}

.css-1aumxhk {
    background-color: #ffffff;
}

.css-qrbaxs {
    background-color: #ffffff;
}

.sidebar .sidebar-content {
    background-color: #ffffff;
    color: #343a40;
}

.sidebar .sidebar-content .sidebar-item a {
    color: #343a40;
}

.sidebar .sidebar-content .sidebar-item a:hover {
    color: #007bff;
}

.sidebar .sidebar-content .sidebar-item.active a {
    color: white;
    background-color: #007bff;
    border-radius: 5px;
}

.sidebar .sidebar-content .sidebar-item.active a:hover {
    background-color: #0056b3;
}

.card {
    padding: 20px;
    margin: 10px 0;
    background-color: white;
    border: 1px solid #e3e3e3;
    border-radius: 10px;
    box-shadow: 2px 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stButton button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
}

.stDataFrame table {
    width: 100%;
    margin: 0;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    border-collapse: collapse;
    background-color: white;
}

.stDataFrame th, .stDataFrame td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.stDataFrame th {
    background-color: #343a40;
    color: white;
}

.stDataFrame tbody tr:nth-child(odd) {
    background-color: #f2f2f2;
}

.stDataFrame tbody tr:hover {
    background-color: #ddd;
}
.streamlit-expanderHeader {
        background-color: white;
        color: black; # Adjust this for expander header color
}                     
</style>
""", unsafe_allow_html=True)

# main path
main_path = './data/'

# Initialize Spark session
spark = SparkSession.builder.appName("StreamlitApp").getOrCreate()

# logo
with st.sidebar:
    st.image('./img/logo.png', width=300)

# Load the CSV file with the list of stats filter_vars.csv
filter_vars_df = pd.read_csv(main_path + 'filter_vars.csv')
stats_list = filter_vars_df['stats'].dropna().tolist()  

# --------------------------------- Module 0: Home Page --------------------------------------------------

# Home page
def homepage(user_name):
    st.markdown(
        f"<div class='jumbotron text-center'><h1>Welcome, {user_name}!</h1><p>to the Football Analytics App</p></div>",
        unsafe_allow_html=True
    )

    # Display instructions
    display_instructions()

# --------------------------------- Module 1: Data Load --------------------------

# Data Load Module
def data_load_module():
    st.markdown("<div class='card'><h3>Data Load</h3></div>", unsafe_allow_html=True)
    
    with st.container():
        st.subheader("Filter Data by Category")

        # Cargar valores únicos para las ligas y temporadas desde un archivo CSV
        unique_values_df = pd.read_csv('./data/unique_leagues_seasons.csv')
        unique_leagues = unique_values_df['league'].dropna().tolist()
        unique_seasons = unique_values_df['season'].dropna().tolist()
        
        # Filtros multiselect para liga y temporada
        league_selection = st.multiselect("Select League(s):", unique_leagues)
        season_selection = st.multiselect("Select Season(s):", unique_seasons)

        # Comprobar si el dataset ya está cargado
        if 'dataset' not in st.session_state or st.session_state['dataset'] is None:
            st.session_state['data_loaded'] = False

        # Botón para cargar o recargar datos
        if st.session_state['data_loaded']:
            if st.button("Re-load Data"):
                # Recargar datos con los filtros seleccionados
                st.session_state['dataset'] = load_filtered_data(league_selection, season_selection)
                st.success("Data reloaded successfully!")
        else:
            if st.button("Load Data"):
                # Cargar datos por primera vez con los filtros seleccionados
                st.session_state['dataset'] = load_filtered_data(league_selection, season_selection)
                st.session_state['data_loaded'] = True
                st.success("Data loaded successfully!")

        # Mostrar los datos cargados, si están disponibles
        if st.session_state['data_loaded'] and st.session_state['dataset'] is not None:
            filtered_data = st.session_state['dataset']
            display_general_stats(filtered_data)
            st.dataframe(filtered_data)



# --------------------------------- Module 2: Dashboard ------------------------------------------

# Dashboard module
def dashboard_module(stats_list):
    st.markdown("<div class='card'><h3>Dashboard</h3></div>", unsafe_allow_html=True)
    
    # Asegúrate de que el dataset esté cargado en session_state
    if 'dataset' not in st.session_state or st.session_state['dataset'] is None:
        st.warning("Please load the dataset first in the Data Load module.")
        return

    # Usar el dataset de session_state
    original_df = st.session_state['dataset']
    
    # Filtros para el análisis primario
    st.subheader("Filters for Primary Analysis")
    primary_players = st.multiselect("Select Player(s):", original_df['Player'].dropna().unique(), key="primary_players")
    primary_teams = st.multiselect("Select Team(s):", original_df['Team within selected timeframe'].dropna().unique(), key="primary_teams")
    primary_leagues = st.multiselect("Select League(s):", original_df['league'].dropna().unique(), key="primary_leagues")
    
    # Selección de estadísticas comunes para el gráfico de radar (aplica para análisis primario y comparación)
    selected_stats = st.multiselect("Select Stats for Spider Chart", stats_list, key="shared_stats")

    # Checkbox para iniciar la comparación
    start_comparison = st.checkbox("Start Comparison", key="comparison_toggle")

    # Función para filtrar y mostrar el análisis basado en la selección
    def display_analysis(selected_players, selected_teams, selected_leagues, title="Primary Analysis"):
        # Hacer una copia del DataFrame original para evitar modificar el dataset global
        df = original_df.copy()

        # Aplicar filtros
        if selected_players:
            df = df[df['Player'].isin(selected_players)]
        elif selected_teams:
            df = df[df['Team within selected timeframe'].isin(selected_teams)]
        elif selected_leagues:
            df = df[df['league'].isin(selected_leagues)]
        
        # Determinar el contexto y mostrar los datos
        if len(selected_players) == 1:
            player_data = df[df['Player'] == selected_players[0]].iloc[0]
            st.markdown(f"### {title} - Demographic & Categorical Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Full Name**: {player_data['Full name']}")
                st.write(f"**Team**: {player_data['Team within selected timeframe']}")
                st.write(f"**Position**: {player_data['Primary position']}")
                st.write(f"**Age**: {player_data['Age']}")
                st.write(f"**Market Value**: {format_market_value(player_data['Market value'])}")
            with col2:
                st.write(f"**League**: {player_data['league']}")
                st.write(f"**Height**: {player_data['Height']}")
                st.write(f"**Weight**: {player_data['Weight']}")
                st.write(f"**Foot**: {player_data['Foot']}")
                st.write(f"**Contract Expires**: {player_data['Contract expires']}")

            # Crear gráfico de radar y tabla de estadísticas
            if selected_stats:
                fig = create_spider_chart(player_data.to_frame().T[selected_stats], selected_stats, title=f"{title} - Performance of {selected_players[0]}")
                st.plotly_chart(fig)
                st.write("### Stats Table")
                st.table(player_data[selected_stats].to_frame().T)

            return player_data.to_frame().T[selected_stats]
        
        elif len(selected_players) > 1 or selected_teams or selected_leagues:
            group_title = "Team" if selected_teams else "League" if selected_leagues else "Group of Players"
            st.markdown(f"### {title} - {group_title} Stats (Average)")
            group_data = df[selected_stats].mean()  # Calcular el promedio solo para las estadísticas seleccionadas
            
            # Mostrar tabla de estadísticas y gráfico de radar
            if selected_stats:
                fig = create_spider_chart(group_data.to_frame().T, selected_stats, title=f"{title} - Average {group_title} Performance")
                st.plotly_chart(fig)
            st.write("### Stats Table")
            st.table(group_data.to_frame().T)

            return group_data.to_frame().T[selected_stats]
    
    # Mostrar el análisis primario o iniciar el modo de comparación
    if not start_comparison:
        display_analysis(primary_players, primary_teams, primary_leagues)
    else:
        # Análisis en dos columnas (Comparación)
        col1, col2 = st.columns(2)
        
        # Columna izquierda: Análisis primario
        with col1:
            st.markdown("### Primary Analysis")
            display_analysis(primary_players, primary_teams, primary_leagues, title="Primary Analysis")
        
        # Columna derecha: Análisis de comparación
        with col2:
            st.markdown("### Comparison Analysis")
            comparison_players = st.multiselect("Select Player(s) for Comparison:", original_df['Player'].dropna().unique(), key="comp_players")
            comparison_teams = st.multiselect("Select Team(s) for Comparison:", original_df['Team within selected timeframe'].dropna().unique(), key="comp_teams")
            comparison_leagues = st.multiselect("Select League(s) for Comparison:", original_df['league'].dropna().unique(), key="comp_leagues")
            display_analysis(comparison_players, comparison_teams, comparison_leagues, title="Comparison Analysis")


# --------------------------------- Module 3: Cluster Analysis ------------------------------------------



# --------------------------------- Module 4: Evolution Analysis ------------------------------------------



# --------------------------------- Module 5: Recommendation System ------------------------------------------



# -------------------------------- side bar de navegacion --------------------------------------------

# Sidebar para guardar y cargar configuraciones
def main():
    with st.sidebar:
        st.title("Football Analytics App")

        # Main menu
        main_option = option_menu(
            menu_title="Main Menu",
            options=["Home Page", "Data Load", "Dashboard", "Cluster Analysis", "Evolution Analysis", "Recommendation System"],
            icons=["cloud-upload", "bounding-box"],
            menu_icon="cast",
            default_index=0,
        )

        # Selector de usuario
        user_name = st.selectbox("Select User", ["User 1", "User 2", "User 3"])
        
        # Mostrar opciones de configuraciones guardadas
        config_files = [f for f in os.listdir('./saved_configs') if f.startswith(f'config_{user_name}_')]
        load_config = st.selectbox("Load configuration", config_files, key="load_config")

        # Botón para cargar la configuración seleccionada
        if st.button("Load Configuration"):
            if load_config:
                load_configuration(load_config)
            else:
                st.warning("Please select a configuration to load.")

        # Botón para guardar la configuración actual
        if st.button("Save Configuration"):
            save_configuration(user_name)

    # Display the selected module in the main interface
    if main_option == "Home Page":
        homepage(user_name)
    elif main_option == "Data Load":
        data_load_module()
    elif main_option == "Cluster Analysis":
        st.warning("This module is under construction.")
    elif main_option == "Dashboard":
        dashboard_module(stats_list)
    elif main_option == "Evolution Analysis":
        st.warning("This module is under construction.")
    elif main_option == "Recommendation System":
        st.warning("This module is under construction.")


if __name__ == "__main__":
    main()