# create a streamlit app with the tittle "Car accidents Analysis", put a side bar with dummy modules
# and a main section with a title and a subtitle

import streamlit as st
import pandas as pd
import plotly.express as px
from math import
from pyspark.sql import SparkSession
from streamlit_option_menu import option_menu

# Initialize Spark session
spark = SparkSession.builder.appName("CarAccidents").getOrCreate()

# --------------------------------- General Functions --------------------------------------------------

# --------------------------------- Module: Home Page --------------------------------------------------

# Display Instructions at the start of the app or within a specific module (dummy instructions)
def display_instructions():
    st.markdown("""
    ### Instructions for Using the Car Accidents Analysis App

    Welcome to the Car Accidents Analysis App! This app is designed to help you analyze car accidents data through various modules. Here’s a step-by-step guide on how to use the app:

    1. **Home Page**:
       - This is the landing page of the app. You can navigate to different modules using the sidebar menu.

    """, unsafe_allow_html=True)

# --------------------------------- Sie Bar --------------------------------------------------

def main():
    with st.sidebar:
        st.title("Football Analytics App")

        # Main menu
        main_option = option_menu(
            options=["Home Page", "Module 1", "Module 2"],
            icons=["cloud-upload", "bounding-box"],
            menu_icon="cast",
            default_index=0,
        )

    # Display the selected module in the main interface
    if main_option == "Home Page":
        display_instructions()
    elif main_option == "Module 1":
        st.info("Module 1 is under construction. Please check back later.")
    elif main_option == "Module 2":
        st.info("Module 2 is under construction. Please check back later.")


if __name__ == "__main__":
    main()