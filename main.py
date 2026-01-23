import streamlit as st
import pandas as pd
import altair as alt
import re

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
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="cp949")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year

    return df

df = load_data()

# =============================
# A. 연도별 트렌드
# =============================
st.subheader("A. 연도별 AI Agent 트렌드 변화")

yearly_trend = (
    df.groupby("Year")
    .size()
    .reset_index(name="Count")
)

chart_a = (
    alt.Chart(yearly_trend)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        tooltip=["Year", "Count"]
    )
    .properties(height=380)
)

st.altair_chart(chart_a, use_container_width=True)

st.markdown("""
👉 **A 단계 요약**  
AI Agent 관련 논의는 최근으로 올수록 **폭발적으로 증가**하고 있습니다.
""")

st.divider()

# =============================
# B. 역할 진화 단계 분석
# =============================
st.subheader("B. AI Agent 역할 진화 단계")

st.markdown("""
AI Agent는 단순한 프로그램이 아니라  
**어떤 역할을 맡고 있는 존재인가**로 이해할 수 있습니다.
""")

# -----------------------------
# 역할 단계 분류 함수
# -----------------------------
def classify_role(text):
    text = str(text).lower()

    if re.search(r"multi|ecosystem|collaboration|swarm", text):
        return "4️⃣ Multi-Agent System"
    if re.search(r"autonomous|self|decision|agentic", text):
        return "3️⃣ Autonomous Agent"
    if re.search(r"chat|assistant|conversation|dialog", text):
        return "2️⃣ Conversational Agent"
    return "1️⃣ Task / Rule Agent"

df["Role_Stage"] = df["Description"].apply(classify_role)

# -----------------------------
# 연도 × 역할 단계 집계
# -----------------------------
role_trend = (
    df.groupby(["Year", "Role_Stage"])
    .size()
    .reset_index(name="Count")
)

# -----------------------------
# 누적 막대 그래프
# -----------------------------
chart_b = (
    alt.Chart(role_trend)
    .mark_bar()
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        color=alt.Color(
            "Role_Stage:N",
            title="AI Agent 역할 단계",
            scale=alt.Scale(
                domain=[
                    "1️⃣ Task / Rule Agent",
                    "2️⃣ Conversational Agent",
                    "3️⃣ Autonomous Agent",
                    "4️⃣ Multi-Agent System"
                ]
            )
        ),
        tooltip=["Year", "Role_Stage", "Count"]
    )
    .properties(height=420)
)

st.altair_chart(chart_b, use_container_width=True)

# -----------------------------
# B 단계 해석
# -----------------------------
st.markdown("""
### 🧠 B 단계 해석 가이드 (특강용)

- 초기: **시키는 대로만 하는 AI**
- 중기: **대화하고 돕는 AI**
- 최근: **스스로 판단하고**
- 현재/미래: **AI들끼리 협력**

📌 즉, AI는  
**도구 → 동료 → 시스템 구성원**으로 이동 중입니다.
""")

st.success("""
🎯 핵심 질문 (학생에게 던질 질문)

👉 나는  
AI에게 **명령하는 사람**이 될까?  
AI와 **협력하는 사람**이 될까?  
AI의 **판단을 설계하는 사람**이 될까?
""")
