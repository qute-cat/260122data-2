import os
from openai import OpenAI


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
# 3. AI Agent 유형별 빈도 (안정 방식)
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
    title="AI Agent 유형별 등장 빈도",
    range_y=[0, 20]
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# 4. 학생 대상 해석
# -------------------------------------------------
st.markdown("""
### 🧠 어떻게 해석하면 좋을까?

- **Task-oriented Agent**
  - 정해진 일을 대신 처리하는 AI
  - 예: 과제 보조, 일정 관리, 간단한 챗봇

- **Conversational Agent**
  - 사람과 대화를 잘하는 AI
  - 예: 상담 챗봇, 고객 응대 AI

📌 **핵심 메시지**
> 지금까지의 AI는  
> **사람을 대신해 일을 ‘처리해주는 도구’에 가까웠다**고 볼 수 있습니다.
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
    title="연도별 AI Agent 유형 변화",
    range_y=[0, 20]
)

st.plotly_chart(fig2, use_container_width=True)

st.header("④ AI가 설명해주는 그래프 해석")

# OpenAI 클라이언트
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 그래프 요약 데이터 생성
summary_text = ""
for _, row in trend.iterrows():
    summary_text += f"{row['연도']}년 {row['AI_Agent_유형']} {row['건수']}건\n"

prompt = f"""
다음은 연도별 AI Agent 유형 변화 데이터 요약입니다.

{summary_text}

이 데이터를 바탕으로
1) 고3 학생 눈높이로 이해할 수 있게 설명하고
2) 진로·전공 선택과 연결되는 핵심 메시지를 3줄 이내로 정리해줘
"""

if st.button("🤖 AI 해석 생성"):
    with st.spinner("AI가 그래프를 해석 중입니다..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 진로 특강을 돕는 교육 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

    st.success("AI 해석 결과")
    st.write(response.choices[0].message.content)



# -------------------------------------------------
# 6. 트렌드 해석
# -------------------------------------------------
st.markdown("""
### 🔍 변화의 방향은?

- 최근으로 갈수록:
  - **Autonomous Agent**
  - **Multi-Agent System**
  이 등장하고 있습니다.

📌 이는 AI가  
> **사람의 지시를 기다리는 존재 →  
> 스스로 판단하고 협력하는 존재**로 발전하고 있다는 신호입니다.
""")

# -------------------------------------------------
# 7. 진로·전공 탐색 시사점
# -------------------------------------------------
st.header("③ 진로·전공 선택에 주는 메시지")

st.markdown("""
### 🎯 앞으로 중요한 역량

✔ 단순 코딩 능력만으로는 부족  
✔ **AI가 무엇을 해야 하는지 정의하는 능력**이 중요

#### 연결 가능한 전공
- 인공지능 / 컴퓨터공학
- 심리학 / 인지과학
- 산업공학 / 서비스기획
- 교육 / 상담 / 정책

📌 **정리**
> AI 시대의 경쟁력은  
> **기술 + 인간 이해 + 문제 해결 능력**의 결합입니다.
""")

# -------------------------------------------------
# 8. 특강 마무리
# -------------------------------------------------
st.success("""
🎓 오늘의 질문

👉 나는 AI를 **만드는 사람**인가?  
👉 AI와 **함께 일하는 사람**인가?  
👉 AI를 **활용해 문제를 해결하는 사람**인가?

이 질문이 여러분의 전공 선택과 대학 생활의 출발점이 되길 바랍니다.
""")
