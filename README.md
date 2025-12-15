# 🎵 나만의 AI 음악 추천기

이 프로젝트는 사용자의 현재 기분과 취향에 맞는 앨범을 추천해주는 Streamlit 기반의 웹 애플리케이션입니다.

다양한 음악적 특징(템포, 에너지, 분위기 등)을 조절하여 개인화된 추천을 받을 수 있으며, Spotify와 MusicBrainz API를 연동하여 풍부한 앨범 정보를 제공합니다.

## ✨ 주요 기능

- **기분 기반 추천**: 템포, 에너지, 분위기, 감상 시간 등 5가지 슬라이더를 조절하여 기분에 맞는 앨범을 추천받을 수 있습니다.
- **장르별 필터링**: 락/인디, 펑크/뉴웨이브 등 원하는 장르 카테고리를 선택하여 추천 결과를 필터링할 수 있습니다.
- **Spotify 연동**: 추천된 앨범의 커버 이미지와 Spotify 바로가기 링크를 제공합니다.
- **MusicBrainz 연동**: 앨범의 장르 정보를 자동으로 가져와 필터링 및 정보 표시에 사용합니다.
- **사용자 앨범 관리**: 추천 데이터베이스에 없는 자신만의 앨범을 직접 추가하고 관리하는 기능을 제공합니다.
- **재미 요소**: 데이터 분석을 기다리는 동안 음악 상식 또는 퀴즈를 풀며 지루함을 덜 수 있습니다.

## ⚙️ 설치 및 실행 방법

이 프로젝트는 Python 패키지 관리 도구인 `uv`를 사용하여 환경을 구성합니다.

### 1. 사전 준비

- **Python**: Python 3.8 이상이 설치되어 있어야 합니다.
- **uv 설치**: 터미널(명령 프롬프트)에 아래 명령어를 입력하여 `uv`를 설치합니다.
  ```bash
  pip install uv
  ```
- **Spotify API 키**:
    1. [Spotify for Developers](https://developer.spotify.com/dashboard/)에 접속하여 로그인 후, `Create App` 버튼을 눌러 새 앱을 생성합니다.
    2. 생성된 앱 대시보드에서 `Client ID`와 `Client Secret`을 복사합니다.
    3. `Edit Settings`를 누르고, `Redirect URIs` 항목에 `http://127.0.0.1:8888`을 추가하고 저장합니다.
    4. `Fin_music_app.py` 파일 상단의 `client_id`와 `client_secret` 변수 값을 자신의 키로 교체해야 합니다.

### 2. 프로젝트 실행

1.  **프로젝트 폴더로 이동**: 터미널에서 `MRA` 폴더로 이동합니다.
    ```bash
    cd /Users/izo/Desktop/MRA/
    ```

2.  **가상 환경 생성 및 패키지 설치 (최초 1회)**
    - 아래 명령어를 실행하여 가상 환경을 만들고 필요한 모든 패키지를 설치합니다.
    ```bash
    uv sync
    ```

3.  **앱 실행**
    - 설치가 완료되면, 아래 명령어로 앱을 실행합니다.
    ```bash
    uv run streamlit run Fin_music_app.py
    ```

## 🛠️ 사용된 기술 및 API

- **언어**: Python
- **프레임워크**: Streamlit
- **패키지 관리**: uv
- **주요 의존성**: (`pyproject.toml` 파일 참조)
  - `streamlit`
  - `spotipy`
  - `musicbrainzngs`
- **API**:
  - [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
  - [MusicBrainz API](https://musicbrainz.org/doc/Development/XML_Web_Service/)