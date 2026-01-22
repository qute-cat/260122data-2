import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import plotly.express as px

# =========================
# 1. 기본 설정
# =========================
st.set_page_config(
    page_title="AI Agents Ecosystem Analysis",
    layout="wide"
)

st.title("📊 AI 에이전트 일자리 생태계 연도·국가 분석")
st.markdown(
    """
    이 웹앱은 **AI 에이전트 관련 일자리·프로젝트·기술 기회 데이터**를 기반으로  
    **연도별 변화**와 **도메인 기반 국가 생태계 분포**를 분석합니다.
    """
)

# =========================
# 2. 데이터 로딩
# =========================
@st.cache_data
def load_csv(file):
    return pd.read_csv(file, encoding="cp949")

# 기본 데이터
BASE_FILE = "AI_Agents_Ecosystem_2026.csv"
df_list = []

try:
    base_df = load_csv(BASE_FILE)
    df_list.append(base_df)
except:
    st.error("기본 데이터 파일을 불러오지 못했습니다.")

# 추가 데이터 업로드
uploaded_files = st.file_uploader(
    "📂 동일한 형식의 CSV 파일 추가 업로드 (선택)",
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        df_list.append(load_csv(file))

df = pd.concat(df_list, ignore_index=True)

# =========================
# 3. 도메인 → 국가 분류
# =========================
TLD_COUNTRY_MAP = {
    "kr": "South Korea",
    "jp": "Japan",
    "cn": "China",
    "tw": "Taiwan",
    "sg": "Singapore",
    "hk": "Hong Kong",
    "de": "Germany",
    "fr": "France",
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "nl": "Netherlands",
    "ca": "Canada",
    "au": "Australia",
    "in": "India",
    "br": "Brazil"
}

def extract_domain(url):
    if pd.isna(url):
        return None
    try:
        return urlparse(url).netloc.replace("www.", "").lower()
    except:
        return None

def infer_country(domain):
    if domain is None:
        return "Unknown"
    tld = domain.split(".")[-1]
    if tld in TLD_COUNTRY_MAP:
        return TLD_COUNTRY_MAP[tld]
    if tld in ["com", "io", "ai", "org", "net"]:
        return "Global"
    return "Other"

df["domain"] = df["Link"].apply(extract_domain)
df["country"] = df["domain"].apply(infer_country)

# =========================
# 4. 연도 추출
# =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Year"] = df["Date"].dt.year

# =========================
# 5. 연도별 × 국가별 집계
# =========================
year_country = (
    df.groupby(["Year", "country"])
      .size()
      .reset_index(name="count")
)

# =========================
# 6. 인터랙티브 시각화
# =========================
st.subheader("📈 연도별 AI 에이전트 생태계 국가 분포")

fig = px.line(
    year_country,
    x="Year",
    y="count",
    color="country",
    markers=True,
    title="Yearly Distribution of AI Agent Ecosystem by Country (Domain-based)"
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Opportunities",
    legend_title="Country (Inferred from Domain)"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 7. 해석 자동 생성
# =========================
st.subheader("🧠 분석 해석")

latest_year = year_country["Year"].max()
latest_data = year_country[year_country["Year"] == latest_year]

global_ratio = (
    latest_data.loc[latest_data["country"] == "Global", "count"].sum()
    / latest_data["]()_
