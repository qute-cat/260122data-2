import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# 1. 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="AI Agent 트렌드 이해",
    layout="wide"
)

st.title("🤖 AI Agent 유형별 트렌드 이해")
st.subheader("고3·대학생 대상 진로·전공 탐색 특강")

st.markdown("""
이 대시는 **AI Agent가 어떤 역할로 발전하고 있는지**를 살펴보고,  
앞으로 **어떤 전공과 역량이 중요해질지** 생각해보기 위한 특강 자료입니다.
""")

# -------------------------------------------------
# 2. 예시 데이터 (CSV 사용 ❌)
# -------------------------------------------------
df = pd.DataFrame({
    "연도": [
        2020, 2020,
        2021, 2021,
        2022, 2022,
        2023, 2023,
        2024, 2024
    ],
    "AI_Agent_유형": [
        "Task-oriented Agent", "Conversational Agent",
        "Task-oriented Agent", "Conversational Agent",
        "Conversational Agent", "Autonomous Agent",
        "Autonomous Agent", "Multi-Agent System",
        "Multi-Agent System", "Autonomous Agent"
    ]
})

# -------------------------------------------------
# 3. AI Agent 유형별 빈도
# -------------------------------------------------
st.header("① AI Agent 유형별 등장 빈도")

type_counts = (
    df
    .groupby("AI_Agent_유형")
    .size()
    .reset_index(name="등장 빈도")
)

fig1 = px.bar(
    type_counts,
    x="AI_Agent_유형",
    y="등장 빈도",
    title="AI Agent 유형별 등장 빈도"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# 4. 학생 대상 해석
# -------------------------------------------------
st.markdown("""
### 🧠 어떻게 해석하면 좋을까?

- **Task-oriented Agent**
  - 정해진 일을 대신 처리하는 AI
  - 예: 과제 보조, 일정 관리, 단순 자동화

- **Conversational Agent**
  - 사람과 대화를 잘하는 AI
  - 예: 상담 챗봇, 고객 응대 AI

📌 **핵심 메시지**  
> 지금까지의 AI는  
> **사람을 돕는 ‘도구’의 역할이 중심**이었습니다.
""")

# -------------------------------------------------
# 5. 연도별 트렌드 변화
# -------------------------------------------------
st.header("② 연도별 AI Agent 트렌드 변화")

trend = (
    df
    .groupby(["연도", "AI_Agent_유형"])
    .size()
    .reset_index(name="건수")
)

fig2 = px.line(
    trend,
    x="연도",
    y="건수",
    color="AI_Agent_유형",
    markers=True,
    title="연도별 AI Agent 유형 변화"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# 6. 그래프 종합 해석 (특강용 고정 텍스트)
# -------------------------------------------------
st.header("③ 그래프 종합 해석 (특강용)")

st.info("""
### 📈 이 그래프가 말해주는 변화

- 초기 AI → **정해진 일을 잘하는 AI**
- 최근 AI → **스스로 판단하고 협력하는 AI**

📌 즉,
> AI는 이제  
> **‘시키는 대로 하는 존재’가 아니라  
> ‘함께 일하는 파트너’로 진화 중**입니다.
""")

# -------------------------------------------------
# 7. 진로·전공 탐색 시사점
# -------------------------------------------------
st.header("④ 진로·전공 선택에 주는 메시지")

st.markdown("""
### 🎯 앞으로 중요한 역량

✔ 단순 기술 습득 ❌  
✔ **AI에게 일을 맡기고 설계하는 능력 ⭕**

#### 연결 가능한 전공
- 인공지능 / 컴퓨터공학
- 심리학 / 인지과
