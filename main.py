# ============================================================
# AI Agents 트렌드 × 진로교육(사고 확장) Streamlit App
# - CSV(Title, Source, Date, Description, Link) 기반
# - 분석(변화/키워드/역할/경로) → 자기화(준비 로드맵) 산출물
# ============================================================

import os
import re
from datetime import date, timedelta
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="AI Agents 트렌드 × 진로교육", layout="wide")


# -------------------------------
# Constants
# -------------------------------
DEFAULT_PATH = "AI_Agents_Ecosystem_2026.csv"
DATA_PATH = os.getenv("AI_AGENT_CSV_PATH", DEFAULT_PATH)

STOP_EN = {
    "the","and","with","for","from","this","that","into","onto","over","under","about","between",
    "using","use","used","new","latest","toward","towards","via","based","approach","system","systems",
    "paper","research","study","studies","results","method","methods","model","models","dataset","data",
    "ai","agent","agents","llm","llms","gpt","openai","anthropic","google","meta","microsoft",
    "framework","tool","tools","application","applications","analysis","report","reports",
    "build","building","improve","improving","improved","evaluate","evaluation","evaluating","benchmark",
    "release","released","update","updated","updates","today","yesterday","tomorrow"
}

ROLE_DEFS = [
    ("설계자(기획/구조화/오케스트레이션)", [
        r"\borchestrat", r"\bworkflow", r"\bpipeline", r"\bplanner", r"\bplanning",
        r"\barchitecture", r"\bdesign", r"\brouter", r"\bcoordinator", r"\bprompt\s*design"
    ]),
    ("구현자(개발/자동화)", [
        r"\bimplement", r"\bimplementation", r"\bbuild", r"\bdev", r"\bdeveloper",
        r"\bcode", r"\blibrary", r"\bsdk\b", r"\bapi\b", r"\bintegration", r"\bplugin",
        r"\bgithub\b", r"\btypescript\b", r"\bpython\b", r"\bnode\b"
    ]),
    ("운영자(배포/모니터링/MLOps)", [
        r"\bdeploy", r"\bdeployment", r"\bops\b", r"\bmlops\b", r"\bmonitor",
        r"\bobservability", r"\bproduction", r"\breliability", r"\binfra", r"\bkubernetes",
        r"\bserver", r"\bscaling", r"\blatency"
    ]),
    ("분석가(리서치/데이터)", [
        r"\barxiv\b", r"\bpaper\b", r"\bstudy\b", r"\bdata\b", r"\bdataset\b",
        r"\bstat", r"\bempirical", r"\bexperiment", r"\bmethodology", r"\btheory",
        r"\bsurvey\b"
    ]),
    ("평가자(Eval/검증/안전)", [
        r"\beval", r"\bevaluation", r"\bbenchmark", r"\btest", r"\btesting",
        r"\bverification", r"\bvalidat", r"\bsafety", r"\balignment", r"\brisk",
        r"\bguardrail", r"\bpolicy"
    ]),
    ("커뮤니케이터(교육/PM/번역)", [
        r"\bguide\b", r"\btutorial", r"\bexplainer", r"\bdocument", r"\bdocumentation",
        r"\bcommunity", r"\bproduct", r"\bpm\b", r"\bteaching", r"\bcourse", r"\bwriting"
    ]),
]

SKILL_TECH = ["Python", "API/연동", "데이터 처리", "LLM/RAG", "에이전트/워크플로우", "클라우드/배포", "보안/윤리"]
SKILL_COG  = ["문제정의", "구조화", "실험/검증", "논리적 글쓰기", "모델링/추론", "정보탐색", "시스템 사고"]
SKILL_ATT  = ["자기주도", "협업", "불확실성 감내", "학습 민첩성", "책임감", "사용자 관점", "끈기"]

ROLE_TO_SKILLS = {
    "설계자(기획/구조화/오케스트레이션)": {
        "tech": ["API/연동", "에이전트/워크플로우", "LLM/RAG"],
        "cog": ["문제정의", "구조화", "시스템 사고", "정보탐색"],
        "att": ["사용자 관점", "협업", "학습 민첩성"]
    },
    "구현자(개발/자동화)": {
        "tech": ["Python", "API/연동", "데이터 처리", "에이전트/워크플로우"],
        "cog": ["구조화", "문제정의", "정보탐색"],
        "att": ["자기주도", "끈기", "책임감"]
    },
    "운영자(배포/모니터링/MLOps)": {
        "tech": ["클라우드/배포", "API/연동", "보안/윤리"],
        "cog": ["시스템 사고", "실험/검증", "문제정의"],
        "att": ["책임감", "불확실성 감내", "협업"]
    },
    "분석가(리서치/데이터)": {
        "tech": ["데이터 처리", "Python", "LLM/RAG"],
        "cog": ["실험/검증", "논리적 글쓰기", "정보탐색", "모델링/추론"],
        "att": ["학습 민첩성", "끈기", "자기주도"]
    },
    "평가자(Eval/검증/안전)": {
        "tech": ["보안/윤리", "데이터 처리", "LLM/RAG"],
        "cog": ["실험/검증", "문제정의", "논리적 글쓰기"],
        "att": ["책임감", "불확실성 감내", "사용자 관점"]
    },
    "커뮤니케이터(교육/PM/번역)": {
        "tech": ["API/연동", "LLM/RAG"],
        "cog": ["논리적 글쓰기", "문제정의", "정보탐색"],
        "att": ["협업", "사용자 관점", "책임감"]
    },
}


# -------------------------------
# Helpers
# -------------------------------
@st.cache_data(show_spinner=False)
def read_csv_safely(path: str) -> pd.DataFrame:
    # 인코딩 fallback (utf-8 → cp949 → latin1)
    last_err = None
    for enc in ("utf-8", "cp949", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
    raise last_err


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = read_csv_safely(path)

    # normalize columns (case-insensitive)
    cols = {c.strip().lower(): c for c in df.columns}
    need = ["title", "source", "date", "description", "link"]
    missing = [n for n in need if n not in cols]
    if missing:
        raise ValueError(f"CSV 컬럼이 예상과 다릅니다. 필요한 컬럼: {', '.join([n.title() for n in need])}")

    df = df.rename(columns={
        cols["title"]: "title",
        cols["source"]: "source",
        cols["date"]: "date",
        cols["description"]: "desc",
        cols["link"]: "link",
    })

    # sanitize types
    for c in ["title", "source", "desc", "link"]:
        df[c] = df[c].astype(str).fillna("").str.strip()

    # parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # domain
    df["domain"] = df["link"].str.extract(r"https?://([^/]+)", expand=False).fillna("")

    # content type (source-based)
    s = df["source"].str.lower()
    df["content_type"] = "news"
    df.loc[s.str.contains("arxiv"), "content_type"] = "paper"
    df.loc[s.str.contains("job"), "content_type"] = "job"

    # role classification (rule-based)
    def classify_role(title: str, desc: str, source: str) -> str:
        text = f"{title} {desc} {source}".lower()
        for role, patterns in ROLE_DEFS:
            for p in patterns:
                if re.search(p, text):
                    return role
        # fallback: content type cues
        if "arxiv" in text:
            return "분석가(리서치/데이터)"
        return "설계자(기획/구조화/오케스트레이션)"

    df["role"] = [classify_role(t, d, s) for t, d, s in zip(df["title"], df["desc"], df["source"])]

    # drop empties + dedupe
    df = df[(df["title"] != "") & (df["link"] != "")]
    df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)

    # month/week for trends
    if df["date"].notna().any():
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["week"] = df["date"].dt.to_period("W").astype(str)
    else:
        df["month"] = ""
        df["week"] = ""

    return df


def tokenize_en(text: str):
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-\+]{2,}", str(text).lower())
    tokens = [t for t in tokens if t not in STOP_EN]
    return tokens


def top_keywords(df: pd.DataFrame, n=25):
    tokens = []
    for t, d in zip(df["title"], df["desc"]):
        tokens.extend(tokenize_en(f"{t} {d}"))
    c = Counter(tokens)
    return c.most_common(n)


def rising_keywords(df_all: pd.DataFrame, recent_days: int = 30, n=15):
    if not df_all["date"].notna().any():
        return []

    cutoff = pd.Timestamp(date.today() - timedelta(days=recent_days))
    recent = df_all[df_all["date"] >= cutoff]
    if len(recent) == 0:
        return []

    all_counts = Counter(tokenize_en(" ".join((df_all["title"] + " " + df_all["desc"]).tolist())))
    recent_counts = Counter(tokenize_en(" ".join((recent["title"] + " " + recent["desc"]).tolist())))

    # score = recent frequency normalized - overall frequency normalized
    all_total = sum(all_counts.values()) or 1
    recent_total = sum(recent_counts.values()) or 1

    scores = []
    for k, rc in recent_counts.items():
        ac = all_counts.get(k, 0)
        score = (rc / recent_total) - (ac / all_total)
        scores.append((k, score, rc, ac))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]


def item_label(row: pd.Series) -> str:
    d = row["date"].date().isoformat() if pd.notna(row["date"]) else ""
    return f"[{row['content_type']}] {d} · {row['title'][:95]}"


def triad_pick(df: pd.DataFrame, keyword: str):
    key = keyword.lower().strip()
    sub = df[
        df["title"].str.lower().str.contains(key, na=False) |
        df["desc"].str.lower().str.contains(key, na=False)
    ].copy()
    picks = {}
    for t in ["paper", "news", "job"]:
        tmp = sub[sub["content_type"] == t].sort_values("date", ascending=False)
        if len(tmp) > 0:
            picks[t] = tmp.iloc[0]
    return picks, sub


# -------------------------------
# Session state
# -------------------------------
st.session_state.setdefault("portfolio", [])     # 선택/기록 누적
st.session_state.setdefault("notes", [])         # 추가 메모
st.session_state.setdefault("student_questions", [])  # 익명 질문


# -------------------------------
# Header
# -------------------------------
st.title("🤖 AI Agents 트렌드 × 진로교육(사고 확장)")
st.caption("CSV 기반 분석 결과를 보며, ‘나는 어떻게 살아가야 하나 / 어떤 준비를 해야 하나’를 확장하고 산출물로 남기는 앱")
st.markdown("""
> **목표:** 트렌드를 ‘정보’로 끝내지 않고,  
> **역할(ROLE) → 역량(SKILL) → 경로(PATH) → 나의 준비(PLAN)**로 연결해 스스로 답을 만들어보게 하기
""")
st.divider()


# -------------------------------
# Data input + filters (Sidebar)
# -------------------------------
with st.sidebar:
    st.header("⚙️ 데이터 설정")

    upload = st.file_uploader("CSV 업로드(선택)", type=["csv"])
    if upload is not None:
        # 업로드 파일 우선
        @st.cache_data(show_spinner=False)
        def load_uploaded(file) -> pd.DataFrame:
            # 업로드는 bytes라 인코딩 추정이 곤란 → pandas가 처리하되 실패시 cp949
            try:
                dfu = pd.read_csv(file)
            except Exception:
                file.seek(0)
                dfu = pd.read_csv(file, encoding="cp949")
            return dfu

        raw = load_uploaded(upload)
        # 임시 파일 경로가 없으니 바로 정규화
        # (간단히: dataframe을 csv로 저장 후 load_data에 넣는 대신, load_data 로직 일부 재사용)
        df = raw.copy()
        cols = {c.strip().lower(): c for c in df.columns}
        need = ["title", "source", "date", "description", "link"]
        missing = [n for n in need if n not in cols]
        if missing:
            st.error(f"업로드 CSV 컬럼이 맞지 않습니다: {', '.join(missing)}")
            st.stop()
        df = df.rename(columns={
            cols["title"]: "title",
            cols["source"]: "source",
            cols["date"]: "date",
            cols["description"]: "desc",
            cols["link"]: "link",
        })
        for c in ["title", "source", "desc", "link"]:
            df[c] = df[c].astype(str).fillna("").str.strip()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["domain"] = df["link"].str.extract(r"https?://([^/]+)", expand=False).fillna("")
        s = df["source"].str.lower()
        df["content_type"] = "news"
        df.loc[s.str.contains("arxiv"), "content_type"] = "paper"
        df.loc[s.str.contains("job"), "content_type"] = "job"

        def classify_role_local(title: str, desc: str, source: str) -> str:
            text = f"{title} {desc} {source}".lower()
            for role, patterns in ROLE_DEFS:
                for p in patterns:
                    if re.search(p, text):
                        return role
            if "arxiv" in text:
                return "분석가(리서치/데이터)"
            return "설계자(기획/구조화/오케스트레이션)"
        df["role"] = [classify_role_local(t, d, s) for t, d, s in zip(df["title"], df["desc"], df["source"])]

        df = df[(df["title"] != "") & (df["link"] != "")]
        df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
        if df["date"].notna().any():
            df["month"] = df["date"].dt.to_period("M").astype(str)
            df["week"] = df["date"].dt.to_period("W").astype(str)
        else:
            df["month"] = ""
            df["week"] = ""
    else:
        # 기본 경로 파일 로딩
        try:
            df = load_data(DATA_PATH)
        except Exception as e:
            st.error("CSV를 불러오지 못했습니다.")
            st.caption(str(e))
            st.markdown(f"- 기본 경로: `{DATA_PATH}`")
            st.stop()

    st.caption(f"데이터: {len(df):,}개 항목")

    st.divider()
    st.header("🔎 필터")

    # date filter
    has_date = df["date"].notna().any()
    if has_date:
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
        dr = st.date_input("기간", value=(min_d, max_d))
        if isinstance(dr, tuple) and len(dr) == 2:
            start_d, end_d = dr
        else:
            start_d, end_d = min_d, max_d
    else:
        start_d = end_d = None
        st.info("Date 파싱이 충분하지 않아 기간 필터가 제한됩니다.")

    sources_all = sorted(df["source"].unique().tolist())
    sources_sel = st.multiselect("Source", sources_all, default=sources_all)

    types_all = ["news", "paper", "job"]
    types_sel = st.multiselect("콘텐츠 타입", types_all, default=types_all)

    # domain top 30
    dom_top = df["domain"].value_counts().head(30).index.tolist()
    dom_sel = st.multiselect("도메인(상위 30)", dom_top, default=[])

    keyword = st.text_input("키워드 검색", placeholder="예: evaluation, agentic, RAG, orchestration ...")

    st.divider()
    st.header("🧑‍🏫 수업 옵션")
    audience = st.radio("대상", ["고3", "대학생"], horizontal=True)
    teacher_mode = st.toggle("교사용 가이드(질문/해설) 표시", value=True)


# apply filters
f = df.copy()
if has_date and start_d and end_d:
    f = f[(f["date"].dt.date >= start_d) & (f["date"].dt.date <= end_d)]
f = f[f["source"].isin(sources_sel)]
f = f[f["content_type"].isin(types_sel)]
if dom_sel:
    f = f[f["domain"].isin(dom_sel)]
if keyword and keyword.strip():
    k = keyword.strip().lower()
    f = f[f["title"].str.lower().str.contains(k, na=False) | f["desc"].str.lower().str.contains(k, na=False)]


# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "① 지금의 변화(Reality)",
    "② 키워드(Topics)",
    "③ 역할 지도(Role Map)",
    "④ 경로 비교(Path)",
    "⑤ 나의 준비 로드맵(Plan)"
])


# ============================================================
# TAB 1: Reality Dashboard
# ============================================================
with tab1:
    st.subheader("지금의 변화 한눈에 보기")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("필터 후 항목", f"{len(f):,}")
    c2.metric("Source 수", f"{f['source'].nunique():,}")
    c3.metric("Domain 수", f"{f['domain'].nunique():,}")
    if f["date"].notna().any():
        c4.metric("최신 날짜", str(f["date"].max().date()))
    else:
        c4.metric("최신 날짜", "-")

    st.divider()

    left, right = st.columns(2)
    with left:
        src = f["source"].value_counts().reset_index()
        src.columns = ["source", "count"]
        fig = px.bar(src.head(12), x="source", y="count", title="Source 분포(상위 12)")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        ct = f["content_type"].value_counts().reset_index()
        ct.columns = ["content_type", "count"]
        fig = px.pie(ct, names="content_type", values="count", title="콘텐츠 타입 비중")
        st.plotly_chart(fig, use_container_width=True)

    if f["domain"].notna().any():
        dom = f["domain"].value_counts().head(15).reset_index()
        dom.columns = ["domain", "count"]
        fig = px.bar(dom, x="domain", y="count", title="Domain Top 15(지식/기회가 생기는 곳)")
        st.plotly_chart(fig, use_container_width=True)

    if f["date"].notna().any():
        st.divider()
        st.subheader("기간별 흐름(주 단위)")
        w = f.dropna(subset=["date"]).groupby(["week", "content_type"]).size().reset_index(name="count")
        fig = px.line(w, x="week", y="count", color="content_type", markers=True, title="주별 등장 추세")
        st.plotly_chart(fig, use_container_width=True)

    st.info("💡 이 화면의 목적: ‘지금 변화가 실제로 존재한다’를 데이터로 체감하기")
    if teacher_mode:
        with st.expander("👩‍🏫 교사용 질문(사고 확장)"):
            st.markdown("""
- 연구(논문) / 산업(뉴스·툴) / 채용(일자리) 중 **어디가 먼저 움직이는 느낌**인가?
- 사람들이 정보를 얻는 곳(도메인)이 한쪽으로 몰려 있다면, 그게 의미하는 것은?
- “변화가 빠르다”는 건 결국 **어떤 능력을 요구**하는가?
""")


# ============================================================
# TAB 2: Topics (Keywords)
# ============================================================
with tab2:
    st.subheader("키워드로 보는 ‘일의 중심축’ 변화")
    st.caption("Title+Description에서 영문 키워드를 추출해 ‘무엇이 반복적으로 등장하는가’를 본다(간단 룰 기반).")

    colA, colB = st.columns(2)

    with colA:
        kw = top_keywords(f, n=25)
        if kw:
            kw_df = pd.DataFrame(kw, columns=["keyword", "count"])
            fig = px.bar(kw_df, x="keyword", y="count", title="키워드 Top 25(필터 기준)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("키워드를 추출할 데이터가 부족합니다. 필터를 완화해보세요.")

    with colB:
        if df["date"].notna().any():
            rising = rising_keywords(df, recent_days=30, n=15)
            if rising:
                r_df = pd.DataFrame(rising, columns=["keyword", "score", "recent_count", "all_count"])
                fig = px.bar(r_df, x="keyword", y="score", title="최근 30일 ‘상승’ 키워드(간단 증감 점수)")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("점수는 ‘최근 비중 - 전체 비중’으로 계산(정교한 트렌딩이 아니라 수업용 신호).")
            else:
                st.info("최근 30일 비교를 할 데이터가 부족합니다(날짜/기간 확인).")
        else:
            st.info("Date가 없어 상승 키워드 분석이 제한됩니다.")

    st.divider()
    st.markdown("### 🧠 학생 사고 확장 질문(화면에 그대로 사용 가능)")
    st.markdown("""
- 지금 반복적으로 등장하는 키워드는 **‘기술’**인가, **‘일의 방식/규칙’**인가?  
- 이 키워드는 사람의 일을 **줄이는가 / 바꾸는가 / 새로 만드는가**?  
- 내가 이 키워드를 ‘수업 과제’로 바꾼다면, **10분짜리 행동**은 무엇일까?
""")
    if teacher_mode:
        with st.expander("👩‍🏫 교사용 운영 팁"):
            st.markdown("""
- 키워드는 ‘유행’이 아니라 **앞으로 자주 만나게 될 문제의 이름**으로 해석하게 돕습니다.
- 학생이 ‘모른다’고 하면 정상입니다. 대신 **모르는 것을 다루는 방식(질문 만들기)**을 학습목표로 잡으세요.
""")


# ============================================================
# TAB 3: Role Map (Roles)
# ============================================================
with tab3:
    st.subheader("‘직업명’이 아니라 ‘역할(ROLE)’로 보기")
    st.caption("CSV 텍스트를 간단한 규칙으로 역할로 분류하고, 학생은 ‘나는 어떤 역할에 끌리는가’를 선택한다.")

    left, right = st.columns(2)
    with left:
        role_dist = f["role"].value_counts().reset_index()
        role_dist.columns = ["role", "count"]
        fig = px.bar(role_dist, x="role", y="count", title="역할 분포(필터 기준)")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        if f["date"].notna().any():
            cutoff = pd.Timestamp(date.today() - timedelta(days=30))
            recent = f[f["date"] >= cutoff]
            comp = pd.DataFrame({
                "전체": f["role"].value_counts(),
                "최근30일": recent["role"].value_counts()
            }).fillna(0).astype(int).reset_index().rename(columns={"index":"role"})
            comp_melt = comp.melt(id_vars=["role"], var_name="range", value_name="count")
            fig = px.bar(comp_melt, x="role", y="count", color="range", barmode="group",
                         title="역할 비교: 전체 vs 최근 30일")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Date가 없어 최근 30일 역할 비교가 제한됩니다.")

    st.divider()
    st.markdown("### 🎯 학생 활동: ‘나의 역할 Top 2’ 선택하기")

    role_choices = list(role_dist["role"].tolist()) if len(role_dist) else [r[0] for r in ROLE_DEFS]
    sel_roles = st.multiselect("끌리는 역할을 2개 선택(권장)", role_choices, default=role_choices[:2])

    reason_like = st.text_area("왜 끌리나요? (이유 1~2줄)", placeholder="예: 문제를 구조화하고 방향을 정하는 일이 재밌을 것 같아서")
    reason_hard = st.text_area("무엇이 부담/어려움으로 느껴지나요? (1~2줄)", placeholder="예: 기술 용어가 낯설고 시작이 막막함")

    # pick an item to anchor
    st.markdown("### 🧷 ‘역할’이 실제로 보이는 사례 1개 고르기")
    f_sel = f.sort_values("date", ascending=False).head(400) if len(f) > 400 else f
    if len(f_sel) == 0:
        st.info("필터 결과가 없습니다. 왼쪽 필터를 완화해보세요.")
    else:
        chosen = st.selectbox("사례 선택(최근순 상위 400개)", f_sel.apply(item_label, axis=1).tolist())
        idx = f_sel.apply(item_label, axis=1).tolist().index(chosen)
        row = f_sel.iloc[idx]

        st.markdown(f"**{row['title']}**")
        st.caption(f"{row['source']} · {row['content_type']} · {row['domain']} · "
                   f"{row['date'].date() if pd.notna(row['date']) else ''} · 분류역할: {row['role']}")
        st.write(row["desc"][:900] + ("…" if len(row["desc"]) > 900 else ""))
        st.link_button("원문 보기", row["link"])

        st.markdown("#### 🔽 이 사례를 ‘나의 기록’에 추가")
        my_role = st.selectbox("내가 보기엔 이 사례의 핵심 역할은?", [r[0] for r in ROLE_DEFS], index=0)
        my_one_line = st.text_input("한 줄 해석(내 언어로)", placeholder="예: 사람은 결국 ‘검증 기준’을 만들고 반복 실험을 설계한다")
        my_next_10 = st.text_input("10분 행동(지금 당장)", placeholder="예: 모르는 용어 3개 정의 찾아 메모하기")

        if st.button("📌 기록 추가", use_container_width=True):
            st.session_state["portfolio"].append({
                "date": str(row["date"].date()) if pd.notna(row["date"]) else "",
                "title": row["title"],
                "source": row["source"],
                "content_type": row["content_type"],
                "domain": row["domain"],
                "link": row["link"],
                "role_auto": row["role"],
                "role_mine": my_role,
                "why_like": reason_like.strip(),
                "why_hard": reason_hard.strip(),
                "one_line": my_one_line.strip(),
                "next10": my_next_10.strip(),
                "my_roles_top2": ", ".join(sel_roles[:2]) if sel_roles else ""
            })
            st.success("기록에 추가했습니다. ⑤ ‘나의 준비 로드맵’에서 자동 정리됩니다.")

    if teacher_mode:
        with st.expander("👩‍🏫 교사용 질문(핵심)"):
            st.markdown("""
- “이 텍스트에서 사람이 하는 일은 ‘무엇을 결정/설계/구현/운영/검증/설명’하는 것인가?”
- “나는 어떤 역할이 더 자연스러운가? 그 이유는 ‘흥미/가치/강점’ 중 무엇인가?”
- “부담(어려움)은 약점 고백이 아니라 **준비 과제**다. 무엇을 준비하면 바뀔까?”
""")


# ============================================================
# TAB 4: Path comparison (Triad)
# ============================================================
with tab4:
    st.subheader("같은 주제, 다른 경로: 논문–실무–채용")
    st.caption("같은 키워드를 기준으로 ‘연구/실무/채용’ 3종 세트를 나란히 보고 경로 다양성을 체감한다.")

    if len(f) == 0:
        st.info("필터 결과가 없습니다. 왼쪽 필터를 완화해보세요.")
    else:
        base = st.selectbox("기준 아이템 선택(최근순 상위 400개)", (f.sort_values("date", ascending=False).head(400)).apply(item_label, axis=1).tolist())
        f_base = f.sort_values("date", ascending=False).head(400)
        idx = f_base.apply(item_label, axis=1).tolist().index(base)
        base_row = f_base.iloc[idx]

        # 자동 키워드 제안
        auto_keys = Counter(tokenize_en(base_row["title"] + " " + base_row["desc"])).most_common(10)
        suggested = auto_keys[0][0] if auto_keys else ""
        key = st.text_input("키워드(자동 제안 → 수정 가능)", value=suggested)

        if key.strip():
            picks, sub = triad_pick(f, key)
            cols = st.columns(3)
            mapping = {"paper": "논문(Research)", "news": "산업/도구(Practice)", "job": "채용(Job)"}

            for i, t in enumerate(["paper", "news", "job"]):
                with cols[i]:
                    st.markdown(f"### {mapping[t]}")
                    if t in picks:
                        r = picks[t]
                        st.markdown(f"**{r['title']}**")
                        st.caption(f"{r['source']} · {r['date'].date() if pd.notna(r['date']) else ''} · {r['domain']} · 역할: {r['role']}")
                        st.write(r["desc"][:260] + ("…" if len(r["desc"]) > 260 else ""))
                        st.link_button("원문 보기", r["link"])
                    else:
                        st.info("해당 유형에서 매칭되는 항목이 없습니다.")

            st.divider()
            st.markdown("### 🧠 학생 사고 확장 질문")
            st.markdown("""
- 같은 주제인데도 **논문/실무/채용**이 강조하는 포인트가 어떻게 다른가?  
- 나는 이 주제를 어떤 경로로 다루고 싶은가? (연구/구현/운영/평가/설명)  
- ‘전공’은 고정이 아니라, **경로에 맞게 재구성되는 준비**다. 내 경로는?
""")

            if st.button("📌 이 주제(키워드)를 기록에 추가", use_container_width=True):
                st.session_state["notes"].append({
                    "topic_keyword": key.strip(),
                    "base_title": base_row["title"],
                    "note": ""
                })
                st.success("주제 메모에 추가했습니다. ⑤에서 함께 정리할 수 있어요.")
        else:
            st.info("키워드를 입력해주세요.")

    if teacher_mode:
        with st.expander("👩‍🏫 교사용 운영 팁"):
            st.markdown("""
- 학생들이 ‘전공=직업’으로 단선적으로 생각할 때, 이 화면이 전환점을 만듭니다.
- 같은 키워드라도 경로마다 다른 질문이 생깁니다:
  - 논문: “무엇이 사실인가?”
  - 실무: “어떻게 구현/적용하는가?”
  - 채용: “어떤 역할을 수행할 수 있는가?”
""")


# ============================================================
# TAB 5: My Plan (Roadmap output)
# ============================================================
with tab5:
    st.subheader("나의 준비 로드맵(산출물)")
    st.caption("선택/기록을 자동 정리하고, ‘이번 주 10분 행동 + 이번 달 미니 프로젝트’로 연결합니다.")

    items = st.session_state.get("portfolio", [])
    notes = st.session_state.get("notes", [])

    if not items and not notes:
        st.info("아직 기록이 없습니다. ③/④ 탭에서 사례 또는 주제를 기록해보세요.")
    else:
        if items:
            p = pd.DataFrame(items)
            st.markdown("### 1) 오늘 내가 만든 기록")
            st.dataframe(p, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### 2) 나의 관심 역할(Top)")
            if "role_mine" in p.columns:
                role_counts = p["role_mine"].value_counts().reset_index()
                role_counts.columns = ["role", "count"]
                fig = px.bar(role_counts, x="role", y="count", title="내가 선택한 역할 분포")
                st.plotly_chart(fig, use_container_width=True)

            # 추천 역량 자동 제안
            st.divider()
            st.markdown("### 3) 역할 기반 ‘추천 역량’(자동 제안)")

            top_role = None
            if "role_mine" in p.columns and p["role_mine"].notna().any():
                top_role = p["role_mine"].value_counts().index[0]

            if top_role and top_role in ROLE_TO_SKILLS:
                sugg = ROLE_TO_SKILLS[top_role]
                st.success(f"가장 많이 선택된 역할: **{top_role}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**기술(Tech)**")
                    st.write(", ".join(sugg["tech"]))
                with col2:
                    st.markdown("**인지(Cognition)**")
                    st.write(", ".join(sugg["cog"]))
                with col3:
                    st.markdown("**태도(Attitude)**")
                    st.write(", ".join(sugg["att"]))
            else:
                st.info("역량 자동 제안은 ‘내가 선택한 역할’이 있을 때 더 정확해집니다.")

            st.divider()
            st.markdown("### 4) 나의 준비 체크(선택/기록)")
            c1, c2, c3 = st.columns(3)
            with c1:
                tech = st.multiselect("기술 역량(체크)", SKILL_TECH, default=[])
            with c2:
                cog = st.multiselect("인지 역량(체크)", SKILL_COG, default=[])
            with c3:
                att = st.multiselect("태도 역량(체크)", SKILL_ATT, default=[])

            st.markdown("### 5) ‘나는 어떻게 살아가야 하나?’를 ‘준비 계획’으로 바꾸기")
            if audience == "고3":
                st.markdown("""
- **핵심:** 전공 확정이 아니라, **역할과 학습 습관**을 만든다  
- **좋은 계획:** “작게 해보고 → 기록하고 → 질문을 업데이트”  
""")
                next10_tpl = "예: 모르는 용어 3개 정의 찾아서 노트에 정리하기"
                month_tpl = "예: 관심 키워드 1개로 미니 발표자료 1장 만들기(역할/역량/경로 정리)"
            else:
                st.markdown("""
- **핵심:** 전공과 무관하게, **경로(연구/실무/채용) 중 어디로 갈지**를 정하고 준비를 쌓는다  
- **좋은 계획:** “작은 프로젝트 → 포트폴리오 → 피드백(멘토/동료)”  
""")
                next10_tpl = "예: 관심 주제 관련 글 1개 읽고 ‘역할/역량/경로’ 3줄 요약"
                month_tpl = "예: Streamlit/노션/깃허브로 ‘트렌드→역할→역량’ 미니 프로젝트 제작"

            next10 = st.text_input("이번 주 10분 행동 1개", value=next10_tpl)
            month_project = st.text_input("이번 달 미니 프로젝트 1개", value=month_tpl)
            help_people = st.text_input("도움 받을 자원/사람(1개)", placeholder="예: 담임/진로쌤, 선배, 커뮤니티, 유튜브 강의, 학교 동아리")

            one_line = st.text_area("나의 한 줄 선언문", placeholder="예: 나는 평가자 역할에 끌리고, 이번 달에는 검증 기준을 만드는 연습을 시작하겠다.")

            st.divider()
            st.markdown("### 6) 산출물 미리보기(복사해서 제출 가능)")
            top2 = p["my_roles_top2"].dropna().iloc[-1] if "my_roles_top2" in p.columns and len(p["my_roles_top2"].dropna()) else ""
            sample_line = p["one_line"].dropna().iloc[-1] if "one_line" in p.columns and len(p["one_line"].dropna()) else ""
            picked_title = p["title"].iloc[-1] if len(p) else ""
            picked_role = p["role_mine"].iloc[-1] if "role_mine" in p.columns and len(p) else ""

            st.code(
f"""[오늘의 진로 사고 확장 기록]

- 내가 본 변화(사례): {picked_title}
- 내가 해석한 핵심 역할: {picked_role}
- 끌리는 역할 Top2: {top2}
- 한 줄 해석: {sample_line}

[나의 준비 계획]

- 기술 역량(체크): {", ".join(tech)}
- 인지 역량(체크): {", ".join(cog)}
- 태도 역량(체크): {", ".join(att)}
- 이번 주 10분 행동: {next10}
- 이번 달 미니 프로젝트: {month_project}
- 도움 받을 자원/사람: {help_people}
- 나의 한 줄 선언문: {one_line}
""",
                language="text"
            )

            colD1, colD2 = st.columns(2)
            with colD1:
                csv_bytes = p.to_csv(index=False).encode("utf-8-sig")
                st.download_button("⬇️ 기록 CSV 다운로드", csv_bytes,
                                   file_name=f"career_portfolio_{date.today().isoformat()}.csv",
                                   mime="text/csv", use_container_width=True)
            with colD2:
                if st.button("🗑️ 기록 전체 삭제", use_container_width=True):
                    st.session_state["portfolio"] = []
                    st.session_state["notes"] = []
                    st.success("기록을 삭제했습니다. (필요하면 새로고침)")

        if notes:
            st.divider()
            st.markdown("### 7) 주제 메모(키워드) 모아보기")
            ndf = pd.DataFrame(notes)
            st.dataframe(ndf, use_container_width=True, hide_index=True)


# ============================================================
# Footer: Student questions (optional, keeps your original intent)
# ============================================================
st.divider()
st.header("❓ 익명 질문 수집(수업용)")

qcol1, qcol2 = st.columns([1, 1])
with qcol1:
    q = st.text_area("질문을 적어주세요", placeholder="예: 문과도 AI 관련 진로가 가능할까요?")
    if st.button("📥 질문 제출", use_container_width=True):
        if q.strip():
            st.session_state["student_questions"].append(q.strip())
            st.success("질문이 저장되었습니다!")
        else:
            st.warning("질문을 입력해주세요.")

def classify_question(text: str) -> str:
    t = str(text).lower()
    if re.search(r"전공|학과|과|선택|편입|복수|부전공", t):
        return "전공/학과"
    if re.search(r"공부|역량|준비|수학|코딩|자격|포트폴리오", t):
        return "역량/준비"
    if re.search(r"직업|취업|일자리|커리어|연봉|회사", t):
        return "진로/직업"
    if re.search(r"불안|걱정|두려|못할|괜찮", t):
        return "불안/고민"
    return "기타"

with qcol2:
    if st.session_state["student_questions"]:
        q_df = pd.DataFrame({
            "question": st.session_state["student_questions"],
            "type": [classify_question(x) for x in st.session_state["student_questions"]]
        })
        dist = q_df["type"].value_counts().reset_index()
        dist.columns = ["type", "count"]
        fig = px.bar(dist, x="type", y="count", title="질문 유형 분포")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("아직 수집된 질문이 없습니다.")
