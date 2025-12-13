# music_app.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import musicbrainzngs
import os
import json

# ==========================================
# 0. 설정 (API, 파일 경로 등)
# ==========================================
CUSTOM_ALBUMS_FILE = "custom_albums.json"

musicbrainzngs.set_useragent(
    "MusicRecommenderDemo", "0.1", "https://example.com"
)

client_id = "490b45532df54ef0847e810393d06a51"
client_secret = "ab2b99ec8c2a4e10a7192809b3bb539c"
REDIRECT_URI = "http://127.0.0.1:8888"
SCOPE = "user-read-private user-read-email"

# ==========================================
# 2. 기본 데이터
# ==========================================
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
    {"artist": "Todd Rundgren", "title": "Something/Anything?"},
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


ATTRS = ["tempo", "energy", "brightness"]
GENRE_MAP = {
    "Rock / Alternative / Indie": ["indie", "alternative", "rock", "power pop", "jangle", "dream"],
    "Punk / Post-Punk / New Wave": ["punk", "post-punk", "new wave", "no wave", "goth", "synth"],
    "Experimental / Noise / Avant-garde": ["experimental", "noise", "avant"],
    "Pop / Singer-Songwriter / Misc": ["pop", "folk", "soft"],
}

# 모든 장르 키워드 추출 (사용자 추가 앨범용)
ALL_GENRE_KEYWORDS = sorted(list(set(kw for sublist in GENRE_MAP.values() for kw in sublist)))


# ==========================================
# 3. 헬퍼 함수 (데이터 관리, API 호출 등)
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

@st.cache_data
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

# ==========================================
# 4. 페이지 렌더링 함수
# ==========================================

def render_main_page(sp):
    st.title("🎧 나만의 AI 음악 추천기")
    st.write("당신의 현재 기분에 딱 맞는 앨범을 골라드립니다!")
    st.divider()

    # --- 사이드바 ---
    st.sidebar.header("🎚️ 기분 설정")
    tempo = st.sidebar.select_slider("Q1. 템포", options=[1, 2, 3, 4, 5], format_func=lambda x: ["매우 느림", "느림", "적당함", "빠름", "매우 빠름"][x-1])
    energy = st.sidebar.select_slider("Q2. 에너지", options=[1, 2, 3, 4, 5], format_func=lambda x: ["잔잔함", "차분함", "중간", "신남", "강렬함"][x-1])
    brightness = st.sidebar.select_slider("Q3. 분위기", options=[1, 2, 3, 4, 5], format_func=lambda x: ["어두움", "조금 어두움", "중간", "밝음", "아주 밝음"][x-1])
    length = st.sidebar.radio("Q4. 감상 시간", options=[1, 2, 3, 4, 5], format_func=lambda x: ["30분 이하", "45분 이하", "1시간 이하", "2시간 이하", "2시간 이상"][x-1])
    genre_category = st.sidebar.selectbox("Q5. 장르", ["전체"] + list(GENRE_MAP.keys()))

    # --- 추천 로직 ---
    if st.sidebar.button("🎵 앨범 추천받기", type="primary"):
        if not sp:
            st.error("스포티파이 인증에 실패했습니다. 페이지를 새로고침하거나 캐시를 삭제해보세요."); return
        
        user_state = {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length}
        
        with st.spinner("앨범 데이터를 수집하고 분석하는 중..."):
            # 1) 모든 앨범 데이터 준비
            all_albums = []
            # 기본 앨범
            for info in ALBUMS:
                data = get_album_data(sp, info)
                if data: all_albums.append(data)
            # 사용자 추가 앨범
            custom_albums = load_custom_albums()
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

            # 2) 점수 계산 + 필터링
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

        # --- 결과 표시 ---
        st.success("분석 완료! 추천 앨범입니다.")
        st.divider()
        if not scored:
            st.warning("조건에 맞는 앨범이 없습니다. 조건을 넓혀보세요!")
        else:
            for i, (score, album) in enumerate(scored[:3], start=1):
                col1, col2 = st.columns([1, 2])
                with col1: st.image(album["image_url"], width=150)
                with col2:
                    st.subheader(f"{i}위. {album['title']}")
                    st.text(f"아티스트: {album['artist']}")
                    if album.get("genres"): st.caption("Genres: " + ", ".join(album["genres"][:5]))
                    st.caption(f"적합도 점수: {score}점")
                    st.link_button("Spotify에서 듣기 ▶", album["spotify_url"])
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
        st.info("아직 추가된 앨범이 없습니다. '새 앨범 추가' 버튼을 눌러 추가해보세요.")
    else:
        st.subheader(f"총 {len(custom_albums)}개의 앨범이 등록되어 있습니다.")
        for i, album in enumerate(reversed(custom_albums)): # 최신순으로
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
        
        # Initialize session state for album titles if not present
        if 'mb_found_album_titles' not in st.session_state:
            st.session_state.mb_found_album_titles = []
        if 'mb_search_artist' not in st.session_state:
            st.session_state.mb_search_artist = ""

        # Button to trigger album search
        if st.form_submit_button("이 아티스트의 앨범 검색"): # Use form_submit_button to stay within the form
            if artist:
                with st.spinner(f"'{artist}'의 앨범을 MusicBrainz에서 검색 중..."):
                    try:
                        releases = musicbrainzngs.search_releases(artist=artist, limit=50).get("release-list", [])
                        album_titles = sorted(list(set(r["title"] for r in releases if "title" in r)))
                        
                        if album_titles:
                            st.session_state.mb_found_album_titles = album_titles
                            st.session_state.mb_search_artist = artist
                            st.success(f"'{artist}'의 앨범 {len(album_titles)}개를 찾았습니다.")
                        else:
                            st.session_state.mb_found_album_titles = []
                            st.session_state.mb_search_artist = ""
                            st.error(f"'{artist}'의 앨범을 MusicBrainz에서 찾을 수 없습니다.")
                    except Exception as e:
                        st.session_state.mb_found_album_titles = []
                        st.session_state.mb_search_artist = ""
                        st.error(f"앨범 검색 중 오류 발생: {e}")
            else:
                st.error("아티스트 이름을 입력해주세요.")
        
        album_title_options = st.session_state.mb_found_album_titles
        
        # Conditional rendering for album title input
        if artist and st.session_state.mb_search_artist == artist and album_title_options:
            title = st.selectbox("앨범 제목 선택*", options=album_title_options)
        else:
            title = st.text_input("앨범 제목* (아티스트 검색 후 선택)", disabled=True)
            if not artist:
                st.warning("먼저 아티스트 이름을 입력하고 '이 아티스트의 앨범 검색' 버튼을 눌러주세요.")
            elif st.session_state.mb_search_artist != artist:
                st.warning("아티스트 이름이 변경되었습니다. 다시 '이 아티스트의 앨범 검색' 버튼을 눌러주세요.")
            elif not album_title_options:
                st.warning("해당 아티스트의 앨범을 찾을 수 없습니다. 다른 아티스트를 시도하거나 직접 입력하세요.")
                title = st.text_input("앨범 제목 직접 입력*", help="검색으로 찾지 못한 경우 직접 입력하세요.") # Allow manual input if search fails

        genre_selection = st.multiselect(
            "장르 선택 (다중 선택 가능)*",
            options=ALL_GENRE_KEYWORDS,
            help="앨범의 장르를 선택해주세요."
        )
        
        st.subheader("음악적 특징*")
        col1, col2 = st.columns(2)
        with col1:
            tempo = st.select_slider("템포", options=[1, 2, 3, 4, 5], format_func=lambda x: ["매우 느림", "느림", "적당함", "빠름", "매우 빠름"][x-1])
            energy = st.select_slider("에너지", options=[1, 2, 3, 4, 5], format_func=lambda x: ["잔잔함", "차분함", "중간", "신남", "강렬함"][x-1])
        with col2:
            brightness = st.select_slider("분위기", options=[1, 2, 3, 4, 5], format_func=lambda x: ["어두움", "조금 어두움", "중간", "밝음", "아주 밝음"][x-1])
            length = st.radio("감상 시간", options=[1, 2, 3, 4, 5], format_func=lambda x: ["30분 이하", "45분 이하", "1시간 이하", "2시간 이하", "2시간 이상"][x-1], horizontal=True)

        submitted = st.form_submit_button("저장하기")
        if submitted:
            if not all([artist, title, genre_selection]):
                st.error("'*' 표시가 된 모든 필드를 채워주세요."); return

            validation_passed = True # Assume valid unless proven otherwise

            # Determine if validation is needed (only if title was manually entered)
            # If title is from selectbox, it's already validated by the search that populated the selectbox.
            is_title_from_selectbox = (artist and 
                                       st.session_state.mb_search_artist == artist and 
                                       st.session_state.mb_found_album_titles and
                                       title in st.session_state.mb_found_album_titles)
            
            if not is_title_from_selectbox: # Only validate if title was manually entered or not found in dropdown
                with st.spinner("MusicBrainz API로 앨범 정보를 확인하는 중..."):
                    mb_genres_for_validation = get_musicbrainz_genres(artist, title)
                
                if not mb_genres_for_validation:
                    with st.spinner("MusicBrainz에서 아티스트 정보를 확인하는 중..."):
                        artist_results = musicbrainzngs.search_artists(artist=artist, limit=1)
                    
                    if artist_results.get("artist-list"):
                        st.error("MusicBrainz에서 해당 아티스트는 찾았지만, 앨범 제목이 정확하지 않은 것 같습니다. 앨범 제목의 철자를 확인해주세요.")
                    else:
                        st.error("MusicBrainz에서 해당 아티스트를 찾을 수 없습니다. 아티스트 이름의 철자를 확인해주세요.")
                    validation_passed = False
            
            if validation_passed:
                new_album = {
                    "artist": artist, "title": title,
                    "features": {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length},
                    "genres": genre_selection
                }
                custom_albums = load_custom_albums()
                if any(a['title'] == title and a['artist'] == artist for a in custom_albums):
                    st.warning("이미 등록된 앨범입니다.")
                else:
                    custom_albums.append(new_album)
                    save_custom_albums(custom_albums)
                    st.success(f"✅ '{title}' 앨범을 성공적으로 추가했습니다!")
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
