import streamlit as st
import math
# 환율 라이브러리가 설치되어 있어야 합니다: pip install forex-python
from forex_python.converter import CurrencyRates

def run_calculator():
    st.header("🧮 공학용 계산기")
    formula = st.text_input("수식을 입력하세요 (예: sin(30) * sqrt(16))", "math.sin(math.radians(30)) * math.sqrt(16)")
    if st.button("계산"):
        try:
            # 안전을 위해 math 라이브러리의 함수를 사용할 수 있도록 합니다.
            result = eval(formula, {"math": math})
            st.success(f"결과: {result}")
        except Exception as e:
            st.error(f"오류 발생: {e}")

def run_unit_converter():
    st.header("⚖️ 단위 변환기 (길이/무게)")
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("카테고리", ["길이 (km ↔ mile)", "무게 (kg ↔ lb)"])
        value = st.number_input("값 입력", value=1.0)
    
    with col2:
        if category == "길이 (km ↔ mile)":
            st.write(f"**Mile:** {value * 0.621371:.2f} mi")
            st.write(f"**KM:** {value / 0.621371:.2f} km")
        else:
            st.write(f"**Pound:** {value * 2.20462:.2f} lb")
            st.write(f"**KG:** {value / 2.20462:.2f} kg")

def run_currency_converter():
    st.header("💱 실시간 환율 (무료 API)")
    st.warning("네트워크 상태에 따라 응답이 느릴 수 있습니다.")
    
    c = CurrencyRates()
    col1, col2 = st.columns(2)
    
    with col1:
        base = st.selectbox("기준 통화", ["USD", "EUR", "KRW", "JPY"])
        amount = st.number_input("금액", value=1.0)
    
    with col2:
        target = st.selectbox("대상 통화", ["KRW", "USD", "JPY", "EUR"])
        if st.button("환율 변환"):
            try:
                rate = c.get_rate(base, target)
                converted = amount * rate
                st.metric(label=f"{target} 결과", value=f"{converted:,.2f} {target}")
            except:
                st.error("현재 환율 정보를 가져올 수 없습니다. 다시 시도해 주세요.")

# 메인 UI 구성
st.title("🛠️ 생활 밀착형 통합 유틸리티")

tab1, tab2, tab3 = st.tabs(["환율 변환", "단위 변환", "공학용 계산기"])

with tab1:
    run_currency_converter()
with tab2:
    run_unit_converter()
with tab3:
    run_calculator()