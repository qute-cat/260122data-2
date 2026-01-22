# main.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import random

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent 유형별 빈도 / 트렌드",
    layout="wide"
)

st.title("🤖 AI Agent 유형별 빈도 및 트렌드 시각화")

# -----------------------------
# 2. 내부 데이터 생성 (CSV 제거)
# -----------------------------
@st.cache_data
def generate_sample_data(n=300):
    agent_types = [
        "Task-oriented Agent",
        "Conversational Agent",
        "Autonomous Agent",
        "Multi-Agent System",
        "Recommender Agent"
    ]

    years = list(range(2019, datetime.now().year + 1))

    data = {
        "agent_type": [random.choice(agent_types) for _ in range(n)],
        "year": [random.choice(years) for _ in range(n)]
    }

    return pd.DataFrame(data)

df = generate_sample_data()

# -----------------------------
# 3. 사이드바 필터
# -----------------------------
st.sidebar.header("🔎 필터")

selected_years = st.sidebar.multiselect(
    "연도 선택",
    sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

filtered_df = df[df["year"].isin(selected_years)]

# -----------------------------
# 4. AI Agent 유형별 빈도
# -----------------------------
st.subheader("📊 AI Agent 유형별 전체 빈도")

agent_freq = (
    filtered_df
    .groupby("agent_type")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

bar_chart = alt.Chart(agent_freq).mark_bar().encode(
    x=alt.X("agent_type:N", sort="-y", title="AI Agent 유형"),
    y=alt.Y("count:Q", title="빈도"),
    tooltip=["agent_type", "count"]
).properties(
    height=400
)

st.altair_chart(bar_chart, use_container_width=True)

# -----------------------------
# 5. 연도별 트렌드
# -----------------------------
st.subheader("📈 연도별 AI Agent 유형 트렌드")

trend_df = (
    filtered_df
    .groupby(["year", "agent_type"])
    .size()
    .reset_index(name="count")
)

line_chart = alt.Chart(trend_df).mark_line(point=True).encode(
    x=alt.X("year:O", title="연도"),
    y=alt.Y("count:Q", title="빈도"),
    color=alt.Color("agent_type:N", title="Agent 유형"),
    tooltip=["year", "agent_type", "count"]
).properties(
    height=450
)

st.altair_chart(line_chart, use_container_width=True)

# -----------------------------
# 6. 원본 데이터 확인
# -----------------------------
with st.expander("📄 생성된 원본 데이터 보기"):
    st.dataframe(filtered_df.reset_index(drop=True))
