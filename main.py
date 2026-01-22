import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 1. 기본 설정
# -----------------------------
st.set_page_config(page_title="AI Agent 트렌드 이해", layout="wide")

st.title("🤖 AI Agent 유형별 트렌드 이해")
st.subheader("고3·대학생 대상 진로·전공 탐색 특강용")

st.markdown("""
이 자료는 **AI Agent가 어떤 역할로 발전하고 있는지**를 통해  
👉 *앞으로 어떤 전공과 역량이 중요해질지* 생각해보도록 돕기 위한 특강 자료입니다.
""")

# -----------------------------
# 2. 예시 데이터 (CSV 불러오지 않음)
# -----------------------------
data = {
    "연도": [2020, 2020, 2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024],
    "AI_Agent_유형": [
        "Task-oriented Agent", "Conversational Agent",
        "Task-oriented Agent", "Conversational Agent",
        "Conversational Agent", "Autonomous Agent",
        "Autonomous Agent", "Multi-Agent System",
        "Multi-Agent System", "Autonomous Agent"
    ]
}

df = pd.DataFrame(data)

# -----------------------------
# 3. AI Agent 유형별 빈도 시각화
# -----------------------------
st.header("① AI Agent 유형별 등장 빈도")

type_counts = df["AI_Agent_유형"].value_counts()

fig1, ax1 = plt.subplots()
type_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("등장 빈도")
ax1.set_xlabel("AI Agent 유형")
ax1.set_ylim(0, 20)

st.pyplot(fig1)

# -----------------------------
# 4. 특강용 해석 (학생 눈높이)
# -----------------------------
st.markdown("""
### 🧠 해석 포인트 (학생용)

- 가장 많이 등장하는 **Task-oriented / Conversational Agent**는  
  👉 *명확한 일을 대신 수행하는 AI*입니다.
- 예시:
  - 챗봇
  - 과제 도와주는 AI
  - 일정 관리, 추천 시스템

📌 **의미**
> 지금까지의 AI는  
> **“스스로 생각하는 존재”라기보다  
> “사람이 시킨 일을 잘 해주는 도구”에 가까웠습니다.**
""")

# -----------------------------
# 5. 연도별 트렌드 시각화
# -----------------------------
st.header("② 연도별 AI Agent 트렌드 변화")

trend = (
    df.groupby(["연도", "AI_Agent_유형"])
    .size()
    .unstack(fill_value=0)
)

fig2, ax2 = plt.subplots()
trend.plot(ax=ax2)
ax2.set_ylabel("등장 빈도")
ax2.set_xlabel("연도")
ax2.set_ylim(0, 20)

st.pyplot(fig2)

# -----------------------------
# 6. 특강용 트렌드 해석
# -----------------------------
st.markdown("""
### 🔍 트렌드 해석 (진로 연결)

- 최근으로 갈수록:
  - **Autonomous Agent**
  - **Multi-Agent System**
  이 점점 등장하고 있습니다.

📌 이것은 무슨 의미일까요?

> AI가 단순히  
> **“시키는 일만 하는 단계”를 넘어  
> “상황을 이해하고, 여러 AI가 협력하는 단계”로 이동 중**이라는 뜻입니다.
""")

# -----------------------------
# 7. 진로·전공 탐색 연결 메시지
# -----------------------------
st.header("③ 진로·전공 탐색에 주는 메시지")

st.markdown("""
### 🎯 고3·대학생에게 중요한 포인트

✔ 단순 코딩만 잘하는 사람 → ❌  
✔ **문제를 정의하고, AI의 역할을 설계하는 사람** → ⭕

#### 앞으로 중요해질 전공·역량 예시
- 컴퓨터공학, 인공지능
- 심리학, 인지과학
- 산업공학, UX/UI
- 교육, 상담, 기획

📌 **정리하면**
> AI 시대의 핵심 역량은  
> **“기술 + 사람 이해 + 문제 해결 능력”의 결합**입니다.
""")

# -----------------------------
# 8. 특강 마무리 메시지
# -----------------------------
st.success("""
🎓 오늘의 핵심 질문

👉 나는 AI를 **만드는 사람**이 되고 싶은가?  
👉 AI와 **함께 일하는 사람**이 되고 싶은가?  
👉 AI를 **활용해 문제를 해결하는 사람**이 되고 싶은가?

이 질문이 여러분의 전공 선택과 대학 생활을 안내해줄 것입니다.
""")
