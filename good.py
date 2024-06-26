import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 이미지 표시
st.image("exercise.jpg", caption="득근")

# 운동 종류별 평균 칼로리 소모량 (분당 칼로리)
CALORIES_PER_MIN = {
    "걷기": 4,
    "달리기": 10,
    "자전거 타기": 8,
    "수영": 12,
    "헬스": 6,
    "테니스": 7,
    "야구": 5,
    "축구": 11,
    "배구": 8
}

# 목표 운동 시간 초기화
def initialize_goal_duration():
    if 'goal_duration' not in st.session_state:
        st.session_state.goal_duration = 0

# 운동 기록 초기화
def initialize_exercise_records():
    if 'exercise_records' not in st.session_state:
        st.session_state.exercise_records = []

# 목표 설정
def set_goal_duration():
    st.sidebar.title("목표 설정")
    goal_duration = st.sidebar.number_input("주간 목표 운동 시간 (분)", min_value=0, step=1)
    if st.session_state.goal_duration != goal_duration:
        st.session_state.goal_duration = goal_duration

# 운동 기록 입력
def record_exercise():
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
            st.session_state.exercise_records.append((date, exercise_type, duration, calories))
            st.success(f"운동 기록이 저장되었습니다. 소모한 칼로리: {calories} kcal")

# 운동 기록 불러오기
def load_exercise_records():
    df = pd.DataFrame(st.session_state.exercise_records, columns=['date', 'exercise_type', 'duration', 'calories'])
    df['date'] = pd.to_datetime(df['date'])
    return df

# 주간 운동 시간 계산
def calculate_weekly_duration(df):
    current_week = datetime.today().isocalendar()[1]
    weekly_duration = df[df['date'].dt.isocalendar().week == current_week]['duration'].sum()
    return weekly_duration

# 주간 목표 달성률 시각화
def visualize_goal_progress(weekly_duration):
    st.sidebar.write("### 주간 목표 달성률")
    st.sidebar.progress(min(1, weekly_duration / st.session_state.goal_duration) if st.session_state.goal_duration > 0 else 0)

# 데이터 시각화
def visualize_data(df):
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
        df.groupby('exercise_type')['calories'].sum().plot(kind='barh', ax=ax)  # 가로 막대 그래프로 변경
        ax.set_xlabel("칼로리 소모량 (kcal)")  # x축 라벨 추가
        ax.set_ylabel("운동 종류")  # y축 라벨 추가
        st.pyplot(fig)
    else:
        st.write("운동 기록이 없습니다.")

# 메인 함수
def main():
    initialize_goal_duration()
    initialize_exercise_records()
    set_goal_duration()
    record_exercise()
    df = load_exercise_records()
    weekly_duration = calculate_weekly_duration(df)
    visualize_goal_progress(weekly_duration)
    visualize_data(df)

if __name__ == "__main__":
    main()
