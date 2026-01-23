import os
import re
from collections import Counter

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
# 페이지 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Agent 트렌드 이해", layout="wide")

st.title("🤖 AI Agent 유형별 트렌드 이해")
st.subheader("고3·대학생 대상 진로·전공 탐색 특강")

st.markdown("""
이 대시는 **AI Agent가 어떤 역할로 발전하고 있는지**를 살펴보고,  
학생들의 **질문과 관심사**를 함께 이해하기 위한 특강용 도구입니다.
""")

# -------------------------------------------------
# 예시 데이터
# -------------------------------------------------
df = pd.DataFrame({
    "연도": [2020,2020,2021,2021,2022,2022,2023,2023,2024,2024],
    "AI_Agent_유형": [
        "Task-oriented Agent","Conversational Agent",
        "Task-oriented Agent","Conversational Agent",
        "Conversational Agent","Autonomous Agent",
        "Autonomous Agent","Multi-Agent System",
        "Multi-Agent System","Autonomous Agent"
    ]
})

# -------------------------------------------------
# 유형별 빈도
# -------------------------------------------------
st.header("① AI Agent 유형별 등장 빈도")

type_counts = df.groupby("AI_Agent_유형").size().reset_index(name="등장 빈도")

fig1 = px.bar(
    type_counts,
    x="AI_Agent_유형",
    y="등장 빈도",
    range_y=[0, 20],
    title="AI Agent 유형별 등장 빈도"
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# 연도별 트렌드
# -------------------------------------------------
st.header("② 연도별 AI Agent 트렌드 변화")

trend = df.groupby(["연도","AI_Agent_유형"]).size().reset_index(name="건수")

fig2 = px.line(
    trend,
    x="연도",
    y="건수",
    color="AI_Agent_유형",
    markers=True,
    range_y=[0, 20],
    title="연도별 AI Agent 유형 변화"
)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# OpenAI 클라이언트
# -------------------------------------------------
client = None
if openai_available and os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------
# 학생 질문 입력 (익명 수집)
# -------------------------------------------------
st.header("③ 학생 질문 (익명)")

if "questions" not in st.session_state:
    st.session_state["questions"] = []

question = st.text_area(
    "✏️ 궁금한 점을 자유롭게 적어주세요 (익명)",
    placeholder="예: 문과도 AI 관련 진로를 가질 수 있나요?"
)

if st.button("📥 질문 제출"):
    if question.strip():
        st.session_state["questions"].append(question.strip())
        st.success("질문이 익명으로 저장되었습니다!")
    else:
        st.warning("질문을 입력해주세요.")

# -------------------------------------------------
# 질문 유형 자동 분류 (규칙 기반)
# -------------------------------------------------
def classify_question(text):
    text = text.lower()
    if re.search("전공|학과|과|컴공|심리", text):
        return "전공/학과"
    if re.search("공부|역량|준비|수학|코딩", text):
        return "역량/공부법"
    if re.search("직업|취업|일자리|커리어", text):
        return "진로/직업"
    if re.search("불안|걱정|괜찮|못할", text):
        return "불안/고민"
    return "기타"

# -------------------------------------------------
# 질문 분석 결과
# -------------------------------------------------
st.header("④ 학생 질문 분석 결과")

if st.session_state["questions"]:
    q_df = pd.DataFrame({
        "질문": st.session_state["questions"],
        "유형": [classify_question(q) for q in st.session_state["questions"]]
    })

    # 유형 분포
    type_dist = q_df["유형"].value_counts().reset_index()
    type_dist.columns = ["질문 유형", "건수"]

    fig_type = px.bar(
        type_dist,
        x="질문 유형",
        y="건수",
        title="학생 질문 유형 분포"
    )
    st.plotly_chart(fig_type, use_container_width=True)

    # -------------------------------------------------
    # 워드클라우드 대체 시각화 (빈도 기반)
    # -------------------------------------------------
    st.subheader("🧠 질문 키워드 클라우드")

    words = []
    for q in st.session_state["questions"]:
        words += re.findall(r"[가-힣]{2,}", q)

    word_freq = Counter(words).most_common(20)

    if word_freq:
        wc_df = pd.DataFrame(word_freq, columns=["키워드","빈도"])

        fig_wc = px.scatter(
            wc_df,
            x="키워드",
            y="빈도",
            size="빈도",
            text="키워드",
            title="학생 질문 키워드 클라우드"
        )
        fig_wc.update_traces(textposition="top center")
        st.plotly_chart(fig_wc, use_container_width=True)
    else:
        st.info("아직 키워드가 충분하지 않습니다.")

else:
    st.info("아직 수집된 질문이 없습니다.")

# -------------------------------------------------
# 마무리 메시지
# -------------------------------------------------
st.success("""
🎯 이 분석이 의미하는 것

- 학생들의 질문은 **이미 진로·전공 고민 중심**
- 기술보다 **불안·가능성·선택**에 더 관심
- 특강의 역할은  
  👉 정답 제시 ❌  
  👉 질문을 구조화해주는 것 ⭕

이제 AI는 설명 도구가 아니라  
**학생 생각을 꺼내주는 도구**입니다.
""")
