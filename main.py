import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import Counter

# =============================
# 페이지 설정
# =============================
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

# =============================
# session_state 초기화
# =============================
if "questions" not in st.session_state:
    st.session_state.questions = []

# =============================
# 타이틀
# =============================
st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.caption("AI Agent 생태계 데이터 기반 트렌드 탐색 + 학생 질문 실시간 분석")

# =============================
# 데이터 로드
# =============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="cp949")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

df = load_data()

# =============================
# A. 연도별 트렌드
# =============================
st.subheader("A. 연도별 AI Agent 트렌드 변화")

yearly_trend = df.groupby("Year").size().reset_index(name="Count")

chart_a = (
    alt.Chart(yearly_trend)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        tooltip=["Year", "Count"]
    )
    .properties(height=320)
)

st.altair_chart(chart_a, use_container_width=True)
st.divider()

# =============================
# B. 역할 진화 단계
# =============================
st.subheader("B. AI Agent 역할 진화")

def classify_role(text):
    text = str(text).lower()
    if re.search(r"multi|ecosystem|collaboration|swarm", text):
        return "Multi-Agent System"
    if re.search(r"autonomous|decision|agentic", text):
        return "Autonomous Agent"
    if re.search(r"chat|assistant|conversation", text):
        return "Conversational Agent"
    return "Task / Rule Agent"

df["Role"] = df["Description"].apply(classify_role)

role_trend = df.groupby(["Year", "Role"]).size().reset_index(name="Count")

chart_b = (
    alt.Chart(role_trend)
    .mark_bar()
    .encode(
        x="Year:O",
        y="Count:Q",
        color="Role:N",
        tooltip=["Year", "Role", "Count"]
    )
    .properties(height=380)
)

st.altair_chart(chart_b, use_container_width=True)
st.divider()

# =============================
# C. 학생 질문 입력
# =============================
st.header("C. 학생 질문 실시간 수집")

with st.form("question_form", clear_on_submit=True):
    q = st.text_input(
        "💬 지금 가장 고민되는 질문을 적어보세요",
        placeholder="예: AI 시대에 심리학 전공은 의미가 있을까요?"
    )
    submit = st.form_submit_button("질문 추가")

    if submit and q.strip():
        st.session_state.questions.append(q.strip())
        st.success("질문이 추가되었습니다!")

# =============================
# 관심영역 추론 (클러스터링 기준)
# =============================
def infer_interest(question):
    q = question.lower()
    if re.search(r"코딩|개발|ai|기술", q):
        return "기술·개발"
    if re.search(r"심리|상담|사람|교육", q):
        return "인간이해·심리"
    if re.search(r"기획|전략|문제", q):
        return "기획·문제해결"
    if re.search(r"법|윤리|사회|정책", q):
        return "판단·윤리·사회"
    if re.search(r"불안|걱정|모르겠", q):
        return "탐색·불안"
    return "복합/탐색중"

# =============================
# D-1. 질문 즉석 투표 (관심영역)
# =============================
st.divider()
st.subheader("D-1. 질문 즉석 투표 (관심 영역)")

if st.session_state.questions:
    interests = [infer_interest(q) for q in st.session_state.questions]
    vote_df = pd.DataFrame(Counter(interests).items(), columns=["관심 영역", "질문 수"])

    vote_chart = (
        alt.Chart(vote_df)
        .mark_bar(cornerRadius=5)
        .encode(
            x="관심 영역:N",
            y="질문 수:Q",
            tooltip=["관심 영역", "질문 수"]
        )
        .properties(height=300)
    )

    st.altair_chart(vote_chart, use_container_width=True)
else:
    st.info("아직 질문이 없습니다.")

# =============================
# D-2. 워드클라우드 (Altair 버전)
# =============================
st.divider()
st.subheader("D-2. 질문 워드클라우드")

if st.session_state.questions:
    words = []
    for q in st.session_state.questions:
        words += re.findall(r"[가-힣A-Za-z]{2,}", q)

    word_freq = Counter(words)
    wc_df = pd.DataFrame(word_freq.items(), columns=["word", "count"])

    wc_chart = (
        alt.Chart(wc_df)
        .mark_text()
        .encode(
            text="word:N",
            size=alt.Size("count:Q", scale=alt.Scale(range=[12, 60])),
            tooltip=["word", "count"]
        )
        .properties(height=350)
    )

    st.altair_chart(wc_chart, use_container_width=True)
else:
    st.info("질문이 쌓이면 워드클라우드가 생성됩니다.")

# =============================
# D-3. 전공군별 자동 클러스터링
# =============================
st.divider()
st.subheader("D-3. 전공군별 자동 클러스터링 결과")

major_map = {
    "기술·개발": "컴퓨터공학 / AI / 데이터",
    "인간이해·심리": "심리학 / 교육 / 상담",
    "기획·문제해결": "경영 / 산업공학 / 행정",
    "판단·윤리·사회": "법 / 철학 / 정책",
    "탐색·불안": "자유·융합전공",
    "복합/탐색중": "복수·연계전공"
}

if st.session_state.questions:
    cluster_data = []

    for q in st.session_state.questions:
        interest = infer_interest(q)
        cluster_data.append({
            "학생 질문": q,
            "분류된 관심 영역": interest,
            "추천 전공군": major_map[interest]
        })

    cluster_df = pd.DataFrame(cluster_data)
    st.dataframe(cluster_df, use_container_width=True)

else:
    st.info("질문이 아직 없어 클러스터링을 할 수 없습니다.")
