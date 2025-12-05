# album_recommender_demo.py

# 점수에 사용하는 속성 (length는 필터 전용)
ATTRS = ["tempo", "energy", "brightness", "focus"]

# ===== 30개 앨범 데이터 =====
ALBUMS = [
    {
        "artist": "Pretenders",
        "title": "Pretenders",
        "tempo": 3, "energy": 3, "brightness": 3, "focus": 3, "length": 3
    },
    {
        "artist": "Joy Division",
        "title": "Closer",
        "tempo": 1, "energy": 2, "brightness": 0, "focus": 4, "length": 2
    },
    {
        "artist": "T. Rex",
        "title": "Electric Warrior",
        "tempo": 2, "energy": 3, "brightness": 4, "focus": 2, "length": 2
    },
    {
        "artist": "The Runaways",
        "title": "The Runaways",
        "tempo": 3, "energy": 4, "brightness": 2, "focus": 1, "length": 2
    },
    {
        "artist": "Sleigh Bells",
        "title": "Treats",
        "tempo": 4, "energy": 4, "brightness": 4, "focus": 3, "length": 2
    },
    {
        "artist": "Tina Turner",
        "title": "Private Dancer",
        "tempo": 2, "energy": 4, "brightness": 3, "focus": 1, "length": 2
    },
    {
        "artist": "Linda Perhacs",
        "title": "Parallelograms",
        "tempo": 1, "energy": 0, "brightness": 4, "focus": 3, "length": 2
    },
    {
        "artist": "The Replacements",
        "title": "Let It Be",
        "tempo": 3, "energy": 4, "brightness": 3, "focus": 2, "length": 2
    },
    {
        "artist": "Bauhaus",
        "title": "In the Flat Field",
        "tempo": 3, "energy": 4, "brightness": 0, "focus": 4, "length": 2
    },
    {
        "artist": "Simon & Garfunkel",
        "title": "Bookends",
        "tempo": 2, "energy": 3, "brightness": 4, "focus": 2, "length": 1
    },
    {
        "artist": "Alvvays",
        "title": "Blue Rev",
        "tempo": 4, "energy": 3, "brightness": 2, "focus": 3, "length": 2
    },
    {
        "artist": "that dog.",
        "title": "Retreat From the Sun",
        "tempo": 3, "energy": 4, "brightness": 3, "focus": 3, "length": 3
    },
    {
        "artist": "Kleenex",
        "title": "LiLiPut",
        "tempo": 4, "energy": 4, "brightness": 4, "focus": 4, "length": 5
    },
    {
        "artist": "N.W.A",
        "title": "Straight Outta Compton",
        "tempo": 3, "energy": 4, "brightness": 1, "focus": 2, "length": 4
    },
    {
        "artist": "Galaxie 500",
        "title": "On Fire",
        "tempo": 1, "energy": 1, "brightness": 3, "focus": 2, "length": 2
    },
    {
        "artist": "The Clash",
        "title": "London Calling",
        "tempo": 3, "energy": 4, "brightness": 3, "focus": 3, "length": 4
    },
    {
        "artist": "The Raincoats",
        "title": "The Raincoats",
        "tempo": 3, "energy": 2, "brightness": 4, "focus": 4, "length": 2
    },
    {
        "artist": "Sigur Rós",
        "title": "Ágætis byrjun",
        "tempo": 1, "energy": 1, "brightness": 0, "focus": 4, "length": 4
    },
    {
        "artist": "Ramones",
        "title": "Ramones",
        "tempo": 5, "energy": 4, "brightness": 2, "focus": 3, "length": 1
    },
    {
        "artist": "The Beatles",
        "title": "The White Album",
        "tempo": 2, "energy": 2, "brightness": 2, "focus": 3, "length": 4
    },
    {
        "artist": "Suburban Lawns",
        "title": "Suburban Lawns",
        "tempo": 4, "energy": 4, "brightness": 2, "focus": 3, "length": 1
    },
    {
        "artist": "The Magnetic Fields",
        "title": "69 Love Songs",
        "tempo": 1, "energy": 1, "brightness": 2, "focus": 2, "length": 5
    },
    {
        "artist": "Young Marble Giants",
        "title": "Colossal Youth",
        "tempo": 1, "energy": 0, "brightness": 1, "focus": 4, "length": 2
    },
    {
        "artist": "Traveling Wilburys",
        "title": "The Traveling Wilburys, Vol. 1",
        "tempo": 3, "energy": 3, "brightness": 3, "focus": 1, "length": 2
    },
    {
        "artist": "Lizzy Mercier Descloux",
        "title": "Press Color",
        "tempo": 2, "energy": 1, "brightness": 1, "focus": 4, "length": 1
    },
    {
        "artist": "Moloko",
        "title": "Do You Like My Tight Sweater?",
        "tempo": 2, "energy": 0, "brightness": 1, "focus": 3, "length": 4
    },
    {
        "artist": "The Go! Team",
        "title": "Thunder, Lightning, Strike",
        "tempo": 4, "energy": 4, "brightness": 4, "focus": 2, "length": 2
    },
    {
        "artist": "Cate Le Bon",
        "title": "Pompeii",
        "tempo": 1, "energy": 1, "brightness": 2, "focus": 4, "length": 2
    },
    {
        "artist": "Mission of Burma",
        "title": "Signals, Calls and Marches",
        "tempo": 3, "energy": 3, "brightness": 2, "focus": 4, "length": 1
    },
    {
        "artist": "The Sundays",
        "title": "Static & Silence",
        "tempo": 2, "energy": 1, "brightness": 1, "focus": 2, "length": 2
    }
]

# ===== 질문 정의 =====

QUESTIONS = [
    {
        "key": "tempo",
        "text": "Q1. 지금 듣고 싶은 템포는?",
        "options": [
            ("1", "매우 느린 편", 1),
            ("2", "조금 느린 편", 2),
            ("3", "적당한 템포", 3),
            ("4", "조금 빠른 편", 4),
            ("5", "매우 빠른 편", 5)
        ]
    },
    {
        "key": "energy",
        "text": "Q2. 지금 듣고 싶은 에너지 레벨은?",
        "options": [
            ("1", "매우 잔잔하고 힘 안 쓰는 느낌", 0),
            ("2", "좀 차분한 편", 1),
            ("3", "중간 정도", 2),
            ("4", "꽤 힘 있고 드라이브감 있는 편", 3),
            ("5", "아주 강하고 몰아치는 느낌", 4)
        ]
    },
    {
        "key": "brightness",
        "text": "Q3. 지금 원하는 분위기(밝기)는?",
        "options": [
            ("1", "아주 어둡고 무거운 느낌", 0),
            ("2", "조금 어두운 편", 1),
            ("3", "중간/중립", 2),
            ("4", "꽤 밝은 편", 3),
            ("5", "아주 반짝이고 밝은 느낌", 4)
        ]
    },
    {
        "key": "focus",
        "text": "Q4. 지금 음악에 어느 정도 집중할 수 있어?",
        "options": [
            ("1", "거의 집중 못 함, 그냥 배경용", 1),
            ("2", "조금은 집중 가능", 2),
            ("3", "적당히 집중 가능", 3),
            ("4", "꽤 집중해서 들을 수 있음", 4),
            ("5", "완전 몰입해서 듣고 싶음", 5)
        ]
    },
    {
        "key": "length",
        "text": "Q5. 지금 앨범을 들을 수 있는 시간은?",
        "options": [
            ("1", "30분 이하", 1),
            ("2", "45분 이하", 2),
            ("3", "1시간 이하", 3),
            ("4", "2시간 이하", 4),
            ("5", "2시간 이상", 5)
        ]
    }
]


def ask_questions():
    user_state = {}
    print("\n지금 상태를 간단하게 알려줘. 거기에 맞춰 앨범을 골라볼게.\n")

    for q in QUESTIONS:
        print(q["text"])
        for code, label, value in q["options"]:
            print(f"  {code}) {label}")

        answer = input("번호 선택: ").strip()
        valid_codes = {code for code, _, _ in q["options"]}

        while answer not in valid_codes:
            print("잘못 입력했어. 1~5 중에서 다시 골라줘.")
            answer = input("번호 선택: ").strip()

        for code, label, value in q["options"]:
            if code == answer:
                user_state[q["key"]] = value
                break

        print()

    return user_state


def score_album(album, user_state):
    score = 0

    for attr in ATTRS:
        if attr == "focus":
            # 몰입도: 사용자가 감당 가능한 수준을 넘으면 감점, 이하면 0점
            diff = album["focus"] - user_state["focus"]

            if diff <= 0:
                attr_score = 0           # 내 집중 한도 이하면 페널티 없음
            elif diff == 1:
                attr_score = -3          # 살짝 더 요구하면 중간 감점
            else:  # diff >= 2
                attr_score = -5          # 훨씬 더 요구하면 큰 감점
        else:
            # tempo / energy / brightness: 감점제
            diff = abs(album[attr] - user_state[attr])

            if diff == 0:
                attr_score = 5   # 완전 일치
            elif diff == 1:
                attr_score = 3   # 거의 일치
            elif diff == 2:
                attr_score = 0   # 애매하면 영향 없음
            elif diff == 3:
                attr_score = -3  # 꽤 안 맞으면 감점
            else:  # diff >= 4
                attr_score = -5  # 완전 반대면 큰 감점

        score += attr_score

    return score


def recommend(user_state, top_k=3):
    user_len = user_state["length"]

    # 1) 길이 필터: 사용자가 들을 수 있는 시간보다 긴 앨범은 제외
    filtered_albums = [
        album for album in ALBUMS
        if album["length"] <= user_len
    ]

    # 길이 조건에 맞는 앨범이 하나도 없으면 추천 불가
    if not filtered_albums:
        return []

    # 2) 점수 계산
    scored = []
    for album in filtered_albums:
        s = score_album(album, user_state)
        scored.append((s, album))

    scored.sort(
    key=lambda x: (-x[0], abs(x[1]["length"] - user_len))
)
    return scored[:top_k]


def main():
    print("🎧 앨범 추천 데모 프로그램 🎧\n")
    input("Enter 키를 눌러 시작하세요...")

    user_state = ask_questions()
    results = recommend(user_state, top_k=3)

    if not results:
        print("\n현재 선택한 시간 안에 들을 수 있는 앨범이 없어요.")
        print("조금 더 넉넉한 시간을 선택해서 다시 시도해줘! 🙂")
        return

    print("===== 추천 결과 TOP 3 =====\n")
    for i, (score, album) in enumerate(results, start=1):
        print(f"{i}. {album['artist']} – {album['title']}  | 점수: {score}")

    print("\n즐거운 감상 되세요! 🎵")


if __name__ == "__main__":
    main()
