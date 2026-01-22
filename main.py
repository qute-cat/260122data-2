import streamlit as st
import pandas as pd
import chardet
from io import BytesIO

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI Agents Ecosystem 2026",
    layout="wide"
)

st.title("🤖 AI Agents Ecosystem 2026 데이터 탐색기")

# -----------------------------
# 2. CSV 로딩 함수 (인코딩 자동 감지)
# -----------------------------
@st.cache_data
def load_data(file):
    raw_data = file.read()
    detected = chardet.detect(raw_data)
    encoding = detected["encoding"]

    file.seek(0)
    df = pd.read_csv(file, encoding=encoding)
    return df, encoding

# -----------------------------
# 3. 파일 업로드
# -----------------------------
uploaded_file = st.file_uploader(
    "CSV 파일을 업로드하세요",
    type=["csv"]
)

if uploaded_file:
    try:
        df, encoding = load_data(uploaded_file)

        st.success(f"파일 로딩 성공! (인코딩: {encoding})")

        # -----------------------------
        # 4. 데이터 미리보기
        # -----------------------------
        st.subheader("📄 데이터 미리보기")
        st.dataframe(df, use_container_width=True)

        # -----------------------------
        # 5. 컬럼 선택 필터
        # -----------------------------
        st.subheader("🔍 컬럼 기반 탐색")

        selected_column = st.selectbox(
            "기준 컬럼 선택",
            df.columns
        )

        unique_values = df[selected_column].dropna().unique()

        selected_values = st.multiselect(
            "값 선택",
            unique_values
        )

        if selected_values:
            filtered_df = df[df[selected_column].isin(selected_values)]
        else:
            filtered_df = df

        st.write(f"선택된 데이터 수: {len(filtered_df)}")
        st.dataframe(filtered_df, use_container_width=True)

        # -----------------------------
        # 6. CSV 다운로드 (PDF 대신)
        # -----------------------------
        st.subheader("⬇️ 데이터 다운로드")

        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="필터링된 데이터 CSV 다운로드",
            data=csv_bytes,
            file_name="filtered_ai_agents_ecosystem.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error("파일을 처리하는 중 오류가 발생했습니다.")
        st.exception(e)

else:
    st.info("왼쪽에서 CSV 파일을 업로드하세요.")
