import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Font Setting
# ---------------------------------------------------------
st.set_page_config(
    page_title="서울 지하철 승객 분석 대시보드",
    page_icon="🚇",
    layout="wide"
)

# Matplotlib 한글 폰트 설정 (Windows 기준 'Malgun Gothic')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.header("🚇 서울 지하철 승각수 데이터 분석 대시보드")
st.markdown("---")

# ---------------------------------------------------------
# Data Loading & Preprocessing
# ---------------------------------------------------------
@st.cache_data
def load_data():
    subway = pd.read_csv('서울지하철.csv', encoding='cp949')
    subway = subway.drop('등록일자', axis=1)
    subway['총승객수'] = subway.승차총승객수 + subway.하차총승객수
    
    # 1. '사용일자' 열을 datetime 날짜 형식으로 변환
    subway['사용일자'] = pd.to_datetime(subway['사용일자'].astype(str))
    
    # 2. '사용요일' 열 추가 (영어 요일명)
    subway['사용요일'] = subway['사용일자'].dt.day_name()
    
    return subway

try:
    subway = load_data()
except Exception as e:
    st.error(f"데이터 파일('서울지하철.csv')을 읽어오는데 실패했습니다: {e}")
    st.stop()

# ---------------------------------------------------------
# Section 1. 기본 데이터 검증 및 개요
# ---------------------------------------------------------
st.subheader("1. 데이터 기본 정보 및 검증")

col1, col2, col3 = st.columns(3)
col1.metric("총 데이터 수", f"{len(subway):,} 건")
col2.metric("결측치 개수", f"{subway.isna().sum().sum()} 개")
col3.metric("중복 행 개수", f"{subway.duplicated().sum()} 개")

with st.expander("데이터 상위 5개 행 및 요약 정보 보기"):
    st.dataframe(subway.head())

st.markdown("---")

# ---------------------------------------------------------
# Section 2. 7월 데이터 분석
# ---------------------------------------------------------
st.subheader("2. 📅 7월 지하철 이용 데이터 분석")

# 3. 7월 데이터 필터링
subway_july = subway[subway['사용일자'].dt.month == 7]

# 4. 통계 정보 출력
col_j1, col_j2, col_j3, col_j4 = st.columns(4)
col_j1.metric("7월 행 개수", f"{len(subway_july):,} 개")
col_j2.metric("총승객수 최대", f"{subway_july['총승객수'].max():,} 명")
col_j3.metric("총승객수 최소", f"{subway_july['총승객수'].min():,} 명")
col_j4.metric("총승객수 평균", f"{round(subway_july['총승객수'].mean(), 2):,} 명")

# 5, 6, 7. 역명별 / 요일별 집계
july_station_sum = subway_july.groupby('역명')['총승객수'].sum()
july_weekday_sum = subway_july.groupby('사용요일')['총승객수'].sum().sort_values(ascending=False)

col_left, col_middle, col_right = st.columns([2,2,3])

with col_left:
    st.write("🏆 7월 승객수 상위 5개 역")
    st.dataframe(july_station_sum.sort_values(ascending=False).head(5), width="stretch")

with col_middle:
    st.write("🔻 7월 승객수 하위 5개 역")
    st.dataframe(july_station_sum.sort_values(ascending=True).head(5), width="stretch")

with col_right:
    st.write("📅 7월 요일별 총승객수 (내림차순)")
    st.dataframe(july_weekday_sum, width="stretch")
    
# 8. 히스토그램 시각화
st.subheader("📊 7월 총승객수 분포 히스토그램 (구간 50)")

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.hist(subway_july['총승객수'], bins=50, color='skyblue', edgecolor='black')
ax1.set_title('7월 총승객수 분포 히스토그램', fontsize=14, pad=12)
ax1.set_xlabel('총승객수', fontsize=12)
ax1.set_ylabel('빈도수 (수량)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig1)

st.markdown("---")

# ---------------------------------------------------------
# Section 3. 최근 날짜 & 10만 명 이상 (subway2) 분석
# ---------------------------------------------------------
# 9. 필터링
latest_date = subway['사용일자'].max()
subway2 = subway[(subway['사용일자'] == latest_date) & (subway['총승객수'] >= 100000)]

st.subheader(f"3. 🔥 최근 날짜({latest_date.strftime('%Y-%m-%d')}) & 총승객수 10만 이상 역 분석")

# 10. 통계치
col_s1, col_s2, col_s3 = st.columns(3)
col_s1.metric("대상 역 개수", f"{len(subway2)} 개")
col_s2.metric("최대 승객수", f"{subway2['총승객수'].max():,} 명")
col_s3.metric("최소 승객수", f"{subway2['총승객수'].min():,} 명")

# 11 & 12. 세로막대 그래프
subway2_sorted = subway2.sort_values(by='총승객수', ascending=False)

#st.subheader("📊 역별 총승객수 현황 (호선별 색상 구분)")
st.markdown("#### 📊 역별 총승객수 현황 (호선별 색상 구분)")

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(
    data=subway2_sorted, 
    x='역명', 
    y='총승객수', 
    hue='호선명', 
    dodge=False,
    ax=ax2
)
ax2.set_title(f'최근 날짜({latest_date.strftime("%Y-%m-%d")}) 총승객수 10만 이상 역별 현황', fontsize=14, pad=12)
ax2.set_xlabel('역명', fontsize=12)
ax2.set_ylabel('총승객수', fontsize=12)
ax2.tick_params(axis='x', rotation=45)
ax2.legend(title='호선명', loc='upper right')
ax2.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

st.pyplot(fig2)

# 13 & 14. 호선명별 개수 및 파이 차트
col_pie_left, col_pie_right = st.columns([1, 2])

line_counts = subway2['호선명'].value_counts()

with col_pie_left:
    st.write("📌 호선별 역 개수 집계")
    st.dataframe(line_counts, width=True)

with col_pie_right:
    st.write("🥧 호선별 비중 (파이 차트)")
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    ax3.pie(
        line_counts, 
        labels=line_counts.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=sns.color_palette('pastel')
    )
    ax3.set_title(f'최근 날짜({latest_date.strftime("%Y-%m-%d")}) 10만 이상 역의 호선별 비중', fontsize=14, pad=12)
    
    st.pyplot(fig3)