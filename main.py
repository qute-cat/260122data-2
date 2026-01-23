import os
import re
from collections import Counter
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px

# =================================================
# 페이지 설정
# =================================================
st.set_page_config(
    page_title="AI Agent 트렌드 이해(진로교육용)",
    layout="wide"
)

# =================================================
# 유틸
# =================================================
STOP_EN = {
    "the","and","with","for","from","this","that","into","onto","over","under","about",
    "agent","agents","ai","llm","model","models","paper","research","using","use","used",
    "new","latest","toward","towards","via","based","approach","system","systems"
}

ROLE_CHOICES = [
    "설계자(기획/구조화)", "구현자(개발/자동화)", "운영자(배포/모니터링)",
    "분석가(데이터/리서치)", "평가자(Eval/검증)", "커뮤니케이터(기획/교육/번역)"
]

SKILL_TECH = ["Python", "API/연동", "데이터 처리", "LLM/RAG", "에이전트/워크플로우", "클라우드/배포", "보안/윤리"]
SKILL_COG  = ["문제정의", "구조화", "실험/검증", "논리적 글쓰기", "모델링/추론", "정보탐색", "시스템 사고"]
SKILL_ATT  = ["자기주도", "협업", "불확실성 감내", "학습 민첩성", "책임감", "사용자 관점", "끈기"]

# =================================================
# 데이터 로딩 (CSV)
# - 배포환경: 동일 폴더에 파일 두거나, Streamlit secrets/환경변수로 경로 지정
# =================================================
DEFAULT_PATH = "AI_Agents_Ecosystem_2026.csv"
DATA_PATH = os.getenv("AI_AGENT_CSV_PATH", DEFAULT_PATH)

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """
    기대 스키마: Title, Source, Date, Description, Link
    """
    df = pd.read_csv(path, encoding="cp949")

    # 컬럼 정규화(대소문자/공백 대응)
    colmap = {c.strip().lower(): c for c in df.columns}
    def pick(name):
        return colmap.get(name.lower())

    # 필수 컬럼 매핑
    title_c = pick("title")
    source_c = pick("source")
    date_c = pick("date")
    desc_c = pick("description")
    link_c = pick("link")

    if not all([title_c, source_c, date_c, desc_c, link_c]):
        raise ValueError(
            "CSV 컬럼이 예상과 다릅니다. 필요한 컬럼: Title, Source, Date, Description, Link"
        )

    df = df.rename(columns={
        title_c: "title",
        source_c: "source",
        date_c: "date",
        desc_c: "desc",
        link_c: "link"
    })

    # 타입/결측 처리
    df["title"] = df["title"].astype(str).fillna("")
    df["source"] = df["source"].astype(str).fillna("")
    df["desc"] = df["desc"].astype(str).fillna("")
    df["link"] = df["link"].astype(str).fillna("")

    # 날짜 파싱
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 도메인 추출
    df["domain"] = df["link"].str.extract(r"https?://([^/]+)", expand=False).fillna("")

    # 간단 콘텐츠 타입(소스 기반)
    s = df["source"].str.lower()
    df["content_type"] = "news"
    df.loc[s.str.contains("arxiv"), "content_type"] = "paper"
    df.loc[s.str.contains("job"), "content_type"] = "job"

    # 기본 정리: 빈 title/link 제거, 링크 중복 제거
    df = df[(df["title"].str.strip() != "") & (df["link"].str.strip() != "")]
    df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)

    return df

# =================================================
# 세션 상태 초기화
# =================================================
if "questions" not in st.session_state:
    st.session_state["questions"] = []

if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = []

# =================================================
# 헤더
# =================================================
st.title("🤖 AI Agent 트렌드 × 진로·전공 탐색(교육용)")
st.caption("고3·대학생 대상 특강/수업에서 ‘트렌드 → 역할 → 역량 → 경로 → 산출물’로 연결하는 대시보드")

st.markdown("""
> **AI는 무엇을 할 수 있느냐보다,  
> 우리는 AI와 함께 무엇을 할 것인가를 묻는 시대입니다.**
""")
st.divider()

# =================================================
# 데이터 로딩 & 사이드바 필터
# =================================================
load_error = None
df = None
try:
    df = load_data(DATA_PATH)
except Exception as e:
    load_error = str(e)

with st.sidebar:
    st.header("⚙️ 데이터 & 필터")

    if load_error:
        st.error("CSV를 불러오지 못했어요.")
        st.caption(load_error)
        st.markdown("""
        **해결 방법**
        - 앱 폴더에 `AI_Agents_Ecosystem_2026.csv` 파일이 있는지 확인
        - 또는 환경변수 `AI_AGENT_CSV_PATH`에 경로 지정
        """)
        st.stop()

    st.caption(f"데이터: {len(df):,}개 항목")

    # 날짜 범위
    min_d = df["date"].min()
    max_d = df["date"].max()

    if pd.isna(min_d) or pd.isna(max_d):
        st.warning("날짜 파싱이 충분하지 않아 기간 필터를 제한적으로 사용합니다.")
        date_range = None
    else:
        d0 = min_d.date()
        d1 = max_d.date()
        date_range = st.date_input("기간", value=(d0, d1))

    # 소스
    sources_all = sorted(df["source"].dropna().unique().tolist())
    sources_sel = st.multiselect("Source", sources_all, default=sources_all)

    # 콘텐츠 타입
    types_all = ["news", "paper", "job"]
    types_sel = st.multiselect("콘텐츠 타입", types_all, default=types_all)

    # 도메인 Top만 제공 (너무 많아질 수 있어서)
    dom_counts = df["domain"].value_counts().head(30)
    dom_all = dom_counts.index.tolist()
    dom_sel = st.multiselect("도메인(상위 30)", dom_all, default=[])

    keyword = st.text_input("키워드 검색", placeholder="예: evaluation, agentic, RAG, orchestration ...")

    st.divider()
    st.header("🧑‍🎓 수업 운영")
    teacher_mode = st.toggle("교사용 모드(해설/가이드 표시)", value=True)

# 필터 적용
f = df.copy()
if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    f = f[(f["date"].dt.date >= start_d) & (f["date"].dt.date <= end_d)]

f = f[f["source"].isin(sources_sel)]
f = f[f["content_type"].isin(types_sel)]
if dom_sel:
    f = f[f["domain"].isin(dom_sel)]

if keyword and keyword.strip():
    k = keyword.strip().lower()
    f = f[
        f["title"].str.lower().str.contains(k, na=False) |
        f["desc"].str.lower().str.contains(k, na=False)
    ]

# =================================================
# 탭 구성(진로교육용)
# =================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 지금의 변화",
    "🧭 역할 번역",
    "🧩 역량 분해",
    "🔁 같은 주제 다른 경로",
    "📒 나의 기록(산출물)"
])

# =================================================
# TAB 1. 지금의 변화 (Reality Dashboard)
# =================================================
with tab1:
    st.subheader("지금, 무슨 일이 일어나고 있을까?")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("필터 후 항목", f"{len(f):,}개")
    c2.metric("Source 수", f"{f['source'].nunique():,}개")
    c3.metric("Domain 수", f"{f['domain'].nunique():,}개")
    if f["date"].notna().any():
        c4.metric("최근 날짜", f"{f['date'].max().date()}")
    else:
        c4.metric("최근 날짜", "-")

    st.divider()

    left, right = st.columns(2)

    with left:
        # Source 분포
        src = f["source"].value_counts().reset_index()
        src.columns = ["source", "count"]
        fig_src = px.bar(src.head(12), x="source", y="count", title="Source 분포(상위 12)")
        st.plotly_chart(fig_src, use_container_width=True)

    with right:
        # Content type 분포
        ct = f["content_type"].value_counts().reset_index()
        ct.columns = ["content_type", "count"]
        fig_ct = px.pie(ct, names="content_type", values="count", title="콘텐츠 타입 비중")
        st.plotly_chart(fig_ct, use_container_width=True)

    # 월별 추세(가능할 때)
    if f["date"].notna().any():
        st.divider()
        st.subheader("기간별 흐름(월 단위)")
        tmp = f.dropna(subset=["date"]).copy()
        tmp["month"] = tmp["date"].dt.to_period("M").astype(str)
        m = tmp.groupby(["month", "content_type"]).size().reset_index(name="count")
        fig_m = px.line(m, x="month", y="count", color="content_type", markers=True, title="월별 등장 추세")
        st.plotly_chart(fig_m, use_container_width=True)

    if teacher_mode:
        with st.expander("👩‍🏫 교사용 해설(운영 포인트)"):
            st.markdown("""
- 이 탭의 목표는 **‘지금 변화가 실제로 존재한다’**를 학생이 체감하게 만드는 것입니다.  
- 여기서 바로 진로 결론을 내리기보다,  
  **“연구/실무/채용이 동시에 움직인다”**는 환경 인식을 먼저 형성합니다.
""")

# =================================================
# 공통: 아이템 선택 UI
# =================================================
def item_label(row: pd.Series) -> str:
    d = ""
    if pd.notna(row["date"]):
        d = str(row["date"].date())
    return f"[{row['content_type']}] {d} · {row['title'][:90]}"

# 표본이 너무 크면 selectbox가 무거워질 수 있어 상위 N 사용
MAX_SELECT = 400
f_for_select = f.sort_values("date", ascending=False).head(MAX_SELECT) if len(f) > 0 else f

# =================================================
# TAB 2. 역할 번역 (Role Translator)
# =================================================
with tab2:
    st.subheader("기술 텍스트를 ‘직무 역할’ 언어로 번역하기")

    if len(f_for_select) == 0:
        st.info("필터 결과가 없습니다. 왼쪽 필터를 완화해보세요.")
    else:
        selected = st.selectbox(
            "아이템 선택(최근순 상위 400개 내)",
            f_for_select.apply(item_label, axis=1).tolist()
        )
        # 라벨로부터 row 찾기
        idx = f_for_select.apply(item_label, axis=1).tolist().index(selected)
        row = f_for_select.iloc[idx]

        st.markdown(f"### {row['title']}")
        st.caption(f"{row['source']} · {row['content_type']} · {row['domain']} · "
                   f"{row['date'].date() if pd.notna(row['date']) else ''}")
        st.write(row["desc"][:900] + ("…" if len(row["desc"]) > 900 else ""))

        st.link_button("원문 보기", row["link"])

        st.divider()
        st.markdown("#### 1) 이 내용이 말하는 ‘사람의 역할’은 무엇인가?")
        role = st.radio("역할 선택", ROLE_CHOICES, horizontal=True)

        st.markdown("#### 2) 근거(한 줄)")
        reason = st.text_area("왜 그렇게 판단했나요?", placeholder="예: 반복적으로 평가/검증을 강조해서")

        st.markdown("#### 3) 다음 행동(10분 과제)")
        next_act = st.text_input("오늘 바로 할 수 있는 행동 1개", placeholder="예: 관련 용어 3개 정의 찾아보기")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("📌 기록에 추가", use_container_width=True):
                st.session_state["portfolio"].append({
                    "date": str(row["date"].date()) if pd.notna(row["date"]) else "",
                    "content_type": row["content_type"],
                    "source": row["source"],
                    "domain": row["domain"],
                    "title": row["title"],
                    "role": role,
                    "reason": reason.strip(),
                    "next_action": next_act.strip(),
                    "link": row["link"]
                })
                st.success("기록에 추가했어요.")
        with col_b:
            if st.button("🧹 입력 초기화", use_container_width=True):
                # 입력 위젯 상태 초기화는 Streamlit 제약상 간단히 안내
                st.info("입력값 초기화가 필요하면 새로고침(F5)하거나 다른 아이템을 선택해 주세요.")

        if teacher_mode:
            with st.expander("👩‍🏫 교사용 해설(질문 예시)"):
                st.markdown("""
- 학생에게 이렇게 물어보면 좋아요.
  - “이 글에서 사람이 하는 일은 ‘결정/설계/구현/운영/검증/설명’ 중 어디에 가까울까?”
  - “왜 그렇게 판단했나? **텍스트 근거를 꼭 1개** 말해보자.”
  - “이 역할을 하려면 **10분 안에 할 수 있는 다음 행동**은 뭘까?”
""")

# =================================================
# TAB 3. 역량 분해 (Skill Decomposer)
# =================================================
with tab3:
    st.subheader("역할을 ‘역량’으로 분해하고, 나의 준비 상태를 점검하기")

    if len(st.session_state["portfolio"]) == 0:
        st.info("먼저 ‘역할 번역’ 탭에서 최소 1개를 기록해 주세요.")
    else:
        p = pd.DataFrame(st.session_state["portfolio"])
        # 최근 기록 선택
        recent_titles = p["title"].tolist()[::-1]
        sel_title = st.selectbox("기준 기록 선택(최근 기록부터)", recent_titles)
        prow = p[p["title"] == sel_title].iloc[0]

        st.markdown(f"### {prow['title']}")
        st.caption(f"{prow['content_type']} · {prow['source']} · {prow['domain']} · 역할: {prow['role']}")
        st.link_button("원문 보기", prow["link"])

        st.divider()
        st.markdown("#### 1) 기술 역량(Tech)")
        tech = st.multiselect("해당 역할에 중요해 보이는 기술 역량", SKILL_TECH, default=[])

        st.markdown("#### 2) 인지 역량(Cognition)")
        cog = st.multiselect("해당 역할에 중요해 보이는 사고/문제해결 역량", SKILL_COG, default=[])

        st.markdown("#### 3) 태도 역량(Attitude)")
        att = st.multiselect("해당 역할에 중요해 보이는 태도/일하는 방식", SKILL_ATT, default=[])

        st.divider()
        st.markdown("#### 4) 나의 준비 상태(짧게)")
        have = st.text_area("내가 이미 갖춘 것(1~2줄)", placeholder="예: 정보탐색은 강점, 글로 정리하는 습관 있음")
        gap = st.text_area("앞으로 키울 것(1~2줄)", placeholder="예: API 연동 경험 부족 → 간단한 프로젝트로 보완")
        plan = st.text_input("이번 주 실행 계획(아주 작게 1개)", placeholder="예: Streamlit으로 데이터 검색 기능 구현해보기")

        if st.button("✅ 역량 점검 기록 저장", use_container_width=True):
            # 같은 title 기록에 역량 필드 덮어쓰기(최근 항목을 우선)
            for i in range(len(st.session_state["portfolio"]) - 1, -1, -1):
                if st.session_state["portfolio"][i]["title"] == sel_title:
                    st.session_state["portfolio"][i]["skills_tech"] = ", ".join(tech)
                    st.session_state["portfolio"][i]["skills_cog"] = ", ".join(cog)
                    st.session_state["portfolio"][i]["skills_att"] = ", ".join(att)
                    st.session_state["portfolio"][i]["have"] = have.strip()
                    st.session_state["portfolio"][i]["gap"] = gap.strip()
                    st.session_state["portfolio"][i]["plan"] = plan.strip()
                    break
            st.success("역량 점검 내용을 기록에 저장했어요.")

        if teacher_mode:
            with st.expander("👩‍🏫 교사용 해설(활동 운영)"):
                st.markdown("""
- 학생이 ‘역량’을 추상적으로 말하면, **근거 문장(텍스트)으로 연결**하게 지도하세요.
- ‘갭’은 약점 고백이 아니라, **다음 행동을 정하는 출발점**이라는 메시지가 중요합니다.
""")

# =================================================
# TAB 4. 같은 주제 다른 경로 (Triad View)
# =================================================
def simple_topic_keywords(text: str):
    text = str(text)
    tokens = re.findall(r"[A-Za-z]{3,}", text.lower())
    tokens = [t for t in tokens if t not in STOP_EN]
    # 빈도 높은 순으로 반환
    c = Counter(tokens)
    return [k for k, _ in c.most_common(10)]

with tab4:
    st.subheader("같은 주제, 다른 경로: 연구(논문)–실무(도구/글)–채용(직무)")

    if len(f_for_select) == 0:
        st.info("필터 결과가 없습니다. 왼쪽 필터를 완화해보세요.")
    else:
        base = st.selectbox(
            "기준 아이템 선택(최근순 상위 400개 내)",
            f_for_select.apply(item_label, axis=1).tolist(),
            key="triad_base"
        )
        idx = f_for_select.apply(item_label, axis=1).tolist().index(base)
        base_row = f_for_select.iloc[idx]

        keys = simple_topic_keywords(base_row["title"] + " " + base_row["desc"])
        auto_key = keys[0] if keys else ""

        st.caption(f"자동 추출 키워드: **{auto_key if auto_key else '(추출 실패)'}**")
        manual_key = st.text_input("키워드 수정(원하면)", value=auto_key)

        if manual_key.strip():
            key = manual_key.strip().lower()
            sub = f[
                f["title"].str.lower().str.contains(key, na=False) |
                f["desc"].str.lower().str.contains(key, na=False)
            ].copy()

            # 각 타입에서 최근 1개씩
            picks = {}
            for t in ["paper", "news", "job"]:
                tmp = sub[sub["content_type"] == t].sort_values("date", ascending=False).head(1)
                if len(tmp) > 0:
                    picks[t] = tmp.iloc[0]

            cols = st.columns(3)
            mapping = {"paper": "논문(연구)", "news": "산업/도구", "job": "채용/직무"}
            for i, t in enumerate(["paper", "news", "job"]):
                with cols[i]:
                    st.markdown(f"### {mapping[t]}")
                    if t in picks:
                        r = picks[t]
                        st.markdown(f"**{r['title']}**")
                        st.caption(f"{r['source']} · {r['date'].date() if pd.notna(r['date']) else ''} · {r['domain']}")
                        st.write(r["desc"][:260] + ("…" if len(r["desc"]) > 260 else ""))
                        st.link_button("원문 보기", r["link"])
                    else:
                        st.info("매칭 항목이 없어요.")

            if teacher_mode:
                with st.expander("👩‍🏫 교사용 질문(토론 촉진)"):
                    st.markdown("""
- 같은 주제인데도 ‘연구–실무–채용’이 다르게 말하는 이유는?
- 나는 이 주제를 어떤 경로로 다루고 싶은가?
  - 연구자(이론/근거) / 개발자(구현) / 운영자(서비스) / 평가자(검증) / 커뮤니케이터(교육·번역)
""")
        else:
            st.info("키워드를 입력해 주세요.")

# =================================================
# TAB 5. 나의 기록(산출물)
# =================================================
with tab5:
    st.subheader("오늘의 산출물: 나의 관심 역할·역량·다음 행동")

    items = st.session_state.get("portfolio", [])
    if not items:
        st.info("아직 기록이 없습니다. ‘역할 번역’ 탭에서 1개 이상 기록해보세요.")
    else:
        p = pd.DataFrame(items)

        st.markdown("#### 1) 기록 목록")
        st.dataframe(p, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### 2) 나의 관심 역할 Top")
        role_counts = p["role"].value_counts().reset_index()
        role_counts.columns = ["role", "count"]
        fig_role = px.bar(role_counts, x="role", y="count", title="관심 역할 분포")
        st.plotly_chart(fig_role, use_container_width=True)

        st.divider()
        st.markdown("#### 3) 오늘의 한 줄 정리")
        one_line = st.text_area(
            "오늘 수업을 한 줄로 정리해보세요",
            placeholder="예: 나는 ‘평가자’ 역할에 끌리고, 이번 주에는 간단한 실험/검증을 해보겠다."
        )

        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("🗑️ 전체 기록 삭제", use_container_width=True):
                st.session_state["portfolio"] = []
                st.success("기록을 모두 삭제했어요. (새로고침하면 화면이 갱신됩니다)")

        with col2:
            # CSV 다운로드(세션 기반)
            csv_bytes = p.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ 기록 CSV 다운로드",
                data=csv_bytes,
                file_name=f"career_portfolio_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        if teacher_mode:
            with st.expander("👩‍🏫 교사용 마무리 멘트(권장)"):
                st.markdown("""
- “오늘의 결론은 전공/직업 ‘결정’이 아니라, **나의 역할 선호를 발견한 것**이다.”
- “다음 행동이 아주 작아도 괜찮다. 중요한 건 **실행 후 다시 해석**하는 것이다.”
""")

# =================================================
# (옵션) 학생 질문 수집 + 간단 분석 섹션
# - 기존 코드의 장점 유지: Q 수집/분석
# =================================================
st.divider()
st.header("❓ 학생 질문 수집(익명) & 흐름 보기")

qcol1, qcol2 = st.columns([1, 1])
with qcol1:
    q = st.text_area("익명 질문 남기기", placeholder="예: 문과도 AI 관련 진로가 가능할까요?")
    if st.button("📥 질문 제출", use_container_width=True):
        if q.strip():
            st.session_state["questions"].append(q.strip())
            st.success("질문이 저장되었습니다!")
        else:
            st.warning("질문을 입력해주세요.")

def classify_question(text: str) -> str:
    text = str(text).lower()
    if re.search("전공|학과|과|컴공|심리|선택", text):
        return "전공/학과"
    if re.search("공부|역량|준비|수학|코딩|포트폴리오", text):
        return "역량/준비"
    if re.search("직업|취업|일자리|커리어|연봉", text):
        return "진로/직업"
    if re.search("불안|걱정|괜찮|못할|두려", text):
        return "불안/고민"
    return "기타"

with qcol2:
    if st.session_state["questions"]:
        q_df = pd.DataFrame({
            "question": st.session_state["questions"],
            "type": [classify_question(x) for x in st.session_state["questions"]]
        })
        dist = q_df["type"].value_counts().reset_index()
        dist.columns = ["type", "count"]
        fig_q = px.bar(dist, x="type", y="count", title="질문 유형 분포")
        st.plotly_chart(fig_q, use_container_width=True)
    else:
        st.info("아직 수집된 질문이 없습니다.")
