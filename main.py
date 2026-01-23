import streamlit as st
import pandas as pd
import altair as alt
import re

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

# -----------------------------
# session_state 초기화 (🔥 핵심)
# -----------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

# -----------------------------
# 페이지 타이틀
# -----------------------------
st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.caption("AI Agent 생태계 데이터 기반 트렌드 탐색")

# -----------------------------
# 데이터 로드 (인코딩 안전 처리)
# -----------------------------
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

yearly_trend = (
    df.groupby("Year")
    .size()
    .reset_index(name="Count")
)

chart_a = (
    alt.Chart(yearly_trend)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        tooltip=["Year", "Count"]
    )
    .properties(height=380)
)

st.altair_chart(chart_a, use_container_width=True)

st.markdown("""
👉 **A 단계 요약**  
AI Agent 관련 논의는 최근으로 올수록 **폭발적으로 증가**하고 있습니다.
""")

st.divider()

# =============================
# B. 역할 진화 단계 분석
# =============================
st.subheader("B. AI Agent 역할 진화 단계")

st.markdown("""
AI Agent는 단순한 프로그램이 아니라  
**어떤 역할을 맡고 있는 존재인가**로 이해할 수 있습니다.
""")

# -----------------------------
# 역할 단계 분류 함수
# -----------------------------
def classify_role(text):
    text = str(text).lower()

    if re.search(r"multi|ecosystem|collaboration|swarm", text):
        return "4️⃣ Multi-Agent System"
    if re.search(r"autonomous|self|decision|agentic", text):
        return "3️⃣ Autonomous Agent"
    if re.search(r"chat|assistant|conversation|dialog", text):
        return "2️⃣ Conversational Agent"
    return "1️⃣ Task / Rule Agent"

df["Role_Stage"] = df["Description"].apply(classify_role)

# -----------------------------
# 연도 × 역할 단계 집계
# -----------------------------
role_trend = (
    df.groupby(["Year", "Role_Stage"])
    .size()
    .reset_index(name="Count")
)

chart_b = (
    alt.Chart(role_trend)
    .mark_bar()
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        color=alt.Color(
            "Role_Stage:N",
            title="AI Agent 역할 단계",
            scale=alt.Scale(
                domain=[
                    "1️⃣ Task / Rule Agent",
                    "2️⃣ Conversational Agent",
                    "3️⃣ Autonomous Agent",
                    "4️⃣ Multi-Agent System"
                ]
            )
        ),
        tooltip=["Year", "Role_Stage", "Count"]
    )
    .properties(height=420)
)

st.altair_chart(chart_b, use_container_width=True)

st.divider()

# =============================
# C. 전공·진로 연결
# =============================
st.subheader("C. AI 시대, 전공·진로는 어떻게 달라질까?")

role_map = pd.DataFrame({
    "AI Agent 단계": [
        "1️⃣ Task / Rule Agent",
        "2️⃣ Conversational Agent",
        "3️⃣ Autonomous Agent",
        "4️⃣ Multi-Agent System"
    ],
    "AI의 역할": [
        "정해진 작업 수행",
        "대화·응답·도움",
        "스스로 판단·행동",
        "여러 AI 간 협력"
    ],
    "사람에게 중요해지는 역량": [
        "문제 정의, 목표 설정",
        "공감, 설명, 소통",
        "판단 기준 설계, 윤리",
        "기획, 조정, 리더십"
    ],
    "연결되는 전공 예시": [
        "산업공학, 기획, 행정",
        "심리학, 교육, 커뮤니케이션",
        "법, 철학, 데이터 해석",
        "경영, 정책, 융합전공"
    ]
})

st.dataframe(role_map, use_container_width=True)

st.divider()

# =============================
# D. 학생 질문 기반 추천
# =============================
st.header("⑤ 학생 질문 기반 맞춤 전공·진로 힌트")

# -----------------------------
# 관심 영역 추론 함수 (누락 보완)
# -----------------------------
def infer_interest(question):
    q = question.lower()

    if re.search(r"코딩|개발|프로그래밍|ai|기술", q):
        return "기술·개발"
    if re.search(r"사람|심리|상담|교육", q):
        return "인간이해·심리"
    if re.search(r"기획|문제|전략", q):
        return "기획·문제해결"
    if re.search(r"윤리|법|사회|정책", q):
        return "판단·윤리·사회"
    if re.search(r"불안|모르겠|걱정", q):
        return "불안·자기효능"
    return "복합/탐색중"

interest_role_map = {
    "기술·개발": {
        "AI 시대 역할": "AI를 구현·개선하는 사람",
        "추천 전공": "컴퓨터공학, 인공지능, 데이터사이언스"
    },
    "인간이해·심리": {
        "AI 시대 역할": "AI와 사람을 연결하는 사람",
        "추천 전공": "심리학, 교육학, 상담, UX"
    },
    "기획·문제해결": {
        "AI 시대 역할": "AI가 풀 문제를 정의하는 사람",
        "추천 전공": "산업공학, 경영, 기획, 행정"
    },
    "판단·윤리·사회": {
        "AI 시대 역할": "AI의 판단 기준을 설계하는 사람",
        "추천 전공": "법, 철학, 사회과학, 정책"
    },
    "불안·자기효능": {
        "AI 시대 역할": "자기 탐색이 필요한 단계",
        "추천 전공": "융합전공, 자유전공"
    },
    "복합/탐색중": {
        "AI 시대 역할": "여러 역할을 탐색 중인 사람",
        "추천 전공": "융합전공, 복수전공, 연계전공"
    }
}

if st.session_state.questions:
    rec_data = []

    for q in st.session_state.questions:
        interest = infer_interest(q)
        role_info = interest_role_map[interest]

        rec_data.append({
            "학생 질문": q,
            "관심 영역": interest,
            "AI 시대 역할": role_info["AI 시대 역할"],
            "추천 전공 방향": role_info["추천 전공"]
        })

    rec_df = pd.DataFrame(rec_data)
    st.dataframe(rec_df, use_container_width=True)

else:
    st.info("아직 질문이 없어 맞춤 추천을 할 수 없습니다.")
