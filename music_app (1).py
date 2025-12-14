# music_app.py
import streamlit as st
import subprocess
import sys

# [자동 설치 코드] google-generativeai가 없으면 자동으로 설치합니다.
try:
    import google.generativeai as genai
except ImportError:
    st.warning("필수 라이브러리(google-generativeai)를 설치하고 있습니다... 잠시만 기다려주세요.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    st.success("설치 완료! 다시 실행됩니다.")
    st.rerun()

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import musicbrainzngs
import os
import json
import concurrent.futures
import random
import traceback

# ==========================================
# 0. 설정 (API, 파일 경로 등)
# ==========================================
CUSTOM_ALBUMS_FILE = "custom_albums.json"

musicbrainzngs.set_useragent(
    "MusicRecommenderDemo", "0.1", "https://example.com"
)

# -------------------------------------------------------------------------
# [중요] 여기에 API 키를 직접 입력하세요!
# -------------------------------------------------------------------------
# Spotify Keys
client_id = "490b45532df54ef0847e810393d06a51"
client_secret = "ab2b99ec8c2a4e10a7192809b3bb539c"

# Gemini API Key (여기에 복사한 키를 붙여넣으세요)
gemini_api_key = "AIzaSyAteZ2CcM4Pakx8oUaIakvqmTNabGzCoYg" 
# -------------------------------------------------------------------------

REDIRECT_URI = "http://127.0.0.1:8888"
SCOPE = "user-read-private user-read-email"

# ==========================================
# 1. 콘텐츠 데이터 (상식 & 퀴즈)
# ==========================================
TRIVIA_LIST = [
    "비틀즈의 'Yesterday'는 폴 매카트니가 꿈속에서 멜로디를 듣고 작곡했습니다.",
    "모차르트는 5살 때 첫 작곡을 했고, 6살 때 첫 연주 여행을 다녔습니다.",
    "CD 한 장의 용량이 74분인 이유는 베토벤 교향곡 9번(합창)의 길이를 다 담기 위해서라는 설이 유력합니다.",
    "식물에게 클래식 음악(특히 모차르트)을 들려주면 성장이 촉진된다는 연구 결과가 있습니다.",
    "퀸의 'Bohemian Rhapsody'는 당시 6분이라는 긴 길이 때문에 라디오 재생을 거절당했었습니다.",
    "마이클 잭슨의 'Thriller' 앨범은 전 세계에서 가장 많이 팔린 앨범(약 6,600만 장 이상)입니다.",
    "가장 긴 피아노 공연 기록은 27시간이 아니라, 독일의 피아니스트가 세운 '52시간'입니다.",
    "우리의 심장 박동수는 듣고 있는 음악의 템포(BPM)에 맞춰 동기화되는 경향이 있습니다.",
    "악보를 전혀 볼 줄 모르는 거장들도 많습니다 (예: 지미 헨드릭스, 에릭 클랩튼, 마이클 잭슨).",
    "유튜브 최초의 10억 조회수 뮤직비디오는 싸이의 '강남스타일'입니다."
]

QUIZ_LIST = [
    ("방탄소년단의 데뷔곡 제목은?", "No More Dream"),
    ("피아노의 건반 개수는 총 몇 개일까요?", "88개"),
    ("비틀즈의 멤버가 아닌 사람은? (존 레논, 폴 매카트니, 엘비스 프레슬리, 링고 스타)", "엘비스 프레슬리"),
    ("음악의 아버지라 불리는 바로크 시대 작곡가는?", "바흐"),
    ("소리가 전혀 나지 않는 존 케이지의 연주곡 제목은?", "4분 33초")
]

# [수정됨] NameError 방지를 위해 상단 정의
ATTRS = ["tempo", "energy", "brightness"]

# ==========================================
# 2. 기본 데이터 (MANUAL_FEATURES & ALBUMS)
# ==========================================
# [수정됨] NameError 방지를 위해 GENRE_MAP을 위로 올림
GENRE_MAP = {
    "Rock / Alternative / Indie": ["indie", "alternative", "rock", "power pop", "jangle", "dream"],
    "Punk / Post-Punk / New Wave": ["punk", "post-punk", "new wave", "no wave", "goth", "synth"],
    "Experimental / Noise / Avant-garde": ["experimental", "noise", "avant"],
    "Pop / Singer-Songwriter / Misc": ["pop", "folk", "soft"],
}

# [수정됨] GENRE_MAP이 정의된 후 실행
ALL_GENRE_KEYWORDS = sorted(list(set(kw for sublist in GENRE_MAP.values() for kw in sublist)))

# [수정됨] SyntaxError 해결: 괄호 {}로 제대로 닫음
MANUAL_FEATURES = {
    "Blue Rev": {"tempo": 4, "energy": 4, "brightness": 2, "length": 2},
    "Palomine": {"tempo": 2, "energy": 2, "brightness": 2, "length": 3},
    "Dancing For Mental Health": {"tempo": 3, "energy": 3, "brightness": 4, "length": 2},
    "Pretenders": {"tempo": 4, "energy": 4, "brightness": 3, "length": 3},
    "EVOL": {"tempo": 2, "energy": 4, "brightness": 1, "length": 2},
    "Retreat From the Sun": {"tempo": 3, "energy": 4, "brightness": 4, "length": 3},
    "Let It Be": {"tempo": 4, "energy": 4, "brightness": 3, "length": 2},
    "The Raincoats": {"tempo": 3, "energy": 2, "brightness": 3, "length": 2},
    "Closer": {"tempo": 3, "energy": 2, "brightness": 1, "length": 2},
    "LiLiPut": {"tempo": 4, "energy": 4, "brightness": 2, "length": 5},
    "Unknown Pleasures": {"tempo": 3, "energy": 1, "brightness": 2, "length": 2},
    "Blondie": {"tempo": 4, "energy": 3, "brightness": 3, "length": 2},
    "Zen Arcade": {"tempo": 5, "energy": 5, "brightness": 2, "length": 4},
    "Hey Babe": {"tempo": 3, "energy": 3, "brightness": 2, "length": 2},
    "Of Skins And Heart": {"tempo": 2, "energy": 2, "brightness": 2, "length": 2},
    "Learning to Crawl": {"tempo": 3, "energy": 2, "brightness": 4, "length": 2},
    "Treats": {"tempo": 5, "energy": 5, "brightness": 5, "length": 2},
    "Dub Housing": {"tempo": 3, "energy": 4, "brightness": 2, "length": 2},
    "Thunder, Lightning, Strike": {"tempo": 4, "energy": 4, "brightness": 4, "length": 2},
    "The Muffs": {"tempo": 5, "energy": 5, "brightness": 3, "length": 2},
    "And Don't the Kids Just Love It": {"tempo": 3, "energy": 3, "brightness": 2, "length": 2},
    "Underwater Moonlight": {"tempo": 2, "energy": 2, "brightness": 3, "length": 2},
    "On Fire": {"tempo": 1, "energy": 1, "brightness": 4, "length": 3},
    "Singles And Sessions 1979-1981": {"tempo": 4, "energy": 4, "brightness": 4, "length": 3},
    "16 Lovers Lane": {"tempo": 2, "energy": 2, "brightness": 4, "length": 2},
    "Big Red Letter Day": {"tempo": 3, "energy": 5, "brightness": 4, "length": 2},
    "A Storm In Heaven": {"tempo": 1, "energy": 4, "brightness": 5, "length": 3},
    "Mr Fantasy": {"tempo": 2, "energy": 2, "brightness": 4, "length": 2},
    "God Bless the Red Krayola and All Who Sail With It": {"tempo": 2, "energy": 1, "brightness": 2, "length": 2},
    "Come Away With ESG": {"tempo": 5, "energy": 4, "brightness": 1, "length": 2},
    "A Walk Across The Rooftops": {"tempo": 1, "energy": 2, "brightness": 3, "length": 2},
    "(I'm) Stranded": {"tempo": 5, "energy": 5, "brightness": 2, "length": 2},
    "London Calling": {"tempo": 4, "energy": 4, "brightness": 4, "length": 4},
    "Electric Warrior": {"tempo": 2, "energy": 3, "brightness": 4, "length": 2},
    "A Wizard / A True Star": {"tempo": 3, "energy": 4, "brightness": 5, "length": 4},
    "Here Come the Warm Jets": {"tempo": 2, "energy": 2, "brightness": 3, "length": 2},
    "The Runaways": {"tempo": 5, "energy": 5, "brightness": 2, "length": 2},
    "Private Dancer": {"tempo": 3, "energy": 5, "brightness": 4, "length": 2},
    "Three Imaginary Boys": {"tempo": 3, "energy": 1, "brightness": 1, "length": 2},
    "Suburban Lawns": {"tempo": 4, "energy": 4, "brightness": 1, "length": 2},
    "Metal Box": {"tempo": 3, "energy": 4, "brightness": 2, "length": 4},
    "The Modern Lovers": {"tempo": 3, "energy": 3, "brightness": 4, "length": 2},
    "Roxy Music": {"tempo": 2, "energy": 3, "brightness": 4, "length": 3},
    "Chomp": {"tempo": 4, "energy": 3, "brightness": 3, "length": 2},
    "Will Anything Happen": {"tempo": 4, "energy": 2, "brightness": 4, "length": 2},
    "Antisocialites": {"tempo": 3, "energy": 2, "brightness": 4, "length": 2},
    "Sunburn": {"tempo": 3, "energy": 2, "brightness": 2, "length": 2},
    "Let's Get Out Of This Country": {"tempo": 2, "energy": 3, "brightness": 4, "length": 2},
    "Hex Enduction Hour": {"tempo": 3, "energy": 2, "brightness": 3, "length": 4},
    "Jesus of Cool": {"tempo": 3, "energy": 4, "brightness": 4, "length": 2},
    "Press Color": {"tempo": 3, "energy": 4, "brightness": 2, "length": 1},
    "Sister": {"tempo": 2, "energy": 3, "brightness": 2, "length": 2},
    "Y": {"tempo": 3, "energy": 5, "brightness": 1, "length": 2},
    "Queen Of Siam": {"tempo": 2, "energy": 2, "brightness": 1, "length": 2},
    "The Infamous": {"tempo": 3, "energy": 5, "brightness": 1, "length": 4},
    "Colossal Youth": {"tempo": 2, "energy": 1, "brightness": 1, "length": 2},
    "Illuminati": {"tempo": 3, "energy": 1, "brightness": 5, "length": 4},
    "The Fugs": {"tempo": 3, "energy": 3, "brightness": 2, "length": 2},
    "The Cars": {"tempo": 3, "energy": 4, "brightness": 3, "length": 2},
    "Remain in Light": {"tempo": 3, "energy": 4, "brightness": 4, "length": 3},
    "Elastica": {"tempo": 4, "energy": 4, "brightness": 2, "length": 2},
    "Nikki and the Corvettes": {"tempo": 4, "energy": 5, "brightness": 4, "length": 2},
    "Star": {"tempo": 2, "energy": 2, "brightness": 2, "length": 3},
    "Blow Away Your Troubles": {"tempo": 2, "energy": 2, "brightness": 5, "length": 4},
    "Alvvays": {"tempo": 2, "energy": 2, "brightness": 3, "length": 2},
    "The Psychedelic Sounds of the 13th Floor Elevators": {"tempo": 3, "energy": 5, "brightness": 5, "length": 2},
    "Forever Breathes the Lonely Word": {"tempo": 3, "energy": 2, "brightness": 3, "length": 2},
    "The 3 Way": {"tempo": 3, "energy": 2, "brightness": 2, "length": 2},
    "Playing With a Different Sex": {"tempo": 5, "energy": 4, "brightness": 2, "length": 3},
    "What Makes It Go": {"tempo": 4, "energy": 4, "brightness": 5, "length": 2},
    "Door Door": {"tempo": 2, "energy": 2, "brightness": 1, "length": 2},
    "The Marshall Mathers LP": {"tempo": 5, "energy": 4, "brightness": 1, "length": 4},
    "Cut": {"tempo": 4, "energy": 5, "brightness": 2, "length": 2},
    "Prayers on Fire": {"tempo": 3, "energy": 5, "brightness": 1, "length": 2},
    "New York Dolls": {"tempo": 4, "energy": 4, "brightness": 4, "length": 2},
    "Something/Anything?": {"tempo": 2, "energy": 5, "brightness": 5, "length": 4},
    "#1 Record": {"tempo": 3, "energy": 4, "brightness": 5, "length": 2},
    "Static & Silence": {"tempo": 1, "energy": 2, "brightness": 2, "length": 2},
    "Giant Steps": {"tempo": 3, "energy": 3, "brightness": 3, "length": 4},
    "Very Necessary": {"tempo": 3, "energy": 5, "brightness": 2, "length": 3},
    "Try Out": {"tempo": 4, "energy": 2, "brightness": 1, "length": 2},
    "Do You Like My Tight Sweater?": {"tempo": 2, "energy": 2, "brightness": 2, "length": 3},
    "Night Time, My Time": {"tempo": 3, "energy": 3 , "brightness": 4, "length": 3},
    "Le Tigre": {"tempo": 4, "energy": 5, "brightness": 2, "length": 2},
    "Crazy Rhythms": {"tempo": 2, "energy": 2, "brightness": 4, "length": 2},
    "Cheap Trick": {"tempo": 3, "energy": 4, "brightness": 3, "length": 2},
    "Love Buzz": {"tempo": 3, "energy": 4, "brightness": 3, "length": 3},
    "Third Eye": {"tempo": 4, "energy": 3, "brightness": 2, "length": 2},
    "No Dice": {"tempo": 3, "energy": 4, "brightness": 4, "length": 1},
    "Strawberry Switchblade": {"tempo": 4, "energy": 3, "brightness": 4, "length": 2},
    "It's a Shame About Ray": {"tempo": 4, "energy": 5, "brightness": 4, "length": 2},
    "Beat Rhythm News (Waddle Ya Play?)": {"tempo": 4, "energy": 4, "brightness": 2, "length": 2},
    "ex:el": {"tempo": 4, "energy": 2, "brightness": 2, "length": 3},
    "Ultraglide in Black": {"tempo": 4, "energy": 4, "brightness": 2, "length": 2},
    "Straight Outta Compton": {"tempo": 4, "energy": 5, "brightness": 2, "length": 4},
    "8-Eyed Spy": {"tempo": 2, "energy": 1, "brightness": 1, "length": 2},
    "Buy": {"tempo": 3, "energy": 3, "brightness": 2, "length": 1},
    "Wasps’ Nests": {"tempo": 2, "energy": 3, "brightness": 3, "length": 2},
    "All Over The Place": {"tempo": 3, "energy": 3, "brightness": 3, "length": 2},
    "Bookends": {"tempo": 2, "energy": 3, "brightness": 4, "length": 1},
    "Quebec": {"tempo": 2, "energy": 3, "brightness": 4, "length": 3},
    "Germ Free Adolescents": {"tempo": 5, "energy": 4, "brightness": 3, "length": 2},
    "The Plimsouls": {"tempo": 4, "energy": 3, "brightness": 4, "length": 2},
    "Parallelograms": {"tempo": 1, "energy": 1, "brightness": 4, "length": 2},
    "Before Hollywood": {"tempo": 3, "energy": 2, "brightness": 3, "length": 2},
    "Shake Some Action": {"tempo": 4, "energy": 3, "brightness": 3, "length": 2},
    "Warm, In Your Coat": {"tempo": 4, "energy": 3, "brightness": 1, "length": 4},
    "Real Life": {"tempo": 3, "energy": 4, "brightness": 3, "length": 2},
    "No New York": {"tempo": 2, "energy": 1, "brightness": 1, "length": 2},
    "Pompeii": {"tempo": 1, "energy": 2, "brightness": 3, "length": 2},
    "Tumult": {"tempo": 3, "energy": 3, "brightness": 1, "length": 3},
    "Boom in the Night": {"tempo": 3, "energy": 3, "brightness": 1, "length": 2},
    "Fire of Love": {"tempo": 4, "energy": 3, "brightness": 3, "length": 2},
    "Submarine Bells": {"tempo": 2, "energy": 2, "brightness": 4, "length": 2},
    "Move": {"tempo": 3, "energy": 4, "brightness": 4, "length": 2},
    "Youth Of America": {"tempo": 3, "energy": 3, "brightness": 2, "length": 2},
    "Floodland": {"tempo": 3, "energy": 4, "brightness": 1, "length": 3},
    "Version 2.0": {"tempo": 4, "energy": 5, "brightness": 4, "length": 3},
    "The Graveyard and the Ballroom": {"tempo": 4, "energy": 5, "brightness": 2, "length": 3},
    "Demonstration Tapes": {"tempo": 4, "energy": 2, "brightness": 4, "length": 4},
    "Echoes": {"tempo": 4, "energy": 4, "brightness": 2, "length": 3},
}

# [수정됨] SyntaxError 해결: 괄호 []로 제대로 닫음
ALBUMS = [
    {"artist": "Alvvays", "title": "Blue Rev"},
    {"artist": "Bettie Serveert", "title": "Palomine"},
    {"artist": "Will Powers", "title": "Dancing For Mental Health"},
    {"artist": "Pretenders", "title": "Pretenders"},
    {"artist": "Sonic Youth", "title": "EVOL"},
    {"artist": "that dog.", "title": "Retreat From the Sun"},
    {"artist": "The Replacements", "title": "Let It Be"},
    {"artist": "The Raincoats", "title": "The Raincoats"},
    {"artist": "Joy Division", "title": "Closer"},
    {"artist": "Kleenex", "title": "LiLiPut"},
    {"artist": "Joy Division", "title": "Unknown Pleasures"},
    {"artist": "Blondie", "title": "Blondie"},
    {"artist": "Hüsker Dü", "title": "Zen Arcade"},
    {"artist": "Juliana Hatfield", "title": "Hey Babe"},
    {"artist": "The Church", "title": "Of Skins And Heart"},
    {"artist": "Pretenders", "title": "Learning to Crawl"},
    {"artist": "Sleigh Bells", "title": "Treats"},
    {"artist": "Pere Ubu", "title": "Dub Housing"},
    {"artist": "The Go! Team", "title": "Thunder, Lightning, Strike"},
    {"artist": "The Muffs", "title": "The Muffs"},
    {"artist": "Television Personalities", "title": "And Don't the Kids Just Love It"},
    {"artist": "The Soft Boys", "title": "Underwater Moonlight"},
    {"artist": "Galaxie 500", "title": "On Fire"},
    {"artist": "Delta 5", "title": "Singles And Sessions 1979-1981"},
    {"artist": "The Go-Betweens", "title": "16 Lovers Lane"},
    {"artist": "Buffalo Tom", "title": "Big Red Letter Day"},
    {"artist": "The Verve", "title": "A Storm In Heaven"},
    {"artist": "Traffic", "title": "Mr Fantasy"},
    {"artist": "The Red Krayola", "title": "God Bless the Red Krayola and All Who Sail With It"},
    {"artist": "ESG", "title": "Come Away With ESG"},
    {"artist": "The Blue Nile", "title": "A Walk Across The Rooftops"},
    {"artist": "The Saints", "title": "(I'm) Stranded"},
    {"artist": "The Clash", "title": "London Calling"},
    {"artist": "T. Rex", "title": "Electric Warrior"},
    {"artist": "Todd Rundgren", "title": "A Wizard / A True Star"},
    {"artist": "Brian Eno", "title": "Here Come the Warm Jets"},
    {"artist": "The Runaways", "title": "The Runaways"},
    {"artist": "Tina Turner", "title": "Private Dancer"},
    {"artist": "The Cure", "title": "Three Imaginary Boys"},
    {"artist": "Suburban Lawns", "title": "Suburban Lawns"},
    {"artist": "Public Image Ltd.", "title": "Metal Box"},
    {"artist": "The Modern Lovers", "title": "The Modern Lovers"},
    {"artist": "Roxy Music", "title": "Roxy Music"},
    {"artist": "Pylon", "title": "Chomp"},
    {"artist": "Shop Assistants", "title": "Will Anything Happen"},
    {"artist": "Alvvays", "title": "Antisocialites"},
    {"artist": "Blake Babies", "title": "Sunburn"},
    {"artist": "Camera Obscura", "title": "Let's Get Out Of This Country"},
    {"artist": "The Fall", "title": "Hex Enduction Hour"},
    {"artist": "Nick Lowe", "title": "Jesus of Cool"},
    {"artist": "Lizzy Mercier Descloux", "title": "Press Color"},
    {"artist": "Sonic Youth", "title": "Sister"},
    {"artist": "The Pop Group", "title": "Y"},
    {"artist": "Lydia Lunch", "title": "Queen Of Siam"},
    {"artist": "Mobb Deep", "title": "The Infamous"},
    {"artist": "Young Marble Giants", "title": "Colossal Youth"},
    {"artist": "The Pastels", "title": "Illuminati"},
    {"artist": "The Fugs", "title": "The Fugs"},
    {"artist": "The Cars", "title": "The Cars"},
    {"artist": "Talking Heads", "title": "Remain in Light"},
    {"artist": "Elastica", "title": "Elastica"},
    {"artist": "Nikki and the Corvettes", "title": "Nikki and the Corvettes"},
    {"artist": "Belly", "title": "Star"},
    {"artist": "The Cleaners From Venus", "title": "Blow Away Your Troubles"},
    {"artist": "Alvvays", "title": "Alvvays"},
    {"artist": "13th Floor Elevators", "title": "The Psychedelic Sounds of the 13th Floor Elevators"},
    {"artist": "Felt", "title": "Forever Breathes the Lonely Word"},
    {"artist": "Lilys", "title": "The 3 Way"},
    {"artist": "Au Pairs", "title": "Playing With a Different Sex"},
    {"artist": "Komeda", "title": "What Makes It Go"},
    {"artist": "The Boys Next Door", "title": "Door Door"},
    {"artist": "Eminem", "title": "The Marshall Mathers LP"},
    {"artist": "The Slits", "title": "Cut"},
    {"artist": "The Birthday Party", "title": "Prayers on Fire"},
    {"artist": "New York Dolls", "title": "New York Dolls"},
    {"artist": "Something/Anything?", "title": "Something/Anything?"},
    {"artist": "Big Star", "title": "#1 Record"},
    {"artist": "The Sundays", "title": "Static & Silence"},
    {"artist": "The Boo Radleys", "title": "Giant Steps"},
    {"artist": "Salt-N-Pepa", "title": "Very Necessary"},
    {"artist": "Kas Product", "title": "Try Out"},
    {"artist": "Moloko", "title": "Do You Like My Tight Sweater?"},
    {"artist": "Sky Ferreira", "title": "Night Time, My Time"},
    {"artist": "Le Tigre", "title": "Le Tigre"},
    {"artist": "The Feelies", "title": "Crazy Rhythms"},
    {"artist": "Cheap Trick", "title": "Cheap Trick"},
    {"artist": "The Hummingbirds", "title": "Love Buzz"},
    {"artist": "Redd Kross", "title": "Third Eye"},
    {"artist": "Badfinger", "title": "No Dice"},
    {"artist": "Strawberry Switchblade", "title": "Strawberry Switchblade"},
    {"artist": "The Lemonheads", "title": "It's a Shame About Ray"},
    {"artist": "Essential Logic", "title": "Beat Rhythm News (Waddle Ya Play?)"},
    {"artist": "808 State", "title": "ex:el"},
    {"artist": "The Dirtbombs", "title": "Ultraglide in Black"},
    {"artist": "N.W.A.", "title": "Straight Outta Compton"},
    {"artist": "8 Eyed Spy", "title": "8-Eyed Spy"},
    {"artist": "The Contortions", "title": "Buy"},
    {"artist": "The 6ths", "title": "Wasps’ Nests"},
    {"artist": "The Bangles", "title": "All Over The Place"},
    {"artist": "Simon & Garfunkel", "title": "Bookends"},
    {"artist": "Ween", "title": "Quebec"},
    {"artist": "X-Ray Spex", "title": "Germ Free Adolescents"},
    {"artist": "The Plimsouls", "title": "The Plimsouls"},
    {"artist": "Linda Perhacs", "title": "Parallelograms"},
    {"artist": "The Go-Betweens", "title": "Before Hollywood"},
    {"artist": "Flamin' Groovies", "title": "Shake Some Action"},
    {"artist": "Romeo Void", "title": "Warm, In Your Coat"},
    {"artist": "Magazine", "title": "Real Life"},
    {"artist": "Various Artists", "title": "No New York"},
    {"artist": "Cate Le Bon", "title": "Pompeii"},
    {"artist": "The Ex", "title": "Tumult"},
    {"artist": "Bush Tetras", "title": "Boom in the Night"},
    {"artist": "The Gun Club", "title": "Fire of Love"},
    {"artist": "The Chills", "title": "Submarine Bells"},
    {"artist": "The Move", "title": "Move"},
    {"artist": "Wipers", "title": "Youth Of America"},
    {"artist": "Sisters of Mercy", "title": "Floodland"},
    {"artist": "Garbage", "title": "Version 2.0"},
    {"artist": "A Certain Ratio", "title": "The Graveyard and the Ballroom"},
    {"artist": "Dolly Mixture", "title": "Demonstration Tapes"},
    {"artist": "The Rapture", "title": "Echoes"},
]

# ==========================================
# 3. 헬퍼 함수
# ==========================================
@st.cache_data
def load_custom_albums():
    if os.path.exists(CUSTOM_ALBUMS_FILE):
        with open(CUSTOM_ALBUMS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_custom_albums(albums):
    with open(CUSTOM_ALBUMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(albums, f, ensure_ascii=False, indent=4)
    st.cache_data.clear()

@st.cache_resource
def get_spotify_client():
    try:
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, scope=SCOPE, cache_path=".spotipy_cache.json", open_browser=True
        ))
    except Exception:
        return None

def get_musicbrainz_genres(artist, title):
    def norm(s): return s.lower().strip() if isinstance(s, str) else ""
    target_title, target_artist = norm(title), norm(artist)
    try:
        result = musicbrainzngs.search_releases(artist=artist, release=title, limit=15)
        releases = result.get("release-list", [])
        if not releases: return []
        def score_release(rel):
            score = 0
            rtitle = norm(rel.get("title", ""))
            if rtitle == target_title: score += 5
            elif target_title in rtitle or rtitle in target_title: score += 3
            ac_list = rel.get("artist-credit", [])
            names = [norm(ac["artist"].get("name", "")) if isinstance(ac, dict) and "artist" in ac else norm(ac) for ac in ac_list]
            if any(n == target_artist for n in names): score += 4
            elif any(target_artist in n or n in target_artist for n in names): score += 2
            return score
        releases_sorted = sorted(releases, key=score_release, reverse=True)
        for rel in releases_sorted:
            genres = []
            try:
                rel_full = musicbrainzngs.get_release_by_id(rel["id"], includes=["genres", "tags"])["release"]
                if "genre-list" in rel_full: genres.extend(g["name"] for g in rel_full["genre-list"])
                if "tag-list" in rel_full: genres.extend(t["name"] for t in rel_full["tag-list"])
                genres = list(dict.fromkeys(genres))
                if genres: return genres
            except Exception: pass
            try:
                rg = rel.get("release-group") or {}; rgid = rg.get("id")
                if rgid:
                    rg_full = musicbrainzngs.get_release_group_by_id(rgid, includes=["genres", "tags"])["release-group"]
                    rg_genres = []
                    if "genre-list" in rg_full: rg_genres.extend(g["name"] for g in rg_full["genre-list"])
                    if "tag-list" in rg_full: rg_genres.extend(t["name"] for t in rg_full["tag-list"])
                    rg_genres = list(dict.fromkeys(rg_genres))
                    if rg_genres: return rg_genres
            except Exception: pass
        return []
    except Exception: return []

def get_album_data(sp, album_info):
    spotify_url, image_url = "https://open.spotify.com/", "https://via.placeholder.com/150"
    try:
        query = f"artist:{album_info['artist']} album:{album_info['title']}"
        results = sp.search(q=query, type='album', limit=1)
        if results['albums']['items']:
            item = results['albums']['items'][0]
            spotify_url, image_url = item['external_urls']['spotify'], item['images'][0]['url'] if item['images'] else image_url
    except Exception: pass
    mb_genres = get_musicbrainz_genres(album_info["artist"], album_info["title"])
    if album_info['title'] in MANUAL_FEATURES:
        data = MANUAL_FEATURES[album_info['title']]
        return {"artist": album_info['artist'], "title": album_info['title'], "spotify_url": spotify_url, "image_url": image_url, "genres": mb_genres, **data}
    return None

def get_gemini_model(api_key):
    """사용 가능한 Gemini 모델을 자동으로 찾아 반환"""
    try:
        genai.configure(api_key=api_key)
        target_model = 'gemini-1.5-flash'
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                if 'models/gemini-1.5-flash' in available_models: target_model = 'models/gemini-1.5-flash'
                elif 'models/gemini-pro' in available_models: target_model = 'models/gemini-pro'
                else: target_model = available_models[0]
        except: pass
        return genai.GenerativeModel(target_model)
    except:
        return None

def call_gemini_recommendation(api_key, mood_profile, sp):
    """제미나이 API: 음악 추천"""
    try:
        model = get_gemini_model(api_key)
        if not model: return []
        
        prompt = f"""
        너는 최고의 음악 추천 DJ야.
        사용자의 기분: 템포 {mood_profile['tempo']}/5, 에너지 {mood_profile['energy']}/5, 분위기 {mood_profile['brightness']}/5.
        
        이 기분에 딱 어울리는 노래 3곡을 추천해줘.
        [중요] 노래 제목과 가수 이름은 Spotify 공식 명칭과 최대한 똑같이 써줘. 부제는 빼줘.
        
        반드시 아래 JSON 형식으로만 답해줘:
        [
            {{"artist": "가수이름", "title": "노래제목", "reason": "한줄 추천 이유"}}
        ]
        """
        response = model.generate_content(prompt)
        text_resp = response.text.replace("```json", "").replace("```", "").strip()
        recommendations = json.loads(text_resp)
        
        final_recs = []
        for rec in recommendations:
            spotify_url = "https://open.spotify.com/"
            image_url = "https://via.placeholder.com/150"
            try:
                # 1차 시도
                query = f"artist:{rec['artist']} track:{rec['title']}"
                results = sp.search(q=query, type='track', limit=1)
                # 2차 시도
                if not results['tracks']['items']:
                    query_broad = f"{rec['artist']} {rec['title']}"
                    results = sp.search(q=query_broad, type='track', limit=1)

                if results['tracks']['items']:
                    item = results['tracks']['items'][0]
                    spotify_url = item['external_urls']['spotify']
                    if item['album']['images']: image_url = item['album']['images'][0]['url']
            except: pass
            
            final_recs.append({
                "artist": rec['artist'], "title": rec['title'],
                "reason": rec['reason'], "spotify_url": spotify_url, "image_url": image_url
            })
        return final_recs
    except Exception as e:
        print(f"[Gemini Rec Error] {e}")
        return []

def generate_ai_content(api_key, content_type):
    """제미나이 API: 실시간 퀴즈/상식 생성"""
    try:
        model = get_gemini_model(api_key)
        if not model: return None

        if content_type == "trivia":
            prompt = "음악에 관한 짧고 흥미로운 상식(TMI)을 딱 하나만 한국어로 말해줘. 예: '비틀즈의 예스터데이는 꿈속에서 작곡되었습니다.' 처럼 한 문장으로."
            response = model.generate_content(prompt)
            return response.text.strip()
        
        elif content_type == "quiz":
            prompt = """
            음악 관련 퀴즈를 하나만 내줘. 
            반드시 아래 JSON 포맷으로만 답변해줘:
            {"question": "문제 내용", "answer": "정답 단어"}
            """
            response = model.generate_content(prompt)
            text_resp = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text_resp)
            
    except Exception as e:
        print(f"[Gemini Content Error] {e}")
        return None

# ==========================================
# 4. 페이지 렌더링 함수 (메인)
# ==========================================

def render_main_page(sp):
    st.title("🎧 나만의 AI 음악 추천기")
    st.write("당신의 현재 기분에 딱 맞는 앨범을 골라드립니다!")
    st.divider()

    st.sidebar.header("🎚️ 기분 설정")
    tempo = st.sidebar.select_slider("Q1. 템포", options=[1, 2, 3, 4, 5], format_func=lambda x: ["매우 느림", "느림", "적당함", "빠름", "매우 빠름"][x-1])
    energy = st.sidebar.select_slider("Q2. 에너지", options=[1, 2, 3, 4, 5], format_func=lambda x: ["잔잔함", "차분함", "중간", "신남", "강렬함"][x-1])
    brightness = st.sidebar.select_slider("Q3. 분위기", options=[1, 2, 3, 4, 5], format_func=lambda x: ["어두움", "조금 어두움", "중간", "밝음", "아주 밝음"][x-1])
    length = st.sidebar.radio("Q4. 감상 시간", options=[1, 2, 3, 4, 5], format_func=lambda x: ["30분 이하", "45분 이하", "1시간 이하", "2시간 이하", "2시간 이상"][x-1])
    genre_category = st.sidebar.selectbox("Q5. 장르", ["전체"] + list(GENRE_MAP.keys()))
    
    st.divider()
    waiting_mode = st.sidebar.radio(
        "⏳ 기다리는 동안 무엇을 할까요?",
        ["음악 상식 읽기", "음악 퀴즈 풀기"],
        index=0
    )

    if st.sidebar.button("🎵 앨범 추천받기", type="primary"):
        if not sp:
            st.error("스포티파이 인증에 실패했습니다."); return
        
        user_state = {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length}
        
        progress_text = st.empty()
        percent_text = st.empty()
        progress_bar = st.progress(0)
        
        all_albums = []
        gemini_results = []
        custom_albums = load_custom_albums()
        total_items = len(ALBUMS) + len(custom_albums) 
        completed_items = 0

        MAX_WORKERS = 8 
        
        # 초기 퀴즈/상식 설정
        current_quiz = random.choice(QUIZ_LIST)
        current_trivia = random.choice(TRIVIA_LIST)
        quiz_start_time = time.time()
        trivia_start_time = time.time()
        
        # [핵심] AI 콘텐츠 버퍼 (미리 만들어두는 공간)
        next_content_buffer = None 

        with st.spinner("데이터 분석 및 AI DJ와 통신 중..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # 1. 앨범 수집용 Future 관리
                main_futures = set()
                
                # 2. 백그라운드 콘텐츠용 Future (별도 관리)
                bg_content_future = None

                # --- 작업 제출 ---
                # A. AI 추천 (최우선)
                has_api_key = gemini_api_key and "여기에" not in gemini_api_key
                if has_api_key:
                    f = executor.submit(call_gemini_recommendation, gemini_api_key, user_state, sp)
                    main_futures.add(f)
                    # Future 객체에 타입 태깅 (꼼수)
                    f.tag = "ai_rec"
                    
                    # B. 첫 번째 AI 콘텐츠 생성 요청 (백그라운드)
                    ctype = "trivia" if waiting_mode == "음악 상식 읽기" else "quiz"
                    bg_content_future = executor.submit(generate_ai_content, gemini_api_key, ctype)

                # C. 로컬 앨범 작업
                for album in ALBUMS:
                    f = executor.submit(get_album_data, sp, album)
                    f.tag = "local"
                    main_futures.add(f)
                
                # --- 메인 루프 (앨범 수집이 끝날 때까지) ---
                while main_futures:
                    # 0.1초마다 체크 (UI 갱신을 위해)
                    # main_futures와 bg_content_future를 모두 감시
                    wait_targets = main_futures.copy()
                    if bg_content_future:
                        wait_targets.add(bg_content_future)
                        
                    done, _ = concurrent.futures.wait(wait_targets, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)
                    
                    for future in done:
                        # 1. 메인 작업(앨범/추천) 완료 처리
                        if future in main_futures:
                            try:
                                result = future.result()
                                if future.tag == "local" and result:
                                    all_albums.append(result)
                                    completed_items += 1
                                elif future.tag == "ai_rec" and result:
                                    gemini_results = result
                            except: pass
                            main_futures.remove(future)
                        
                        # 2. 백그라운드 AI 콘텐츠 완료 처리
                        elif future == bg_content_future:
                            try:
                                result = future.result()
                                if result:
                                    next_content_buffer = result # 버퍼에 저장
                            except: pass
                            # 즉시 다음 콘텐츠 생성 요청 (무한 리필)
                            ctype = "trivia" if waiting_mode == "음악 상식 읽기" else "quiz"
                            bg_content_future = executor.submit(generate_ai_content, gemini_api_key, ctype)

                    # 진행률 업데이트
                    progress = min(completed_items / total_items, 1.0)
                    percent_text.text(f"진행률 {int(progress * 100)}%")
                    progress_bar.progress(progress)

                    # === 대기 화면 콘텐츠 UI 업데이트 ===
                    current_time = time.time()
                    
                    if waiting_mode == "음악 상식 읽기":
                        # 10초 경과 시 교체 시도
                        if current_time - trivia_start_time > 10:
                            if next_content_buffer: # AI가 만들어둔 게 있으면 사용
                                current_trivia = next_content_buffer
                                next_content_buffer = None # 사용했으니 비움
                            else: # 없으면 정적 리스트 사용
                                current_trivia = random.choice(TRIVIA_LIST)
                            trivia_start_time = current_time
                        progress_text.info(f"💡 알고 계셨나요?\n\n{current_trivia}")
                        
                    elif waiting_mode == "음악 퀴즈 풀기":
                        elapsed_time = current_time - quiz_start_time
                        if elapsed_time < 5:
                            countdown = 5 - int(elapsed_time)
                            progress_text.warning(f"❓ 퀴즈! (⏳ {countdown}초 후 공개)\n\nQ. {current_quiz[0]}")
                        elif elapsed_time < 8:
                            progress_text.success(f"✅ 정답!\n\nA. {current_quiz[1]}")
                        else:
                            # 8초 경과(한 사이클 끝) 시 교체 시도
                            if next_content_buffer and isinstance(next_content_buffer, dict):
                                current_quiz = (next_content_buffer['question'], next_content_buffer['answer'])
                                next_content_buffer = None
                            else:
                                current_quiz = random.choice(QUIZ_LIST)
                            quiz_start_time = current_time
                            progress_text.warning(f"❓ 퀴즈! (⏳ 5초 후 공개)\n\nQ. {current_quiz[0]}")

            # 사용자 추가 앨범 (순차 처리)
            for album in custom_albums:
                spotify_url, image_url = "https://open.spotify.com/", "https://via.placeholder.com/150"
                try:
                    query = f"artist:{album['artist']} album:{album['title']}"
                    results = sp.search(q=query, type='album', limit=1)
                    if results['albums']['items']:
                        item = results['albums']['items'][0]
                        spotify_url, image_url = item['external_urls']['spotify'], item['images'][0]['url'] if item['images'] else image_url
                except: pass
                all_albums.append({**album, **album['features'], "spotify_url": spotify_url, "image_url": image_url})
                completed_items += 1
                progress = min(completed_items / total_items, 1.0)
                percent_text.text(f"진행률 {int(progress * 100)}%")
                progress_bar.progress(progress)

        progress_text.empty(); percent_text.empty(); progress_bar.empty()

        # 결과 1: 로컬 추천
        scored = []
        for data in all_albums:
            if genre_category != "전체":
                keywords = GENRE_MAP[genre_category]
                genres_lower = [g.lower() for g in data.get("genres", [])]
                if genres_lower and not any(any(kw in g for g in genres_lower) for kw in keywords):
                    continue
            if data["length"] <= length:
                score = sum(5 if abs(data[attr] - user_state[attr]) == 0 else 3 if abs(data[attr] - user_state[attr]) == 1 else 0 if abs(data[attr] - user_state[attr]) == 2 else -3 for attr in ATTRS)
                scored.append((score, data))
        
        scored.sort(key=lambda x: (-x[0], abs(x[1]["length"] - length)))

        st.success("분석 완료! 추천 앨범입니다.")
        st.divider()
        
        st.subheader("💿 알고리즘 추천 (DB 기반)")
        if not scored:
            st.warning("조건에 맞는 앨범이 없습니다. 조건을 넓혀보세요!")
        else:
            for i, (score, album) in enumerate(scored[:3], start=1):
                col1, col2 = st.columns([1, 2])
                with col1: st.image(album["image_url"], width=150)
                with col2:
                    st.write(f"**{i}위. {album['title']}**")
                    st.text(f"아티스트: {album['artist']}")
                    if album.get("genres"): st.caption("Genres: " + ", ".join(album["genres"][:5]))
                    st.caption(f"적합도 점수: {score}점")
                    st.link_button("Spotify에서 듣기 ▶", album["spotify_url"])
        
        st.divider()

        # 결과 2: AI 추천
        st.subheader("🤖 AI의 특별 추천 (Generative AI)")
        
        if not gemini_results:
            if "여기에" in gemini_api_key:
                 st.info("💡 코드 상단의 'gemini_api_key' 변수에 키를 입력하면 AI 추천을 받을 수 있습니다.")
            else:
                 st.warning("AI가 추천곡을 찾지 못했습니다. (네트워크 오류 또는 검색 실패)")
        else:
            for i, song in enumerate(gemini_results, start=1):
                col1, col2 = st.columns([1, 2])
                with col1: st.image(song["image_url"], width=150)
                with col2:
                    st.write(f"**AI Pick {i}. {song['title']}**")
                    st.text(f"아티스트: {song['artist']}")
                    st.info(f"💡 추천 이유: {song['reason']}")
                    st.link_button("Spotify에서 듣기 ▶", song["spotify_url"])
                st.divider()

    st.divider()
    if st.button("💿 등록된 앨범 관리하기"):
        st.session_state.page = 'list_albums'
        st.rerun()

def render_list_page():
    st.title("💿 등록된 앨범 목록")
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'main'; st.rerun()
    if st.button("➕ 새 앨범 추가"):
        st.session_state.page = 'add_album'; st.rerun()
    st.divider()
    
    custom_albums = load_custom_albums()
    if not custom_albums:
        st.info("아직 추가된 앨범이 없습니다.")
    else:
        st.subheader(f"총 {len(custom_albums)}개의 앨범이 등록되어 있습니다.")
        for i, album in enumerate(reversed(custom_albums)): 
            idx = len(custom_albums) - 1 - i
            col1, col2, col3 = st.columns([3, 4, 1])
            with col1: st.text(album['artist'])
            with col2: st.text(album['title'])
            with col3:
                if st.button("삭제", key=f"delete_{idx}"):
                    custom_albums.pop(idx)
                    save_custom_albums(custom_albums)
                    st.rerun()
        st.divider()

def render_add_page(sp):
    st.title("➕ 새 앨범 추가")
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.page = 'list_albums'; st.rerun()

    with st.form("add_album_form"):
        st.subheader("앨범 정보")
        artist = st.text_input("아티스트*")
        
        if 'mb_found_album_titles' not in st.session_state:
            st.session_state.mb_found_album_titles = []
        if 'mb_search_artist' not in st.session_state:
            st.session_state.mb_search_artist = ""

        if st.form_submit_button("이 아티스트의 앨범 검색"): 
            if artist:
                with st.spinner(f"'{artist}'의 앨범을 MusicBrainz에서 검색 중..."):
                    try:
                        releases = musicbrainzngs.search_releases(artist=artist, limit=50).get("release-list", [])
                        album_titles = sorted(list(set(r["title"] for r in releases if "title" in r)))
                        st.session_state.mb_found_album_titles = album_titles
                        st.session_state.mb_search_artist = artist
                        if album_titles: st.success(f"앨범 {len(album_titles)}개를 찾았습니다.")
                        else: st.error("앨범을 찾을 수 없습니다.")
                    except: st.error("검색 중 오류 발생")
            else: st.error("아티스트 이름을 입력해주세요.")
        
        album_title_options = st.session_state.mb_found_album_titles
        if artist and st.session_state.mb_search_artist == artist and album_title_options:
            title = st.selectbox("앨범 제목 선택*", options=album_title_options)
        else:
            title = st.text_input("앨범 제목* (아티스트 검색 후 선택)", disabled=True)

        genre_selection = st.multiselect("장르 선택*", options=ALL_GENRE_KEYWORDS)
        
        st.subheader("음악적 특징*")
        col1, col2 = st.columns(2)
        with col1:
            tempo = st.select_slider("템포", options=[1, 2, 3, 4, 5])
            energy = st.select_slider("에너지", options=[1, 2, 3, 4, 5])
        with col2:
            brightness = st.select_slider("분위기", options=[1, 2, 3, 4, 5])
            length = st.radio("감상 시간", options=[1, 2, 3, 4, 5], horizontal=True)

        if st.form_submit_button("저장하기"):
            if not all([artist, title, genre_selection]):
                st.error("모든 필드를 채워주세요."); return
            
            new_album = {
                "artist": artist, "title": title,
                "features": {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length},
                "genres": genre_selection
            }
            custom_albums = load_custom_albums()
            custom_albums.append(new_album)
            save_custom_albums(custom_albums)
            st.success(f"✅ '{title}' 추가 완료!")
            time.sleep(1)
            st.session_state.page = 'list_albums'
            st.rerun()

# ==========================================
# 5. 메인 앱 실행 로직
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'main'

sp_client = get_spotify_client()

if st.session_state.page == 'main':
    render_main_page(sp_client)
elif st.session_state.page == 'list_albums':
    render_list_page()
elif st.session_state.page == 'add_album':
    render_add_page(sp_client)