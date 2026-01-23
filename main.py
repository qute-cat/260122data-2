import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 기본 설정
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
# 헤더 영역
# -----------------------------
st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.markdown(
    """
    > AI Agent는 단순한 **보조 역할**에서 출발해  
    > **계획 → 자율 실행 → 다중 에이전트 협업** 단계로 빠르게 진화하고 있습니다.
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
# TAB 1: 연도별 트렌드 변화 (가독성 개선 선 그래프)
# ======================================================
with tab1:
    st.subheader("📈 연도별 AI Agent 트렌드 변화 (핵심 유형)")

    st.markdown(
        """
        - **Assistant**: 질문 응답, 정보 제공 중심  
        - **Planner**: 목표 설정과 작업 분해  
        - **Autonomous Agent**: 스스로 판단하고 실행  
        - **Multi-Agent**: 여러 Agent 간 협업
        """
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    core_agents = [
        "Assistant",
        "Planner",
        "Autonomous-Agent",
        "Multi-Agent"
    ]

    for agent in core_agents:
        ax.plot(
            df["year"],
            df[agent],
            marker="o",
            linewidth=2,
            label=agent
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Mentions / Adoption Index")
    ax.set_title("Evolution of Core AI Agent Roles")
    ax.set_xticks(df["year"])
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    st.pyplot(fig)

    st.info(
        "👉 2022년 이후부터 **자율성(Autonomous)** 과 "
        "**협업(Multi-Agent)** 중심으로 급격한 변화가 나타납니다."
    )

# ======================================================
# TAB 2: AI Agent 역할 진화 단계 (누적 영역 그래프)
# ======================================================
with tab2:
    st.subheader("🧠 AI Agent 역할 진화 단계 시각화")

    st.markdown(
        """
        이 그래프는 **AI Agent의 역할 중심이 어떻게 이동했는지**를 보여줍니다.
        
        **보조 → 도구 활용 → 계획 → 자율 → 협업**
        """
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))

    ax2.stackplot(
        df["year"],
        df["Assistant"],
        df["Tool-User"],
        df["Planner"],
        df["Autonomous-Agent"],
        df["Multi-Agent"],
        labels=df.columns[1:],
        alpha=0.85
    )

    ax2.set_xlabel("Year")
    ax2.set_ylabel("Relative Importance")
    ax2.set_title(
        "Shift from Assistive AI to Autonomous & Multi-Agent Systems"
    )
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.2)

    st.pyplot(fig2)

    st.success(
        "✔️ 최근 AI Agent는 **혼자 똑똑한 존재**가 아니라, "
        "**함께 일하는 시스템**으로 진화하고 있습니다."
    )

# -----------------------------
# 푸터
# -----------------------------
st.divider()
st.caption(
    "© AI Agent Trend Visualization | Educational & Research Use"
)
