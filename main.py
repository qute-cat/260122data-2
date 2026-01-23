import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import re
import openai

# ==============================
# 🔐 OpenAI API 설정
# ==============================
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# ==============================
# 🤖 AI 에이전트 역할 설명
# ==============================
"""
이 앱에는 3개의 AI 에이전트가 존재합니다.

1. 질문 해석 에이전트
   - 학생 질문에서 핵심 키워드를 추출
   - 전공군 자동 분류에 사용

2. 답변 생성 에이전트
   - 학생 질문에 대해 진로·전공 중심의 답변 생성
   - OpenAI API 사용

3. 분석 에이전트
   - 국가별, 전공군별 AI 활용 정도를 집계
   - 교육적 의사결정을 위한 데이터 제공
"""

# ==============================
# 🧠 세션 상태 초기화
# ==============================
if "questions" not in st.session_state:
    st.session_state.questions = []

if "ai_usage" not in st.session_state:
    st.session_state.ai_usage = []

# ==============================
# 🎓 전공군 분류 함수
# ==============================
def classify_major(text):
    text = text.lower()
    if any(k in text for k in ["심리", "교육", "사회", "상담"]):
        return "사회과학"
    if any(k in text for k in ["문학", "역사", "철학", "언어"]):
        return "인문"
    if any(k in text for k in ["화학", "물리", "생물", "수학"]):
        return "자연과학"
    if any(k in text for k in ["컴퓨터", "공학", "ai", "데이터"]):
        return "공학"
    if any(k in text for k in ["미술", "체육", "음악", "디자인"]):
        return "예체능"
    return "기타"

# ==============================
# 🤖 AI 답변 생성 함수
# ==============================
def generate_ai_answer(question):
    if not openai.api_key:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다."

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 고등학생을 위한 진로 상담 AI다."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

# ==============================
# 🧩 UI 시작
# ==============================
st.title("🎓 학생 질문 기반 진로 탐색 & AI 에이전트 대시보드")

st.markdown("### 📝 질문 입력")
country = st.selectbox("국가 선택", ["Korea", "Japan", "USA", "China", "Other"])
question = st.text_input("궁금한 질문을 입력하세요")

if st.button("질문 등록"):
    if question.strip():
        major_group = classify_major(question)
        st.session_state.questions.append({
            "question": question,
            "country": country,
            "major": major_group,
            "votes": 0
        })

# ==============================
# 📊 질문 목록 & 투표
# ==============================
st.markdown("## 📌 학생 질문 목록")

for i, q in enumerate(st.session_state.questions):
    col1, col2 = st.columns([4, 1])
    col1.write(f"**[{q['major']}]** {q['question']}")
    if col2.button("👍", key=f"vote_{i}"):
        q["votes"] += 1

    if st.button("🤖 AI 답변 보기", key=f"ai_{i}"):
        answer = generate_ai_answer(q["question"])
        st.info(answer)
        st.session_state.ai_usage.append(q["country"])

# ==============================
# ☁️ 가독성 좋은 키워드 시각화
# ==============================
st.markdown("## 🔤 질문 키워드 분석")

all_text = " ".join([q["question"] for q in st.session_state.questions])
words = re.findall(r"[가-힣a-zA-Z]{2,}", all_text)
counter = Counter(words)
df_words = pd.DataFrame(counter.items(), columns=["word", "count"]).sort_values("count", ascending=False).head(20)

if not df_words.empty:
    chart = alt.Chart(df_words).mark_bar().encode(
        x=alt.X("count:Q", title="빈도"),
        y=alt.Y("word:N", sort="-x", title="키워드")
    ).properties(height=400)

    st.altair_chart(chart, use_container_width=True)

# ==============================
# 🌍 국가별 AI 에이전트 활성화 (A안)
# ==============================
st.markdown("## 🌍 국가별 AI 에이전트 활성화 현황")

if st.session_state.ai_usage:
    df_country = pd.DataFrame(st.session_state.ai_usage, columns=["country"])
    df_count = df_country.value_counts().reset_index()
    df_count.columns = ["country", "ai_calls"]

    chart_country = alt.Chart(df_count).mark_bar().encode(
        x="country:N",
        y="ai_calls:Q",
        tooltip=["ai_calls"]
    ).properties(height=300)

    st.altair_chart(chart_country, use_container_width=True)
else:
    st.info("아직 AI 답변이 호출되지 않았습니다.")
