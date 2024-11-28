import streamlit as st
from pyspark.sql import SparkSession
import pandas as pd
import plotly.express as px
from math import isnan
import plotly.graph_objects as go

# Initialize Spark session
spark = SparkSession.builder.appName("FootballAnalyticsApp").getOrCreate()

# --------------------------------- General Functions --------------------------------------------------

def add_sidebar_background():
    sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #a3c1dd, #bfdcf0); /* Degradado azul más saturado */
            color: black;
        }
        [data-testid="stSidebar"] .css-1v3fvcr {
            color: black;  /* Cambiar el color del texto del sidebar */
        }
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

# --------------------------------- Module: Home Page --------------------------------------------------

# Display Instructions at the start of the app or within a specific module
def display_instructions():
    st.markdown("""
    ### Instructions for Using the Football Analytics App

    Welcome to the Football Analytics App! This app is designed to help you analyze football data through various modules. Here’s a step-by-step guide on how to use the app:

    1. **Home Page**:
       - This is the landing page of the app. You can navigate to different modules using the sidebar menu.

    2. **Data Load Module**:
       - **Purpose**: Load and filter football data based on leagues and seasons.
       - **Steps**:
         1. Select the leagues you are interested in from the "Select League(s)" multiselect box.
         2. Select the seasons you are interested in from the "Select Season(s)" multiselect box.
         3. Click the "Load Data" button to load the data for the first time.
         4. If you want to reload the data with different filters, click the "Re-load Data" button.
         5. Once the data is loaded, you will see general statistics and a table of the filtered data.

    3. **Dashboard Module**:
       - **Purpose**: Perform primary analysis and comparison of players, teams, or leagues.
       - **Steps**:
         1. Ensure the data is loaded in the Data Load module.
         2. Select players, teams, or leagues for primary analysis using the multiselect boxes.
         3. Select the statistics you want to analyze using the "Select Stats for Spider Chart" multiselect box.
         4. If you want to compare different entities, check the "Start Comparison" checkbox.
         5. The analysis will be displayed based on your selections, including demographic information, spider charts, and statistics tables.

    4. **Cluster Analysis Module**:
       - **Purpose**: This module is under construction and will be available in future updates.

    5. **Evolution Analysis Module**:
       - **Purpose**: Analyze the evolution of player performance over multiple seasons.
       - **Steps**:
         1. Ensure the data is loaded in the Data Load module.
         2. Select players for evolution analysis using the "Select Player(s)" multiselect box.
         3. Select the seasons you want to analyze using the "Select Season(s)" multiselect box.
         4. Select the statistics you want to analyze using the "Select Stats for Line Chart" multiselect box.
         5. The evolution analysis will be displayed as a line chart showing the performance of selected players over the selected seasons.

    6. **Recommendation System Module**:
       - **Purpose**: This module is under construction and will be available in future updates.

    7. **Configuration Management**:
       - **Save Configuration**: Save your current settings and selections by clicking the "Save Configuration" button in the sidebar.
       - **Load Configuration**: Load a previously saved configuration by selecting it from the "Load configuration" dropdown and clicking the "Load Configuration" button.

    ### Example Usage
    1. Start by loading the data in the Data Load module.
    2. Navigate to the Dashboard module to perform primary analysis or comparisons.
    3. Use the Evolution Analysis module to track player performance over time.
    4. Save your configurations for future use.

    Feel free to explore the different modules and functionalities of the app. If you have any questions or need further assistance, please refer to the documentation or contact support.
    """, unsafe_allow_html=True)

# --------------------------------- Module: Data Load -------------------------------------------------- 

# Cached function to load and filter data based on user selections
@st.cache_data
def load_filtered_data(league_selection, season_selection):
    file_path = './data/football-players-DB.csv'
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    # Apply filters based on selections
    if league_selection:
        df = df.filter(df.league.isin(league_selection))
    if season_selection:
        df = df.filter(df.season.isin(season_selection))
    
    # Convert Spark DataFrame to Pandas for compatibility with Streamlit components
    return df.toPandas()

# Function to display general statistics
def display_general_stats(df):
    # Calculate general statistics
    num_teams = df['Team within selected timeframe'].nunique()
    num_players = df['Player'].nunique()
    num_leagues = df['league'].nunique()
    num_rows = df.shape[0]

    # Display stats in containers
    with st.container(border=True):
        st.subheader("General Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Number of Teams", num_teams)
        with col2:
            st.metric("Number of Players", num_players)
        with col3:
            st.metric("Number of Leagues", num_leagues)
        with col4:
            st.metric("Number of Rows", num_rows)

# --------------------------------- Module: Dashboard --------------------------------------------------

# convert market value to money format
def format_market_value(value):
    return f"${value:,.2f}"

# create a radar chart for the given data
def create_spider_chart(data, stats, title="Radar Chart", legend_name=None, color=None):
    import plotly.graph_objects as go

    fig = go.Figure()

    # Añadir traza para el conjunto de datos
    fig.add_trace(go.Scatterpolar(
        r=data.iloc[0].values.tolist(),
        theta=stats,
        fill='toself',
        name=legend_name,  # Nombre para la leyenda
        line=dict(color=color) if color else None  # Asignar color si se proporciona
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True),
        ),
        showlegend=True,
        title=title
    )
    return fig

