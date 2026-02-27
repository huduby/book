import streamlit as st
import requests
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="날씨 옷차림 추천",
    page_icon="🌤️",
    layout="centered",
)

# ── 스타일 ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; }

.main { background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 100%); }

.weather-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.6);
}

.temp-big {
    font-size: 4rem;
    font-weight: 700;
    color: #0369a1;
    line-height: 1;
}

.outfit-item {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-left: 4px solid #0ea5e9;
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    font-size: 1rem;
}

.forecast-card {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    flex: 1;
}

.tag {
    display: inline-block;
    background: #0ea5e9;
    color: white;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.85rem;
    margin: 0.2rem;
}

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(14,165,233,0.4);
}
</style>
""", unsafe_allow_html=True)


# ── 도시 → 위경도 변환 ────────────────────────────────────────
CITY_COORDS = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "인천": (37.4563, 126.7052),
    "대구": (35.8714, 128.6014),
    "대전": (36.3504, 127.3845),
    "광주": (35.1595, 126.8526),
    "제주": (33.4890, 126.4983),
    "수원": (37.2636, 127.0286),
    "도쿄": (35.6762, 139.6503),
    "뉴욕": (40.7128, -74.0060),
    "런던": (51.5074, -0.1278),
    "파리": (48.8566, 2.3522),
    "방콕": (13.7563, 100.5018),
    "싱가포르": (1.3521, 103.8198),
}


def get_weather(lat, lon):
    """Open-Meteo API 호출 (무료, 키 없음)"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m",
                    "apparent_temperature", "precipitation",
                    "weather_code", "wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "weather_code"],
        "timezone": "auto",
        "forecast_days": 5,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def weather_code_to_emoji(code):
    if code == 0:          return "☀️", "맑음"
    elif code in (1,2):    return "🌤️", "구름 조금"
    elif code == 3:        return "☁️", "흐림"
    elif code in range(51,68): return "🌧️", "비"
    elif code in range(71,78): return "❄️", "눈"
    elif code in range(80,83): return "🌦️", "소나기"
    elif code in (95,96,99):  return "⛈️", "뇌우"
    else:                  return "🌡️", "기타"


def get_outfit_recommendation(temp, feels_like, humidity, precip, wind):
    """기온·체감온도 기반 옷차림 추천"""
    outfits = []
    tips = []

    # 상의
    if feels_like >= 28:
        outfits += ["👕 반팔 티셔츠", "🩳 반바지 / 원피스"]
        tips.append("자외선 차단제 필수! 통기성 좋은 소재 추천")
    elif feels_like >= 23:
        outfits += ["👕 반팔 티셔츠", "👖 얇은 긴 바지 또는 청바지"]
    elif feels_like >= 17:
        outfits += ["👔 긴팔 셔츠 / 얇은 니트", "👖 청바지 또는 슬랙스"]
        tips.append("낮과 밤 기온 차이를 대비해 얇은 겉옷 챙기기")
    elif feels_like >= 10:
        outfits += ["🧥 가디건 / 후드집업", "👖 두꺼운 청바지 또는 면바지"]
        outfits.append("🧣 얇은 스카프 또는 머플러")
    elif feels_like >= 3:
        outfits += ["🧥 코트 또는 패딩 (중간 두께)", "🧤 장갑", "🧣 머플러"]
    else:
        outfits += ["🧥 두꺼운 패딩 / 롱패딩", "🧤 방한 장갑", "🧣 두꺼운 머플러", "🎩 귀마개 / 방한 모자"]
        tips.append("체온 유지가 중요! 레이어드 착장 추천")

    # 우산
    if precip > 1:
        outfits.append("☂️ 우산 또는 우비")
        tips.append("오늘 비 예보! 방수 신발 추천")
    elif precip > 0.1:
        outfits.append("☂️ 우산 (접이식)")

    # 바람
    if wind > 7:
        tips.append(f"강풍 주의 ({wind:.1f}m/s) — 바람막이 겉옷 추천")

    # 습도
    if humidity > 80:
        tips.append("습도가 높아요. 통기성 좋은 소재 선택하세요")

    return outfits, tips


# ── UI ──────────────────────────────────────────────────────
st.markdown("## 🌤️ 날씨 기반 옷차림 추천")
st.markdown("오늘 날씨에 딱 맞는 옷차림을 알려드려요.")

col1, col2 = st.columns([3, 1])
with col1:
    city_list = list(CITY_COORDS.keys())
    city = st.selectbox("도시 선택", city_list, index=0)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("날씨 조회")

if search or "weather_data" in st.session_state:
    if search:
        lat, lon = CITY_COORDS[city]
        with st.spinner("날씨 정보를 불러오는 중..."):
            try:
                data = get_weather(lat, lon)
                st.session_state["weather_data"] = data
                st.session_state["weather_city"] = city
            except Exception as e:
                st.error(f"날씨 정보를 가져올 수 없습니다: {e}")
                st.stop()

    data = st.session_state["weather_data"]
    city = st.session_state.get("weather_city", city)

    cur = data["current"]
    temp      = cur["temperature_2m"]
    feels     = cur["apparent_temperature"]
    humidity  = cur["relative_humidity_2m"]
    precip    = cur["precipitation"]
    wind      = cur["wind_speed_10m"]
    w_code    = cur["weather_code"]

    emoji, desc = weather_code_to_emoji(w_code)
    outfits, tips = get_outfit_recommendation(temp, feels, humidity, precip, wind)

    # 현재 날씨 카드
    st.markdown(f"""
    <div class="weather-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:1.1rem; color:#64748b; margin-bottom:0.3rem">
                    📍 {city} · {datetime.now().strftime("%m월 %d일 %H시")}
                </div>
                <div class="temp-big">{temp:.0f}°C</div>
                <div style="color:#64748b; margin-top:0.3rem">
                    체감 {feels:.0f}°C &nbsp;|&nbsp; 습도 {humidity}% &nbsp;|&nbsp; 강수 {precip}mm
                </div>
            </div>
            <div style="font-size:4rem">{emoji}</div>
        </div>
        <div style="margin-top:0.8rem">
            <span class="tag">{desc}</span>
            <span class="tag">바람 {wind:.1f}m/s</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 추천 옷차림
    st.markdown("### 👗 오늘의 추천 옷차림")
    for item in outfits:
        st.markdown(f'<div class="outfit-item">{item}</div>', unsafe_allow_html=True)

    if tips:
        st.markdown("### 💡 오늘의 팁")
        for tip in tips:
            st.info(tip)

    # 5일 예보
    st.markdown("### 📅 5일 예보")
    daily = data["daily"]
    days = daily["time"]
    max_t = daily["temperature_2m_max"]
    min_t = daily["temperature_2m_min"]
    w_codes = daily["weather_code"]

    cols = st.columns(5)
    for i, col in enumerate(cols):
        date_str = datetime.strptime(days[i], "%Y-%m-%d").strftime("%m/%d")
        e, d = weather_code_to_emoji(w_codes[i])
        with col:
            st.markdown(f"""
            <div class="forecast-card">
                <div style="font-size:0.85rem; color:#64748b">{date_str}</div>
                <div style="font-size:2rem">{e}</div>
                <div style="font-size:0.8rem; color:#64748b">{d}</div>
                <div style="font-weight:700; color:#dc2626">{max_t[i]:.0f}°</div>
                <div style="color:#3b82f6">{min_t[i]:.0f}°</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("데이터 출처: Open-Meteo API (무료, API 키 불필요)")