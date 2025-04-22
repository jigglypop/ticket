# 티켓링크 예매 매크로 사용법

이 매크로는 브라우저가 아니라 HTTP 레벨에서 직접 티켓링크 API를 호출해  
초저지연으로 좌석 예약을 시도합니다.  

---

## 📦 환경 준비

1. Python 3.8 이상  
2. 필수 라이브러리 설치
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔐 `.env` 파일 설정

프로젝트 최상위(`main.py`와 동일 폴더)에 `.env` 파일을 만들고,  
다음 변수를 설정합니다:

```dotenv
# .env
TICKET_EMAIL=your_email@example.com   # 로그인 이메일
TICKET_PASS=your_password             # 로그인 비밀번호
EVENT_ID=XXXXXX                       # 예매할 공연/이벤트 ID
TARGET_DATE=2025-05-01                # 예매 오픈 일자 (YYYY-MM-DD)
TARGET_TIME=10:00:00                  # 예매 오픈 시각 (HH:MM:SS)
SEAT_NAME=A1                          # 예약할 좌석 이름 (예: A1)
```

> **TIP.**  
> - `.gitignore` 에 `.env` 추가하여 민감 정보 유출 방지  
> - 실제 엔드포인트나 CSRF 헤더 키 이름은 개발자 도구 네트워크 탭 확인 후 조정

---

## 🚀 실행 방법

터미널에서 프로젝트 루트로 이동 후:

```bash
python main.py

```

- 로그인이 완료되면 설정한 시각(`TARGET_DATE` + `TARGET_TIME`)까지  
  50ms 간격으로 좌석 상태를 폴링(polling)합니다.  
- 원하는 좌석이 나타나면 즉시 예약 요청을 보내고 성공 여부를 출력합니다.

---

## ⚙️ 코드 구조 개요

```text
book_macro.py
├─ load_dotenv()                # .env 로드
├─ async def login(...)         # CSRF → 로그인 처리
├─ async def poll_seats(...)    # 좌석 조회 반복(polling)
├─ async def book_seat(...)     # 좌석 예약 요청
└─ async def main()             # 전체 워크플로우 실행
```

- `httpx.AsyncClient(http2=True)` 로 HTTP/2 연결 유지  
- `asyncio.sleep(0.05)` 으로 50ms 간격 조회  
- `datetime.fromisoformat` → 타임스탬프 계산

---

## ⚠️ 주의사항

- **서비스 약관** 위반 소지 및 IP 차단 위험  
- 캡차·SMS 인증 단계 자동화는 **불가능** 혹은 **위험**  
- 무차별 과도 요청은 네트워크 차단 대상  
- 민감정보(`.env`)는 절대 공개 저장소에 커밋 금지  

---

## 🛠️ 커스터마이징

- **CSRF 헤더/쿠키 키**: 실제 응답 헤더 네임에 맞춰 수정  
- **API 엔드포인트**: 네트워크 탭에서 최신 URL로 동기화  
- **폴링 주기**(`sleep`): 서버 과부하를 고려해 조절  
