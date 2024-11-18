import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Folder to store configurations
CONFIG_FOLDER = "./configs"

# Ensure the folder exists
os.makedirs(CONFIG_FOLDER, exist_ok=True)

from datetime import date

def save_configuration(user_name):
    # Definir el nombre del archivo con formato `config_user_fecha.json`
    date_str = datetime.now().strftime("%Y%m%d")
    config_filename = f"config_{user_name}_{date_str}.json"
    config_path = os.path.join('./saved_configs', config_filename)

    # Convertir el DataFrame en un diccionario y manejar las fechas
    df = st.session_state['dataset'].copy()
    
    # Convertir todas las columnas de tipo `datetime` y `date` a cadenas
    for column in df.columns:
        if df[column].dtype == 'datetime64[ns]':
            df[column] = df[column].dt.strftime('%Y-%m-%d')
        elif df[column].dtype == 'object':
            # Intentar convertir las fechas en formato `object` que parecen ser `date`
            df[column] = df[column].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime) else x)

    config_data = {
        "filters": {
            "leagues": st.session_state.get('league_selection', []),
            "seasons": st.session_state.get('season_selection', [])
        },
        "dataset": df.to_dict(orient='records')  # Guardar en formato JSON compatible
    }

    # Guardar el archivo JSON
    with open(config_path, 'w') as file:
        json.dump(config_data, file)
    
    st.success(f"Configuration saved successfully as {config_filename}!")

def load_configuration(selected_config):
    # Ruta del archivo de configuración seleccionado
    config_path = os.path.join('./saved_configs', selected_config)

    # Cargar el archivo JSON
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # Restaurar los filtros de la configuración
    st.session_state['league_selection'] = config_data['filters']['leagues']
    st.session_state['season_selection'] = config_data['filters']['seasons']

    # Restaurar el dataset en session_state
    st.session_state['dataset'] = pd.DataFrame(config_data['dataset'])
    st.success(f"Configuration {selected_config} loaded successfully!")


# Function to list available configurations for a user
def get_user_configurations(user_name):
    config_files = [f for f in os.listdir(CONFIG_FOLDER) if f.startswith(user_name)]
    return config_files