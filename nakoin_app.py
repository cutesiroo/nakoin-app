# 🧩 덱 구성 추가
if "deck" not in st.session_state:
    st.session_state.deck = []

if menu == "덱 구성":
    st.subheader("내 카드 덱 구성하기 (최대 5장)")
    available_cards = [name for name, data in people.items() if data['owned'] > 0]
    selected = st.multiselect("카드를 선택하세요", available_cards, default=st.session_state.deck, max_selections=5)
    if selected:
        st.session_state.deck = selected
        st.success("덱이 저장되었습니다!")
    st.markdown("---")
    for name in st.session_state.deck:
        info = people[name]
        st.markdown(f"**{name}** [{info['grade']}] - {info['ability']}")

# ⚔️ 배틀 시스템 구현
if menu == "배틀":
    st.subheader("배틀 시뮬레이션")
    deck = st.session_state.get("deck", [])
    if len(deck) < 1:
        st.warning("덱에 카드가 최소 1장 이상 있어야 합니다.")
        st.stop()

    # 임의 적 덱 생성
    enemy_pool = [name for name in people.keys() if name not in deck]
    enemy_deck = random.sample(enemy_pool, min(5, len(enemy_pool)))

    st.markdown("### ⚔️ 우리 덱 vs 상대 덱")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### [내 덱]")
        for name in deck:
            st.markdown(f"- {name} ({people[name]['grade']})")
    with col2:
        st.markdown("#### [상대 덱]")
        for name in enemy_deck:
            st.markdown(f"- {name} ({people[name]['grade']})")

    if st.button("전투 시작!"):
        st.markdown("---")
        st.subheader("📜 전투 로그")
        total_score = 0
        for my_card, en_card in zip(deck, enemy_deck):
            my_level = ["일반", "고급", "희귀", "영웅", "전설", "비밀"].index(people[my_card]['grade']) + 1
            en_level = ["일반", "고급", "희귀", "영웅", "전설", "비밀"].index(people[en_card]['grade']) + 1
            result = my_level - en_level + random.randint(-1, 1)
            if result > 0:
                st.success(f"{my_card} 이(가) {en_card} 을(를) 이겼습니다!")
                total_score += 1
            elif result == 0:
                st.info(f"{my_card} 와 {en_card} 의 전투는 무승부입니다.")
            else:
                st.error(f"{my_card} 이(가) {en_card} 에게 패배했습니다.")
                total_score -= 1
        st.markdown("---")
        if total_score > 0:
            st.success("🎉 전투 승리!")
        elif total_score == 0:
            st.info("⚖️ 무승부")
        else:
            st.error("😭 전투 패배...")

# 메뉴에 '덱 구성', '배틀' 추가
menu = st.sidebar.radio("메뉴", ["대시보드", "거래소", "차트", "상장", "덱 구성", "배틀"])

# 저장
with open(os.path.join(USER_FOLDER, f"{username}.json"), 'w') as f:
    json.dump(st.session_state.data, f)
