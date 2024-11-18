import streamlit as st
from pyspark.sql import SparkSession
import pandas as pd
import plotly.express as px
from math import isnan

# Initialize Spark session
spark = SparkSession.builder.appName("FootballAnalyticsApp").getOrCreate()

# --------------------------------- General Functions --------------------------------------------------


# --------------------------------- Module: Home Page --------------------------------------------------

# Display Instructions at the start of the app or within a specific module
def display_instructions():
    st.markdown("## Instructions")
    st.markdown("""
    1. **In Data Selection Module**: Start by creating a DataFrame to work with.
    
    2. **Select Your Approach**:
       - **Data Filtering & Selection**: Filter the dataset by specific criteria such as season, league, team, etc.
       - **Scouting**: Filter by in-game stats, age, and other relevant metrics.
    
    3. **Save Configuration**: Once you've selected your filters and approach, save the configuration to keep your settings.
    
    4. **WIP**: More features are coming soon!
    """)

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

# Function to generate a spider chart
def create_spider_chart(data, selected_stats, title="Spider Chart", color=None):
    fig = px.line_polar(
        r=data[selected_stats].values.flatten(),
        theta=selected_stats,
        line_close=True,
        title=title
    )
    fig.update_traces(fill='toself', line=dict(color=color))
    return fig