import os
import re
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# OpenAI 안전 로딩
# -------------------------------------------------
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="AI Agent 트렌드 이해",
    layout="wide"
)

# -------------------------------------------------
# 헤더 영역
# -------------------------------------------------
st.title("🤖 AI Agent 트렌드 & 학생 질문 이해")
st.caption("고3·대학생 대상 진로·전공 탐색 특강용 대시보드")

st.markdown("""
> **AI는 무엇을 할 수 있느냐보다,  
> 우리는 AI와 함께 무엇을 할 것인가를 묻는 시대입니다.**
""")

st.divider()

# -------------------------------------------------
# 예시 데이터 (CSV 없이도 작동)
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
# 탭 구성
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 AI 트렌드",
    "❓ 학생 질문",
    "🧠 질문 분석",
    "🎯 진로 시사점"
])

# =================================================
# 📊 TAB 1. AI 트렌드
# =================================================
with tab1:
    st.subheader("AI Agent는 어떻게 진화하고 있을까?")

    col1, col2 = st.columns(2)

    with col1:
        type_counts = df.groupby("AI_Agent_유형").size().reset_index(name="등장 빈도")

        fig1 = px.bar(
            type_counts,
            x="AI_Agent_유형",
            y="등장 빈도",
            range_y=[0, 20],
            title="AI Agent 유형별 등장 빈도"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        trend = df.groupby(["연도","AI_Agent_유형"]).size().reset_index(name="건수")

        fig2 = px.line(
            trend,
            x="연도",
            y="건수",
            color="AI_Agent_유형",
            markers=True,
            range_y=[0, 20],
            title="연도별 AI Agent 트렌드 변화"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📘 학생 눈높이 해석 보기"):
        st.markdown("""
        - 초기 AI → **정해진 일을 대신 처리**
        - 최근 AI → **스스로 판단하고 협력**
        
        👉 앞으로 중요한 건  
        **코딩 실력만이 아니라,  
        AI에게 ‘무엇을 맡길지’ 설계하는 능력**
        """)

# =================================================
# ❓ TAB 2. 학생 질문
# =================================================
with tab2:
    st.subheader("익명 질문 남기기")

    if "questions" not in st.session_state:
        st.session_state["questions"] = []

    question = st.text_area(
        "궁금한 점을 자유롭게 적어주세요",
        placeholder="예: 문과도 AI 관련 진로를 선택할 수 있나요?"
    )

    if st.button("📥 질문 제출", use_container_width=True):
        if question.strip():
            st.session_state["questions"].append(question.strip())
            st.success("질문이 익명으로 저장되었습니다!")
        else:
            st.warning("질문을 입력해주세요.")

# =================================================
# 🧠 TAB 3. 질문 분석
# =================================================
with tab3:
    st.subheader("학생 질문에서 보이는 흐름")

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

    if st.session_state["questions"]:
        q_df = pd.DataFrame({
            "질문": st.session_state["questions"],
            "유형": [classify_question(q) for q in st.session_state["questions"]]
        })

        col1, col2 = st.columns(2)

        with col1:
            type_dist = q_df["유형"].value_counts().reset_index()
            type_dist.columns = ["질문 유형", "건수"]

            fig_type = px.bar(
                type_dist,
                x="질문 유형",
                y="건수",
                title="질문 유형 분포"
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            words = []
            for q in st.session_state["questions"]:
                words += re.findall(r"[가-힣]{2,}", q)

            word_freq = Counter(words).most_common(15)

            if word_freq:
                wc_df = pd.DataFrame(word_freq, columns=["키워드","빈도"])

                fig_wc = px.scatter(
                    wc_df,
                    x="키워드",
                    y="빈도",
                    size="빈도",
                    text="키워드",
                    title="학생 질문 키워드"
                )
                fig_wc.update_traces(textposition="top center")
                st.plotly_chart(fig_wc, use_container_width=True)
    else:
        st.info("아직 수집된 질문이 없습니다.")

# =================================================
# 🎯 TAB 4. 진로 시사점
# =================================================
with tab4:
    st.subheader("이 특강이 전하고 싶은 메시지")

    st.markdown("""
    ### ✔ 학생들에게
    - AI 시대의 진로는 **정답이 아니라 방향**
    - 전공은 출발점이지, 한계를 정하는 게 아님

    ### ✔ 교육자에게
    - 학생들은 이미 기술보다 **불안과 선택**을 묻고 있음
    - AI는 답변기가 아니라 **생각 촉진 도구**
    """)

    st.success("""
    🎓 오늘의 질문  
    👉 나는 AI를 **만드는 사람**인가  
    👉 AI와 **함께 일하는 사람**인가  
    👉 AI로 **문제를 해결하는 사람**인가
    """)
