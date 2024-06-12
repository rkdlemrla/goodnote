import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# 이미지 표시
st.image("exercise.jpg", caption="득근")

# 운동 종류별 평균 칼로리 소모량 (분당 칼로리)
CALORIES_PER_MIN = {
    "걷기": 4,  # 예: 4 kcal/min
    "달리기": 10,  # 예: 10 kcal/min
    "자전거 타기": 8,  # 예: 8 kcal/min
    "수영": 12,  # 예: 12 kcal/min
    "헬스": 6,  # 예: 6 kcal/min
    "테니스": 7,  # 예: 7 kcal/min
    "야구": 5,  # 예: 5 kcal/min
    "축구": 11,  # 예: 11 kcal/min
    "배구": 8  # 예: 8 kcal/min
}

# 데이터베이스 초기화
conn = sqlite3.connect('exercise.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS exercise (
        id INTEGER PRIMARY KEY,
        date TEXT,
        exercise_type TEXT,
        duration INTEGER,
        calories INTEGER
    )
''')
conn.commit()

# 목표 설정
st.sidebar.title("목표 설정")
goal_duration = st.sidebar.number_input("주간 목표 운동 시간 (분)", min_value=0, step=1)
if 'goal_duration' not in st.session_state or st.session_state.goal_duration != goal_duration:
    st.session_state.goal_duration = goal_duration

# 운동 기록 입력
st.title("운동 기록 및 통계 웹앱")

with st.form(key='exercise_form'):
    exercise_type = st.selectbox("운동 종류", list(CALORIES_PER_MIN.keys()))
    date = st.date_input("운동 날짜", datetime.today())
    duration = st.number_input("운동 시간 (분)", min_value=0, step=1)
    submit_button = st.form_submit_button(label='기록 저장')

if submit_button:
    if duration <= 0:
        st.error("운동 시간은 0보다 커야 합니다.")
    else:
        calories = duration * CALORIES_PER_MIN[exercise_type]
        c.execute('''
            INSERT INTO exercise (date, exercise_type, duration, calories)
            VALUES (?, ?, ?, ?)
        ''', (date, exercise_type, duration, calories))
        conn.commit()
        st.success(f"운동 기록이 저장되었습니다. 소모한 칼로리: {calories} kcal")
        df = pd.read_sql('SELECT * FROM exercise', conn)
        df['date'] = pd.to_datetime(df['date'])

# 운동 기록 불러오기
df = pd.read_sql('SELECT * FROM exercise', conn)
df['date'] = pd.to_datetime(df['date'])

# 주간 운동 시간 계산
current_week = datetime.today().isocalendar()[1]
weekly_duration = df[df['date'].dt.isocalendar().week == current_week]['duration'].sum()

# 주간 목표 달성률 시각화
st.sidebar.write("### 주간 목표 달성률")
st.sidebar.progress(min(1, weekly_duration / goal_duration) if goal_duration > 0 else 0)

# 데이터 시각화
st.write("### 운동 기록")
st.write(df)

st.write("### 날짜별 운동 시간")
if not df.empty:
    fig, ax = plt.subplots()
    df.groupby('date')['duration'].sum().plot(ax=ax)
    ax.set_ylabel("운동 시간 (분)")
    st.pyplot(fig)
else:
    st.write("운동 기록이 없습니다.")

st.write("### 운동 종류별 칼로리 소모량")
if not df.empty:
    fig, ax = plt.subplots()
    df.groupby('exercise_type')['calories'].sum().plot(kind='bar', ax=ax)
    ax.set_ylabel("칼로리 소모량 (kcal)")
    st.pyplot(fig)
else:
    st.write("운동 기록이 없습니다.")

# 데이터베이스 연결 해제
conn.close()
