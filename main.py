import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Agents Ecosystem Analysis",
    layout="wide"
)

st.title("AI 에이전트 생태계 분석 대시보드")
st.caption("산업군 · 역할 유형 · 글로벌 vs 국가 기반 구조 분석")

# =========================
# 1. 데이터 로딩 (인코딩 안전)
# =========================

@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            try:
                return pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(uploaded_file, encoding="cp949")
        else:
            try:
                return pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv("AI_Agents_Ecosystem_2026.csv", encoding="cp949")
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
        return None


uploaded_file = st.file_uploader(
    "같은 형식의 CSV 파일 업로드",
    type=["csv"]
)

df = load_data(uploaded_file)

if df is None:
    st.stop()

st.success(f"데이터 로딩 완료: {len(df):,}건")

# =========================
# 2. 기본 컬럼 확인
# =========================

text_columns = df.select_dtypes(include="object").columns.tolist()

if not text_columns:
    st.error("텍스트 기반 분석을 위한 컬럼이 없습니다.")
    st.stop()

text_col = text_columns[0]

st.caption(f"분석 기준 텍스트 컬럼: `{text_col}`")

# =========================
# 3. 산업군 태깅
# =========================

def tag_industry(text):
    if pd.isna(text):
        return "Unknown"
    t = text.lower()
    if any(k in t for k in ["edu", "school", "learn", "course", "university"]):
        return "Education / HR"
    if any(k in t for k in ["health", "medical", "bio", "clinic"]):
        return "Healthcare"
    if any(k in t for k in ["bank", "finance", "fintech", "insurance"]):
        return "Finance"
    if any(k in t for k in ["gov", "public", "policy", "ministry"]):
        return "Public / Gov"
    if any(k in t for k in ["media", "content", "creative", "design"]):
        return "Media / Creative"
    if any(k in t for k in ["enterprise", "business", "b2b", "workflow"]):
        return "Enterprise / B2B"
    if any(k in t for k in ["ai", "platform", "software", "cloud", "saas"]):
        return "Tech / Platform"
    return "Unknown"

df["industry_tag"] = df[text_col].apply(tag_industry)

# =========================
# 4. AI 에이전트 역할 유형 태깅
# =========================

def tag_agent_role(text):
    if pd.isna(text):
        return "Unknown"
    t = text.lower()
    if any(k in t for k in ["decision", "recommend", "insight", "strategy"]):
        return "Decision Support Agent"
    if any(k in t for k in ["automate", "workflow", "execute", "task"]):
        return "Task Automation Agent"
    if any(k in t for k in ["plan", "orchestrate", "manage", "coordinate"]):
        return "Planning / Orchestration Agent"
    if any(k in t for k in ["assistant", "chat", "copilot", "support"]):
        return "Interaction / Assistant Agent"
    if any(k in t for k in ["create", "generate", "design", "content"]):
        return "Creative Agent"
    if any(k in t for k in ["monitor", "analyze", "detect", "evaluate"]):
        return "Monitoring / Analysis Agent"
    if any(k in t for k in ["learn", "coach", "train", "mentor"]):
        return "Learning / Coaching Agent"
    return "Unknown"

df["agent_role"] = df[text_col].apply(tag_agent_role)

# =========================
# 5. 산업군 × 역할 유형 매트릭스
# =========================

st.subheader("산업군 × AI 에이전트 역할 유형 분포")

matrix_df = (
    df
    .groupby(["industry_tag", "agent_role"])
    .size()
    .reset_index(name="count")
)

heatmap_df = matrix_df.pivot(
    index="industry_tag",
    columns="agent_role",
    values="count"
).fillna(0)

fig_matrix = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues",
    labels=dict(
        x="AI 에이전트 역할 유형",
        y="산업군",
        color="기회 수"
    ),
    title="산업군 × AI 에이전트 역할 유형 매트릭스"
)

fig_matrix.update_layout(
    height=500,
    xaxis_title="AI 에이전트 역할 유형",
    yaxis_title="산업군"
)

st.plotly_chart(fig_matrix, use_container_width=True)

# =========================
# 6. 정책·산업 해석 텍스트
# =========================

st.subheader("정책·산업 해석 요약")

st.markdown("""
**해석 요약**

- AI 에이전트는 산업별로 단일한 역할이 아니라,  
  산업 특성에 따라 서로 다른 역할 조합으로 확산되고 있음
- 기술·플랫폼 및 B2B 산업에서는  
  업무 자동화 및 의사결정 보조 역할이 핵심 축으로 나타남
- 이는 AI 에이전트 인력 정책이  
  단순 개발자 양성을 넘어 역할 기반 역량 체계로 전환되어야 함을 시사함

**교육·인력양성 시사점**

- 코딩 중심 교육 → 기획·운영·조율·해석 역량 중심 교육 필요
- AI 에이전트를 ‘도구’가 아닌 ‘업무 수행 주체’로 이해하는 인재 양성 필요
""")

st.caption("© AI Agents Ecosystem Analysis Dashboard")
