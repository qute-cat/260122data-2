import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

st.title("AI Agent는 어떻게 진화하고 있을까?")

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("AI_Agents_Ecosystem_2026.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

@st.cache_data
def load_data():
    try:
        # 1차 시도: UTF-8
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            # 2차 시도: CP949 (한국 엑셀 최다)
            df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="cp949")
        except UnicodeDecodeError:
            st.error(
                "CSV 파일 인코딩을 읽을 수 없습니다. "
                "UTF-8 또는 CP949 형식으로 저장해 주세요."
            )
            st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

# -----------------------------
# 연도별 트렌드 집계
# -----------------------------
yearly_trend = (
    df.groupby("Year")
    .size()
    .reset_index(name="Count")
)

# 연도 공백 채우기
all_years = pd.DataFrame({
    "Year": range(yearly_trend["Year"].min(), yearly_trend["Year"].max() + 1)
})

yearly_trend = all_years.merge(
    yearly_trend, on="Year", how="left"
).fillna(0)

# -----------------------------
# 시각화
# -----------------------------
st.subheader("📈 연도별 AI Agent 트렌드 변화")

chart = (
    alt.Chart(yearly_trend)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="관련 트렌드/사례 수"),
        tooltip=["Year", "Count"]
    )
    .properties(
        height=400
    )
)

st.altair_chart(chart, use_container_width=True)

# -----------------------------
# 해석 가이드
# -----------------------------
st.caption(
    "연도별 AI Agent 관련 담론의 증가 추이를 보여줍니다. "
    "특히 최근 몇 년간 AI Agent가 기술 실험 단계를 넘어 "
    "생태계·전략·조직 단위의 논의로 확장되고 있음을 확인할 수 있습니다."
)
