import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.caption("AI Agent 생태계 데이터 기반 트렌드 탐색")

# -----------------------------
# 데이터 로드 (인코딩 안전 처리)
# -----------------------------
@st.cache_data
def load_data():
    try:
        # 1차 시도: UTF-8
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            # 2차 시도: CP949 (한글 Windows 엑셀)
            df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="cp949")
        except UnicodeDecodeError:
            st.error(
                "❌ CSV 파일 인코딩을 읽을 수 없습니다.\n\n"
                "👉 UTF-8 또는 CP949 형식으로 저장해 주세요."
            )
            st.stop()

    # 날짜 / 연도 처리
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year

    return df

# -----------------------------
# 데이터 불러오기
# -----------------------------
df = load_data()

if df.empty:
    st.warning("데이터가 비어 있습니다.")
    st.stop()

# -----------------------------
# 연도별 트렌드 집계
# -----------------------------
yearly_trend = (
    df.groupby("Year")
    .size()
    .reset_index(name="Count")
)

# 연도 공백 채우기 (시각화 안정성)
all_years = pd.DataFrame({
    "Year": range(
        int(yearly_trend["Year"].min()),
        int(yearly_trend["Year"].max()) + 1
    )
})

yearly_trend = (
    all_years
    .merge(yearly_trend, on="Year", how="left")
    .fillna(0)
)

# -----------------------------
# 시각화
# -----------------------------
st.subheader("📈 연도별 AI Agent 트렌드 변화")

chart = (
    alt.Chart(yearly_trend)
    .mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6
    )
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="관련 트렌드 / 사례 수"),
        tooltip=[
            alt.Tooltip("Year:O", title="연도"),
            alt.Tooltip("Count:Q", title="건수")
        ]
    )
    .properties(height=420)
)

st.altair_chart(chart, use_container_width=True)

# -----------------------------
# 해석 가이드 (특강용)
# -----------------------------
st.markdown("""
### 🧠 어떻게 해석하면 좋을까?

- AI Agent 관련 논의는 **특정 시점 이후 급격히 증가**
- 단순 기술 소개 → **생태계·조직·전략 단위로 확장**
- AI는 이제  
  👉 *도구*가 아니라  
  👉 **역할을 가진 행위자(agent)** 로 다뤄지고 있음
""")

st.success("""
🎯 핵심 메시지

AI Agent의 진화는  
**기술 발전의 역사이자,  
사람의 역할이 재정의되는 과정**입니다.
""")
