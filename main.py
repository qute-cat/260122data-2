import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse
from fpdf import FPDF

# ===============================
# 기본 설정
# ===============================

st.set_page_config(
    page_title="AI Agents Ecosystem Policy Dashboard",
    layout="wide"
)

st.title("AI 에이전트 생태계 통합 분석 대시보드")
st.caption("산업 · 역할 · 국가 · 연도 · 정책 시사점 통합 분석")

# ===============================
# 1. 데이터 로딩 (인코딩 안전)
# ===============================

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


uploaded_file = st.file_uploader("같은 형식의 CSV 업로드", type=["csv"])
df = load_data(uploaded_file)

if df is None:
    st.stop()

st.success(f"데이터 로딩 완료: {len(df):,}건")

# ===============================
# 2. 분석 기준 컬럼 자동 탐색
# ===============================

text_columns = df.select_dtypes(include="object").columns.tolist()
text_col = text_columns[0]

year_col = None
for c in df.columns:
    if "year" in c.lower():
        year_col = c
        break

st.caption(f"텍스트 기준 컬럼: `{text_col}`")
if year_col:
    st.caption(f"연도 기준 컬럼: `{year_col}`")
else:
    st.warning("연도 컬럼이 없어 연도 분석은 비활성화됩니다.")

# ===============================
# 3. 도메인 기반 국가/글로벌 구분
# ===============================

def extract_region(text):
    if pd.isna(text):
        return "Unknown"
    try:
        domain = urlparse(text).netloc.lower()
        if domain.endswith((".com", ".io", ".ai", ".org")):
            return "Global"
        return domain.split(".")[-1].upper()
    except:
        return "Unknown"

df["region"] = df[text_col].apply(extract_region)

# ===============================
# 4. 산업군 태깅
# ===============================

def tag_industry(text):
    t = str(text).lower()
    if any(k in t for k in ["edu", "school", "learn"]):
        return "Education / HR"
    if any(k in t for k in ["health", "medical"]):
        return "Healthcare"
    if any(k in t for k in ["bank", "finance"]):
        return "Finance"
    if any(k in t for k in ["gov", "policy"]):
        return "Public / Gov"
    if any(k in t for k in ["media", "content"]):
        return "Media / Creative"
    if any(k in t for k in ["enterprise", "b2b"]):
        return "Enterprise / B2B"
    if any(k in t for k in ["ai", "platform", "software"]):
        return "Tech / Platform"
    return "Unknown"

df["industry"] = df[text_col].apply(tag_industry)

# ===============================
# 5. AI 에이전트 역할 태깅
# ===============================

def tag_role(text):
    t = str(text).lower()
    if any(k in t for k in ["decision", "recommend"]):
        return "Decision Support"
    if any(k in t for k in ["automate", "task"]):
        return "Task Automation"
    if any(k in t for k in ["plan", "orchestrate"]):
        return "Planning / Orchestration"
    if any(k in t for k in ["assistant", "chat"]):
        return "Interaction Assistant"
    if any(k in t for k in ["create", "generate"]):
        return "Creative Agent"
    if any(k in t for k in ["monitor", "analyze"]):
        return "Monitoring / Analysis"
    return "Unknown"

df["role"] = df[text_col].apply(tag_role)

# ===============================
# 6. 연도별 변화 분석 (①)
# ===============================

if year_col:
    st.subheader("연도별 AI 에이전트 생태계 변화")

    year_counts = df.groupby(year_col).size().reset_index(name="count")

    fig_year = px.line(
        year_counts,
        x=year_col,
        y="count",
        markers=True,
        title="연도별 AI 에이전트 기회 변화"
    )

    fig_year.update_yaxes(range=[0, year_counts["count"].max() * 1.1])
    st.plotly_chart(fig_year, use_container_width=True)

# ===============================
# 7. 한국(KR) 심층 분석 (②)
# ===============================

st.subheader("한국(KR) AI 에이전트 생태계 심층 분석")

kr_df = df[df["region"] == "KR"]

if not kr_df.empty:
    fig_kr = px.sunburst(
        kr_df,
        path=["industry", "role"],
        title="한국 AI 에이전트 산업 × 역할 구조"
    )
    st.plotly_chart(fig_kr, use_container_width=True)
else:
    st.info("KR 데이터가 없습니다.")

# ===============================
# 8. 산업 × 역할 매트릭스
# ===============================

st.subheader("산업군 × AI 에이전트 역할 매트릭스")

matrix = (
    df.groupby(["industry", "role"])
    .size()
    .reset_index(name="count")
)

heatmap_df = matrix.pivot(
    index="industry",
    columns="role",
    values="count"
).fillna(0)

fig_matrix = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_matrix, use_container_width=True)

# ===============================
# 9. Executive Summary 생성 (③)
# ===============================

st.subheader("정책·산업 Executive Summary")

global_ratio = (df["region"] == "Global").mean() * 100

summary_text = f"""
AI 에이전트 관련 기회의 {global_ratio:.1f}%가 글로벌 플랫폼 기반에서 발생하고 있으며,
가장 활발한 산업군은 {df["industry"].value_counts().idxmax()},
주요 역할 유형은 {df["role"].value_counts().idxmax()}로 나타났다.

이는 AI 정책이 국내 고용 중심 접근을 넘어
글로벌 생태계 연계형 인력·산업 전략으로 전환될 필요가 있음을 시사한다.
"""

st.markdown(summary_text)

# ===============================
# 10. PDF 보고서 자동 생성 (③)
# ===============================

if st.button("📄 정책 보고서 PDF 생성"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, summary_text)
    pdf.output("AI_Agents_Policy_Report.pdf")
    st.success("PDF 생성 완료 (로컬 실행 시 파일 생성)")

# ===============================
# 11. LLM 기반 태깅 옵션 (④)
# ===============================

st.subheader("고급 옵션: LLM 기반 태깅 (선택)")

st.info("""
- OpenAI API 키가 있을 경우 사용 가능
- 기본값은 OFF (규칙 기반 태깅 유지)
- 정책 보고서용 신뢰성 확보를 위해 옵션 처리
""")

st.toggle("LLM 기반 태깅 사용 (실험적)", value=False)

st.caption("© AI Agents Ecosystem Policy Dashboard")
