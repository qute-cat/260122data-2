import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("ai_agent_trend.csv")

df = load_data()

# -----------------------------
# 헤더
# -----------------------------
st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.markdown(
    """
    AI Agent는 단순한 **보조 도구**에서 출발해  
    **계획 → 자율 실행 → 다중 에이전트 협업** 단계로 빠르게 진화하고 있습니다.
    """
)

st.divider()

# -----------------------------
# 탭 구성
# -----------------------------
tab1, tab2 = st.tabs([
    "📈 연도별 트렌드 변화",
    "🧠 역할 진화 단계 시각화"
])

# ======================================================
# TAB 1: 연도별 트렌드 변화 (가독성 개선)
# ======================================================
with tab1:
    st.subheader("📈 연도별 AI Agent 트렌드 변화")

    long_df = df.melt(
        id_vars="year",
        value_vars=[
            "Assistant",
            "Planner",
            "Autonomous-Agent",
            "Multi-Agent"
        ],
        var_name="Agent Type",
        value_name="Index"
    )

    fig1 = px.line(
        long_df,
        x="year",
        y="Index",
        color="Agent Type",
        markers=True,
        title="Evolution of Core AI Agent Roles"
    )

    fig1.update_layout(
        xaxis_title="Year",
        yaxis_title="Mentions / Adoption Index",
        legend_title="Agent Type",
        hovermode="x unified"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info(
        "👉 2022년 이후부터 **자율성(Autonomous)** 과 "
        "**협업(Multi-Agent)** 중심으로 급격한 변화가 나타납니다."
    )

# ======================================================
# TAB 2: 역할 진화 단계 (누적 영역 그래프)
# ======================================================
with tab2:
    st.subheader("🧠 AI Agent 역할 진화 단계")

    stack_df = df.melt(
        id_vars="year",
        var_name="Agent Type",
        value_name="Index"
    )

    fig2 = px.area(
        stack_df,
        x="year",
        y="Index",
        color="Agent Type",
        title="Shift from Assistive AI to Autonomous & Multi-Agent Systems"
    )

    fig2.update_layout(
        xaxis_title="Year",
        yaxis_title="Relative Importance",
        hovermode="x unified"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.success(
        "✔️ AI는 더 이상 혼자 똑똑한 존재가 아니라, "
        "**함께 사고하고 협업하는 시스템**으로 진화하고 있습니다."
    )

# -----------------------------
# 푸터
# -----------------------------
st.divider()
st.caption("© AI Agent Trend Visualization | Education & Lecture Use")
