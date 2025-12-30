import requests
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def get_pitcher_names(season=2025):
    url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
    data = requests.get(url).json()
    df = pd.DataFrame(data=data['data'])
    columns = ['PlayerName', 'xMLBAMID', 'FangraphsID']
    return df[columns]

@st.cache_data(ttl=3600)
def get_batter_names(season=2025):
    url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=bat&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
    data = requests.get(url).json()
    df = pd.DataFrame(data=data['data'])
    columns = ['PlayerName', 'xMLBAMID', 'FangraphsID']
    return df[columns]
