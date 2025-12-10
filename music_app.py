# music_app.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# ==========================================
# 1. API 설정 (기존과 동일)
# ==========================================
client_id = "490b45532df54ef0847e810393d06a51"
client_secret = "ab2b99ec8c2a4e10a7192809b3bb539c"
REDIRECT_URI = "http://127.0.0.1:8888"
SCOPE = "user-read-private user-read-email"

# 비상용 수동 데이터
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

# ==========================================
# 2. 기능 함수들
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
            open_browser=True # 앱에서는 브라우저 자동 열기 시도
        ))
        return sp
    except:
        return None

def get_album_data(sp, album_info):
    """API로 커버 사진과 링크를 가져오고, 수동 데이터로 분석"""
    
    # 1. 스포티파이 검색 (커버 이미지 & 링크 확보용)
    spotify_url = "https://open.spotify.com/"
    image_url = "https://via.placeholder.com/150" # 기본 이미지
    
    try:
        query = f"artist:{album_info['artist']} album:{album_info['title']}"
        results = sp.search(q=query, type='album', limit=1)
        if results['albums']['items']:
            item = results['albums']['items'][0]
            album_id = item['id']
            spotify_url = item['external_urls']['spotify']
            if item['images']:
                image_url = item['images'][0]['url'] # 제일 큰 사진
    except:
        pass 

    # 2. 분석 데이터 매칭
    if album_info['title'] in MANUAL_FEATURES:
        data = MANUAL_FEATURES[album_info['title']]
        full_data = {
            "artist": album_info['artist'],
            "title": album_info['title'],
            "spotify_url": spotify_url,
            "image_url": image_url,
            **data
        }
        return full_data
    return None

# ==========================================
# 3. 화면 디자인 (UI)
# ==========================================
st.set_page_config(page_title="Music Recommender", page_icon="🎧")

st.title("🎧 나만의 AI 음악 추천기")
st.write("당신의 현재 기분에 딱 맞는 앨범을 골라드립니다!")
st.divider()

# --- 사이드바: 입력 받기 ---
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

# --- 메인 화면: 추천 로직 ---
if st.sidebar.button("🎵 앨범 추천받기", type="primary"):
    sp = get_spotify_client()
    if not sp:
        st.error("스포티파이 인증에 실패했습니다.")
    else:
        user_state = {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length}
        
        with st.spinner("Spotify에서 앨범 커버를 가져오는 중..."):
            scored = []
            progress_bar = st.progress(0)
            
            for i, album_info in enumerate(ALBUMS):
                data = get_album_data(sp, album_info)
                if data:
                    if data['length'] <= length:
                        score = 0
                        for attr in ATTRS:
                            diff = abs(data[attr] - user_state[attr])
                            if diff == 0: score += 5
                            elif diff == 1: score += 3
                            elif diff == 2: score += 0
                            else: score += -3
                        scored.append((score, data))
                progress_bar.progress((i + 1) / len(ALBUMS))
            
            scored.sort(key=lambda x: (-x[0], abs(x[1]["length"] - length)))

        # 결과 보여주기
        st.success("분석 완료! 추천 앨범입니다.")
        st.divider()

        if not scored:
            st.warning("조건에 맞는 앨범이 없습니다. 조건을 넓혀보세요!")
        else:
            # TOP 3 카드 형태로 보여주기
            for i, (score, album) in enumerate(scored[:3], start=1):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(album['image_url'], width=150)
                
                with col2:
                    st.subheader(f"{i}위. {album['title']}")
                    st.text(f"아티스트: {album['artist']}")
                    st.caption(f"적합도 점수: {score}점")
                    st.link_button("Spotify에서 듣기 ▶", album['spotify_url'])
                st.divider()