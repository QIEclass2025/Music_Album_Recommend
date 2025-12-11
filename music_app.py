# music_app.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# 🔹 MusicBrainz 라이브러리
import musicbrainzngs

# ==========================================
# 0. MusicBrainz API 설정
# ==========================================
musicbrainzngs.set_useragent(
    "MusicRecommenderDemo",
    "0.1",
    "https://example.com"  # 적당한 URL/메일 주소로 바꿔도 됨
)

# ==========================================
# 1. Spotify API 설정
# ==========================================
client_id = "490b45532df54ef0847e810393d06a51"
client_secret = "ab2b99ec8c2a4e10a7192809b3bb539c"
REDIRECT_URI = "http://127.0.0.1:8888"
SCOPE = "user-read-private user-read-email"

# ==========================================
# 2. 수동 속성 데이터
# ==========================================
MANUAL_FEATURES = {
    "Pretenders": {"tempo": 4, "energy": 4, "brightness": 3, "length": 2},
    "Closer": {"tempo": 3, "energy": 2, "brightness": 1, "length": 2},
    "Electric Warrior": {"tempo": 3, "energy": 4, "brightness": 4, "length": 2},
    "The Runaways": {"tempo": 5, "energy": 5, "brightness": 4, "length": 1},
    "Treats": {"tempo": 5, "energy": 5, "brightness": 5, "length": 1},
    "Private Dancer": {"tempo": 3, "energy": 3, "brightness": 3, "length": 2},
    "Parallelograms": {"tempo": 1, "energy": 1, "brightness": 2, "length": 2},
    "Let It Be": {"tempo": 4, "energy": 4, "brightness": 3, "length": 1},
    "In the Flat Field": {"tempo": 5, "energy": 4, "brightness": 1, "length": 2},
    "Bookends": {"tempo": 1, "energy": 1, "brightness": 2, "length": 1},
    "Blue Rev": {"tempo": 4, "energy": 4, "brightness": 4, "length": 1},
    "Ramones": {"tempo": 5, "energy": 5, "brightness": 3, "length": 1},
    "The White Album": {"tempo": 3, "energy": 3, "brightness": 3, "length": 5},
    "Colossal Youth": {"tempo": 2, "energy": 1, "brightness": 2, "length": 2},
    "London Calling": {"tempo": 4, "energy": 5, "brightness": 3, "length": 3},
}

ALBUMS = [
    {"artist": "Pretenders", "title": "Pretenders"},
    {"artist": "Joy Division", "title": "Closer"},
    {"artist": "T. Rex", "title": "Electric Warrior"},
    {"artist": "The Runaways", "title": "The Runaways"},
    {"artist": "Sleigh Bells", "title": "Treats"},
    {"artist": "Tina Turner", "title": "Private Dancer"},
    {"artist": "Linda Perhacs", "title": "Parallelograms"},
    {"artist": "The Replacements", "title": "Let It Be"},
    {"artist": "Bauhaus", "title": "In the Flat Field"},
    {"artist": "Simon & Garfunkel", "title": "Bookends"},
    {"artist": "Alvvays", "title": "Blue Rev"},
    {"artist": "Ramones", "title": "Ramones"},
    {"artist": "The Beatles", "title": "The White Album"},
    {"artist": "Young Marble Giants", "title": "Colossal Youth"},
    {"artist": "The Clash", "title": "London Calling"},
]

ATTRS = ["tempo", "energy", "brightness"]

# 🔹 장르 카테고리 → 키워드 매핑
GENRE_MAP = {
    "Rock / Alternative / Indie": ["indie", "alternative", "rock", "power pop", "jangle", "dream"],
    "Punk / Post-Punk / New Wave": ["punk", "post-punk", "new wave", "no wave", "goth", "synth"],
    "Experimental / Noise / Avant-garde": ["experimental", "noise", "avant"],
    "Pop / Singer-Songwriter / Misc": ["pop", "folk", "soft"],
}

# ==========================================
# 3. Spotify 클라이언트
# ==========================================
@st.cache_resource
def get_spotify_client():
    """스포티파이 연결 (한 번만 실행)"""
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=".spotipy_cache.json",
            open_browser=True
        ))
        return sp
    except Exception as e:
        st.error(f"Spotify 인증 중 오류: {e}")
        return None

# ==========================================
# 4. MusicBrainz 장르 함수 (네가 준 버전 그대로)
# ==========================================
@st.cache_data
def get_musicbrainz_genres(artist, title):
    """
    MusicBrainz에서 artist + title로 release 여러 개를 검색하고,
    - 릴리즈 제목/아티스트가 가장 잘 맞는 후보들을 우선으로 정렬한 뒤
    - 각 릴리즈에서 genre/tag를 시도하고,
    - 없으면 release-group(앨범 묶음)에서 genre/tag를 한 번 더 시도한다.

    최종적으로 장르 문자열 리스트를 반환. 실패하면 [].
    """
    def norm(s):
        return s.lower().strip() if isinstance(s, str) else ""

    target_title = norm(title)
    target_artist = norm(artist)

    try:
        # 1) 여러 릴리즈를 받아서 스코어링
        result = musicbrainzngs.search_releases(
            artist=artist,
            release=title,
            limit=15  # 여러 후보 중에서 골라보기
        )
        releases = result.get("release-list", [])
        if not releases:
            return []

        def score_release(rel):
            score = 0

            # 제목 유사도
            rtitle = norm(rel.get("title", ""))
            if rtitle == target_title:
                score += 5
            elif target_title in rtitle or rtitle in target_title:
                score += 3

            # 아티스트 유사도
            ac_list = rel.get("artist-credit", [])
            names = []
            for ac in ac_list:
                if isinstance(ac, dict) and "artist" in ac:
                    names.append(norm(ac["artist"].get("name", "")))
                elif isinstance(ac, str):
                    names.append(norm(ac))

            if any(n == target_artist for n in names):
                score += 4
            elif any(target_artist in n or n in target_artist for n in names):
                score += 2

            return score

        # 2) 가장 점수 높은 릴리즈부터 장르 확인
        releases_sorted = sorted(releases, key=score_release, reverse=True)

        for rel in releases_sorted:
            genres = []

            # --- (a) 릴리즈 단위 장르 시도 ---
            try:
                rel_full = musicbrainzngs.get_release_by_id(
                    rel["id"],
                    includes=["genres", "tags"]
                )["release"]

                if "genre-list" in rel_full:
                    genres.extend(g["name"] for g in rel_full["genre-list"])
                if "tag-list" in rel_full:
                    genres.extend(t["name"] for t in rel_full["tag-list"])

                genres = list(dict.fromkeys(genres))
                if genres:
                    return genres
            except Exception:
                pass

            # --- (b) 릴리즈 그룹(release-group) 단위 장르 시도 ---
            try:
                rg = rel.get("release-group") or {}
                rgid = rg.get("id")
                if rgid:
                    rg_full = musicbrainzngs.get_release_group_by_id(
                        rgid,
                        includes=["genres", "tags"]
                    )["release-group"]

                    rg_genres = []
                    if "genre-list" in rg_full:
                        rg_genres.extend(g["name"] for g in rg_full["genre-list"])
                    if "tag-list" in rg_full:
                        rg_genres.extend(t["name"] for t in rg_full["tag-list"])

                    rg_genres = list(dict.fromkeys(rg_genres))
                    if rg_genres:
                        return rg_genres
            except Exception:
                pass

        # 모든 후보에서 장르를 못 찾은 경우
        return []

    except Exception:
        return []

# ==========================================
# 5. 앨범 데이터 통합 (Spotify + MusicBrainz + 수동속성)
# ==========================================
def get_album_data(sp, album_info):
    """Spotify 커버/링크 + MusicBrainz 장르 + 수동 속성 합치기"""
    spotify_url = "https://open.spotify.com/"
    image_url = "https://via.placeholder.com/150"

    # 1) Spotify 검색으로 커버 / 링크
    try:
        query = f"artist:{album_info['artist']} album:{album_info['title']}"
        results = sp.search(q=query, type='album', limit=1)
        if results['albums']['items']:
            item = results['albums']['items'][0]
            spotify_url = item['external_urls']['spotify']
            if item['images']:
                image_url = item['images'][0]['url']
    except Exception:
        pass

    # 2) MusicBrainz 장르
    mb_genres = get_musicbrainz_genres(album_info["artist"], album_info["title"])

    # 3) 수동 속성 합치기
    if album_info['title'] in MANUAL_FEATURES:
        data = MANUAL_FEATURES[album_info['title']]
        return {
            "artist": album_info['artist'],
            "title": album_info['title'],
            "spotify_url": spotify_url,
            "image_url": image_url,
            "genres": mb_genres,
            **data,
        }
    return None

# ==========================================
# 6. UI
# ==========================================
st.set_page_config(page_title="Music Recommender", page_icon="🎧")

st.title("🎧 나만의 AI 음악 추천기")
st.write("당신의 현재 기분에 딱 맞는 앨범을 골라드립니다!")
st.divider()

st.sidebar.header("🎚️ 기분 설정")

tempo = st.sidebar.select_slider(
    "Q1. 듣고 싶은 템포는?",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: ["매우 느림", "느림", "적당함", "빠름", "매우 빠름"][x-1]
)

energy = st.sidebar.select_slider(
    "Q2. 에너지 레벨은?",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: ["잔잔함", "차분함", "중간", "신남", "강렬함"][x-1]
)

brightness = st.sidebar.select_slider(
    "Q3. 원하는 분위기는?",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: ["어두움", "조금 어두움", "중간", "밝음", "아주 밝음"][x-1]
)

length = st.sidebar.radio(
    "Q4. 감상 시간은?",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: ["30분 이하", "45분 이하", "1시간 이하", "2시간 이하", "2시간 이상"][x-1]
)

genre_category = st.sidebar.selectbox(
    "Q5. 장르 선택",
    ["전체",
     "Rock / Alternative / Indie",
     "Punk / Post-Punk / New Wave",
     "Experimental / Noise / Avant-garde",
     "Pop / Singer-Songwriter / Misc"]
)

# ==========================================
# 7. 추천 로직
# ==========================================
if st.sidebar.button("🎵 앨범 추천받기", type="primary"):
    sp = get_spotify_client()
    if not sp:
        st.error("스포티파이 인증에 실패했습니다.")
    else:
        user_state = {
            "tempo": tempo,
            "energy": energy,
            "brightness": brightness,
            "length": length,
        }

        with st.spinner("Spotify / MusicBrainz에서 정보를 가져오는 중..."):
            scored = []
            progress_bar = st.progress(0)

            # 1) 모든 앨범 데이터 수집
            album_datas = []
            for i, album_info in enumerate(ALBUMS):
                data = get_album_data(sp, album_info)
                if data:
                    album_datas.append(data)
                progress_bar.progress((i + 1) / len(ALBUMS))

            # 2) 점수 계산 + 필터 적용
            for data in album_datas:
                # (1) 장르 필터
                if genre_category != "전체":
                    keywords = GENRE_MAP[genre_category]
                    genres_lower = [g.lower() for g in data.get("genres", [])]

                    # 장르가 아예 없으면 너무 빡세니까 일단 통과시킴
                    if genres_lower:
                        ok = any(
                            any(kw in g for g in genres_lower)
                            for kw in keywords
                        )
                        if not ok:
                            continue

                # (2) 길이 필터
                if data["length"] <= length:
                    score = 0
                    for attr in ATTRS:
                        diff = abs(data[attr] - user_state[attr])
                        if diff == 0:
                            score += 5
                        elif diff == 1:
                            score += 3
                        elif diff == 2:
                            score += 0
                        else:
                            score += -3
                    scored.append((score, data))

            scored.sort(key=lambda x: (-x[0], abs(x[1]["length"] - length)))

        st.success("분석 완료! 추천 앨범입니다.")
        st.divider()

        if not scored:
            st.warning("조건에 맞는 앨범이 없습니다. 조건을 넓혀보세요!")
        else:
            for i, (score, album) in enumerate(scored[:3], start=1):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.image(album["image_url"], width=150)

                with col2:
                    st.subheader(f"{i}위. {album['title']}")
                    st.text(f"아티스트: {album['artist']}")
                    if album.get("genres"):
                        st.caption("Genres (MusicBrainz): " + ", ".join(album["genres"][:5]))
                    st.caption(f"적합도 점수: {score}점")
                    st.link_button("Spotify에서 듣기 ▶", album["spotify_url"])
                st.divider()