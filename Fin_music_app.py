# music_app.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import musicbrainzngs
import os
import json
import concurrent.futures
import random

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
# 1. 콘텐츠 데이터 (상식 & 퀴즈)
# ==========================================

# 1-1. 음악 상식 리스트
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
    "유튜브 최초의 10억 조회수 뮤직비디오는 싸이의 '강남스타일'입니다.",
    "피아노 건반은 과거에 코끼리 상아로 만들었으나, 현재는 동물 보호를 위해 플라스틱이나 합성 재료를 씁니다.",
    "바이올린 활은 보통 말의 꼬리털(말총)로 만들며, 송진을 발라 마찰력을 높입니다.",
    "성악에서 사람의 목소리는 가장 정교하고 아름다운 악기로 취급됩니다.",
    "레코드판(LP)은 바깥쪽에서 시작해 안쪽으로 가면서 재생됩니다.",
    "좋아하는 음악을 들으면 뇌에서 도파민(행복 호르몬)이 분비되어 기분이 좋아집니다.",
    "세계에서 가장 큰 악기는 미국 버지니아주 루레이 동굴에 있는 '종유석 오르간'입니다.",
    "개는 인간보다 청력이 발달해 높은 주파수 음역대를 들을 수 있어, 음악에 다르게 반응할 수 있습니다.",
    "베토벤은 청력을 완전히 잃은 후에도 피아노 진동을 몸으로 느끼며 작곡을 계속했습니다.",
    "과거 기타 줄은 양의 창자(거트)를 꼬아서 만들었습니다.",
    "K-Pop 아이돌의 '칼군무'와 '응원법'은 해외 팬들에게 매우 신선한 충격을 주는 문화입니다.",
    "스트라디바리우스 바이올린은 수백억 원을 호가하며, 그 음색의 비밀은 아직 완전히 밝혀지지 않았습니다.",
    "메탈리카는 2013년 남극에서 콘서트를 열어, 1년 안에 7개 대륙 모두에서 공연한 밴드가 되었습니다.",
    "우주비행사 크리스 해드필드는 국제우주정거장(ISS) 무중력 상태에서 기타를 치며 노래했습니다.",
    "가수들이 음정을 보정할 때 쓰는 '오토튠' 기술은 원래 지질학자가 석유 매장지를 탐사하는 데이터 분석법에서 유래했습니다.",
    "다빈치의 '모나리자' 배경 속에 숨겨진 악보가 있다는 미스터리한 주장이 제기된 적이 있습니다.",
    "영화 해리포터의 신비로운 테마곡 소리는 '첼레스타'라는 건반 악기로 연주되었습니다.",
    "재즈(Jazz)라는 단어의 정확한 어원은 아무도 모릅니다. (Jasm, Jass 등 여러 설이 존재)",
    "세계에서 가장 짧은 노래는 그라인드코어 밴드 Napalm Death의 'You Suffer'로, 딱 1.316초입니다.",
    "음악 치료는 치매 환자의 잃어버린 기억을 순간적으로 되살리는 데 큰 효과가 있습니다.",
    "고양이는 인간의 음악보다, 고양이의 주파수에 맞춘 '고양이 전용 음악'에 더 반응합니다.",
    "방탄소년단의 팬클럽 'ARMY'는 'Adorable Representative M.C for Youth'의 약자입니다.",
    "일렉트릭 기타의 명가 '펜더(Fender)'의 창립자 레오 펜더는 정작 기타를 칠 줄 몰랐습니다.",
    "오케스트라가 연주 전 튜닝할 때 기준이 되는 음은 오보에가 부는 '라(A, 440Hz)'입니다.",
    "세계 최대 음원 플랫폼 스포티파이(Spotify)는 미국이 아닌 스웨덴 기업입니다.",
    "힙합 문화(DJ, 랩, 비보잉, 그래피티)는 1970년대 뉴욕 브롱크스 빈민가 파티에서 시작되었습니다.",
    "한국의 가야금은 12줄, 거문고는 6줄이며 명주실을 꼬아 만듭니다.",
    "노래방 기계(Karaoke)는 일본에서 처음 발명되었으며 '가짜(Kara) 오케스트라(Oke)'라는 뜻입니다.",
    "머라이어 캐리의 캐럴은 매년 12월만 되면 차트 1위를 차지해 '크리스마스 연금'이라 불립니다.",
    "음악의 3요소는 리듬(Rhythm), 멜로디(Melody), 하모니(Harmony)입니다.",
    "지휘자가 지휘봉을 쓰는 주된 이유는 넓은 무대 끝에 있는 연주자에게도 손짓을 명확히 보여주기 위해서입니다.",
    "프레데릭 쇼팽은 '피아노의 시인'이라는 별명을 가지고 있습니다.",
    "바흐는 '음악의 아버지', 헨델은 '음악의 어머니'라 불리지만 둘 다 남성입니다.",
    "세계 최초의 아이돌(팬덤형) 그룹은 영국의 비틀즈라고 보는 시각이 많습니다.",
    "LP판의 한 면에는 여러 개의 홈이 있는 게 아니라, 사실 단 하나의 긴 나선형 홈이 이어져 있습니다.",
    "일렉트릭 기타는 앰프(증폭기)를 끄면 줄 튕기는 소리밖에 안 들려 아주 조용합니다.",
    "존 케이지의 '4분 33초'는 연주자가 무대에서 아무 소리도 내지 않고 4분 33초간 앉아있는 곡입니다.",
    "오페라 가수들은 마이크를 쓰지 않고도 거대한 공연장을 울릴 수 있는 발성 훈련을 합니다.",
    "인간이 들을 수 있는 가청 주파수는 약 20Hz에서 20,000Hz 사이입니다.",
    "빠른 템포의 음악을 들으며 술을 마시면 평소보다 더 빨리 마시게 된다는 연구가 있습니다.",
    "공포 영화 효과음에는 '워터폰(Waterphone)'이라는 기괴한 소리를 내는 악기가 자주 쓰입니다."
]

# 1-2. 음악 퀴즈 리스트
QUIZ_LIST = [
    ("방탄소년단의 데뷔곡 제목은?", "No More Dream"),
    ("피아노의 건반 개수는 총 몇 개일까요?", "88개"),
    ("비틀즈의 멤버가 아닌 사람은? (존 레논, 폴 매카트니, 엘비스 프레슬리, 링고 스타)", "엘비스 프레슬리"),
    ("음악의 아버지라 불리는 바로크 시대 작곡가는?", "바흐"),
    ("소리가 전혀 나지 않는 존 케이지의 연주곡 제목은?", "4분 33초"),
    ("모차르트의 오페라 중 '밤의 여왕 아리아'가 나오는 작품은?", "마술피리"),
    ("가수 아이유의 공식 팬클럽 이름은?", "유애나"),
    ("일반적인 어쿠스틱/일렉트릭 기타의 줄 개수는?", "6개"),
    ("영화 '보헤미안 랩소디'의 주인공인 전설적인 록 밴드는?", "Queen (퀸)"),
    ("우리나라 최초의 창작 동요 '반달'을 지은 사람은?", "윤극영"),
    ("다음 중 금관악기가 아닌 것은? (트럼펫, 색소폰, 호른, 튜바)", "색소폰 (색소폰은 목관악기입니다)"),
    ("악보에서 '점점 세게'를 뜻하는 이탈리아어 용어는?", "크레센도 (Crescendo)"),
    ("마이클 잭슨의 트레이드 마크인, 뒤로 미끄러지듯 걷는 춤은?", "문워크 (Moonwalk)"),
    ("오케스트라 튜닝의 기준이 되는 악기는?", "오보에"),
    ("계이름 '도(Do)'는 알파벳으로 무엇일까요?", "C"),
    ("비발디의 바이올린 협주곡 '사계' 중 가장 유명한 계절은?", "봄"),
    ("1969년 열린 전설적인 록 페스티벌의 이름은?", "우드스탁 페스티벌"),
    ("한국 대중음악상(KMA)은 판매량보다 무엇을 중시하나요?", "음악성"),
    ("걸그룹 블랙핑크의 데뷔곡이 아닌 것은? (붐바야, 휘파람, How You Like That)", "How You Like That"),
    ("가수 싸이의 '강남스타일' 포인트 안무 이름은?", "말춤"),
    ("뉴진스(NewJeans)의 데뷔곡 중 하나인 이 곡은? (Hype Boy, Attention, Ditto)", "Attention (또는 Hype Boy)"),
    ("세계적인 첼리스트 요요마가 연주하는 악기는?", "첼로"),
    ("국악기 중 줄이 12개인 악기는?", "가야금"),
    ("국악기 중 줄이 6개이며 술대로 쳐서 소리 내는 악기는?", "거문고"),
    ("베토벤의 교향곡 5번의 별명은?", "운명 교향곡"),
    ("베토벤의 교향곡 9번의 별명은?", "합창 교향곡"),
    ("쇼팽이 주로 작곡한 악기 분야는?", "피아노"),
    ("록 밴드 너바나(Nirvana)의 리드 보컬 이름은?", "커트 코베인"),
    ("가수 김광석의 대표곡이 아닌 것은? (서른 즈음에, 이등병의 편지, 붉은 노을)", "붉은 노을 (이문세의 곡)"),
    ("악보에서 '도돌이표'를 만나면 어떻게 해야 할까요?", "지정된 구간을 반복한다"),
    ("4분의 4박자에서 한 마디에 들어가는 4분 음표의 개수는?", "4개"),
    ("다음 중 현악기가 아닌 것은? (바이올린, 비올라, 첼로, 플루트)", "플루트 (목관악기)"),
    ("드럼 세트에서 발로 밟아 소리 내는 큰 북의 이름은?", "베이스 드럼 (킥 드럼)"),
    ("가수 조용필의 별명은?", "가왕"),
    ("엘비스 프레슬리의 별명은?", "로큰롤의 제왕"),
    ("마돈나의 별명은?", "팝의 여왕"),
    ("SM 엔터테인먼트의 설립자는?", "이수만"),
    ("JYP 엔터테인먼트의 수장은?", "박진영"),
    ("하이브(HYBE) 의장인 방시혁의 별명은?", "히트맨 뱅"),
    ("뮤지컬 '오페라의 유령', '캣츠'를 만든 작곡가는?", "앤드류 로이드 웨버"),
    ("영화 '타이타닉'의 주제곡 'My Heart Will Go On'을 부른 가수는?", "셀린 디온"),
    ("영화 '겨울왕국'의 주제곡 'Let It Go'를 부른 캐릭터는?", "엘사"),
    ("재즈에서 즉흥적으로 연주하는 것을 무엇이라고 할까요?", "임프로비제이션 (Improvisation) / 애드립"),
    ("힙합 문화의 4대 요소가 아닌 것은? (MC, DJ, 비보잉, 발레)", "발레"),
    ("우리나라의 대표적인 민요로, 유네스코 인류무형문화유산인 곡은?", "아리랑"),
    ("판소리에서 고수가 치는 악기는?", "북"),
    ("사물놀이 악기가 아닌 것은? (꽹과리, 징, 장구, 해금)", "해금 (사물놀이는 타악기 중심)"),
    ("바이올린, 비올라, 첼로, 콘트라베이스 중 가장 큰 악기는?", "콘트라베이스"),
    ("피아노의 원래 이름인 '피아노포르테'의 뜻은?", "약하고(Piano) 강하게(Forte) 연주할 수 있는 악기"),
    ("세계 3대 테너가 아닌 사람은? (루치아노 파바로티, 플라시도 도밍고, 호세 카레라스, 안드레아 보첼리)", "안드레아 보첼리 (팝페라 가수로 분류됨)"),
    ("다음 중 건반 악기가 아닌 것은? (피아노, 오르간, 하프시코드, 하프)", "하프 (현악기)"),
    ("지휘자가 지휘할 때 서 있는 단상의 이름은?", "포디움")
]


# ==========================================
# 2. 기본 데이터 (MANUAL_FEATURES & ALBUMS)
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

# !!! 병렬 처리 시 데드락 방지를 위해 캐시 제거 !!!
# @st.cache_data 
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
    
    st.divider()
    # 대기 모드 선택 (상식 vs 퀴즈)
    waiting_mode = st.sidebar.radio(
        "⏳ 기다리는 동안 무엇을 할까요?",
        ["음악 상식 읽기", "음악 퀴즈 풀기"],
        index=0,
        help="데이터 분석 중 지루하지 않게 즐길 거리를 선택하세요."
    )

    # --- 추천 로직 ---
    if st.sidebar.button("🎵 앨범 추천받기", type="primary"):
        if not sp:
            st.error("스포티파이 인증에 실패했습니다. 페이지를 새로고침하거나 캐시를 삭제해보세요."); return
        
        user_state = {"tempo": tempo, "energy": energy, "brightness": brightness, "length": length}
        
        # 진행률 표시줄과 텍스트 공간 생성
        progress_text = st.empty()
        percent_text = st.empty()  # 퍼센트 표시용 텍스트 공간
        progress_bar = st.progress(0)
        
        # 1) 데이터 수집 (병렬 처리 적용)
        all_albums = []
        custom_albums = load_custom_albums()
        total_items = len(ALBUMS) + len(custom_albums)
        completed_items = 0

        # 병렬 처리를 위한 작업자(Worker) 수 설정
        MAX_WORKERS = 8 
        
        # 퀴즈 모드용 변수
        current_quiz = random.choice(QUIZ_LIST)
        quiz_start_time = time.time() # 퀴즈 시작 시간 기록
        quiz_state = "question" # question (5초) -> answer (3초)
        
        # 상식 모드용 변수
        current_trivia = random.choice(TRIVIA_LIST)
        trivia_start_time = time.time()

        with st.spinner("데이터를 분석하고 있습니다..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # 작업 예약
                future_to_album = {executor.submit(get_album_data, sp, album): album for album in ALBUMS}
                
                # Non-blocking 폴링 방식 사용
                pending_futures = set(future_to_album.keys())
                
                while pending_futures:
                    # 0.1초 동안 완료된 작업이 있는지 확인
                    done, _ = concurrent.futures.wait(pending_futures, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)
                    
                    # 완료된 작업 처리
                    for future in done:
                        try:
                            data = future.result()
                            if data: all_albums.append(data)
                        except Exception: pass
                        
                        completed_items += 1
                        progress = min(completed_items / total_items, 1.0)
                        
                        # 퍼센트 텍스트 및 프로그레스 바 업데이트
                        percent_text.text(f"진행률 {int(progress * 100)}%")
                        progress_bar.progress(progress)
                        
                        pending_futures.remove(future)

                    # === 대기 화면 콘텐츠 업데이트 로직 ===
                    current_time = time.time()
                    
                    if waiting_mode == "음악 상식 읽기":
                        if current_time - trivia_start_time > 10:
                            current_trivia = random.choice(TRIVIA_LIST)
                            trivia_start_time = current_time
                        progress_text.info(f"💡 알고 계셨나요?\n\n{current_trivia}")
                        
                    elif waiting_mode == "음악 퀴즈 풀기":
                        elapsed_time = current_time - quiz_start_time
                        
                        if elapsed_time < 5:
                            countdown = 5 - int(elapsed_time)
                            progress_text.warning(f"❓ 퀴즈! (⏳ {countdown}초 후 공개)\n\nQ. {current_quiz[0]}")
                            quiz_state = "question"
                        elif elapsed_time < 8: # 5초 + 3초 = 8초
                            progress_text.success(f"✅ 정답!\n\nA. {current_quiz[1]}")
                            quiz_state = "answer"
                        else:
                            current_quiz = random.choice(QUIZ_LIST)
                            quiz_start_time = current_time
                            quiz_state = "question"
                            progress_text.warning(f"❓ 퀴즈! (⏳ 5초 후 공개)\n\nQ. {current_quiz[0]}")

            # 사용자 추가 앨범 처리 (병렬 처리 미적용)
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

        progress_text.empty() # 텍스트 지우기
        percent_text.empty()  # 퍼센트 텍스트 지우기
        progress_bar.empty()  # 바 지우기

        # 2) 점수 계산 + 필터링 (기존 로직)
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
        if st.form_submit_button("이 아티스트의 앨범 검색"): 
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
                title = st.text_input("앨범 제목 직접 입력*", help="검색으로 찾지 못한 경우 직접 입력하세요.")

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

            validation_passed = True

            is_title_from_selectbox = (artist and 
                                       st.session_state.mb_search_artist == artist and 
                                       st.session_state.mb_found_album_titles and
                                       title in st.session_state.mb_found_album_titles)
            
            if not is_title_from_selectbox:
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