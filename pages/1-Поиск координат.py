import numpy as np
import pandas as pd
import requests
import io
import os
import matplotlib.pyplot as plt
import seaborn as sns
import osmnx as ox
import geopandas as gpd
sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(20,20))
from shapely import wkt
import streamlit as st
import streamlit as st
import pandas as pd 
import geopandas as gpd 
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

st.set_page_config(
page_title="Геокодер адресов",
page_icon="🔎",
layout="wide",
initial_sidebar_state="expanded",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Определитель количества остановок')
st.info('Данный модуль помогает узнать по координатам сколько в заданном радиусе от вас остановок', icon="ℹ️")

def get_bus_stop_around_area(point, dist, len_=True):
  data = ox.geometries_from_point(center_point=point, tags={'highway': 'bus_stop'}, dist=dist)

  if len_:
    return int(len(data))
  else:
    return data


def main():
  file = st.file_uploader("Загрузите файл в формате xlsx")
  if file is not None:
    file.seek(0)
    df_address = pd.read_excel(file)
    st.write(df_address.head())
    st.write(df_address.shape)
    selection = st.selectbox("Выберите столбец с широтой", df_address.columns.tolist())
    df_address["latitude"] = df_address[selection]
    selection = st.selectbox("Выберите столбец с долготой", df_address.columns.tolist())
    df_address["longitude"] = df_address[selection]
    dist = st.slider('Укажите радиус', min_value=100, max_value=1000, value=150, step=10)
    df_address["radius"] = dist

    if st.checkbox("Найти остановки по координатам"):
      with st.spinner('Ожидайте, идет поиск...'):
        busstation = []
        for lat, lon in zip(df_address['latitude'], df_address['longitude']):

          try:
            busstation.append(get_bus_stop_around_area(point=(lat, lon), dist=dist))
            if busstation[-1] ==  max(busstation):
              max_cords = (lat, lon)

          except:
            busstation.append(0)
        df_address['Кол-во остановок'] = busstation
        st.success('Готово!')
        st.write(df_address.head())


    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
      df_address.to_excel(writer,index=False)
      writer.close()
      st.download_button(
      label="📥 Нажмите, чтобы скачать данные с координатами остановок",
      data=buffer,
      file_name=f"Координаты_'{os.path.splitext(file.name)[0]}'.xlsx",
      mime="application/vnd.ms-excel"
      )
    try:
      # center on Liberty Bell, add marker
      mk = {"radius": 6}
      tiles = "cartodbdarkmatter"
      m = get_bus_stop_around_area(point=max_cords, dist=dist, len_=False).explore(tiles=tiles, color="red", tooltip="name", marker_kwds=mk)
      folium.Marker(
        max_cords, popup="Liberty Bell", tooltip="Liberty Bell"
      ).add_to(m)

    # call to render Folium map in Streamlit
      st_folium(m, width=725)
    except:
      pass
if __name__ == "__main__":
  main()