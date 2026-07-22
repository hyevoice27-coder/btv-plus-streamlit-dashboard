from __future__ import annotations

import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "contents.csv"
PROVIDERS = ["Netflix", "TVING", "Wavve", "Disney+", "왓챠", "Laftel"]
TYPE_LABELS = {"movie": "영화", "series": "드라마", "animation": "애니/키즈", "variety": "예능", "documentary": "다큐"}
GENRE_TABS = ["전체", "영화", "드라마", "예능", "애니/키즈"]

st.set_page_config(page_title="B tv+ 월별 신작", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
      .stApp { background:#08090e; color:#f7f7fa; }
      [data-testid="stHeader"] { background:rgba(8,9,14,.8); backdrop-filter:blur(16px); }
      .block-container { max-width:1500px; padding-top:2rem; padding-bottom:5rem; }
      .simple-title { font-size:clamp(2rem,4.6vw,4.1rem); line-height:1.08; letter-spacing:-.05em; margin:1.1rem 0 2rem; font-weight:900; }
      .section-heading { display:flex; align-items:baseline; gap:.55rem; margin:1.2rem 0 .9rem; }
      .section-heading h2 { font-size:1.45rem; margin:0; letter-spacing:-.03em; }
      .section-heading span { color:#777986; font-size:.9rem; }
      .content-card { border:1px solid #2c2e38; background:#15161d; border-radius:13px; overflow:hidden; margin-bottom:1.2rem; box-shadow:0 10px 26px rgba(0,0,0,.18); }
      .poster-wrap { position:relative; aspect-ratio:2/3; overflow:hidden; background:#273d35; }
      .poster-wrap img { width:100%; height:100%; object-fit:cover; display:block; }
      .poster-fallback { height:100%; display:grid; place-items:center; padding:1.2rem; text-align:center; font-size:1.15rem; font-weight:900; }
      .product-badge { position:absolute; left:.58rem; top:.58rem; z-index:2; border-radius:5px; padding:.36rem .56rem; font-size:.63rem; line-height:1; font-weight:900; box-shadow:0 4px 12px rgba(0,0,0,.25); }
      .product-badge.max { background:#ff2d78; color:#fff; }
      .product-badge.both { background:#fff; color:#090a0f; }
      .card-body { padding:.82rem .82rem .9rem; }
      .card-title { font-size:.98rem; font-weight:900; line-height:1.3; margin:0 0 .42rem; word-break:keep-all; }
      .card-meta { color:#a6a7b4; font-size:.72rem; line-height:1.55; margin:.08rem 0; }
      .card-cast { color:#d0d1d8; font-size:.7rem; line-height:1.5; margin:.3rem 0 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .ott-area { border-top:1px solid #2a2b34; margin-top:.72rem; padding-top:.65rem; }
      .ott-label { color:#8b8d99; font-size:.65rem; font-weight:700; margin-bottom:.42rem; }
      .ott-badges { display:flex; flex-wrap:wrap; gap:.28rem; }
      .ott-badge { border-radius:4px; padding:.28rem .42rem; font-size:.6rem; line-height:1; font-weight:900; }
      .ott-badge.yes { color:#70f3c5; background:#073b34; }
      .ott-badge.unknown { color:#ffd85b; background:#3a310b; }
      .ott-empty { color:#60626d; font-size:.62rem; }
      div[data-testid="stTabs"] button { font-weight:800; }
      div[role="radiogroup"] { gap:.5rem; flex-wrap:wrap; }
      div[role="radiogroup"] label { border:1px solid rgba(255,255,255,.14); border-radius:999px; padding:.35rem .85rem; min-height:2.5rem; }
      div[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.1); border-radius:16px; overflow:hidden; }
      [data-testid="stSidebar"] { background:#111219; }
      .small-note { color:rgba(255,255,255,.38); font-size:.75rem; line-height:1.5; }
      .mobile-brand { display:none; }
      .mobile-brand img { display:block; height:36px; width:auto; }
      @media (max-width:700px) {
        .block-container { padding-left:1rem; padding-right:1rem; }
        .simple-title { font-size:2rem; }
        .card-title { font-size:.88rem; }
        .mobile-brand { display:flex; align-items:center; min-height:52px; margin-bottom:.75rem; }
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    if "cast" not in frame.columns:
        frame["cast"] = ""
    for provider in PROVIDERS:
        if provider not in frame.columns:
            frame[provider] = "X"
        frame[provider] = frame[provider].str.upper().replace({"TRUE": "O", "FALSE": "X"})
    return frame


@st.cache_data
def image_data_uri(relative_path: str) -> str:
    if not relative_path:
        return ""
    path = ROOT / relative_path
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def product_filter(frame: pd.DataFrame, product: str) -> pd.DataFrame:
    if product == "B tv+ max":
        return frame[frame["product"].isin(["btv-plus-max", "both"])]
    if product == "B tv+":
        return frame[frame["product"] == "both"]
    return frame


def genre_filter(frame: pd.DataFrame, genre: str) -> pd.DataFrame:
    if genre == "전체":
        return frame

    target_types = {
        "영화": {"movie"},
        "드라마": {"series"},
        "예능": {"variety"},
        "애니/키즈": {"animation"},
    }[genre]
    genre_keywords = {
        "영화": r"영화",
        "드라마": r"드라마",
        "예능": r"예능|버라이어티",
        "애니/키즈": r"애니|키즈|아동",
    }[genre]

    type_matches = frame["type"].str.lower().isin(target_types)
    genre_matches = frame["genres"].str.contains(genre_keywords, case=False, na=False, regex=True)
    return frame[type_matches | genre_matches]


def card_html(item: pd.Series) -> str:
    badge_class = "max" if item["product"] == "btv-plus-max" else "both"
    product_label = "B tv+ max 전용" if badge_class == "max" else "B tv+ · max 동시 편성"
    poster = image_data_uri(item["poster"])
    poster_html = f'<img src="{poster}" alt="{html.escape(item["title"])} 포스터">' if poster else f'<div class="poster-fallback">{html.escape(item["title"])}</div>'
    cast = html.escape(item.get("cast", "").replace("|", " · ")) or "출연진 확인 필요"
    ott_badges = []
    for provider in PROVIDERS:
        value = item.get(provider, "X")
        if value == "O":
            ott_badges.append(f'<span class="ott-badge yes">{provider} ✓</span>')
        elif value == "?":
            ott_badges.append(f'<span class="ott-badge unknown">{provider} ?</span>')
    badges = "".join(ott_badges) or '<span class="ott-empty">별도 OTT 월정액 편성 없음</span>'
    return f"""
      <article class="content-card">
        <div class="poster-wrap">
          <span class="product-badge {badge_class}">{product_label}</span>
          {poster_html}
        </div>
        <div class="card-body">
          <h3 class="card-title">{html.escape(item['title'])}</h3>
          <p class="card-meta">{html.escape(item['release_date'])} 편성 · {TYPE_LABELS.get(item['type'], item['type'])}</p>
          <p class="card-meta">{html.escape(item['genres'].replace('|', ' · '))}</p>
          <p class="card-cast">{cast}</p>
          <div class="ott-area">
            <div class="ott-label">다른 OTT 월정액 편성</div>
            <div class="ott-badges">{badges}</div>
          </div>
        </div>
      </article>
    """


def render_cards(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.info("조건에 맞는 신작이 없습니다.")
        return
    for start in range(0, len(frame), 5):
        columns = st.columns(5)
        for column, (_, item) in zip(columns, frame.iloc[start : start + 5].iterrows()):
            with column:
                st.markdown(card_html(item), unsafe_allow_html=True)


def section_heading(title: str, count: int) -> None:
    st.markdown(f'<div class="section-heading"><h2>{title}</h2><span>{count}</span></div>', unsafe_allow_html=True)


def render_genre_views(frame: pd.DataFrame, prefix: str, featured_ids: list[str] | None = None) -> None:
    genre = st.radio(
        "장르 선택",
        GENRE_TABS,
        horizontal=True,
        key=f"genre-filter-{prefix}",
        label_visibility="collapsed",
    )
    items = genre_filter(frame, genre)

    if featured_ids:
        featured = items[items["id"].isin(featured_ids)]
        if not featured.empty:
            section_heading("주목할 만한 신작", len(featured))
            render_cards(featured)

    title = "전체 신작" if prefix == "전체" and genre == "전체" else f"{prefix} {genre} 신작"
    section_heading(title, len(items))
    render_cards(items)


def render_ott_table(frame: pd.DataFrame) -> None:
    table = frame[["title", "release_date", *PROVIDERS]].rename(columns={"title": "콘텐츠", "release_date": "편성일"})

    def decorate(value: str) -> str:
        if value == "O":
            return "background-color:#087f67;color:#c6ffeb;font-weight:800;text-align:center"
        if value == "?":
            return "background-color:#6b5600;color:#ffe991;font-weight:800;text-align:center"
        if value == "X":
            return "background-color:#20212a;color:#777985;font-weight:800;text-align:center"
        return ""

    st.markdown("## OTT 편성현황")
    st.caption("O: 월정액 제공 · ?: 확인 필요 · X: 미편성")
    st.dataframe(table.style.map(decorate, subset=PROVIDERS), hide_index=True, width="stretch", height=min(760, 45 + 36 * len(table)))


def render_popular_content(month: str) -> None:
    known_titles = {1: "가족관계증명서", 2: "아파트", 3: "결혼의 완성"}
    st.markdown(f'<div class="simple-title">B tv+ max {month[:4]}년 {int(month[5:])}월 인기 콘텐츠 TOP 30</div>', unsafe_allow_html=True)
    for start in range(1, 31, 6):
        columns = st.columns(6)
        for column, rank in zip(columns, range(start, min(start + 6, 31))):
            with column:
                poster = ROOT / "assets" / "popular" / f"popular-{rank:02d}.jpg"
                if poster.exists():
                    st.image(str(poster), width="stretch")
                st.markdown(f"**{rank}위** — {known_titles.get(rank, f'B tv+ max 인기 {rank}위')}")


data = load_data()
months = sorted(data["month"].unique(), reverse=True)

st.image(str(ROOT / "assets" / "btv-plus-logo.png"), width=150)

with st.sidebar:
    st.image(str(ROOT / "assets" / "btv-plus-logo.png"), width=150)
    st.markdown("### 데이터 관리")
    uploaded = st.file_uploader("수정한 CSV 미리보기", type="csv", help="업로드한 내용은 현재 브라우저에서만 미리보기 됩니다.")
    if uploaded is not None:
        data = pd.read_csv(uploaded, dtype=str).fillna("")
        st.success("업로드한 CSV를 미리보는 중입니다.")
    st.download_button("현재 CSV 내려받기", DATA_FILE.read_bytes(), file_name="contents.csv", mime="text/csv")
    st.markdown('<p class="small-note">영구 반영은 GitHub의 data/contents.csv 파일을 교체하면 됩니다.</p>', unsafe_allow_html=True)

section = st.radio("메뉴", ["월별 신작", "월별 인기 콘텐츠"], horizontal=True, label_visibility="collapsed")
selected_month = st.selectbox(
    "월 선택",
    months,
    index=months.index("2026-07") if "2026-07" in months else 0,
    format_func=lambda value: f"{value[:4]}년 {int(value[5:])}월",
    label_visibility="collapsed",
)
month_data = data[data["month"] == selected_month].copy()

if section == "월별 인기 콘텐츠":
    render_popular_content(selected_month)
else:
    st.markdown(f'<div class="simple-title">B tv+ &amp; B tv+ max {selected_month[:4]}년 {int(selected_month[5:])}월 신작</div>', unsafe_allow_html=True)
    product_tabs = st.tabs(["전체", "B tv+ max", "B tv+", "OTT 편성현황"])
    featured_ids = {
        "2026-07": ["jul-01", "jul-07", "jul-08"],
        "2026-08": ["aug-01", "aug-02", "aug-03"],
    }.get(selected_month, [])

    with product_tabs[0]:
        render_genre_views(product_filter(month_data, "전체"), "전체", featured_ids)
    with product_tabs[1]:
        render_genre_views(product_filter(month_data, "B tv+ max"), "B tv+ max", featured_ids)
    with product_tabs[2]:
        render_genre_views(product_filter(month_data, "B tv+"), "B tv+", featured_ids)
    with product_tabs[3]:
        render_ott_table(month_data)

st.divider()
st.caption("OTT 제공 정보는 확인 시점에 따라 달라질 수 있습니다. 최종 확인일: 2026.07.15")
