# social-auto-upload - TikTok 자동 업로드

Playwright 기반 TikTok 영상 자동 업로드 도구.
MoneyPrinterTurbo와 연동하여 **영상 생성 → 업로드** 파이프라인을 구성합니다.

> 원본: [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload)

---

## 전체 구성도

```
부모 폴더/
├── MoneyPrinterTurbo/      ← 영상 생성 레포
└── social-auto-upload/     ← 이 레포 (TikTok 업로드)
```

두 레포가 **같은 부모 폴더**에 나란히 있어야 파이프라인이 동작합니다.
전체 세팅 가이드는 **MoneyPrinterTurbo의 README**를 참고하세요.

## 지원 플랫폼

| 플랫폼 | 로그인 | 영상 업로드 | 예약 발행 | 헤드리스 |
|---|---|---|---|---|
| TikTok | O | O | O | O |
| 抖音 (Douyin) | O | O | O | O |
| Bilibili | O | O | O | O |
| 小红书 | O | O | O | O |
| YouTube | O | O | - | O |

> 현재 파이프라인에서는 **TikTok**만 사용 중.

---

## 세팅 가이드 (이 레포만 단독 사용할 때)

### Step 1. 클론 및 의존성 설치

```bash
git clone https://github.com/BudongJW/social-auto-upload.git
cd social-auto-upload

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Step 2. 설정 파일 생성

```bash
copy conf.example.py conf.py            # Windows
# cp conf.example.py conf.py            # Mac/Linux
```

`conf.py` 내용:

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
XHS_SERVER = "http://127.0.0.1:11901"  # 샤오홍슈 전용 (TikTok 사용 시 무시)
LOCAL_CHROME_PATH = ""                  # 빈 문자열 = Playwright 내장 Chromium 사용
LOCAL_CHROME_HEADLESS = True            # True = 헤드리스 (자동화), False = 브라우저 표시
DEBUG_MODE = True
```

> `LOCAL_CHROME_PATH`를 빈 문자열로 두면 Playwright가 자동 설치한 Chromium을 사용합니다.
> 별도 Chrome을 쓰고 싶으면 경로를 지정하세요 (예: `C:/Program Files/Google/Chrome/Application/chrome.exe`).

### Step 3. TikTok 로그인 (최초 1회)

```bash
python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

1. Chromium 브라우저가 **일반 모드**로 열림 (헤드리스 아님)
2. TikTok 로그인 페이지가 표시됨
3. **구글/이메일/전화번호** 등으로 로그인
4. 로그인 완료 후 Playwright Inspector 창에서 **▶ Resume** 버튼 클릭
5. `cookies/tk_uploader/account.json` 파일이 생성됨 (세션 쿠키 저장)

> 쿠키가 만료되면 이 과정을 다시 실행하면 됩니다.
> 만료 증상: 업로드 시 "Cookie expired. Re-login required." 메시지 출력.

---

## 사용 방법

### MoneyPrinterTurbo 파이프라인 연동 (권장)

```bash
cd ../MoneyPrinterTurbo
venv\Scripts\activate
python auto_pipeline.py
```

자동으로 `videos/` 폴더에 영상 + 메타데이터가 복사된 후 TikTok 업로드가 진행됩니다.

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

| 증상 | 해결 |
|---|---|
| `ENOENT` 에러 | `conf.py`의 `LOCAL_CHROME_PATH = ""`인지 확인 (빈 문자열이어야 함) |
| Cookie expired 메시지 | Step 3 TikTok 로그인 다시 실행 |
| 업로드 중 멈춤 | TikTok UI 변경일 수 있음. `LOCAL_CHROME_HEADLESS = False`로 바꿔서 브라우저 확인 |
| `playwright._impl._errors.Error` | `playwright install chromium` 재실행 |
| conf 모듈 import 에러 | `conf.py` 파일이 존재하는지 확인 (`conf.example.py`에서 복사) |

## 수정 사항 (원본 대비)

- **executable_path 빈 문자열 크래시 수정**: `"" → None` 폴백
- **cookie_auth 타임아웃 수정**: `networkidle → domcontentloaded + 5s wait`
- **모달 오버레이 자동 처리**: 콘텐츠 체크 모달, joyride 튜토리얼, "Continue to post?" 확인 모달
- **헤드리스 모드 기본 활성화**: `conf.py`에서 `LOCAL_CHROME_HEADLESS = True`

## 디렉토리 구조

```
social-auto-upload/
├── conf.py                              # 설정 (conf.example.py에서 복사)
├── conf.example.py                      # 설정 예제
├── cookies/
│   └── tk_uploader/
│       └── account.json                 # TikTok 쿠키 (로그인 후 생성)
├── videos/                              # 업로드할 영상 + 메타데이터
│   ├── example.mp4
│   └── example.txt
├── uploader/
│   └── tk_uploader/
│       ├── main_chrome.py               # TikTok 업로드 (Playwright)
│       └── tk_config.py                 # TikTok 셀렉터 설정
└── utils/
    ├── files_times.py                   # 메타데이터 파싱
    └── base_social_media.py             # 공통 유틸
```

## 라이선스

MIT License - 원본 프로젝트 라이선스를 따름.
