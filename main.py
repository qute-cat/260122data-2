import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")

# -----------------------------
# Session State 초기화 (KeyError 방지)
# -----------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "votes" not in st.session_state:
    st.session_state.votes = {}

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

# -----------------------------
# 데이터 로드
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

# -----------------------------
# A. 연도별 트렌드 집계
# -----------------------------
yearly_trend = (
    df.dropna(subset=["Year"])
    .groupby("Year")
    .size()
    .reset_index(name="Count")
)

all_years = pd.DataFrame({
    "Year": range(int(yearly_trend["Year"].min()), int(yearly_trend["Year"].max()) + 1)
})

yearly_trend = all_years.merge(
    yearly_trend, on="Year", how="left"
).fillna(0)

# -----------------------------
# A-1. 시각화
# -----------------------------
st.subheader("📈 연도별 AI Agent 트렌드 변화")

bar = alt.Chart(yearly_trend).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X("Year:O", title="연도"),
    y=alt.Y("Count:Q", title="사례 수"),
    tooltip=["Year", "Count"]
)

line = alt.Chart(yearly_trend).mark_line(
    point=True,
    strokeWidth=3
).encode(
    x="Year:O",
    y="Count:Q"
)

st.altair_chart((bar + line).properties(height=380), use_container_width=True)

st.caption(
    "AI Agent 논의는 단순 자동화 → 협업 → 자율적 의사결정 구조로 확장되고 있습니다."
)

# -----------------------------
# B. AI Agent 역할 진화 단계
# -----------------------------
st.subheader("🧠 AI Agent 역할의 진화 단계")

st.markdown("""
**AI Agent는 단번에 똑똑해진 것이 아니라, 역할이 단계적으로 진화해 왔습니다.**

1️⃣ **도구형 Agent**  
- 단순 명령 수행 (예: 검색, 요약)  
- 인간의 지시 없이는 스스로 움직이지 않음  

2️⃣ **보조형 Agent**  
- 추천, 초안 작성, 선택지 제안  
- 인간의 판단을 돕는 조력자 역할  

3️⃣ **협업형 Agent**  
- 사람과 목표를 공유  
- 여러 Agent 간 역할 분담 가능  

4️⃣ **자율형 Agent**  
- 목표 설정 → 실행 → 평가를 스스로 수행  
- 조직·서비스 단위로 작동
""")

# -----------------------------
# C. 질문 즉석 입력 & 투표
# -----------------------------
st.subheader("❓ 지금 떠오른 질문을 남겨보세요")

new_q = st.text_input("질문을 입력하세요 (짧게!)")

if st.button("질문 등록"):
    if new_q.strip():
        st.session_state.questions.append(new_q.strip())
        st.session_state.votes[new_q.strip()] = 0

# 투표
if st.session_state.questions:
    st.markdown("### 📊 질문 투표")
    for q in st.session_state.questions:
        col1, col2 = st.columns([5, 1])
        col1.write(q)
        if col2.button("👍", key=q):
            st.session_state.votes[q] += 1
            st.session_state.selected_question = q

# -----------------------------
# D. 워드클라우드 (가독성 개선)
# -----------------------------
st.subheader("☁️ 질문 키워드 한눈에 보기")

if st.session_state.questions:
    text = " ".join(st.session_state.questions)

    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    if not os.path.exists(font_path):
        font_path = None  # Streamlit Cloud fallback

    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=900,
        height=400,
        max_words=50,
        collocations=False
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# -----------------------------
# D-1. 선택된 질문에 대한 AI 해설
# -----------------------------
if st.session_state.selected_question:
    st.subheader("🤖 AI의 생각")

    st.markdown(f"""
**선택된 질문:**  
> *{st.session_state.selected_question}*

**AI 해설:**  
이 질문은 AI Agent의 *역할 확장*과 *인간의 선택* 사이의 관계를 고민하게 합니다.  
앞으로 AI는 ‘대신 결정하는 존재’라기보다,  
👉 **결정을 더 잘하게 돕는 존재**로 진화할 가능성이 큽니다.
""")
