import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import re

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")

# -----------------------------
# Session State 초기화 (KeyError 방지)
# -----------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "votes" not in st.session_state:
    st.session_state.votes = {}

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

# -----------------------------
# 데이터 로드
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

# -----------------------------
# A. 연도별 AI Agent 트렌드
# -----------------------------
yearly_trend = (
    df.dropna(subset=["Year"])
    .groupby("Year")
    .size()
    .reset_index(name="Count")
)

all_years = pd.DataFrame({
    "Year": range(int(yearly_trend["Year"].min()), int(yearly_trend["Year"].max()) + 1)
})

yearly_trend = all_years.merge(
    yearly_trend, on="Year", how="left"
).fillna(0)

st.subheader("📈 연도별 AI Agent 트렌드 변화")

chart = (
    alt.Chart(yearly_trend)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        tooltip=["Year", "Count"]
    )
    .properties(height=380)
)

st.altair_chart(chart, use_container_width=True)

st.caption(
    "AI Agent 논의는 자동화 도구 → 협업 파트너 → 자율적 실행 주체로 진화하고 있습니다."
)

# -----------------------------
# B. AI Agent 역할 진화 설명
# -----------------------------
st.subheader("🧠 AI Agent 역할의 진화")

st.markdown("""
AI Agent는 한 번에 완성된 존재가 아니라 **역할이 단계적으로 확장**되어 왔습니다.

**① 도구형 Agent**  
- 명령 수행 중심 (검색, 요약)  
- 인간 지시 없이는 행동 불가  

**② 보조형 Agent**  
- 추천, 초안, 비교 제안  
- 인간의 판단을 보조  

**③ 협업형 Agent**  
- 인간과 목표 공유  
- 여러 Agent 간 역할 분담  

**④ 자율형 Agent**  
- 목표 설정 → 실행 → 평가  
- 서비스·조직 단위로 작동
""")

# -----------------------------
# C. 질문 입력 & 투표
# -----------------------------
st.subheader("❓ 지금 떠오른 질문을 남겨보세요")

new_q = st.text_input("질문을 입력하세요 (짧게)")

if st.button("질문 등록"):
    if new_q.strip():
        st.session_state.questions.append(new_q.strip())
        st.session_state.votes[new_q.strip()] = 0

if st.session_state.questions:
    st.markdown("### 📊 질문 투표")
    for q in st.session_state.questions:
        col1, col2 = st.columns([5, 1])
        col1.write(q)
        if col2.button("👍", key=q):
            st.session_state.votes[q] += 1
            st.session_state.selected_question = q

# -----------------------------
# D. 키워드 빈도 시각화 (워드클라우드 대체)
# -----------------------------
st.subheader("☁️ 질문 핵심 키워드")

if st.session_state.questions:
    stopwords = {"AI", "에이전트", "어떻게", "왜", "무엇", "할까", "인가"}
    words = []

    for q in st.session_state.questions:
        cleaned = re.sub(r"[^\w\s]", "", q)
        for w in cleaned.split():
            if len(w) > 1 and w not in stopwords:
                words.append(w)

    counter = Counter(words)
    keyword_df = pd.DataFrame(counter.most_common(15), columns=["Keyword", "Count"])

    keyword_chart = (
        alt.Chart(keyword_df)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title="빈도"),
            y=alt.Y("Keyword:N", sort="-x", title="키워드"),
            tooltip=["Keyword", "Count"]
        )
        .properties(height=400)
    )

    st.altair_chart(keyword_chart, use_container_width=True)

# -----------------------------
# D-1. 선택 질문 AI 해설
# -----------------------------
if st.session_state.selected_question:
    st.subheader("🤖 AI의 해설")

    st.markdown(f"""
**선택된 질문**  
> *{st.session_state.selected_question}*

**AI 해설**  
이 질문은 AI Agent의 진화가  
단순한 기술 문제가 아니라 **인간의 선택과 역할 재정의 문제**임을 보여줍니다.

앞으로 AI는  
👉 *결정을 대신하는 존재*가 아니라  
👉 *더 나은 결정을 가능하게 하는 파트너*로 발전할 가능성이 큽니다.
""")
