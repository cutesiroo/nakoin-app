import streamlit as st
import random
import json
import os
import pandas as pd
import time

# 로그인 및 사용자별 저장
st.set_page_config(page_title="나코인 거래소", layout="wide")

st.title("🔐 나코인 거래소 - 로그인")

username = st.text_input("닉네임을 입력하세요")
password = st.text_input("비밀번호를 입력하세요", type="password")
login_btn = st.button("로그인")

if login_btn and username and password:
    USER_FOLDER = "users"
    os.makedirs(USER_FOLDER, exist_ok=True)
    USER_FILE = os.path.join(USER_FOLDER, f"{username}.json")

    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            user_data = json.load(f)
            if user_data.get("password") != password:
                st.error("❌ 비밀번호가 일치하지 않습니다.")
                st.stop()
    else:
        user_data = {
            "password": password,
            "balance": 50000,
            "people": {
                "존미니": {"price": 1000, "popularity": 75, "owned": 0, "history": [1000]},
                "지민": {"price": 1200, "popularity": 90, "owned": 0, "history": [1200]},
                "서준": {"price": 800, "popularity": 45, "owned": 0, "history": [800]}
            }
        }
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)

    st.success(f"✅ {username}님 환영합니다!")
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.data = user_data

if not st.session_state.get("logged_in"):
    st.stop()

# 이후 기존 나코인 기능 실행
balance = st.session_state.data['balance']
people = st.session_state.data['people']

CHARACTER_TRAITS = {
    "존미니": "📈 안정형 (변동폭 작음)",
    "지민": "⚡ 공격형 (가격 변동 큼)",
    "서준": "🎯 인기형 (인기도 잘 변동됨)"
}

SECRET_CHARACTER = {
    "코드네임X": {
        "price": 2000,
        "popularity": 95,
        "owned": 0,
        "history": [2000],
        "secret": True,
        "unlocked": False
    }
}

if balance >= 70000 and "코드네임X" not in people:
    people.update(SECRET_CHARACTER)
    people["코드네임X"]["unlocked"] = True
    st.balloons()
    st.success("🎉 비밀 캐릭터 '코드네임X' 해금!")

for name, person in people.items():
    if name == "지민":
        delta_price = random.randint(-300, 300)
    elif name == "존미니":
        delta_price = random.randint(-80, 80)
    else:
        delta_price = random.randint(-150, 150)

    if name == "서준":
        delta_pop = random.randint(-5, 5)
    else:
        delta_pop = random.randint(-3, 3)

    person['price'] = max(100, person['price'] + delta_price)
    person['popularity'] = min(100, max(0, person['popularity'] + delta_pop))
    person['history'].append(person['price'])

menu = st.sidebar.radio("🎮 메뉴 선택", ["🏠 대시보드", "🛒 거래하기", "📈 차트 보기", "🧍 신규 상장"])

st.title(f"🪙 {username}님의 나코인 거래소")

def get_grade(pop):
    if pop >= 90:
        return "⭐️⭐️⭐️ 레전드"
    elif pop >= 70:
        return "⭐️⭐️ 하트"
    elif pop >= 40:
        return "⭐️ 보통"
    else:
        return "💩 비호감"

def get_ai_recommendations(people):
    ranked = sorted(people.items(), key=lambda x: x[1]['popularity'] / max(x[1]['price'], 1), reverse=True)
    return ranked[:3]

def get_ranking():
    ranks = []
    for file in os.listdir("users"):
        if file.endswith(".json"):
            with open(os.path.join("users", file), 'r') as f:
                data = json.load(f)
                total = data['balance'] + sum(p['owned'] * p['price'] for p in data['people'].values())
                ranks.append((file.replace(".json", ""), total))
    return sorted(ranks, key=lambda x: x[1], reverse=True)

if menu == "🏠 대시보드":
    st.subheader("🤖 AI 추천 TOP3")
    for name, info in get_ai_recommendations(people):
        trait = CHARACTER_TRAITS.get(name, "")
        st.markdown(f"💡 **{name}** {trait} — 💵 {info['price']} | 🔥 {info['popularity']} | 🏷 {get_grade(info['popularity'])}")
        time.sleep(0.1)
    st.markdown(f"### 💰 현재 잔고: `{balance}` 원")

    st.subheader("🏆 전체 유저 랭킹")
    for i, (user, score) in enumerate(get_ranking(), 1):
        st.markdown(f"{i}위. **{user}** — 총 자산: {score}원")

elif menu == "🛒 거래하기":
    st.subheader("🎯 인물 코인 거래")
    selected = st.selectbox("👤 인물 선택", list(people.keys()))
    p = people[selected]
    st.markdown(f"**💲 {selected}** — 가격: `{p['price']}` | 인기: `{p['popularity']}` | 등급: `{get_grade(p['popularity'])}` | 보유: `{p['owned']}`개")

    col1, col2 = st.columns(2)
    with col1:
        qty = st.number_input("구매 수량", min_value=1, value=1, key="buy")
        if st.button("🛒 구매"):
            cost = qty * p['price']
            if balance >= cost:
                p['owned'] += qty
                st.session_state.data['balance'] -= cost
                st.success(f"🎉 {selected} 코인 {qty}개 구매 완료!")
            else:
                st.error("❌ 잔고 부족")

    with col2:
        qty2 = st.number_input("판매 수량", min_value=1, value=1, key="sell")
        if st.button("💵 판매"):
            if p['owned'] >= qty2:
                p['owned'] -= qty2
                st.session_state.data['balance'] += qty2 * p['price']
                st.success(f"💸 {selected} 코인 {qty2}개 판매 완료!")
            else:
                st.error("❌ 보유 수량 부족")

elif menu == "📈 차트 보기":
    st.subheader("📊 가격 추이 차트")
    chart_data = {name: pd.Series(info['history'][-20:]) for name, info in people.items()}
    st.line_chart(pd.DataFrame(chart_data))

elif menu == "🧍 신규 상장":
    st.subheader("🧬 새로운 코인 상장하기")
    new_name = st.text_input("🔤 이름")
    new_price = st.number_input("💸 시작 가격", min_value=100, value=1000)
    new_pop = st.slider("🔥 인기도", 0, 100, 50)

    if st.button("🚀 상장하기"):
        if new_name in people:
            st.error("⚠️ 이미 존재하는 인물입니다.")
        elif st.session_state.data['balance'] < 10000:
            st.error("❌ 수수료 부족 (1만 원 필요)")
        else:
            people[new_name] = {
                "price": new_price,
                "popularity": new_pop,
                "owned": 0,
                "history": [new_price]
            }
            st.session_state.data['balance'] -= 10000
            st.success(f"🎉 {new_name} 상장 완료!")

# 자동 저장 (개별 유저 저장)
with open(os.path.join("users", f"{username}.json"), 'w') as f:
    json.dump(st.session_state.data, f)
