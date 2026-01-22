import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------
# 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="AI Agent Ecosystem Analyzer",
    layout="wide"
)

st.title("🤖 AI Agent Ecosystem: 유형별 빈도 & 트렌드 분석")

# ---------------------------------
# 1. 데이터 로딩 (내장 CSV)
# ---------------------------------
@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            return pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding=enc), enc
        except:
            pass
    raise ValueError("CSV 인코딩을 확인해주세요.")

df, encoding = load_data()
st.success(f"기본 데이터 로딩 완료 (인코딩: {encoding})")

# ---------------------------------
# 2. 컬럼 선택
# ---------------------------------
columns = df.columns.tolist()

year_col = st.selectbox("연도 컬럼 선택", columns)
agent_col = st.selectbox("AI Agent 유형 컬럼 선택", columns)
country_col = st.selectbox("국가 컬럼 선택 (선택)", ["없음"] + columns)

# ---------------------------------
# 3. 데이터 정제
# ---------------------------------
df = df.copy()
df[year_col] = df[year_col].astype(str)

if country_col != "없음":
    selected_countries = st.multiselect(
        "분석할 국가 선택",
        sorted(df[country_col].dropna().unique()),
        default=sorted(df[country_col].dropna().unique())
    )
    df = df[df[country_col].isin(selected_countries)]

# ---------------------------------
# 4. AI Agent 유형별 전체 빈도
# ---------------------------------
st.subheader("① AI Agent 유형별 전체 빈도")

agent_count = (
    df[agent_col]
    .value_counts()
    .reset_index(name="빈도")
)
agent_count.columns = ["AI Agent 유형", "빈도"]

fig_freq = px.bar(
    agent_count,
    x="AI Agent 유형",
    y="빈도",
    text="빈도"
)

st.plotly_chart(fig_freq, use_container_width=True)

# ---------------------------------
# 5. 연도별 AI Agent 유형 트렌드
# ---------------------------------
st.subheader("② 연도별 AI Agent 유형 트렌드")

trend_df = (
    df[[year_col, agent_col]]
    .value_counts()
    .reset_index(name="건수")
)

fig_trend = px.line(
    trend_df,
    x=year_col,
    y="건수",
    color=agent_col,
    markers=True
)

st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------
# 6. 글로벌 vs 국가 비교
# ---------------------------------
if country_col != "없음":
    st.subheader("③ 글로벌 vs 국가별 AI Agent 유형 비교")

    compare_year = st.selectbox(
        "비교 연도 선택",
        sorted(df[year_col].unique())
    )

    compare_df = (
        df[df[year_col] == compare_year][[country_col, agent_col]]
        .value_counts()
        .reset_index(name="건수")
    )

    fig_country = px.bar(
        compare_df,
        x=agent_col,
        y="건수",
        color=country_col,
        barmode="group"
    )

    st.plotly_chart(fig_country, use_container_width=True)

# ---------------------------------
# 7. 정책·산업 보고서용 해석
# ---------------------------------
st.subheader("📘 정책·산업 보고서용 해석 가이드")

st.markdown("""
### 🔹 산업적 시사점
- AI Agent 유형 빈도는 **시장 성숙도 및 수요 검증 지표**
- 연도별 증가 유형은 **투자·상용화 가속 구간**
- 국가별 편차는 **국가 전략 산업 및 정책 개입 효과**를 반영

### 🔹 교육·인력양성 시사점
- 성장 유형 → **신규 직무·역량 수요 급증**
- 정체 유형 → **전환 교육(reskilling) 필요**
- 국가별 차이 → **교육 정책 및 인재 파이프라인 격차**
""")
