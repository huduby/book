import streamlit as st
import feedparser
import re
from datetime import datetime
from collections import Counter
from urllib.parse import quote

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="📰 뉴스 트렌드 대시보드",
    page_icon="📰",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; }

.news-card {
    background: white;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin: 0.45rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
    transition: all 0.2s;
}
.news-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transform: translateY(-1px);
}
.news-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.3rem;
    line-height: 1.4;
}
.news-title a {
    color: #1e293b;
    text-decoration: none;
}
.news-title a:hover { color: #2563eb; }
.news-meta {
    color: #94a3b8;
    font-size: 0.78rem;
}
.source-badge {
    display: inline-block;
    border-radius: 6px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.4rem;
}
.keyword-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.2rem;
    cursor: pointer;
}
.word-cloud-item {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 8px;
    margin: 0.2rem;
    background: rgba(37,99,235,0.08);
    color: #1d4ed8;
}
.stat-card {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
}
.stat-num {
    font-size: 2.5rem;
    font-weight: 900;
    line-height: 1;
}
.stat-label {
    font-size: 0.85rem;
    opacity: 0.85;
    margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── RSS 피드 목록 ─────────────────────────────────────────────
RSS_SOURCES = {
    "연합뉴스 (속보)":    "https://www.yonhapnewstv.co.kr/category/news/headline/feed/",
    "YTN 뉴스":           "https://www.ytn.co.kr/rss/allnews.xml",
    "KBS 뉴스":           "http://world.kbs.co.kr/rss/rss_news.htm?lang=k",
    "BBC 코리아":         "https://feeds.bbci.co.uk/korean/rss.xml",
    "조선일보":           "https://www.chosun.com/arc/outboundfeeds/rss/",
    "한겨레":             "https://www.hani.co.kr/rss/",
    "매일경제":           "https://www.mk.co.kr/rss/30000001/",
    "Hacker News (IT)":   "https://hnrss.org/frontpage",
    "TechCrunch":         "https://techcrunch.com/feed/",
    "BBC World":          "http://feeds.bbci.co.uk/news/world/rss.xml",
}

SOURCE_COLORS = [
    "#ef4444","#f97316","#eab308","#22c55e",
    "#14b8a6","#3b82f6","#8b5cf6","#ec4899","#64748b","#0ea5e9",
]

STOPWORDS = set([
    "이","가","을","를","은","는","의","와","과","에","도","로","으로",
    "에서","까지","부터","이다","있다","없다","하다","그","이","저",
    "및","등","또","때","더","한","수","것","말","a","the","in","of",
    "to","and","is","for","with","on","at","by","that","this",
    "was","are","it","from","an","as","be","has","had","we","our",
    "their","will","have","but","not","or","they","which","what",
    "기자","뉴스","AP","AFP","기사","보도","시간","통해","대한",
    "있는","하는","위해","때문","하고","있어","이번","지난","오는",
])


# ── 함수 ─────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # 5분 캐시
def fetch_rss(url: str, source_name: str) -> list:
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:20]:
            title   = entry.get("title", "")
            link    = entry.get("link", "#")
            summary = re.sub(r'<[^>]+>', '', entry.get("summary", ""))[:200]
            published = entry.get("published", entry.get("updated", ""))
            articles.append({
                "title":     title,
                "link":      link,
                "summary":   summary,
                "published": published,
                "source":    source_name,
            })
        return articles
    except Exception as e:
        return []


def filter_by_keyword(articles: list, keyword: str) -> list:
    if not keyword:
        return articles
    kw = keyword.lower()
    return [a for a in articles
            if kw in a["title"].lower() or kw in a["summary"].lower()]


def extract_words(articles: list) -> Counter:
    text = " ".join([a["title"] + " " + a["summary"] for a in articles])
    words = re.findall(r'[가-힣a-zA-Z]{2,10}', text)
    return Counter(w for w in words if w.lower() not in STOPWORDS)


def get_source_color(source: str) -> str:
    idx = list(RSS_SOURCES.keys()).index(source) if source in RSS_SOURCES else 0
    return SOURCE_COLORS[idx % len(SOURCE_COLORS)]


def format_time(pub_str: str) -> str:
    if not pub_str:
        return ""
    try:
        import email.utils
        t = email.utils.parsedate_to_datetime(pub_str)
        return t.strftime("%m/%d %H:%M")
    except:
        return pub_str[:16] if pub_str else ""


# ── 세션 초기화 ───────────────────────────────────────────────
if "keywords" not in st.session_state:
    st.session_state.keywords = ["AI", "경제", "날씨"]
if "selected_sources" not in st.session_state:
    st.session_state.selected_sources = list(RSS_SOURCES.keys())[:4]
if "all_articles" not in st.session_state:
    st.session_state.all_articles = []


# ── UI ──────────────────────────────────────────────────────
st.markdown("# 📰 뉴스 트렌드 대시보드")
st.markdown("여러 언론사 RSS를 실시간으로 파싱해 뉴스를 한눈에 모아봅니다.")

# ─── 사이드바 ───
with st.sidebar:
    st.markdown("## ⚙️ 설정")

    st.markdown("### 📡 뉴스 소스")
    selected = st.multiselect(
        "언론사 선택",
        list(RSS_SOURCES.keys()),
        default=st.session_state.selected_sources,
        label_visibility="collapsed"
    )
    st.session_state.selected_sources = selected

    st.markdown("### 🔍 관심 키워드")
    new_kw = st.text_input("키워드 추가", placeholder="예: 반도체, ChatGPT")
    if st.button("➕ 추가") and new_kw:
        if new_kw not in st.session_state.keywords:
            st.session_state.keywords.append(new_kw)

    for i, kw in enumerate(st.session_state.keywords):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f'<span class="keyword-badge" style="background:#e0e7ff;color:#3730a3">🔖 {kw}</span>',
                       unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"del_kw_{i}"):
                st.session_state.keywords.pop(i)
                st.rerun()

    st.markdown("---")
    fetch_btn = st.button("🔄 뉴스 새로고침", use_container_width=True, type="primary")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")


# ─── 뉴스 불러오기 ───
if fetch_btn or not st.session_state.all_articles:
    if not st.session_state.selected_sources:
        st.warning("언론사를 1개 이상 선택해주세요.")
        st.stop()

    with st.spinner("뉴스를 불러오는 중..."):
        all_articles = []
        progress = st.progress(0)
        for i, src in enumerate(st.session_state.selected_sources):
            url = RSS_SOURCES[src]
            articles = fetch_rss(url, src)
            all_articles.extend(articles)
            progress.progress((i + 1) / len(st.session_state.selected_sources))
        st.session_state.all_articles = all_articles
        progress.empty()

articles = st.session_state.all_articles

if not articles:
    st.warning("뉴스를 불러올 수 없습니다. 언론사를 선택하고 새로고침해 주세요.")
    st.stop()

# ─── 통계 ───
total = len(articles)
sources_cnt = len(set(a["source"] for a in articles))
word_freq = extract_words(articles)
top_word = word_freq.most_common(1)[0][0] if word_freq else "N/A"

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">총 기사 수</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="stat-card" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)"><div class="stat-num">{sources_cnt}</div><div class="stat-label">언론사</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="stat-card" style="background:linear-gradient(135deg,#059669,#047857)"><div class="stat-num">{len(st.session_state.keywords)}</div><div class="stat-label">관심 키워드</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown(f'<div class="stat-card" style="background:linear-gradient(135deg,#dc2626,#b91c1c)"><div class="stat-num">{top_word}</div><div class="stat-label">가장 많이 등장한 단어</div></div>', unsafe_allow_html=True)

st.markdown("")

# ─── 탭 ───
tab1, tab2, tab3 = st.tabs(["📋 전체 뉴스", "🔍 키워드 필터", "📊 단어 빈도"])

# ── TAB 1: 전체 뉴스 ─────────────────────────────────────────
with tab1:
    sort_opt = st.selectbox("정렬", ["최신순", "언론사별"], label_visibility="collapsed")
    sorted_articles = articles if sort_opt == "최신순" else sorted(articles, key=lambda x: x["source"])

    search_q = st.text_input("", placeholder="🔎 제목/내용 검색...", label_visibility="collapsed")
    display = filter_by_keyword(sorted_articles, search_q)

    st.caption(f"{len(display)}개 기사")

    for art in display[:50]:  # 최대 50개
        color = get_source_color(art["source"])
        pub = format_time(art["published"])
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">
                <a href="{art['link']}" target="_blank">{art['title']}</a>
            </div>
            <div style="margin: 0.3rem 0; color:#475569; font-size:0.85rem">{art['summary'][:120]}{'...' if len(art['summary'])>120 else ''}</div>
            <div class="news-meta">
                <span class="source-badge" style="background:{color}22; color:{color}; border:1px solid {color}44">{art['source']}</span>
                {pub}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 2: 키워드 필터 ───────────────────────────────────────
with tab2:
    st.markdown("#### 키워드별 뉴스")

    for kw in st.session_state.keywords:
        filtered = filter_by_keyword(articles, kw)
        with st.expander(f"🔖 **{kw}** — {len(filtered)}개 기사", expanded=len(filtered) > 0):
            if not filtered:
                st.info(f"'{kw}' 관련 기사가 없습니다.")
            for art in filtered[:10]:
                color = get_source_color(art["source"])
                pub = format_time(art["published"])
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">
                        <a href="{art['link']}" target="_blank">{art['title']}</a>
                    </div>
                    <div class="news-meta">
                        <span class="source-badge" style="background:{color}22; color:{color}; border:1px solid {color}44">{art['source']}</span>
                        {pub}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    if not st.session_state.keywords:
        st.info("사이드바에서 관심 키워드를 추가하세요.")

# ── TAB 3: 단어 빈도 ─────────────────────────────────────────
with tab3:
    st.markdown("#### 📊 자주 등장하는 단어 TOP 30")

    top_words = word_freq.most_common(30)

    if top_words:
        # 막대 차트 (streamlit 내장)
        import pandas as pd
        df = pd.DataFrame(top_words, columns=["단어", "빈도"])
        st.bar_chart(df.set_index("단어"), height=350)

        # 워드클라우드 스타일 뱃지
        st.markdown("#### 🌥️ 단어 구름")
        max_cnt = top_words[0][1] if top_words else 1
        html = ""
        for word, cnt in top_words:
            size = 0.8 + (cnt / max_cnt) * 1.4
            opacity = 0.5 + (cnt / max_cnt) * 0.5
            html += f'<span class="word-cloud-item" style="font-size:{size:.2f}rem; opacity:{opacity:.2f}">{word} <small style="color:#94a3b8">({cnt})</small></span>'
        st.markdown(html, unsafe_allow_html=True)

        # 언론사별 기사 수
        st.markdown("#### 📡 언론사별 기사 수")
        source_cnt = Counter(a["source"] for a in articles)
        df_src = pd.DataFrame(source_cnt.most_common(), columns=["언론사", "기사 수"])
        st.bar_chart(df_src.set_index("언론사"), height=250)

st.markdown("---")
st.caption("데이터 출처: 각 언론사 공개 RSS 피드 (feedparser 라이브러리 사용, API 키 불필요)")