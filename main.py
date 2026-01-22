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

st.markdown("""
이 웹앱은 **AI 에이전트 관련 일자리·프로젝트·기술 기회 데이터**를 기반으로  
연도별 변화와 **도메인 기반 국가 생태계 분포**를 분석합니다.
""")

# =========================
# 2. 데이터 로딩
# =========================
@st.cache_data
def load_csv(file):
    return pd.read_csv(file, encoding="cp949")

BASE_FILE = "AI_Agents_Ecosystem_2026.csv"
df_list = []

try:
    base_df = load_csv(BASE_FILE)
    df_list.append(base_df)
except Exception as e:
    st.error("기본 데이터 파일을 불러오지 못했습니다.")

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
# 5. 연도 × 국가 집계
# =========================
year_country = (
    df.groupby(["Year", "country"])
      .size()
      .reset_index(name="count")
)

# =========================
# 6. Plotly 시각화
# =========================
st.subheader("📈 연도별 AI 에이전트 생태계 국가 분포")

fig = px.line(
    year_country,
    x="Year",
    y="count",
    color="country",
    markers=True,
    title="Yearly Distribution of AI Agent Ecosystem (Domain-based Country)"
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Opportunities",
    legend_title="Country"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 7. 해석 자동 생성
# =========================
st.subheader("🧠 분석 해석")

latest_year = int(year_country["Year"].max())
latest_data = year_country[year_country["Year"] == latest_year]

total_count = latest_data["count"].sum()
global_count = latest_data.loc[
    latest_data["country"] == "Global", "count"
].sum()

global_ratio = (global_count / total_count) * 100 if total_count > 0 else 0

st.markdown(f"""
### 🔎 {latest_year}년 기준 해석

- AI 에이전트 관련 기회의 **{global_ratio:.1f}%**가  
  특정 국가가 아닌 **글로벌 도메인(Global)**을 기반으로 생성되고 있습니다.
- 이는 AI 에이전트 일자리 생태계가  
  **국가 중심 구조에서 글로벌·원격·플랫폼 중심 구조로 이동**하고 있음을 시사합니다.
""")

non_global = latest_data[latest_data["country"] != "Global"]

if not non_global.empty:
    top_row = non_global.sort_values("count", ascending=False).iloc[0]
    st.markdown(f"""
- 글로벌을 제외하면 **{top_row['country']}** 기반 도메인이 가장 높은 비중을 차지합니다.
- 이는 해당 국가가 **AI 에이전트 기술·일자리 생태계의 주요 거점**으로 기능하고 있음을 의미합니다.
""")

st.markdown("""
📌 **해석 유의사항**  
본 분석은 고용 위치가 아니라,  
**AI 에이전트 기회가 생성·공유되는 디지털 생태계의 기반 국가**를 추정한 결과입니다.
""")
