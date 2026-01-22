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
연도별 변화와 **도메인 기반 국가 생태계 구조**를 분석합니다.
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
except:
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
# 6. 그래프 ① 연도별 국가 분포
# =========================
st.subheader("📈 연도별 AI 에이전트 생태계 국가 분포")

max_y = max(20, year_country["count"].max() + 1)

fig1 = px.line(
    year_country,
    x="Year",
    y="count",
    color="country",
    markers=True,
    title="Yearly Distribution by Country (Domain-based)"
)

fig1.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Opportunities",
    legend_title="Country",
    yaxis=dict(range=[0, max_y], dtick=1)
)

st.plotly_chart(fig1, use_container_width=True)

# =========================
# 7. 그래프 ② Global vs Country 비교
# =========================
st.subheader("🌍 Global vs 국가 기반 생태계 비교")

df["ecosystem_type"] = df["country"].apply(
    lambda x: "Global" if x == "Global" else "Country-based"
)

year_ecosystem = (
    df.groupby(["Year", "ecosystem_type"])
      .size()
      .reset_index(name="count")
)

fig2 = px.bar(
    year_ecosystem,
    x="Year",
    y="count",
    color="ecosystem_type",
    barmode="stack",
    title="Global vs Country-based AI Agent Ecosystem (Yearly)"
)

fig2.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Opportunities",
    legend_title="Ecosystem Type"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# 8. 해석 자동 생성
# =========================
st.subheader("🧠 분석 해석")

latest_year = int(df["Year"].max())
latest = df[df["Year"] == latest_year]

global_count = (latest["ecosystem_type"] == "Global").sum()
country_count = (latest["ecosystem_type"] == "Country-based").sum()
total = global_count + country_count

global_ratio = (global_count / total) * 100 if total > 0 else 0

st.markdown(f"""
### 🔎 {latest_year}년 기준 종합 해석

- AI 에이전트 관련 기회의 **{global_ratio:.1f}%**가  
  **글로벌 플랫폼·도메인 기반(Global)**에서 발생하고 있습니다.
- 이는 AI 에이전트 일자리 생태계가  
  **국가 단위 고용시장보다 글로벌 디지털 생태계 중심으로 구조 전환**되고 있음을 보여줍니다.
- 국가 기반 기회는 여전히 존재하지만,  
  글로벌 생태계가 **확산 속도와 접근성 측면에서 우위를 점하고 있음**을 시사합니다.
""")

st.markdown("""
📌 **해석 유의사항**  
본 분석은 고용 위치가 아닌,  
AI 에이전트 기회가 생성·유통되는 **디지털 생태계의 기반 구조**를 추정한 결과입니다.
""")
