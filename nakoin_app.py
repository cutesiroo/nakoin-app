import streamlit as st
import random
import json
import os
import pandas as pd

# 파일명
SAVE_FILE = "nakoin_data.json"

# 기본값 초기화
def default_data():
    return {
        "balance": 10000,
        "people": {
            "존미니": {"price": 1000, "popularity": 75, "owned": 0, "history": [1000]},
            "지민": {"price": 1200, "popularity": 90, "owned": 0, "history": [1200]},
            "서준": {"price": 800, "popularity": 45, "owned": 0, "history": [800]},
        }
    }

# 저장된 데이터 불러오기
def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    else:
        return default_data()

# 데이터 저장
def save_data(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

# 등급 판별
def get_grade(pop):
    if pop >= 90:
        return "⭐️⭐️⭐️ 레전드"
    elif pop >= 70:
        return "⭐️⭐️ 하트"
    elif pop >= 40:
        return "⭐️ 보통"
    else:
        return "💩 비호감"

# AI 추천 TOP3 (인기도 / 가격)
def get_ai_recommendations(people):
    ranked = sorted(people.items(), key=lambda x: x[1]['popularity'] / max(x[1]['price'], 1), reverse=True)
    return ranked[:3]

# Streamlit 시작
st.set_page_config(page_title="나코인 거래소", layout="wide", initial_sidebar_state="expanded")
st.title("📈 나코인 (나를 판매하자!)")

# 세션 상태
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# 데이터 바인더
balance = st.session_state.data['balance']
people = st.session_state.data['people']

# 가격, 인기도 변동
for person in people.values():
    delta_price = random.randint(-150, 150)
    delta_pop = random.randint(-3, 3)
    person['price'] = max(100, person['price'] + delta_price)
    person['popularity'] = min(100, max(0, person['popularity'] + delta_pop))
    person['history'].append(person['price'])

# AI 추천
st.subheader("🤖 AI 추천 TOP3")
for name, info in get_ai_recommendations(people):
    st.markdown(f"**{name}** — 가격: {info['price']}, 인기도: {info['popularity']}, 등급: {get_grade(info['popularity'])}")

st.divider()
st.subheader(f"💰 현재 잔고: {balance} 원")

# 인물 목록
st.write("### 현재 사다 버 수 있는 인물 코인")
selected = st.selectbox("거래할 인물", list(people.keys()))
p = people[selected]

st.markdown(f"**💲 {selected}** — 가격: {p['price']} 원 | 인기도: {p['popularity']} | 등급: {get_grade(p['popularity'])} | 보유: {p['owned']} 개")

col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("규별", min_value=1, value=1, key="buy")
    if st.button("📅 구매"):
        cost = qty * p['price']
        if balance >= cost:
            p['owned'] += qty
            st.session_state.data['balance'] -= cost
            st.success(f"{selected} 구매 성공!")
        else:
            st.error("잔고가 부족합니다.")

with col2:
    qty2 = st.number_input("규별", min_value=1, value=1, key="sell")
    if st.button("💸 판매"):
        if p['owned'] >= qty2:
            p['owned'] -= qty2
            st.session_state.data['balance'] += qty2 * p['price']
            st.success(f"{selected} 판매 성공!")
        else:
            st.error("보유가 부족합니다.")

# 가격 차트
st.write("### 가격 변화 차트")
chart_data = {name: pd.Series(info['history'][-20:]) for name, info in people.items()}
st.line_chart(pd.DataFrame(chart_data))

# 새 인물 상장
st.divider()
st.write("### 🚀 새 인물 상장 (1만원 수수료)")
new_name = st.text_input("이름")
new_price = st.number_input("가격", min_value=100, value=1000)
new_pop = st.slider("인기도", 0, 100, 50)

if st.button("+ 상장"):
    if new_name in people:
        st.error("기존에 있는 인물입니다.")
    elif st.session_state.data['balance'] < 10000:
        st.error("수수료가 부족합니다.")
    else:
        people[new_name] = {
            "price": new_price,
            "popularity": new_pop,
            "owned": 0,
            "history": [new_price]
        }
        st.session_state.data['balance'] -= 10000
        st.success(f"{new_name} 상장 성공!")

# 자동 저장
save_data(st.session_state.data)
