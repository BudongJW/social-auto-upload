# social-auto-upload - TikTok 자동 업로드

Playwright 기반 TikTok 영상 자동 업로드 도구.
MoneyPrinterTurbo와 연동하여 영상 생성 → 업로드 파이프라인 구성.

> 원본: [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload)

---

## 지원 플랫폼

| 플랫폼 | 로그인 | 영상 업로드 | 예약 발행 | 헤드리스 |
|---|---|---|---|---|
| TikTok | O | O | O | O |
| 抖音 (Douyin) | O | O | O | O |
| Bilibili | O | O | O | O |
| 小红书 | O | O | O | O |
| YouTube | O | O | - | O |

> 현재 파이프라인에서는 **TikTok**만 사용 중.

## 사전 준비

```bash
# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

## 설정

`conf.py` (없으면 `conf.example.py` 복사):

```python
LOCAL_CHROME_PATH = ""          # 빈 문자열 = Playwright 내장 Chromium 사용
LOCAL_CHROME_HEADLESS = True    # True = 헤드리스 (자동화), False = 브라우저 표시
```

## TikTok 쿠키 설정 (최초 1회)

```bash
python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

1. 브라우저가 열림
2. TikTok 로그인 (구글/이메일 등)
3. Playwright 디버거에서 ▶ (Resume) 클릭
4. `cookies/tk_uploader/account.json`에 쿠키 저장됨

> 쿠키 만료 시 위 과정 반복.

## 사용 방법

### MoneyPrinterTurbo 파이프라인 연동 (권장)

```bash
cd ../MoneyPrinterTurbo
python auto_pipeline.py
```

자동으로 `videos/` 폴더에 영상 + 메타데이터 복사 후 TikTok 업로드.

### 단독 업로드

`videos/` 폴더에 영상 파일과 동일 이름의 `.txt` 파일 배치:

```
videos/
├── my_video.mp4
└── my_video.txt     # 1줄: 제목 / 2줄: 해시태그
```

`.txt` 형식:
```
Why Cats Are The Best Pets
#cats #pets #catlover #shorts #fyp
```

## 수정 사항 (원본 대비)

- **executable_path 빈 문자열 크래시 수정**: `"" → None` 폴백
- **cookie_auth 타임아웃 수정**: `networkidle → domcontentloaded + 5s wait`
- **모달 오버레이 자동 처리**: 콘텐츠 체크 모달, joyride 튜토리얼, "Continue to post?" 확인 모달
- **헤드리스 모드 기본 활성화**: `conf.py`에서 `LOCAL_CHROME_HEADLESS = True`

## 디렉토리 구조

```
social-auto-upload/
├── conf.py                              # 설정
├── cookies/tk_uploader/account.json     # TikTok 쿠키 (로그인 후 생성)
├── videos/                              # 업로드할 영상 + 메타데이터
├── uploader/
│   └── tk_uploader/
│       └── main_chrome.py               # TikTok 업로드 (Playwright)
└── utils/
    └── files_times.py                   # 메타데이터 파싱
```

## 라이선스

MIT License - 원본 프로젝트 라이선스를 따름.
