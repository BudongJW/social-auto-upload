# social-auto-upload - TikTok 자동 업로드

[Playwright](https://playwright.dev/) 기반 TikTok 영상 자동 업로드 도구.
[MoneyPrinterTurbo](https://github.com/BudongJW/MoneyPrinterTurbo)와 연동하여 **영상 생성 → 업로드** 파이프라인을 구성합니다.

**전체 파이프라인 세팅 가이드는 [MoneyPrinterTurbo README](https://github.com/BudongJW/MoneyPrinterTurbo#readme)를 참고하세요.**

> 원본: [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload)

---

## 전체 구성도

```
부모 폴더/
├── MoneyPrinterTurbo/      ← 영상 생성 + 파이프라인 (메인 레포)
└── social-auto-upload/     ← 이 레포 (TikTok 업로드)
```

두 레포가 **같은 부모 폴더**에 나란히 있어야 파이프라인이 동작합니다.

## 지원 플랫폼

| 플랫폼 | 로그인 | 영상 업로드 | 예약 발행 | 헤드리스 |
|---|---|---|---|---|
| [TikTok](https://www.tiktok.com/) | O | O | O | O |
| Douyin (抖音) | O | O | O | O |
| [Bilibili](https://www.bilibili.com/) | O | O | O | O |
| Xiaohongshu (小红书) | O | O | O | O |
| [YouTube](https://www.youtube.com/) | O | O | - | O |

> 현재 파이프라인에서는 **TikTok**만 사용 중.

---

## 이 레포만 단독으로 사용할 때

### Step 1. 사전 설치

| 프로그램 | 다운로드 | 설치 확인 |
|---|---|---|
| **Python 3.10~3.12** | [python.org/downloads](https://www.python.org/downloads/) | `python --version` |
| **Git** | [git-scm.com](https://git-scm.com/download/win) | `git --version` |

### Step 2. 클론 및 의존성 설치

```bash
git clone https://github.com/BudongJW/social-auto-upload.git
cd social-auto-upload

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (Chromium 자동 다운로드, ~150MB)
playwright install chromium
```

### Step 3. 설정 파일 생성

```bash
copy conf.example.py conf.py            # Windows
# cp conf.example.py conf.py            # Mac/Linux
```

`conf.py`에서 확인할 항목:

```python
LOCAL_CHROME_PATH = ""          # 빈 문자열 = Playwright 내장 Chromium 사용 (수정 불필요)
LOCAL_CHROME_HEADLESS = True    # True = 백그라운드 자동 업로드
```

> 별도 Chrome을 쓰고 싶으면 `LOCAL_CHROME_PATH`에 경로 입력.
> 예: `"C:/Program Files/Google/Chrome/Application/chrome.exe"`

### Step 4. TikTok 로그인 (최초 1회)

```bash
python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

1. Chromium 브라우저가 **일반 모드**로 열림
2. [TikTok](https://www.tiktok.com/) 로그인 (구글/이메일/전화번호)
3. 로그인 완료 후 Playwright Inspector에서 **▶ Resume** 클릭
4. `cookies/tk_uploader/account.json` 파일 생성됨

> 쿠키 만료 시(보통 며칠~2주) 이 과정을 다시 실행.
> 만료 증상: "Cookie expired. Re-login required." 메시지.

---

## 사용 방법

### MoneyPrinterTurbo 파이프라인 연동 (권장)

```bash
cd ../MoneyPrinterTurbo
venv\Scripts\activate
python auto_pipeline.py
```

또는 `MoneyPrinterTurbo/run_pipeline.bat` 더블클릭.

자동으로 영상 생성 → `videos/`에 복사 → TikTok 업로드 → 임시 파일 삭제.

### 단독 업로드 (영상 파일을 직접 넣을 때)

`videos/` 폴더에 **영상 파일**과 **동일 이름의 .txt 파일**을 함께 배치:

```
videos/
├── my_video.mp4
└── my_video.txt
```

`.txt` 파일 형식 (1줄: 제목, 2줄: 해시태그):
```
Why Cats Are The Best Pets
#cats #pets #catlover #shorts #fyp
```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `ENOENT` 에러 | Chrome 경로 문제 | `conf.py`의 `LOCAL_CHROME_PATH = ""` 확인 |
| Cookie expired | 세션 만료 | Step 4 TikTok 로그인 다시 실행 |
| 업로드 중 멈춤 | TikTok UI 변경 | `LOCAL_CHROME_HEADLESS = False`로 바꿔서 확인 |
| `playwright` 에러 | 브라우저 미설치 | `playwright install chromium` 재실행 |
| `conf` import 에러 | 설정 파일 없음 | `conf.example.py` → `conf.py` 복사 |
| `pip install` 실패 | Python 버전 | Python 3.10~3.12 권장 |

## 수정 사항 (원본 대비)

- **executable_path 빈 문자열 크래시 수정**: `"" → None` 폴백
- **cookie_auth 타임아웃 수정**: `networkidle → domcontentloaded + 5s wait`
- **모달 오버레이 자동 처리**: 콘텐츠 체크 모달, joyride 튜토리얼, "Continue to post?" 확인 모달
- **헤드리스 모드 기본 활성화**: `conf.py`에서 `LOCAL_CHROME_HEADLESS = True`

## 디렉토리 구조

```
social-auto-upload/
├── conf.py                     # 설정 (conf.example.py에서 복사)
├── conf.example.py             # 설정 예제
├── cookies/tk_uploader/        # TikTok 쿠키 (로그인 후 자동 생성, .gitignore 대상)
├── videos/                     # 업로드할 영상 (파이프라인 완료 시 자동 삭제)
├── uploader/tk_uploader/       # TikTok 업로드 로직 (Playwright)
└── utils/                      # 유틸리티 (메타데이터 파싱 등)
```

## 라이선스

MIT License - 원본 프로젝트 라이선스를 따름.
