import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import Counter

# =============================
# 페이지 설정
# =============================
st.set_page_config(
    page_title="AI Agent Evolution",
    layout="wide"
)

st.title("🤖 AI Agent는 어떻게 진화하고 있을까?")
st.caption("AI Agent 생태계 데이터 + 학생 질문 기반 진로 탐색")

# =============================
# OpenAI API (안전 처리)
# =============================
try:
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    openai_ready = True
except Exception:
    openai_ready = False

# =============================
# 데이터 로드 (CSV)
# =============================
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
    .properties(height=350)
)

st.altair_chart(chart_a, use_container_width=True)

st.markdown("""
🧠 **의미**  
AI Agent는 최근 몇 년 사이  
**기술 실험 → 실제 활용 → 생태계 논의** 단계로 이동하고 있습니다.
""")

st.divider()

# =============================
# B. AI Agent 역할 진화
# =============================
st.subheader("B. AI Agent의 역할은 어떻게 달라졌을까?")

st.markdown("""
AI Agent는 단순한 프로그램이 아니라  
**‘무슨 역할을 맡는 존재인가’**로 이해할 수 있습니다.
""")

# 역할 분류 함수
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

role_trend = (
    df.groupby(["Year", "Role_Stage"])
    .size()
    .reset_index(name="Count")
)

chart_b = (
    alt.Chart(role_trend)
    .mark_bar()
    .encode(
        x=alt.X("Year:O", title="연도"),
        y=alt.Y("Count:Q", title="사례 수"),
        color=alt.Color(
            "Role_Stage:N",
            title="AI Agent 역할 단계",
            scale=alt.Scale(domain=[
                "1️⃣ Task / Rule Agent",
                "2️⃣ Conversational Agent",
                "3️⃣ Autonomous Agent",
                "4️⃣ Multi-Agent System"
            ])
        ),
        tooltip=["Year", "Role_Stage", "Count"]
    )
    .properties(height=420)
)

st.altair_chart(chart_b, use_container_width=True)

st.markdown("""
### 🔍 역할 단계 해설 (학생용)

- **1️⃣ Task Agent**: 시키는 일만 정확히 수행  
- **2️⃣ Conversational Agent**: 대화하며 돕는 존재  
- **3️⃣ Autonomous Agent**: 스스로 판단하고 행동  
- **4️⃣ Multi-Agent System**: AI들끼리 협력하는 구조

👉 AI는 **도구 → 동료 → 시스템 구성원**으로 진화 중
""")

st.divider()

# =============================
# C. 전공·진로 연결
# =============================
st.subheader("C. AI 시대, 사람에게 더 중요해지는 역할")

role_map = pd.DataFrame({
    "AI Agent 단계": [
        "1️⃣ Task Agent",
        "2️⃣ Conversational Agent",
        "3️⃣ Autonomous Agent",
        "4️⃣ Multi-Agent System"
    ],
    "AI의 역할": [
        "정해진 작업 수행",
        "대화·응답·지원",
        "판단·행동",
        "협력·조정"
    ],
    "사람의 핵심 역량": [
        "문제 정의",
        "공감·소통",
        "판단 기준·윤리",
        "기획·리더십"
    ],
    "연결 전공 예시": [
        "산업공학, 행정",
        "심리, 교육, UX",
        "법, 철학, 데이터",
        "경영, 정책, 융합"
    ]
})

st.dataframe(role_map, use_container_width=True)

st.success("""
🎯 핵심 메시지  
AI 시대 전공 선택은  
**AI보다 잘하는 게 아니라  
AI가 못하는 역할을 고르는 것**
""")

st.divider()

# =============================
# D. 학생 질문 수집 + 분석
# =============================
st.subheader("D. 학생 질문 (익명 참여)")

if "questions" not in st.session_state:
    st.session_state["questions"] = []

question = st.text_input("✏️ 궁금한 점을 적어주세요")

if st.button("질문 제출"):
    if question.strip():
        st.session_state["questions"].append(question.strip())
        st.success("질문이 저장되었습니다!")
    else:
        st.warning("질문을 입력해주세요.")

# -----------------------------
# 질문 분석
# -----------------------------
if st.session_state["questions"]:
    st.subheader("📊 질문 키워드 한눈에 보기")

    words = []
    for q in st.session_state["questions"]:
        words += re.findall(r"[가-힣]{2,}", q)

    freq = Counter(words).most_common(15)
    wc_df = pd.DataFrame(freq, columns=["키워드", "빈도"])

    chart_wc = (
        alt.Chart(wc_df)
        .mark_circle()
        .encode(
            x="키워드:N",
            y="빈도:Q",
            size="빈도:Q",
            tooltip=["키워드", "빈도"]
        )
        .properties(height=300)
    )

    st.altair_chart(chart_wc, use_container_width=True)

    st.divider()

    # =============================
    # E. AI 즉석 답변
    # =============================
    st.subheader("🤖 AI가 답해줍니다")

    selected_q = st.selectbox(
        "AI에게 답변을 요청할 질문을 선택하세요",
        st.session_state["questions"]
    )

    if st.button("AI 답변 보기"):
        if openai_ready:
            with st.spinner("AI가 답변을 생성 중입니다..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "너는 고등학생을 위한 진로 특강 AI다. 어렵지 않게 설명해라."
                            },
                            {
                                "role": "user",
                                "content": selected_q
                            }
                        ],
                        temperature=0.6,
                        max_tokens=200
                    )
                    st.markdown("### 💡 AI의 답변")
                    st.write(response.choices[0].message.content)
                except Exception:
                    st.error("AI 응답을 불러오지 못했습니다.")
        else:
            st.warning("OpenAI API 설정이 되어 있지 않습니다.")

else:
    st.info("아직 수집된 질문이 없습니다.")

# =============================
# 마무리
# =============================
st.success("""
🎓 오늘의 결론

AI는 점점 똑똑해지지만  
**진로를 선택하는 건 여전히 사람의 몫**입니다.

AI를 두려워하기보다  
👉 **AI와 어떤 관계를 맺을지** 고민해 보세요.
""")
