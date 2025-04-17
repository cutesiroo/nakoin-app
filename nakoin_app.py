# 🃏 나코인 v14-1: 카드 UI + 뽑기 애니메이션 버전
import streamlit as st
import random
import json
import os
import time
from datetime import datetime

st.set_page_config(page_title="나코인 뽑기", layout="wide")
USER_FOLDER = "users"
os.makedirs(USER_FOLDER, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")

# 스타일 (카드 UI용)
st.markdown("""
<style>
.card {
    background-color: #2e2f3e;
    border-radius: 20px;
    box-shadow: 8px 8px 16px #141427, -8px -8px 16px #22224b;
    padding: 2rem;
    margin-bottom: 2rem;
    color: #f4f4f8;
    text-align: center;
    border: 1px solid #43445c;
}
</style>
""", unsafe_allow_html=True)

# 로그인
st.title("🎴 나코인 뽑기 v14-1")
username = st.text_input("닉네임")
password = st.text_input("비밀번호", type="password")
if st.button("로그인") and username and password:
    user_file = os.path.join(USER_FOLDER, f"{username}.json")
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        if user_data.get("password") != password:
            st.error("비밀번호가 틀렸습니다.")
            st.stop()
    else:
        user_data = {"password": password, "cards": {}, "history": []}
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
    st.session_state.logged_in = True
    st.session_state.username = username
    st.experimental_rerun()

if not st.session_state.get("logged_in"):
    st.stop()

username = st.session_state.username
USER_FILE = os.path.join(USER_FOLDER, f"{username}.json")
with open(USER_FILE, 'r') as f:
    user_data = json.load(f)

st.header("✨ 카드 뽑기")

GRADE_POOL = {
    "일반": 50,
    "고급": 25,
    "희귀": 15,
    "영웅": 7,
    "전설": 2,
    "비밀": 1
}
grade_counts = {g: 0 for g in GRADE_POOL}

if st.button("🧪 한 장 뽑기!"):
    with st.spinner("카드를 생성하는 중..."):
        time.sleep(1.5)
    grade = random.choices(list(GRADE_POOL.keys()), weights=GRADE_POOL.values())[0]
    grade_counts[grade] += 1
    name = f"{grade} {grade_counts[grade]}"
    user_data["cards"][name] = {
        "grade": grade,
        "ability": "능력 미지정"
    }
    with open(USER_FILE, 'w') as f:
        json.dump(user_data, f)
    st.success(f"{grade} 카드 '{name}' 을 뽑았습니다!")

    with st.container():
        st.markdown(f"<div class='card'><h2>{name}</h2><p>등급: {grade}</p><p>능력: 능력 미지정</p></div>", unsafe_allow_html=True)
