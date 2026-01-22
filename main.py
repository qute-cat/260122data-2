import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="AI Agents Ecosystem Dashboard",
    layout="wide"
)

st.title("🌍 AI 에이전트 일자리 생태계 분석 대시보드")
st.caption("연도별 변화 · 도메인 기반 국가 분석 · 정책/산업 해석 제공")

# ---------------------------
# 데이터 로딩
# ---------------------------
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_csv("AI_Agents_Ecosystem_2026.csv")

uploaded_file = st.file_uploader(
    "같은 형식의 CSV 파일을 업로드하면 자동으로 반영됩니다",
    type="csv"
)

df = load_data(uploaded_file)

st.success(f"데이터 로딩 완료: {len(df)} rows")

# ---------------------------
# 컬럼 자동 탐색
# ---------------------------
columns_lower = {c.lower(): c for c in df.columns}

year_col = columns_lower.get("year")
domain_col = (
    columns_lower.get("domain")
    or columns_lower.get("url")
    or columns_lower.get("website")
)

if not year_col or not domain_col:
    st.error("❌ 연도(year) 또는 도메인(domain/url) 컬럼을 찾지 못했습니다.")
    st.stop()

# ---------------------------
# 국가 추정 (도메인 기반)
# ---------------------------
def infer_country(domain):
    if pd.isna(domain):
        return "Unknown"
    match = re.search(r"\.([a-z]{2})$", domain.lower())
    if match:
        return match.group(1).upper()
    return "Global"

df["Country"] = df[domain_col].apply(infer_country)

# ---------------------------
# 연도별 집계
# ---------------------------
year_count = (
    df.groupby(year_col)
    .size()
    .reset_index(name="Count")
    .sort_values(year_col)
)

# ---------------------------
# 연도별 글로벌 트렌드
# ---------------------------
st.subheader("📈 연도별 AI 에이전트 생태계 변화 (글로벌)")

fig_global = px.line(
    year_count,
    x=year_col,
    y="Count",
    markers=True,
    title="연도별 AI 에이전트 관련 생태계 규모 변화"
)

fig_global.update_yaxes(range=[0, 20])
st.plotly_chart(fig_global, use_container_width=True)

# ---------------------------
# 국가별 연도 비교
# ---------------------------
st.subheader("🌐 국가별 AI 에이전트 생태계 변화")

country_year = (
    df.groupby([year_col, "Country"])
    .size()
    .reset_index(name="Count")
)

selected_countries = st.multiselect(
    "비교할 국가 선택 (도메인 기준)",
    sorted(country_year["Country"].unique()),
    default=["GLOBAL", "KR", "US"]
)

filtered = country_year[country_year["Country"].isin(selected_countries)]

fig_country = px.line(
    filtered,
    x=year_col,
    y="Count",
    color="Country",
    markers=True,
    title="국가별 연도 변화 비교"
)

fig_country.update_yaxes(range=[0, 20])
st.plotly_chart(fig_country, use_container_width=True)

# ---------------------------
# 글로벌 vs 특정 국가 비교
# ---------------------------
st.subheader("🌍 글로벌 vs 특정 국가 비교")

target_country = st.selectbox(
    "비교할 국가 선택",
    sorted(df["Country"].unique())
)

compare_df = country_year[
    country_year["Country"].isin(["Global", target_country])
]

fig_compare = px.line(
    compare_df,
    x=year_col,
    y="Count",
    color="Country",
    markers=True,
    title=f"Global vs {target_country} AI 에이전트 생태계 비교"
)

fig_compare.update_yaxes(range=[0, 20])
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------------
# 해석 섹션
# ---------------------------
st.divider()
st.header("🧠 데이터 해석")

st.subheader("① 정책·산업 보고서용 해석")

st.markdown("""
- 연도별 데이터는 **AI 에이전트 관련 산업·일자리 생태계가 단기적으로 어떻게 확산 또는 정체되는지**를 보여준다.
- 글로벌 트렌드는 기술 주도 산업의 성숙도 및 투자 집중 시점을 반영한다.
- 국가별 차이는 **디지털 전환 정책, 스타트업 생태계, 규제 환경**의 영향을 간접적으로 시사한다.
- 특정 국가가 글로벌 대비 완만한 증가를 보일 경우, 이는 **도입기 혹은 제도 정비 단계**로 해석 가능하다.
""")

st.subheader("② 산업 vs 교육·인력양성 시사점")

st.markdown("""
**[산업 측면]**
- AI 에이전트 수요 증가는 자동화, 의사결정 보조, 운영 최적화 영역에서의 실질적 활용 확산을 의미한다.
- 국가별 격차는 기업의 기술 채택 속도 및 산업 구조 차이를 반영한다.

**[교육·인력양성 측면]**
- AI 에이전트 생태계 성장은 단순 개발자가 아닌  
  **기획자·운영자·윤리·정책 이해 인력** 수요 증가로 연결된다.
- 연도별 완만한 증가 구간은 **커리큘럼 개편 및 재교육 정책 개입의 적기**로 해석할 수 있다.
""")

st.success("✅ 분석 및 해석이 포함된 대시보드 구성 완료")
