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
# 1. 데이터 로딩 (로컬 CSV 고정)
# ---------------------------------
@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            return pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding=enc), enc
        except:
            pass
    raise ValueError("CSV 파일 인코딩을 확인해주세요.")

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
    df.groupby(agent_col, as_index=False)
    .size()
    .rename(columns={"size": "빈도"})
)

fig_freq = px.bar(
    agent_count,
    x=agent_col,
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
# 5. 연도별 AI Agent 유형 트렌드
# ---------------------------------
st.subheader("② 연도별 AI Agent 유형 트렌드")

trend_df = (
    df
    .groupby([year_col, agent_col], as_index=False)
    .size()
    .rename(columns={"size": "건수"})
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
# 6. 글로벌 vs 국가 비교
# ---------------------------------
if country_col != "없음":
    st.subheader("③ 글로벌 vs 국가별 AI Agent 유형 비교")

    compare_year = st.selectbox(
        "비교 연도 선택",
        sorted(df[year_col].unique())
    )

    compare_df = (
        df[df[year_col] == compare_year]
        .groupby([country_col, agent_col], as_index=False)
        .size()
        .rename(columns={"size": "건수"})
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
- **등장 빈도가 높은 AI Agent 유형**은 이미 시장성과 기술 성숙도가 확보된 영역
- 연도별 증가 추세는 **산업 내 투자 집중과 비즈니스 모델 확산의 신호**
- 국가별 편중은 **국가 주도 AI 전략 산업** 가능성을 시사

### 🔹 교육·인력양성 시사점
- 성장 중인 Agent 유형은 **신규 직무·핵심 역량 수요 증가**
- 정체/감소 유형은 **전환 교육(reskilling) 필요 영역**
- 국가별 차이는 **교육 정책·인재 양성 체계 격차**를 반영
""")
