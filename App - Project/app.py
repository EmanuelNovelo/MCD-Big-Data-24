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
import plotly.graph_objects as go

# --------------------------------- py's functions --------------------------------------------------

from utils import (
    add_sidebar_background,
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

# Add custom CSS styles to the sidebar
add_sidebar_background()

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

    # insert header image
    st.image('./img/header.png', use_container_width=True)

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
# Dashboard module
def dashboard_module(stats_list):
    st.markdown("<div class='card'><h3>Dashboard</h3></div>", unsafe_allow_html=True)
    
    # Asegúrate de que el dataset esté cargado en session_state
    if 'dataset' not in st.session_state or st.session_state['dataset'] is None:
        st.warning("Please load the dataset first in the Data Load module.")
        return

    original_df = st.session_state['dataset']
    
    # Nueva sección de filtro de temporadas
    st.subheader("Filter by Seasons")
    all_seasons = sorted(original_df['season'].dropna().unique())
    selected_seasons = st.multiselect(
        "Select Season(s):", 
        options=all_seasons, 
        default=[all_seasons[0]] if all_seasons else []
    )
    
    # Filtrar el dataset por las temporadas seleccionadas
    filtered_df = original_df[original_df['season'].isin(selected_seasons)]

    # Filtros de jugadores, equipos y ligas
    st.subheader("Filters for Primary Analysis")
    primary_players = st.multiselect("Select Player(s):", filtered_df['Player'].dropna().unique(), key="primary_players")
    primary_teams = st.multiselect("Select Team(s):", filtered_df['Team within selected timeframe'].dropna().unique(), key="primary_teams")
    primary_leagues = st.multiselect("Select League(s):", filtered_df['league'].dropna().unique(), key="primary_leagues")
    selected_stats = st.multiselect("Select Stats for Spider Chart", stats_list, key="shared_stats")
    start_comparison = st.checkbox("Start Comparison", key="comparison_toggle")

    # Nueva función para manejar promedios
    def aggregate_data(df, group_by, stats):
        aggregated = df.groupby(group_by).agg({
            **{stat: 'mean' for stat in stats},
            'Team within selected timeframe': lambda x: ', '.join(x.unique()),
            'league': lambda x: ', '.join(x.unique())
        }).reset_index()
        return aggregated

    def display_analysis(selected_players, selected_teams, selected_leagues, title="Primary Analysis", color="blue"):
        df = filtered_df.copy()

        # Aplicar filtros
        if selected_players:
            df = df[df['Player'].isin(selected_players)]
        elif selected_teams:
            df = df[df['Team within selected timeframe'].isin(selected_teams)]
        elif selected_leagues:
            df = df[df['league'].isin(selected_leagues)]

        # Agregar mensajes de promedio debido a datos repetidos
        if len(df) > 1:  # Si hay más de un registro filtrado
            if selected_players and len(selected_seasons) == 1:
                # Para jugadores en una sola temporada
                st.info(f"{', '.join(df['Player'].unique())} average due to multiple records in the selected season ({selected_seasons[0]}).")
            elif len(selected_seasons) > 1:
                # Para jugadores, equipos o ligas en múltiples temporadas
                if selected_players:
                    st.info(f"{', '.join(df['Player'].unique())} average due to multiple seasons selected ({', '.join(map(str, selected_seasons))}).")
                elif selected_teams:
                    st.info(f"{', '.join(df['Team within selected timeframe'].unique())} average due to multiple seasons selected ({', '.join(map(str, selected_seasons))}).")
                elif selected_leagues:
                    st.info(f"{', '.join(df['league'].unique())} average due to multiple seasons selected ({', '.join(map(str, selected_seasons))}).")

        if not df.empty:
            # Agregar promedios por temporada
            aggregated_data = aggregate_data(df, ['Player', 'season'], selected_stats)

            # Mostrar información demográfica y gráfica
            if len(selected_players) == 1:
                player_data = aggregated_data[aggregated_data['Player'] == selected_players[0]]
                st.markdown(f"### {title} - Demographic & Categorical Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Player(s):** {selected_players[0]}")
                    st.write(f"**Teams:** {', '.join(player_data['Team within selected timeframe'].unique())}")
                    st.write(f"**Leagues:** {', '.join(player_data['league'].unique())}")
                    #st.write(f"**Age:** {', '.join(player_data['Age'].astype(str).unique())}")
                    #st.write(f"**Market Value:** {format_market_value(player_data['Market Value'].mean())}")
                with col2:
                    st.write(f"**Seasons:** {', '.join(player_data['season'].astype(str).unique())}")
                    #st.write(f"**Height:** {', '.join(player_data['Height'].astype(str).unique())}")
                    #st.write(f"**Weight:** {', '.join(player_data['Weight'].astype(str).unique())}")
                    #st.write(f"**Foot:** {', '.join(player_data['Foot'].astype(str).unique())}")
                    #st.write(f"**Contract Expiry:** {', '.join(player_data['Contract expires'].astype(str).unique())}")


                if selected_stats:
                    fig = create_spider_chart(
                        player_data[selected_stats].mean().to_frame().T,
                        selected_stats,
                        title=f"{title} - Performance of {selected_players[0]}",
                        legend_name=selected_players[0],
                        color=color
                    )
                    st.plotly_chart(fig)
                    st.write("### Stats Table")
                    st.table(player_data[selected_stats].mean().to_frame().T)

                return player_data[selected_stats].mean().to_frame().T

            elif len(selected_players) > 1 or selected_teams or selected_leagues:
                group_title = "Team" if selected_teams else "League" if selected_leagues else "Group of Players"
                group_data = aggregated_data[selected_stats].mean()
                if selected_stats:
                    fig = create_spider_chart(
                        group_data.to_frame().T,
                        selected_stats,
                        title=f"{title} - Average {group_title} Performance",
                        legend_name=f"Average {group_title}",
                        color=color
                    )
                    st.plotly_chart(fig)
                st.write("### Stats Table")
                st.table(group_data.to_frame().T)

                return group_data.to_frame().T

    if not start_comparison:
        primary_data = display_analysis(primary_players, primary_teams, primary_leagues, title="Primary Analysis", color="blue")
    else:
        col1, col2 = st.columns(2)
        with col1:
            primary_data = display_analysis(primary_players, primary_teams, primary_leagues, title="Primary Analysis", color="blue")
        with col2:
            comparison_players = st.multiselect("Select Player(s) for Comparison:", filtered_df['Player'].dropna().unique(), key="comp_players")
            comparison_teams = st.multiselect("Select Team(s) for Comparison:", filtered_df['Team within selected timeframe'].dropna().unique(), key="comp_teams")
            comparison_leagues = st.multiselect("Select League(s) for Comparison:", filtered_df['league'].dropna().unique(), key="comp_leagues")
            comparison_data = display_analysis(comparison_players, comparison_teams, comparison_leagues, title="Comparison Analysis", color="red")

        if selected_stats and primary_data is not None and comparison_data is not None:
            combined_fig = go.Figure()
            combined_fig.add_trace(go.Scatterpolar(
                r=primary_data.iloc[0].values.tolist(),
                theta=selected_stats,
                fill='toself',
                name="Primary Analysis",
                line=dict(color="blue")
            ))
            combined_fig.add_trace(go.Scatterpolar(
                r=comparison_data.iloc[0].values.tolist(),
                theta=selected_stats,
                fill='toself',
                name="Comparison Analysis",
                line=dict(color="red")
            ))
            st.markdown("### Combined Radar Chart")
            st.plotly_chart(combined_fig)



# --------------------------------- Module 3: Cluster Analysis ------------------------------------------

def cluster_analysis_module(stats_list):

    st.info("This module is under construction.")

# --------------------------------- Module 4: Evolution Analysis ------------------------------------------

# If player found in more than one season then we can do evolution analysis, else not
def evolution_analysis_module(stats_list):
    st.markdown("<div class='card'><h3>Evolution Analysis</h3></div>", unsafe_allow_html=True)
    
    # Check if dataset is loaded in session state
    if 'dataset' not in st.session_state or st.session_state['dataset'] is None:
        st.warning("Please load the dataset first in the Data Load module.")
        return
    
    original_df = st.session_state['dataset']
    
    # Validate if the required columns exist in the dataset
    required_columns = ['Player', 'season', 'Age', 'Team within selected timeframe', 'league'] + stats_list
    missing_columns = [col for col in required_columns if col not in original_df.columns]
    if missing_columns:
        st.error(f"The dataset is missing the following required columns: {', '.join(missing_columns)}")
        return
    
    # Display filters for evolution analysis
    st.subheader("Filters for Evolution Analysis")
    
    # Multiselect for players
    evolution_players = st.multiselect("Select Player(s):", original_df['Player'].dropna().unique(), key="evolution_players")
    
    # Multiselect for seasons with all seasons selected by default
    all_seasons = original_df['season'].dropna().unique()
    selected_seasons = st.multiselect(
        "Select Season(s):", 
        options=sorted(all_seasons), 
        default=sorted(all_seasons), 
        key="evolution_seasons"
    )
    
    # Multiselect for stats
    selected_stats = st.multiselect("Select Stats for Line Chart", stats_list, key="evolution_stats")

    # Ensure at least one player, one stat, and one season are selected
    if not evolution_players:
        st.warning("Please select at least one player for Evolution Analysis.")
        return

    if not selected_seasons:
        st.warning("Please select at least one season for Evolution Analysis.")
        return

    if not selected_stats:
        st.warning("Please select at least one stat for the line chart.")
        return

    # Filter data for the selected players and seasons
    player_data = original_df[
        (original_df['Player'].isin(evolution_players)) & 
        (original_df['season'].isin(selected_seasons))
    ]

    # Handle players appearing multiple times in a season by taking the highest value for each stat
    player_data = player_data.groupby(['Player', 'season']).agg({
        **{stat: 'max' for stat in selected_stats},  # Highest value for each stat
        'Age': 'max',  # Use max (it will always be the same for a player in a season)
        'Team within selected timeframe': lambda x: ', '.join(set(x)),  # Concatenate teams
        'league': lambda x: ', '.join(set(x))  # Concatenate leagues
    }).reset_index()

    # Reshape data for Plotly (long format)
    melted_data = player_data.melt(
        id_vars=['Player', 'season', 'Age', 'Team within selected timeframe', 'league'],
        value_vars=selected_stats,
        var_name='Stat',
        value_name='Value'
    )

    # Generate line chart for evolution analysis
    st.markdown("### Evolution Analysis - Performance Over Seasons")
    fig = px.line(
        melted_data,
        x='season',  # Eje X representa las temporadas
        y='Value',  # Eje Y representa el valor de las estadísticas
        color='Player',  # Diferenciar jugadores con colores únicos
        line_dash='Stat',  # Diferenciar estadísticas con estilos de línea
        title="Performance Evolution Over Seasons",
        labels={"season": "Season", "Value": "Stat Value", "Player": "Player", "Stat": "Statistic"},
        markers=True
    )

    # Display the chart
    fig.update_layout(
        legend_title="Legend",
        xaxis_title="Season",
        yaxis_title="Value",
        hovermode="x unified"
    )
    st.plotly_chart(fig)

    # Información detallada de las temporadas para cada jugador
    st.markdown("### Detailed Season Information")

    for player in evolution_players:
        # Filtrar los datos para el jugador actual
        player_data_filtered = player_data[player_data['Player'] == player]
        
        st.markdown(f"#### {player}")
        # Crear un season_data por jugador
        season_data = player_data_filtered[player_data_filtered['season'].isin(selected_seasons)]
        
        with st.container(border=True):
            if not season_data.empty:
                # Crear columnas dinámicas para las temporadas seleccionadas
                cols = st.columns(len(selected_seasons))
                for idx, season in enumerate(sorted(selected_seasons)):
                    season_info = season_data[season_data['season'] == season]

                    with cols[idx]:  # Información de cada temporada en su columna
                        st.markdown(f"##### Season: {season}")
                        if not season_info.empty:
                            # Obtener datos únicos para la temporada
                            teams = season_info['Team within selected timeframe'].unique()
                            leagues = season_info['league'].unique()
                            ages = season_info['Age'].unique()

                            st.write(f"**Teams:** {', '.join(teams)}")
                            st.write(f"**Leagues:** {', '.join(leagues)}")
                            st.write(f"**Age:** {', '.join(map(str, ages))}")

                            # Añadir mensaje para casos con múltiples registros en una temporada
                            if len(season_info) > 1:
                                st.info(f"Data point shown is the highest reach in one of the teams/leagues for {season}.")

                            # Mostrar estadísticas seleccionadas
                            for stat in selected_stats:
                                max_value = season_info[stat].max()
                                st.write(f"**{stat}:** {max_value}")
                        else:
                            st.write("No data available for this season.")



# --------------------------------- Module 5: Recommendation System ------------------------------------------

def recommendation_system_module():

    st.info("This module is under construction.")

# -------------------------------- side bar de navegacion --------------------------------------------

# Sidebar para guardar y cargar configuraciones
def main():

    # change background color of the Main Menu box
    st.markdown("""
        <style>
        /* Cambiar fondo de la caja del Main Menu */
        .css-1v3fvcr { /* Selector específico del Main Menu */
            background: linear-gradient(180deg, #2c3e50, #4a6073); /* Degradado más tenue */
            color: white;
            padding: 10px; /* Margen interno */
            border-radius: 10px; /* Bordes redondeados */
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); /* Sombra suave */
        }

        /* Modificar los textos dentro de selectbox */
        .stSelectbox > div {
            color: white !important;
        }

        /* Botones */
        .stButton > button {
            background-color: #1f77b4; 
            color: white;
            border-radius: 12px;
        }

        /* Cambiar el texto de Load Configuration */
        .stSelectbox {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

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
        cluster_analysis_module(stats_list)
    elif main_option == "Dashboard":
        dashboard_module(stats_list)
    elif main_option == "Evolution Analysis":
        evolution_analysis_module(stats_list)
    elif main_option == "Recommendation System":
        recommendation_system_module()


if __name__ == "__main__":
    main()