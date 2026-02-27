import streamlit as st
import requests
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="📚 도서 검색기",
    page_icon="📚",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;600&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; }
h1, h2, h3 { font-family: 'Noto Serif KR', serif; }

.book-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    border: 1px solid #f1f5f9;
    transition: all 0.2s;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.book-card:hover {
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}
.book-cover {
    width: 80px;
    min-width: 80px;
    height: 110px;
    object-fit: cover;
    border-radius: 6px;
    background: #f1f5f9;
}
.cover-placeholder {
    width: 80px;
    min-width: 80px;
    height: 110px;
    background: linear-gradient(135deg, #c7d2fe, #a5b4fc);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
}
.book-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.2rem;
}
.book-author {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 0.4rem;
}
.book-meta {
    color: #94a3b8;
    font-size: 0.8rem;
}
.badge {
    display: inline-block;
    background: #e0e7ff;
    color: #4338ca;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.78rem;
    margin: 0.1rem;
}
.wishlist-item {
    background: #fafafa;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin: 0.3rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


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
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# ── 사이드바: 관심 도서 목록 ──────────────────────────────────
with st.sidebar:
    st.markdown("## 📌 관심 도서 목록")
    st.caption(f"총 {len(st.session_state.wishlist)}권")

    if not st.session_state.wishlist:
        st.info("검색 후 ❤️ 버튼으로 추가하세요")
    else:
        for i, book in enumerate(st.session_state.wishlist):
            st.markdown(f"""
            <div class="wishlist-item">
                <div>
                    <div style="font-weight:600;font-size:0.9rem">{book['title'][:25]}{'...' if len(book['title'])>25 else ''}</div>
                    <div style="color:#64748b;font-size:0.8rem">{book.get('author','알 수 없음')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("삭제", key=f"del_{i}"):
                st.session_state.wishlist.pop(i)
                st.rerun()

        if st.button("📋 전체 목록 초기화"):
            st.session_state.wishlist = []
            st.rerun()

        # 텍스트로 내보내기
        export_text = "\n".join([f"- {b['title']} / {b.get('author','')}" for b in st.session_state.wishlist])
        st.download_button("📥 목록 다운로드", export_text, file_name="wishlist.txt", mime="text/plain")


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

# 빠른 검색 예시
st.markdown("**빠른 검색:** " + " ".join([
    f'<span class="badge" style="cursor:pointer">{q}</span>'
    for q in ["해리포터", "어린왕자", "파친코", "채식주의자", "데미안"]
]), unsafe_allow_html=True)

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

    # 상세보기 패널
    if st.session_state.selected_book:
        bk = st.session_state.selected_book
        with st.expander("📖 상세 정보", expanded=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                cover = get_cover_url(bk.get("cover_i"), "L")
                if cover:
                    st.image(cover, width=150)
                else:
                    st.markdown('<div class="cover-placeholder">📖</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f"### {bk.get('title','')}")
                st.markdown(f"**저자:** {', '.join(bk.get('author_name', ['알 수 없음']))}")
                st.markdown(f"**최초 출판:** {bk.get('first_publish_year', 'N/A')}년")
                if bk.get("number_of_pages_median"):
                    st.markdown(f"**페이지:** {bk['number_of_pages_median']}p")
                if bk.get("ratings_average"):
                    stars = "⭐" * round(bk["ratings_average"])
                    st.markdown(f"**평점:** {stars} ({bk['ratings_average']:.1f})")
                subjects = bk.get("subject", [])[:8]
                if subjects:
                    badges = "".join([f'<span class="badge">{s}</span>' for s in subjects])
                    st.markdown(f"**분야:** {badges}", unsafe_allow_html=True)
                ol_url = f"https://openlibrary.org{bk.get('key','')}"
                st.markdown(f"[🔗 Open Library에서 보기]({ol_url})")
            if st.button("✖ 닫기"):
                st.session_state.selected_book = None
                st.rerun()

    # 책 목록
    for bk in results:
        title  = bk.get("title", "제목 없음")
        authors = ", ".join(bk.get("author_name", ["알 수 없음"])[:2])
        year   = bk.get("first_publish_year", "")
        pages  = bk.get("number_of_pages_median", "")
        rating = bk.get("ratings_average", None)
        cover  = get_cover_url(bk.get("cover_i"))

        c1, c2 = st.columns([6, 1])
        with c1:
            if cover:
                cover_html = f'<img src="{cover}" class="book-cover" onerror="this.style.display=\'none\'">'
            else:
                cover_html = '<div class="cover-placeholder">📖</div>'

            rating_html = f"⭐ {rating:.1f}" if rating else ""
            pages_html  = f"· {pages}p" if pages else ""

            st.markdown(f"""
            <div class="book-card">
                {cover_html}
                <div>
                    <div class="book-title">{title}</div>
                    <div class="book-author">✍️ {authors}</div>
                    <div class="book-meta">{year}년 {pages_html} {rating_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📋 상세", key=f"det_{bk.get('key',title)}"):
                st.session_state.selected_book = bk
                st.rerun()

            already = any(w["title"] == title for w in st.session_state.wishlist)
            if not already:
                if st.button("❤️", key=f"wish_{bk.get('key',title)}"):
                    st.session_state.wishlist.append({"title": title, "author": authors, "year": year})
                    st.success("관심 목록에 추가!")
                    st.rerun()
            else:
                st.markdown("✅")

st.markdown("---")
st.caption("데이터 출처: Open Library API (무료, API 키 불필요) · openlibrary.org")