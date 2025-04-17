# 🃏 나코인 v12 - 코인 제거 + 카드배틀 게임 전환 (들여쓰기 오류 수정)
import streamlit as st
import random
import json
import os
import pandas as pd
import base64
import time
from datetime import datetime

st.set_page_config(page_title="카드배틀 아레나", layout="wide")

USER_FOLDER = "users"
os.makedirs(USER_FOLDER, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")

# 테마 설정
THEMES = {
    "밝은 테마": {"bg": "#f8f5ef", "card": "#ffffff", "border": "#dcd4b6", "toolbar": "#ede4d1"},
    "어두운 테마": {"bg": "#2b2b2b", "card": "#3a3a3a", "border": "#555", "toolbar": "#444"},
    "나무 테마": {"bg": "#f5f0e1", "card": "#f7f2e8", "border": "#c9bfa4", "toolbar": "#e4d3b2"}
}

if "theme" not in st.session_state:
    st.session_state.theme = "밝은 테마"

THEME = THEMES[st.session_state.theme]

# 스타일
st.markdown(f"""
<style>
body {{ background-color: {THEME['bg']}; }}
.card {{
    background-color: {THEME['card']};
    border-radius: 20px;
    box-shadow: 6px 6px 18px rgba(0,0,0,0.08);
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 2px solid {THEME['border']};
    animation: fadein 0.8s ease-in;
    width: 100%;
}}
.card img {{
    border-radius: 16px;
    margin-bottom: 1rem;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
}}
.toolbar {{
    background-color: {THEME['toolbar']};
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
}}
</style>
""", unsafe_allow_html=True)

# 로그인
st.title("카드배틀 아레나")
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
            "people": {
                "존미니": {"owned": 1, "image": "", "trait": "안정형", "ability": "가격이 급격히 하락하지 않음", "grade": "일반"},
                "지민": {"owned": 1, "image": "", "trait": "공격형", "ability": "드물게 큰 상승폭 발생", "grade": "고급"},
                "서준": {"owned": 1, "image": "", "trait": "인기형", "ability": "인기도가 빠르게 변함", "grade": "일반"},
                "하나": {"owned": 1, "image": "", "trait": "지능형", "ability": "전투 시 자동 대응", "grade": "희귀"},
                "강태": {"owned": 1, "image": "", "trait": "탱커형", "ability": "타격 반감 능력 보유", "grade": "영웅"},
                "리아": {"owned": 1, "image": "", "trait": "전설형", "ability": "첫 턴에 선공 보장", "grade": "전설"},
                "???": {"owned": 0, "image": "", "trait": "암호화", "ability": "조건 해금 필요", "grade": "비밀"}
            }
        }
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)
    st.success(f"{username}님 환영합니다!")
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.data = user_data

if not st.session_state.get("logged_in"):
    st.stop()

people = st.session_state.data['people']

# 덱 초기화
if "deck" not in st.session_state:
    st.session_state.deck = []

menu = st.sidebar.radio("메뉴", ["보유 카드", "덱 구성", "배틀", "뽑기"])

# HUD
st.markdown(f"""
<div class='toolbar'>
    <div>🎴 사용자: {username}</div>
    <div>🧩 보유 카드 수: {sum(p['owned'] for p in people.values())}장</div>
</div>
""", unsafe_allow_html=True)

def show_image(base64_data):
    if base64_data:
        return base64.b64decode(base64_data.encode())
    return None

if menu == "보유 카드":
    st.subheader("보유 중인 카드")
    for name, info in people.items():
        if info['owned'] > 0:
            st.markdown(f"**{name}** [{info['grade']}] - {info['ability']}")

elif menu == "덱 구성":
    st.subheader("내 카드 덱 구성하기 (최대 5장)")
    available_cards = [name for name, data in people.items() if data['owned'] > 0]
    selected = st.multiselect("카드를 선택하세요", available_cards, default=st.session_state.deck, max_selections=5)
    if selected:
        st.session_state.deck = selected
        st.success("덱이 저장되었습니다!")
    for name in st.session_state.deck:
        st.markdown(f"- {name} [{people[name]['grade']}] — {people[name]['ability']}")

elif menu == "배틀":
    st.subheader("배틀 시뮬레이션")
    deck = st.session_state.get("deck", [])
    if not deck:
        st.warning("덱에 최소 1장 이상이 필요합니다.")
    else:
        enemy_pool = [k for k in people if k not in deck]
        enemy_deck = random.sample(enemy_pool, min(5, len(enemy_pool)))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 내 덱")
            for name in deck:
                st.markdown(f"- {name} ({people[name]['grade']})")
        with col2:
            st.markdown("#### 상대 덱")
            for name in enemy_deck:
                st.markdown(f"- {name} ({people[name]['grade']})")
        if st.button("전투 시작!"):
            st.subheader("📜 전투 로그")
            score = 0
            for me, en in zip(deck, enemy_deck):
                my_lv = ["일반", "고급", "희귀", "영웅", "전설", "비밀"].index(people[me]["grade"])
                en_lv = ["일반", "고급", "희귀", "영웅", "전설", "비밀"].index(people[en]["grade"])
                result = my_lv - en_lv + random.randint(-1, 1)
                if result > 0:
                    st.success(f"{me} → {en} 승리")
                    score += 1
                elif result == 0:
                    st.info(f"{me} ↔ {en} 무승부")
                else:
                    st.error(f"{me} ← {en} 패배")
                    score -= 1
            if score > 0:
                st.success("🎉 최종 승리!")
            elif score == 0:
                st.info("⚖️ 무승부")
            else:
                st.error("😭 최종 패배...")

# 뽑기 기능
elif menu == "뽑기":
    st.subheader("🎁 카드 뽑기")
    card_pool = [
        ("일반", 50), ("고급", 25), ("희귀", 15), ("영웅", 7), ("전설", 2), ("비밀", 1)
    ]
    card_defs = {
        "일반": ["준기", "보라"],
        "고급": ["다온"],
        "희귀": ["시우"],
        "영웅": ["세아"],
        "전설": ["루카"],
        "비밀": ["X"]
    }
if st.button("한 장 뽑기!"):
    with st.spinner("✨ 카드를 소환 중..."):
        time.sleep(1.5)
        grades, probs = zip(*card_pool)
        grade = random.choices(grades, weights=probs)[0]
        # 이름 자동 생성
        count = sum(1 for k, v in people.items() if v.get('grade') == grade and k.startswith(grade)) + 1
        name = f"{grade} {count}"
        st.success(f"🎉 {name} [{grade}] 카드를 뽑았습니다!")
        if name not in people:
            people[name] = {"owned": 1, "image": "", "trait": f"{grade}형", "ability": "능력 미지정", "grade": grade}
        else:
            people[name]['owned'] += 1

# 저장
with open(os.path.join(USER_FOLDER, f"{username}.json"), 'w') as f:
    json.dump(st.session_state.data, f)
