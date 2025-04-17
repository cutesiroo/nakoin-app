# 🃏 나코인 v14 통합판 - 도윤의 카드 배틀 앱 최종버전
# 기능: 로그인, 카드 뽑기 (애니메이션 + 사운드), 카드 일러스트, 덱 구성, 배틀 시각화 포함

import streamlit as st
import random
import json
import os
import time
from datetime import datetime

# 설정
st.set_page_config(page_title="나코인 v14", layout="wide")
USER_FOLDER = "users"
os.makedirs(USER_FOLDER, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")

# 등급별 일러스트
CARD_IMAGES = {
    "일반": "https://picsum.photos/seed/common/400/225",
    "고급": "https://picsum.photos/seed/rare/400/225",
    "희귀": "https://picsum.photos/seed/epic/400/225",
    "영웅": "https://picsum.photos/seed/hero/400/225",
    "전설": "https://picsum.photos/seed/legend/400/225",
    "비밀": "https://picsum.photos/seed/secret/400/225"
}

GRADE_POOL = {
    "일반": 50,
    "고급": 25,
    "희귀": 15,
    "영웅": 7,
    "전설": 2,
    "비밀": 1
}
GRADE_LIST = list(GRADE_POOL.keys())
grade_counts = {g: 0 for g in GRADE_POOL}

# 로그인 처리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🎮 나코인 로그인")
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
            user_data = {"password": password, "cards": {}, "deck": [], "history": []}
            with open(user_file, 'w') as f:
                json.dump(user_data, f)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# 유저 파일 로드
username = st.session_state.username
USER_FILE = os.path.join(USER_FOLDER, f"{username}.json")
with open(USER_FILE, 'r') as f:
    user_data = json.load(f)

# 로그아웃 버튼
if st.button("🔓 로그아웃"):
    st.session_state.clear()
    st.rerun()

# 메뉴
menu = st.sidebar.radio("🌟 메뉴 선택", ["카드 뽑기", "내 카드", "덱 구성", "배틀"])

# 1. 카드 뽑기
if menu == "카드 뽑기":
    st.title("🎁 카드 뽑기")
    if st.button("🧪 한 장 뽑기!"):
        with st.spinner("카드를 소환 중..."):
            time.sleep(1.5)
        grade = random.choices(list(GRADE_POOL.keys()), weights=GRADE_POOL.values())[0]
        grade_counts[grade] += 1
        name = f"{grade} {grade_counts[grade]}"
        img_url = CARD_IMAGES.get(grade)
        user_data["cards"][name] = {
            "grade": grade,
            "image": img_url,
            "ability": "능력 미지정"
        }
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)
        st.success(f"{grade} 카드 '{name}' 을 획득했습니다!")
        st.image(img_url, caption=f"{name} - {grade}", use_column_width=True)

# 2. 카드 목록
elif menu == "내 카드":
    st.title("📦 보유 카드 목록")
    cards = user_data.get("cards", {})
    if not cards:
        st.info("아직 카드가 없습니다. 먼저 뽑기를 해보세요.")
    else:
        for name, info in cards.items():
            st.markdown(f"### {name}")
            st.image(info["image"], width=300)
            st.markdown(f"등급: `{info['grade']}`")
            st.markdown(f"능력: `{info['ability']}`")
            st.markdown("---")

# 3. 덱 구성
elif menu == "덱 구성":
    st.title("🧩 덱 구성하기 (최대 5장)")
    all_cards = list(user_data["cards"].keys())
    selected = st.multiselect("덱에 추가할 카드 선택", all_cards, default=user_data.get("deck", []), max_selections=5)
    if selected:
        user_data["deck"] = selected
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)
        st.success("덱이 저장되었습니다!")
    for name in selected:
        st.markdown(f"- {name} ({user_data['cards'][name]['grade']})")

# 4. 배틀
elif menu == "배틀":
    st.title("⚔️ 카드 배틀 시뮬레이션")
    deck = user_data.get("deck", [])[:5]
    if not deck:
        st.warning("덱이 비어 있습니다.")
        st.stop()
    enemy_deck = random.sample(list(user_data["cards"].keys()), len(deck)) if len(user_data["cards"]) >= 2 else deck
    st.markdown("👑 **내 덱**")
    for name in deck:
        st.markdown(f"- {name} ({user_data['cards'][name]['grade']})")
    st.markdown("💀 **적 덱**")
    for name in enemy_deck:
        st.markdown(f"- {name} ({user_data['cards'][name]['grade']})")
    if st.button("전투 시작!"):
        st.subheader("📜 전투 로그")
        score = 0
        for my_card, enemy_card in zip(deck, enemy_deck):
            my_g = GRADE_LIST.index(user_data["cards"][my_card]["grade"])
            en_g = GRADE_LIST.index(user_data["cards"][enemy_card]["grade"])
            delta = my_g - en_g + random.choice([-1, 0, 1])
            if delta > 0:
                st.success(f"🟢 {my_card} ➤ {enemy_card} 승리")
                score += 1
            elif delta == 0:
                st.info(f"🟡 {my_card} ↔ {enemy_card} 무승부")
            else:
                st.error(f"🔴 {my_card} ⇦ {enemy_card} 패배")
                score -= 1
        st.markdown("---")
        if score > 0:
            st.balloons()
            st.success("🏆 최종 승리!")
        elif score == 0:
            st.info("⚖️ 무승부")
        else:
            st.error("💥 최종 패배...")
