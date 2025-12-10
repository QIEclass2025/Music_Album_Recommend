# album_recommender_demo.py
import tkinter as tk
from tkinter import ttk
import musicbrainzngs

# ===== MusicBrainz API Setup =====
# Set a user-agent to identify our app to the MusicBrainz servers
musicbrainzngs.set_useragent(
    "AlbumRecommenderDemo",
    "0.1",
    "https://github.com/your-username/your-repo",  # Replace with your actual repo if you have one
)

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


def score_album(album, user_state):
    score = 0
    for attr in ATTRS:
        if attr == "focus":
            diff = album["focus"] - user_state["focus"]
            if diff <= 0: attr_score = 0
            elif diff == 1: attr_score = -3
            else: attr_score = -5
        else:
            diff = abs(album[attr] - user_state[attr])
            if diff == 0: attr_score = 5
            elif diff == 1: attr_score = 3
            elif diff == 2: attr_score = 0
            elif diff == 3: attr_score = -3
            else: attr_score = -5
        score += attr_score
    return score


def recommend(user_state, top_k=3):
    user_len = user_state["length"]
    filtered_albums = [album for album in ALBUMS if album["length"] <= user_len]
    if not filtered_albums: return []
    
    scored = [(score_album(album, user_state), album) for album in filtered_albums]
    scored.sort(key=lambda x: (-x[0], abs(x[1]["length"] - user_len)))
    return scored[:top_k]

def get_tracklist(artist_name, album_title):
    try:
        artist_result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        if not artist_result['artist-list']:
            return ["- 아티스트 정보를 찾을 수 없습니다."]
        artist_id = artist_result['artist-list'][0]['id']

        release_result = musicbrainzngs.search_releases(arid=artist_id, release=album_title, limit=1, primarytype="album")
        if not release_result['release-list']:
            return ["- 앨범 정보를 찾을 수 없습니다."]
        release_id = release_result['release-list'][0]['id']

        album_details = musicbrainzngs.get_release_by_id(release_id, includes=["recordings"])
        track_list = ["\n수록곡:"]
        for track in album_details['release']['medium-list'][0]['track-list']:
            track_list.append(f"  {track['number']}. {track['recording']['title']}")
        return track_list
    except Exception as e:
        return [f"- 트랙 정보 오류: {e}"]


class AlbumRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 앨범 추천 프로그램 🎧")
        self.root.geometry("450x400")

        self.user_state_vars = {}
        self.current_question_index = 0

        self.root.configure(background='#2E2E2E')

        self.container = ttk.Frame(self.root, style='Dark.TFrame')
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_current_question()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_current_question(self):
        self.clear_container()
        self.root.geometry("450x400")

        question_data = QUESTIONS[self.current_question_index]
        key = question_data["key"]

        frame = ttk.LabelFrame(self.container, text=question_data["text"])
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        var = tk.IntVar()
        self.user_state_vars[key] = var
        if len(question_data["options"]) > 2:
             var.set(question_data["options"][2][2])
        else:
             var.set(question_data["options"][0][2])

        for _, label, value in question_data["options"]:
            rb = ttk.Radiobutton(frame, text=label, variable=var, value=value)
            rb.pack(anchor=tk.W, padx=15, pady=5)

        button_frame = ttk.Frame(self.container, style='Dark.TFrame')
        button_frame.pack(pady=10)
        next_button = ttk.Button(button_frame, text="다음", command=self.next_question)
        next_button.pack()

    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index < len(QUESTIONS):
            self.show_current_question()
        else:
            self.show_recommendations()

    def show_recommendations(self):
        self.clear_container()
        self.root.geometry("550x500")
        
        user_state = {key: var.get() for key, var in self.user_state_vars.items()}
        results = recommend(user_state, top_k=3)

        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        title_label = ttk.Label(frame, text="===== 추천 결과 TOP 3 =====", style='Title.TLabel')
        title_label.pack(pady=(10, 20))

        if not results:
            no_results_label = ttk.Label(frame, text="추천할 앨범이 없어요. 😢")
            no_results_label.pack(pady=10)
        else:
            for i, (score, album) in enumerate(results, start=1):
                result_text = f"{i}. {album['artist']} – {album['title']}  | 점수: {score}"
                result_label = ttk.Label(frame, text=result_text, style='Result.TLabel')
                result_label.pack(anchor=tk.W, padx=10, pady=(10,0))
                
                # Fetch and display tracklist
                track_list = get_tracklist(album['artist'], album['title'])
                track_text = "\n".join(track_list)
                track_label = ttk.Label(frame, text=track_text, justify=tk.LEFT, style='Track.TLabel')
                track_label.pack(anchor=tk.W, padx=10, pady=(0, 10))

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=30, fill='x')
        
        restart_button = ttk.Button(button_frame, text="다시 시작", command=self.restart)
        restart_button.pack(side='left', expand=True, padx=20)

        exit_button = ttk.Button(button_frame, text="종료", command=self.root.destroy)
        exit_button.pack(side='right', expand=True, padx=20)

    def restart(self):
        self.current_question_index = 0
        self.user_state_vars = {}
        self.show_current_question()

def main_gui():
    root = tk.Tk()
    
    BG_DARK = "#2E2E2E"
    BG_LIGHT = "#FAEBD7"
    TEXT_DARK = "#1C1C1C"
    BUTTON_BG = "#DDC0A9"
    BUTTON_ACTIVE_BG = "#C9A887"
    
    FONT_NORMAL = ("Helvetica", 11)
    FONT_BOLD = ("Helvetica", 12, "bold")
    FONT_TITLE = ("Helvetica", 14, "bold")
    FONT_RESULT = ("Helvetica", 12, "bold")
    FONT_TRACK = ("Helvetica", 10)

    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure('.', background=BG_LIGHT, foreground=TEXT_DARK, font=FONT_NORMAL, bordercolor=BG_LIGHT)
    
    style.configure('Dark.TFrame', background=BG_DARK)
    style.configure('TFrame', background=BG_LIGHT)

    style.configure('TLabelFrame', background=BG_LIGHT, relief="recess", borderwidth=1)
    style.configure('TLabelFrame.Label', background=BG_LIGHT, foreground=TEXT_DARK, font=FONT_TITLE, padding=(10, 5))

    style.configure('TLabel', background=BG_LIGHT, foreground=TEXT_DARK)
    style.configure('Title.TLabel', font=("Helvetica", 16, "bold"))
    style.configure('Result.TLabel', font=FONT_RESULT)
    style.configure('Track.TLabel', font=FONT_TRACK)

    style.configure('TRadiobutton', background=BG_LIGHT, foreground=TEXT_DARK, font=FONT_NORMAL)
    
    style.configure('TButton', font=FONT_BOLD, borderwidth=0, relief="flat", padding=5)
    style.map('TButton',
        background=[('!active', BUTTON_BG), ('active', BUTTON_ACTIVE_BG)],
        foreground=[('!active', TEXT_DARK)]
    )

    app = AlbumRecommenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()