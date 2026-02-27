import os
import streamlit as st
from datetime import datetime
import requests
import pandas as pd

import folium
from streamlit_folium import st_folium
######## 퀴즈 api
# url = "https://opentdb.com/api.php?amount=1"
# def fetch_trivia():
#     import requests
#     try:
#         response = requests.get(url)
#         data = response.json()
#         return data['results']
#     except Exception as e:
#         return f"데이터를 가져오는 중 오류가 발생했습니다: {e}"

# print(fetch_trivia())

######날씨 api
# st.title("🌤️ 실시간 날씨 앱")

# # 서울 좌표
# lat = 37.57
# lon = 126.98

# url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

# response = requests.get(url).json()
# weather = response["current_weather"]

# st.metric("현재 기온", f"{weather['temperature']}°C")
# st.metric("풍속", f"{weather['windspeed']} km/h")
# st.write("관측 시간:", weather["time"])

## 국가 정보 API : REST Countries API
import streamlit.components.v1 as components

st.title("🌍 국가 정보 검색 앱")

country = st.text_input("국가 이름 입력", "south korea")

if country:
    url = f"https://restcountries.com/v3.1/name/{country}"
    response = requests.get(url).json()
    
    data = response[0]
    
    st.subheader(data["name"]["common"])
    st.image(data["flags"]["png"])
    st.write("수도:", data.get("capital", ["정보 없음"])[0])
    st.write("인구:", data["population"])
    st.write("지역:", data["region"])

    # google_maps_url = data["maps"]["googleMaps"]
    # osm_map = data["maps"]["openStreetMaps"]
    
    # print(osm_map)
    # st.subheader("📍 OpenStreetMap 지도")
    # components.iframe(osm_map, width=600, height=400)
    
    # st.subheader("🗺️ Google Maps 링크")
    # st.link_button("Google Maps에서 열기", google_maps_url)


    # st.title("📍 국가 위치 지도")

    # country = "korea"
    # url = f"https://restcountries.com/v3.1/name/{country}"
    # data = requests.get(url).json()[0]

    lat, lon = data["latlng"]
    
    # 지도 생성
    m = folium.Map(location=[lat, lon], zoom_start=5)

    # 마커 추가
    folium.Marker(
        [lat, lon],
        tooltip=data["name"]["common"]
    ).add_to(m)

    # Streamlit에 지도 출력
    st_folium(m, width=700, height=500)

# TVMaze API