from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "contents.csv"
PROVIDERS = ["Netflix", "TVING", "Wavve", "Disney+", "왓챠", "Laftel"]
TYPE_LABELS = {
    "movie": "영화",
    "series": "드라마",
    "animation": "애니",
    "variety": "예능",
    "documentary": "다큐",
}

st.set_page_config(
    page_title="B tv+ 월별 신작",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(circle at 85% 0%, #321c37 0, transparent 30rem), #090a0f; color: #f7f7fa; }
      [data-testid="stHeader"] { background: rgba(9,10,15,.72); backdrop-filter: blur(16px); }
      .block-container { max-width: 1480px; padding-top: 2rem; padding-bottom: 5rem; }
      .eyebrow { color:#ff5b95; font-size:.78rem; font-weight:800; letter-spacing:.12em; }
      .hero-title { font-size:clamp(2.3rem,6vw,4.9rem); line-height:1.02; letter-spacing:-.055em; margin:.65rem 0 1rem; font-weight:900; }
      .hero-title span { color:rgba(255,255,255,.52); }
      .hero-copy { color:rgba(255,255,255,.55); line-height:1.7; margin-bottom:1.8rem; }
      .content-card { border:1px solid rgba(255,255,255,.1); background:#15161d; border-radius:18px; padding:1rem; min-height:178px; }
      .content-card h3 { margin:.55rem 0 .35rem; font-size:1.1rem; line-height:1.35; }
      .content-card p { color:rgba(255,255,255,.55); font-size:.8rem; line-height:1.55; margin:.2rem 0; }
      .pill { display:inline-block; border-radius:999px; padding:.28rem .6rem; background:#ff2d78; font-size:.68rem; font-weight:800; }
      .ott-o { color:#fff; background:#ff2d78; border-radius:999px; display:inline-grid; place-items:center; width:30px; height:30px; font-weight:900; }
      .ott-x { color:rgba(255,255,255,.38); background:rgba(255,255,255,.07); border-radius:999px; display:inline-grid; place-items:center; width:30px; height:30px; font-weight:900; }
      div[data-testid="stTabs"] button { font-weight:800; }
      div[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.1); border-radius:16px; overflow:hidden; }
      [data-testid="stSidebar"] { background:#111219; }
      .small-note { color:rgba(255,255,255,.38); font-size:.75rem; line-height:1.5; }
      @media (max-width:640px) { .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    for provider in PROVIDERS:
        if provider not in frame.columns:
            frame[provider] = "X"
        frame[provider] = frame[provider].str.upper().replace({"TRUE": "O", "FALSE": "X"})
    return frame


def product_name(value: str) -> str:
    return "B tv+ max 전용" if value == "btv-plus-max" else "B tv+ · max 동시 편성"


def product_filter(frame: pd.DataFrame, product: str) -> pd.DataFrame:
    if product == "B tv+ max":
        return frame[frame["product"].isin(["btv-plus-max", "both"])]
    if product == "B tv+":
        return frame[frame["product"] == "both"]
    return frame


def render_cards(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.info("조건에 맞는 신작이 없습니다.")
        return

    for start in range(0, len(frame), 4):
        columns = st.columns(4)
        for column, (_, item) in zip(columns, frame.iloc[start : start + 4].iterrows()):
            with column:
                poster = ROOT / item["poster"] if item["poster"] else None
                if poster and poster.exists():
                    st.image(str(poster), use_container_width=True)
                st.markdown(
                    f"""
                    <div class="content-card">
                      <span class="pill">{product_name(item['product'])}</span>
                      <h3>{item['title']}</h3>
                      <p><b>{item['release_date']} 공개</b> · {TYPE_LABELS.get(item['type'], item['type'])}</p>
                      <p>{item['genres'].replace('|', ' · ')}</p>
                      <p>{item['synopsis']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_ott_table(frame: pd.DataFrame) -> None:
    table = frame[["title", "release_date", *PROVIDERS]].rename(
        columns={"title": "콘텐츠", "release_date": "공개일"}
    )

    def decorate(value: str) -> str:
        if value == "O":
            return "background-color:#ff2d78;color:white;font-weight:800;text-align:center"
        if value == "X":
            return "background-color:#20212a;color:#777985;font-weight:800;text-align:center"
        return ""

    styled = table.style.map(decorate, subset=PROVIDERS)
    st.markdown("### OTT 편성현황")
    st.caption("O: 월정액 제공 · X: 미제공 또는 제공 여부 확인 필요")
    st.dataframe(styled, hide_index=True, use_container_width=True, height=min(760, 45 + 36 * len(table)))


data = load_data()
months = sorted(data["month"].unique(), reverse=True)

with st.sidebar:
    st.image(str(ROOT / "assets" / "btv-plus-logo.png"), width=150)
    st.markdown("### 데이터 관리")
    uploaded = st.file_uploader("수정한 CSV 미리보기", type="csv", help="업로드한 내용은 현재 브라우저에서만 미리보기 됩니다.")
    if uploaded is not None:
        data = pd.read_csv(uploaded, dtype=str).fillna("")
        st.success("업로드한 CSV를 미리보는 중입니다.")
    st.download_button("현재 CSV 내려받기", DATA_FILE.read_bytes(), file_name="contents.csv", mime="text/csv")
    st.markdown('<p class="small-note">영구 반영은 GitHub의 data/contents.csv 파일을 교체하면 됩니다.</p>', unsafe_allow_html=True)

selected_month = st.selectbox(
    "월 선택",
    months,
    format_func=lambda value: f"{value[:4]}년 {int(value[5:])}월",
    label_visibility="collapsed",
)
month_data = data[data["month"] == selected_month].copy()

st.markdown('<div class="eyebrow">B tv+ MONTHLY PREMIERE</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="hero-title">{selected_month[:4]}년 {int(selected_month[5:])}월<br><span>새로운 이야기를 만나보세요</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-copy">B tv+와 B tv+ max 신작, 주요 OTT의 월정액 제공 여부를 한곳에서 비교하세요.</div>',
    unsafe_allow_html=True,
)

tab_all, tab_max, tab_plus, tab_ott = st.tabs(["전체", "B tv+ max", "B tv+", "OTT 편성현황"])

with tab_all:
    query = st.text_input("작품명 검색", placeholder="작품명을 입력하세요", key="all_query")
    filtered = product_filter(month_data, "전체")
    if query:
        filtered = filtered[filtered["title"].str.contains(query, case=False, na=False)]
    render_cards(filtered)

with tab_max:
    render_cards(product_filter(month_data, "B tv+ max"))

with tab_plus:
    render_cards(product_filter(month_data, "B tv+"))

with tab_ott:
    render_ott_table(month_data)

st.divider()
st.caption("OTT 제공 정보는 확인 시점에 따라 달라질 수 있습니다. 최종 확인일: 2026.07.15")
