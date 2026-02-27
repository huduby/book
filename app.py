# pip install streamlit wikipedia google-generativeai dotenv
# https://github.com/huduby/webapp_project.git
import os
import streamlit as st
import wikipedia
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # .env 파일에서 환경 변수 로드

GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_API_KEY = os.getenv("GEMINI_API")
# 1. 설정: 위키피디아 언어 설정 및 AI API 키 설정
wikipedia.set_lang("ko")
# 여기에 본인의 Gemini API 키를 입력하세요.
genai.configure(api_key=GEMINI_API_KEY)
# for m in genai.list_models():
#     # generateContent 지원 모델만 필터링
#     if "generateContent" in getattr(m, "supported_generation_methods", []):
#         print(m.name, m.supported_generation_methods)

def get_history_of_today():
    """오늘 날짜의 위키피디아 사건 요약을 가져옵니다."""
    today = datetime.now()
    # 위키피디아의 날짜 문서 제목 형식 (예: 2월 5일)
    date_str = f"{today.month}월 {today.day}일"
    
    try:
        # 해당 날짜의 페이지 요약 가져오기
        page = wikipedia.page(date_str)
        return page.summary[:1500] # 너무 길면 잘라서 전달
    except Exception as e:
        return f"데이터를 가져오는 중 오류가 발생했습니다: {e}"

def ask_ai_interpretation(history_data):
    """AI에게 역사적 사건에 대한 재해석을 요청합니다."""
    model = genai.GenerativeModel(GEMINI_MODEL)
    # print(model)
    prompt = f"""
    아래는 오늘 날짜에 일어난 역사적 사건들의 요약이야.
    이 내용 중에서 가장 흥미로운 사건 하나를 골라서 다음 형식으로 말해줘.
    
    1. 오늘의 사건: (사건 이름과 연도)
    2. 타임머신 브리핑: (사건을 실감나게 설명)
    3. 오늘의 교훈: (현대를 사는 우리에게 주는 메시지)
    
    내용: {history_data}
    """
    
    # API 키가 없을 경우를 대비한 예외 처리
    try:
        # print(prompt)
        response = model.generate_content(prompt)
        # print(response.text)
        return response.text
    except Exception as e:
        return "AI 연결 설정(API 키)이 필요합니다. 위키피디아 데이터만 표시합니다.\n\n" + history_data

# 2. Streamlit UI 구성
st.set_page_config(page_title="AI 역사 타임머신", page_icon="⏳")
st.title("⏳ AI 역사 타임머신")
st.subheader("오늘, 역사 속으로 떠나는 여행")

if st.button("과거로 이동하기"):
    with st.spinner('역사 데이터를 수집하고 AI가 분석 중입니다...'):
        # 데이터 가져오기
        history_summary = get_history_of_today()
        
        # AI 해석 가져오기
        result = ask_ai_interpretation(history_summary)
        
        st.success("도착했습니다!")
        st.markdown("---")
        st.markdown(result)
        
        # 하단에 출처 표시
        st.caption(f"출처: 위키피디아 '{datetime.now().month}월 {datetime.now().day}일' 문서")
else:
    st.info("위 버튼을 누르면 오늘 날짜에 일어난 역사적 사건과 AI의 조언을 볼 수 있습니다.")