import streamlit as st
import pandas as pd
import numpy as np
import ast

artists = []
selected_year = ""
selected_artist = ""
search_keyword = ""

# 세션 저장
if "clicked_row" not in st.session_state:
    st.session_state.clicked_row = False
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
    
# 페이지 기본 설정(탭 제목, 아이콘, 레이아웃 등)
st.set_page_config(
    page_title="2019-2023 가사 검색",
    page_icon="🚀",
    layout="centered"
)
    
st.title("🚀 2019-2023 가사 검색")
st.subheader("그 때 그 시절의 노래를 찾아보세요!", divider="yellow", text_alignment="center")
st.write("")
# 파일읽어오기
@st.cache_data(show_spinner="CSV 파일을 불러오는 중입니다...")
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

df = load_data('data/lyrics_2019_2023.csv')
years = np.arange(2019, 2024)
with open('data/artists.txt', 'r', encoding='utf-8') as f:
    artists_data = f.readlines()
artists = artists_data[0].strip().split("/")

col1 , col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("년도 선택", years, index=None)
with col2:
    selected_artist = st.selectbox("가수 선택", artists, index=None)

search_str = ""
search_keyword = st.text_input("곡명 검색").strip()

if st.button("검색"):
    if selected_year is not None:
        search_str = f" (year == {selected_year}) "
    if selected_artist is not None:
        if search_str != "":
            search_str += " and "
        search_str += f" (artist == '{selected_artist.strip()}') "
    if search_keyword != "":
        if search_str != "":
            search_str += " and "
        search_str += f" (lyrics.str.contains('{search_keyword}')) "
    # st.write(search_str)
    if search_str != "":
        st.session_state.last_query = search_str
        st.session_state.clicked_row = True
    else:
        st.warning("검색 조건을 하나 이상 선택하세요.")
        st.session_state.clicked_row = False
        
if st.session_state.clicked_row:
    filtered_df = df.query(st.session_state.last_query)
    filtered_df = filtered_df.groupby("song_id")[["artist", "song_name","lyrics"]].max()
        
    st.write(f"검색 결과: {len(filtered_df)}곡")
    
    data = st.dataframe(filtered_df,
                 selection_mode='single-row',
                 on_select = "rerun",
                 use_container_width=True,
                 key="lyrics_table")
    
    st.divider()
    # # 가사 표시 로직
    if data.selection.rows:
        idx = data.selection.rows[0]
        selected_song = filtered_df.iloc[idx]
        st.subheader(f"✅ {selected_song['song_name']} 가사")
        
        lyrics_lst = ast.literal_eval(selected_song['lyrics']) # 객체로 만들기
        lyrics_lines = '<br>'.join(lyrics_lst)
        st.markdown(f"{lyrics_lines}", unsafe_allow_html=True)
        # st.code(lyrics_lines, language=None)
    else:
        st.info("👉 가사를 보려면 목록에서 행을 클릭하세요.")
    
