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

if uploaded:
    new_df = load_ai_jobs(uploaded)
    df = pd.concat([df, new_df]).reset_index(drop=True)

# -----------------------------
# 연도 선택
# -----------------------------
years = sorted(df["Year"].dropna().unique())
selected_years = st.multiselect(
    "📅 비교할 연도 선택",
    years,
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

