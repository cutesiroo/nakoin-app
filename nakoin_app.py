# 🪙 나코인 v8 - 툴바 & 카드 크기 확대 버전
import streamlit as st
import random
import json
import os
import pandas as pd
import time
import base64
from datetime import datetime

st.set_page_config(page_title="나코인 거래소", layout="wide")

USER_FOLDER = "users"
os.makedirs(USER_FOLDER, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")

# 🔧 스타일: 툴바 크기 확장 + 카드 확대
st.markdown("""
<style>
body {
    background-color: #f8f5ef;
    font-family: 'Verdana';
}
.stApp {
    background-color: #f8f5ef;
}
.card {
    background-color: #fff;
    border-radius: 20px;
    box-shadow: 6px 6px 18px rgba(0,0,0,0.08);
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 2px solid #dcd4b6;
    animation: fadein 0.8s ease-in;
    width: 100%;
}
.card img {
    border-radius: 16px;
    margin-bottom: 1rem;
    max-height: 280px;
}
.stButton>button {
    background-color: #b0d8c5;
    border-radius: 10px;
    padding: 0.6em 2em;
    font-size: 1.1em;
    border: none;
    color: #2c2c2c;
    font-weight: bold;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #9ccab0;
    transform: scale(1.05);
}
@keyframes fadein {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}
.toolbar {
    background-color: #ede4d1;
    padding: 18px 30px;
    border-radius: 20px;
    margin-bottom: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 22px;
    font-weight: bold;
    color: #2f2f2f;
    box-shadow: 4px 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# 로그인
st.title("나코인 거래소")
username = st.text_input("닉네임")
password = st.text_input("비밀번호", type="password")
login_btn = st.button("로그인")

if login_btn and username and password:
    USER_FILE = os.path.join(USER_FOLDER, f"{username}.json")

    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            user_data = json.load(f)
            if user_data.get("password") != password:
                st.error("비밀번호가 일치하지 않습니다.")
                st.stop()
    else:
        user_data = {
            "password": password,
            "balance": 50000,
            "people": {
                "존미니": {"price": 1000, "popularity": 75, "owned": 0, "history": [1000], "image": "", "trait": "안정형"},
                "지민": {"price": 1200, "popularity": 90, "owned": 0, "history": [1200], "image": "", "trait": "공격형"},
                "서준": {"price": 800, "popularity": 45, "owned": 0, "history": [800], "image": "", "trait": "인기형"}
            },
            "last_login": ""
        }
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)

    st.success(f"{username}님 환영합니다!")
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.data = user_data

if not st.session_state.get("logged_in"):
    st.stop()

balance = st.session_state.data['balance']
people = st.session_state.data['people']
last_login = st.session_state.data.get("last_login", "")

# HUD 툴바
st.markdown(f"""
<div class='toolbar'>
    <div>👤 사용자: {username}</div>
    <div>💰 잔고: {balance:,} 원</div>
</div>
""", unsafe_allow_html=True)

# 출석 보상
if last_login != TODAY:
    bonus = random.randint(3000, 10000)
    balance += bonus
    st.session_state.data['balance'] = balance
    st.session_state.data['last_login'] = TODAY
    st.toast(f"출석 보상 지급: +{bonus}원")

# 가격 변동 + 이벤트
if random.randint(1, 10) == 1:
    st.info("모든 캐릭터 가격이 20% 상승했습니다!")
    for p in people.values():
        p['price'] = int(p['price'] * 1.2)

for name, p in people.items():
    trait = p.get("trait", "")
    if trait == "공격형":
        dp = random.randint(-300, 300)
    elif trait == "안정형":
        dp = random.randint(-80, 80)
    else:
        dp = random.randint(-150, 150)
    p['price'] = max(100, p['price'] + dp)
    p['popularity'] = min(100, max(0, p['popularity'] + random.randint(-3, 3)))
    p['history'].append(p['price'])

menu = st.sidebar.radio("메뉴", ["대시보드", "거래소", "차트", "상장"])

def show_image(base64_data):
    if base64_data:
        return base64.b64decode(base64_data.encode())
    return None

if menu == "대시보드":
    st.subheader("보유 캐릭터")
    for name, info in people.items():
        if info['owned'] > 0:
            st.markdown(f"- {name} ({info['trait']}) — {info['owned']}개 | 가격 {info['price']} | 인기 {info['popularity']}")

elif menu == "거래소":
    st.subheader("캐릭터 거래")
    for name, info in people.items():
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            if info.get("image"):
                img = show_image(info['image'])
                st.image(img, use_column_width=True)
            st.markdown(f"<h3 style='margin-top:0;'>{name}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:18px;'>특성: {info['trait']}<br>가격: {info['price']}<br>인기: {info['popularity']}<br>보유: {info['owned']}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"{name} 구매", key=f"buy_{name}"):
                    if balance >= info['price']:
                        info['owned'] += 1
                        st.session_state.data['balance'] -= info['price']
                        st.toast(f"{name} 구매 완료")
                    else:
                        st.error("잔고 부족")
            with c2:
                if info['owned'] > 0 and st.button(f"{name} 판매", key=f"sell_{name}"):
                    info['owned'] -= 1
                    st.session_state.data['balance'] += info['price']
                    st.toast(f"{name} 판매 완료")
            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "차트":
    st.subheader("가격 변화 추이")
    df = pd.DataFrame({k: pd.Series(v['history'][-20:]) for k,v in people.items()})
    st.line_chart(df)

elif menu == "상장":
    st.subheader("새 캐릭터 상장")
    new_name = st.text_input("이름")
    new_price = st.number_input("시작 가격", min_value=100, value=1000)
    new_pop = st.slider("인기도", 0, 100, 50)
    new_trait = st.selectbox("특성", ["안정형", "공격형", "인기형"])
    new_img = st.file_uploader("이미지 업로드 (선택)", type=["jpg", "png", "jpeg"])

    if st.button("상장하기"):
        if new_name in people:
            st.error("이미 존재하는 캐릭터입니다")
        elif balance < 10000:
            st.error("수수료 부족 (1만 원 필요)")
        else:
            img_base64 = base64.b64encode(new_img.read()).decode() if new_img else ""
            people[new_name] = {
                "price": new_price,
                "popularity": new_pop,
                "owned": 0,
                "history": [new_price],
                "trait": new_trait,
                "image": img_base64
            }
            st.session_state.data['balance'] -= 10000
            st.success(f"{new_name} 상장 완료")

# 저장
with open(os.path.join(USER_FOLDER, f"{username}.json"), 'w') as f:
    json.dump(st.session_state.data, f)
