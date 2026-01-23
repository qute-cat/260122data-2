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

st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.subheader("고3·대학생 대상 진로·전공 탐색 특강")

st.markdown("""
이 대시는 **AI Agent의 역할 변화**를 중심으로  
기술 발전이 **전공·진로 선택에 어떤 의미를 갖는지** 함께 생각해보기 위한 자료입니다.
""")

# -------------------------------------------------
# 탭 구성
# -------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 AI Agent 진화 트렌드",
    "❓ 학생 질문 & 분석",
    "🎯 진로·전공 시사점"
])

# =================================================
# Tab 1. AI Agent 진화 트렌드
# =================================================
with tab1:
    st.header("① AI Agent 유형별 등장 빈도")

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
    st.header("③ AI Agent 역할 진화 단계 (Evolution Map)")

    evolution_df = pd.DataFrame({
        "연도": [2020, 2021, 2022, 2023, 2024],
        "역할_단계": [1, 2, 2, 3, 4],
        "역할_설명": [
            "도구 (Tool)",
            "보조자 (Assistant)",
            "대화자 (Conversational)",
            "자율 판단자 (Autonomous)",
            "협력자 (Multi-Agent)"
        ]
    })

    fig3 = px.scatter(
        evolution_df,
        x="연도",
        y="역할_단계",
        size=[20]*5,
        text="역할_설명",
        range_y=[0, 5],
        title="AI Agent의 역할 진화 단계"
    )

    fig3.update_traces(textposition="top center")
    fig3.update_yaxes(
        tickvals=[1,2,3,4],
        ticktext=[
            "도구",
            "보조자",
            "자율 판단자",
            "협력자"
        ]
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
**해석 포인트**

- AI는 단순한 **기능 향상**이 아니라  
  👉 **역할 자체가 바뀌고 있음**
- 이제 AI는  
  ❌ “말 잘하는 프로그램”  
  ✅ “함께 일하는 존재”
    """)

# =================================================
# Tab 2. 학생 질문 & 분석
# =================================================
with tab2:
    st.header("④ 학생 질문 (익명 수집)")

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

    st.header("⑤ 질문 분석 결과")

    if st.session_state["questions"]:
        q_df = pd.DataFrame({
            "질문": st.session_state["questions"],
            "유형": [classify_question(q) for q in st.session_state["questions"]]
        })

        type_dist = q_df["유형"].value_counts().reset_index()
        type_dist.columns = ["질문 유형", "건수"]

        fig_q = px.bar(
            type_dist,
            x="질문 유형",
            y="건수",
            title="학생 질문 유형 분포"
        )
        st.plotly_chart(fig_q, use_container_width=True)

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
                text="키워드"
            )
            fig_wc.update_traces(textposition="top center")
            st.plotly_chart(fig_wc, use_container_width=True)
    else:
        st.info("아직 수집된 질문이 없습니다.")

# =================================================
# Tab 3. 진로·전공 시사점
# =================================================
with tab3:
    st.header("⑥ 진로·전공 선택에 주는 메시지")

    st.markdown("""
### 앞으로 중요한 역량은?

- ✔ 코딩 자체보다 **문제 정의 능력**
- ✔ AI에게 **무엇을 시킬지 설계하는 능력**
- ✔ 기술 + 인간 이해의 결합

### 연결 가능한 전공
- 인공지능 / 컴퓨터공학
- 심리학 / 인지과학
- 산업공학 / 서비스기획
- 교육 / 상담 / 정책

> AI 시대의 경쟁력은  
> **AI를 이기는 것 ❌  
> AI와 일하는 법을 아는 것 ⭕**
    """)

    st.success("""
🎓 오늘의 질문

나는  
- AI를 만드는 사람인가?
- AI와 함께 일하는 사람인가?
- AI를 활용해 문제를 해결하는 사람인가?

이 질문이 여러분의 전공 선택의 출발점이 되길 바랍니다.
""")
