import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Agent Job Ecosystem", layout="wide")
st.title("🤖 AI 에이전트 일자리 생태계 변화 (연도별)")

# -----------------------------
# 데이터 로딩 함수
# -----------------------------
@st.cache_data
def load_ai_jobs(file):
    df = pd.read_csv(file, encoding="cp949")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

# -----------------------------
# 기본 데이터 로딩
# -----------------------------
df = load_ai_jobs("AI_Agents_Ecosystem_2026.csv")

# -----------------------------
# 추가 데이터 업로드
# -----------------------------
st.sidebar.header("📂 데이터 업로드")
uploaded = st.sidebar.file_uploader(
    "같은 형식의 CSV 업로드",
    type="csv"
)

if uploaded is not None:
    new_df = load_ai_jobs(uploaded)
    df = pd.concat([df, new_df], ignore_index=True)

# -----------------------------
# 연도 선택
# -----------------------------
years = sorted(df["Year"].dropna().unique().tolist())

selected_years = st.multiselect(
    "📅 비교할 연도 선택",
    options=years,
    default=years
)

df_year = df[df["Year"].isin(selected_years)]

# -----------------------------
# 1️⃣ 연도별 전체 규모 변화
# -----------------------------
st.subheader("📈 연도별 AI 에이전트 일자리 규모 변화")

year_count = (
    df_year
    .groupby("Year")
    .size()
    .reset_index(name="Count")
)

fig1 = px.line(
    year_count,
    x="Year",
    y="Count",
    markers=True,
    labels={"Count": "게시물 수"},
    title="연도별 AI 에이전트 관련 일자리/포스트 수"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 2️⃣ 연도 × Source 분포
# -----------------------------
st.subheader("🏷️ 연도별 Source 구성 변화")

source_year = (
    df_year
    .groupby(["Year", "Source"])
    .size()
    .reset_index(name="Count")
)

fig2 = px.bar(
    source_year,
    x="Year",
    y="Count",
    color="Source",
    barmode="stack",
    title="연도별 Source 구성"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 데이터 요약
# -----------------------------
with st.expander("🔍 데이터 요약"):
    st.write("행 수:", len(df_year))
    st.dataframe(df_year.head())
