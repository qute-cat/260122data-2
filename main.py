import os

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# OpenAI 라이브러리 안전 처리
# -------------------------------------------------
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

# -------------------------------------------------
# 1. 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="AI Agent 트렌드 이해",
    layout="wide"
)

st.title("🤖 AI Agent 유형별 트렌드 이해")
st.subheader("고3·대학생 대상 진로·전공 탐색 특강")

st.markdown(
    """
이 대시는 **AI Agent가 어떤 역할로 발전하고 있는지**를 살펴보고,  
앞으로 **어떤 전공과 역량이 중요해질지** 생각해보기 위한 특강 자료입니다.
"""
)

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
    title="AI Agent 유형별 등장 빈도",
    range_y=[0, 20]
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# 4. 기본 해석
# -------------------------------------------------
st.markdown(
    """
### 🧠 어떻게 해석하면 좋을까?

- **Task-oriented Agent**  
  정해진 일을 대신 처리하는 AI (과제 보조, 일정 관리)

- **Conversational Agent**  
  사람과 대화를 잘하는 AI (상담, 고객 응대)

📌 **핵심 메시지**  
> 지금까지의 AI는  
> **사람을 돕는 도구 중심**으로 발전해 왔습니다.
"""
)

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

# -------------------------------------------------
# 6. OpenAI 클라이언트 준비
# -------------------------------------------------
client = None
if openai_available and os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------
# 7. AI 그래프 해석 버튼
# -------------------------------------------------
st.header("③ AI가 설명해주는 그래프 해석")

if not openai_available:
    st.warning("⚠️ AI 해석 기능은 현재 환경에서 사용할 수 없습니다.")
    st.info("openai 라이브러리가 설치된 환경에서 사용 가능합니다.")

elif not os.getenv("OPENAI_API_KEY"):
    st.warning("⚠️ OpenAI API Key가 설정되어 있지 않습니다.")
    st.info("Streamlit Secrets에 OPENAI_API_KEY를 추가해주세요.")

else:
    if st.button("🤖 AI로 그래프 해석 보기"):
        with st.spinner("AI가 그래프를 해석 중입니다..."):
            summary_text = ""
            for _, row in trend.iterrows():
                summary_text += f"{row['연도']}년 {row['AI_Agent_유형']} {row['건수']}건\n"

            prompt = f"""
다음은 연도별 AI Agent 유형 변화 데이터 요약입니다.

{summary_text}

이 데이터를 바탕으로
1) 고3 학생도 이해할 수 있게 설명하고
2) 진로·전공 선택과 연결되는 핵심 메시지를 3줄 이내로 정리해줘
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 고등학생과 대학생을 위한 진로 특강 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

        st.success("AI 해석 결과")
        st.write(response.choices[0].message.content)

# -------------------------------------------------
# 8. ⭐ 학생 질문 입력 → AI 응답 ⭐
# -------------------------------------------------
st.header("④ 학생 질문 → AI 답변")

st.markdown(
    """
그래프와 설명을 보고 **궁금해진 점을 자유롭게 질문해보세요.**  
(예: *이런 AI는 어떤 전공이 유리한가요?*, *문과도 가능한가요?*)
"""
)

student_question = st.text_area(
    "✏️ 질문을 입력하세요",
    placeholder="예: AI Agent 시대에 문과 학생은 어떤 준비를 하면 좋을까요?"
)

if openai_available and os.getenv("OPENAI_API_KEY"):
    if st.button("🙋 AI에게 질문하기") and student_question.strip():
        with st.spinner("AI가 질문에 답변 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 고3·대학생을 대상으로 진로와 전공을 설명하는 친절한 멘토야. "
                            "전문용어는 풀어서 설명하고, 불안감을 줄이는 방향으로 답변해."
                        )
                    },
                    {"role": "user", "content": student_question}
                ],
                temperature=0.5
            )

        st.success("AI 답변")
        st.write(response.choices[0].message.content)

elif student_question.strip():
    st.info("💡 AI 답변 기능을 사용하려면 OpenAI API Key 설정이 필요합니다.")

# -------------------------------------------------
# 9. 진로·전공 시사점
# -------------------------------------------------
st.header("⑤ 진로·전공 선택에 주는 메시지")

st.markdown(
    """
### 🎯 앞으로 중요한 역량

✔ 단순 코딩만 잘하는 사람 ❌  
✔ **AI에게 일을 시킬 수 있는 사람 ⭕**

#### 연결 전공 예시
- 인공지능 / 컴퓨터공학
- 심리학 / 인지과학
- 산업공학 / 서비스기획
- 교육 / 상담 / 정책

📌 **정리**  
> AI 시대의 경쟁력은  
> **기술 + 인간 이해 + 문제 정의 능력**입니다.
"""
)

# -------------------------------------------------
# 10. 특강 마무리
# -------------------------------------------------
st.success(
    """
🎓 오늘의 질문

👉 나는 AI를 **만드는 사람**인가?  
👉 AI와 **함께 일하는 사람**인가?  
👉 AI를 **활용해 문제를 해결하는 사람**인가?

이 질문이 여러분의 전공 선택과 대학 생활의 출발점이 되길 바랍니다.
"""
)
