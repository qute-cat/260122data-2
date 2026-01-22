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
# 데이터 로딩 (인코딩 순차 시도)
# ---------------------------------
@st.cache_data
def load_data(file):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc), enc
        except:
            pass
    raise ValueError("지원하지 않는 인코딩입니다.")

uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

if not uploaded_file:
    st.info("CSV 파일을 업로드해주세요.")
    st.stop()

df, encoding = load_data(uploaded_file)
st.success(f"데이터 로딩 완료 (인코딩: {encoding})")

# ---------------------------------
# 컬럼 자동 탐색
# ---------------------------------
columns = df.columns.tolist()

year_col = st.selectbox("연도 컬럼 선택", columns)
agent_col = st.selectbox("AI Agent 유형 컬럼 선택", columns)
country_col = st.selectbox("국가 컬럼 선택 (선택)", ["없음"] + columns)

# ---------------------------------
# 데이터 정제
# ---------------------------------
df[year_col] = df[year_col].astype(str)

if country_col != "없음":
    selected_countries = st.multiselect(
        "분석할 국가 선택",
        sorted(df[country_col].dropna().unique()),
        default=sorted(df[country_col].dropna().unique())
    )
    df = df[df[country_col].isin(selected_countries)]

# ---------------------------------
# 1️⃣ AI Agent 유형별 전체 빈도
# ---------------------------------
st.subheader("① AI Agent 유형별 전체 빈도")

agent_count = (
    df[agent_col]
    .value_counts()
    .reset_index()
)
agent_count.columns = ["AI Agent 유형", "빈도"]

fig_freq = px.bar(
    agent_count,
    x="AI Agent 유형",
    y="빈도",
    text="빈도"
)
fig_freq.update_layout(
    xaxis_title="AI Agent 유형",
    yaxis_title="등장 빈도",
    yaxis_range=[0, agent_count["빈도"].max() * 1.2]
)

st.plotly_chart(fig_freq, use_container_width=True)

# ---------------------------------
# 2️⃣ 연도별 AI Agent 유형 트렌드
# ---------------------------------
st.subheader("② 연도별 AI Agent 유형 트렌드")

trend_df = (
    df
    .groupby([year_col, agent_col])
    .size()
    .reset_index(name="건수")
)

fig_trend = px.line(
    trend_df,
    x=year_col,
    y="건수",
    color=agent_col,
    markers=True
)
fig_trend.update_layout(
    xaxis_title="연도",
    yaxis_title="건수",
    yaxis_range=[0, trend_df["건수"].max() * 1.2]
)

st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------
# 3️⃣ 글로벌 vs 국가 비교 (선택 시)
# ---------------------------------
if country_col != "없음":
    st.subheader("③ 글로벌 vs 국가별 AI Agent 유형 비교")

    compare_year = st.selectbox(
        "비교 연도 선택",
        sorted(df[year_col].unique())
    )

    compare_df = (
        df[df[year_col] == compare_year]
        .groupby([country_col, agent_col])
        .size()
        .reset_index(name="건수")
    )

    fig_country = px.bar(
        compare_df,
        x=agent_col,
        y="건수",
        color=country_col,
        barmode="group"
    )
    fig_country.update_layout(
        xaxis_title="AI Agent 유형",
        yaxis_title="건수"
    )

    st.plotly_chart(fig_country, use_container_width=True)

# ---------------------------------
# 4️⃣ 정책·산업 보고서용 해석
# ---------------------------------
st.subheader("📘 정책·산업 보고서용 해석 가이드")

st.markdown("""
### 🔹 산업적 시사점
- **빈도가 높은 AI Agent 유형**은 이미 상용화·시장 수요가 검증된 영역으로 해석 가능
- 연도별 증가 추세는 **투자 집중 및 산업 구조 변화의 신호**
- 특정 국가에서만 급증하는 유형은 **국가 주도 전략 산업**일 가능성

### 🔹 교육·인력양성 시사점
- 빠르게 성장하는 Agent 유형은 **신규 직무·역량 수요 증가**
- 정체·감소 유형은 **재교육(reskilling) 필요 영역**
- 국가별 차이는 **교육과정·인력정책 격차**를 반영
""")
