import streamlit as st
import requests
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="📚 도서 검색기",
    page_icon="📚",
)

# ── API 함수 ─────────────────────────────────────────────────
def search_books(query: str, limit: int = 15) -> list:
    """Open Library Search API"""
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": limit, "fields": "key,title,author_name,first_publish_year,isbn,cover_i,subject,number_of_pages_median,ratings_average"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("docs", [])


def get_cover_url(cover_id, size="M"):
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"
    return None


def get_book_detail(ol_key: str) -> dict:
    """작품 상세 정보 (설명 등)"""
    url = f"https://openlibrary.org{ol_key}.json"
    try:
        r = requests.get(url, timeout=8)
        return r.json()
    except:
        return {}

# ── 세션 초기화 ───────────────────────────────────────────────
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

# ── 메인 ─────────────────────────────────────────────────────
st.markdown("# 📚 도서 검색기")
st.markdown("Open Library의 수백만 권 도서 데이터베이스를 검색하세요.")

# 검색 바
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    query = st.text_input("", placeholder="책 제목, 저자명, ISBN 입력...", label_visibility="collapsed")
with col2:
    limit = st.selectbox("", [10, 20, 30], label_visibility="collapsed")
with col3:
    search_btn = st.button("🔍 검색", use_container_width=True)

if search_btn and query:
    with st.spinner(f"'{query}' 검색 중..."):
        try:
            results = search_books(query, limit)
            st.session_state.search_results = results
            st.session_state.selected_book = None
        except Exception as e:
            st.error(f"검색 실패: {e}")

# 검색 결과
if st.session_state.search_results:
    results = st.session_state.search_results
    st.markdown(f"### 검색 결과 ({len(results)}권)")

    # 책 목록
    for bk in results:
        title  = bk.get("title", "제목 없음")
        authors = ", ".join(bk.get("author_name", ["알 수 없음"])[:2])
        year   = bk.get("first_publish_year", "")
        pages  = bk.get("number_of_pages_median", "")
        rating = bk.get("ratings_average", None)
        cover  = get_cover_url(bk.get("cover_i"))
        subjects = bk.get("subject", [])[:8]

        c1, c2 = st.columns([2,5],vertical_alignment="center",border=False,gap="medium")
        with c1:
            if cover:
                st.markdown(f"""
                    <div style="
                        width:140px;
                        height:200px;
                        border:1px solid #8C8C8C;
                        padding:4px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    ">
                        <img src="{cover}" 
                            style="max-width:100%; max-height:100%; object-fit:contain;">
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div align="center" style="width:150;height:200;">📖</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"##### {title}")
            st.markdown(f"<div>✍️ 저자: {authors}</div>", unsafe_allow_html=True)
            st.markdown(f"<div>🔊 최초 출판: {year}년</div>", unsafe_allow_html=True)
            if pages:
                st.markdown(f"<div>📄 페이지: {pages}p</div>", unsafe_allow_html=True)
            if rating:
                stars = "⭐" * round(rating)
                st.markdown(f"<div>⭐ 평점: {stars} ({rating:.1f})</div>", unsafe_allow_html=True)
            if subjects:
                badges = "".join([f'<span class="badge">{s}</span>' for s in subjects])
                st.markdown(f"📚 분야: {badges}", unsafe_allow_html=True)
            ol_url = f"https://openlibrary.org{bk.get('key','')}"
            st.markdown(f"[🔗 Open Library에서 보기]({ol_url})")       
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)    

st.markdown("---")
st.caption("데이터 출처: Open Library API (무료, API 키 불필요) · openlibrary.org")