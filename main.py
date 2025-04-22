# book_macro.py

import os
import time
import asyncio
from datetime import datetime
import httpx
from dotenv import load_dotenv

# 1) .env 로드
load_dotenv()  
EMAIL       = os.getenv("TICKET_EMAIL")
PASSWORD    = os.getenv("TICKET_PASS")
EVENT_ID    = os.getenv("EVENT_ID")
TARGET_DATE = os.getenv("TARGET_DATE")      # YYYY-MM-DD
TARGET_TIME = os.getenv("TARGET_TIME")      # HH:MM:SS
SEAT_NAME   = os.getenv("SEAT_NAME")

# 2) 로그인 함수
async def login(client: httpx.AsyncClient):
    # (1) CSRF 토큰 획득
    resp = await client.get("https://ticketlink.kakao.com/login")
    csrf = resp.headers.get("x-csrf-token") or resp.cookies.get("csrf_token")
    # (2) 로그인 요청
    payload = {"email": EMAIL, "password": PASSWORD}
    headers = {"x-csrf-token": csrf}
    await client.post("https://ticketlink.kakao.com/api/v1/auth", json=payload, headers=headers)
    print("[+] 로그인 완료")

# 3) 좌석 조회 폴링
async def poll_seats(client: httpx.AsyncClient, target_ts: float) -> bool:
    url = f"https://ticketlink.kakao.com/api/v1/events/{EVENT_ID}/seats"
    while time.time() < target_ts:
        await asyncio.sleep(0.05)  # 50ms 간격
        r = await client.get(url)
        seats = r.json().get("seats", [])
        for seat in seats:
            if seat.get("name") == SEAT_NAME and seat.get("available"):
                print(f"[+] 좌석 {SEAT_NAME} 발견!")
                return True
    print("[-] 좌석 폴링 타임아웃")
    return False

# 4) 예약 요청
async def book_seat(client: httpx.AsyncClient) -> bool:
    payload = {"eventId": EVENT_ID, "seat": SEAT_NAME}
    r = await client.post("https://ticketlink.kakao.com/api/v1/book", json=payload)
    return r.status_code == 200

# 5) 메인 실행
async def main():
    # 목표 시각 타임스탬프로 변환
    dt = datetime.fromisoformat(f"{TARGET_DATE}T{TARGET_TIME}")
    target_ts = dt.timestamp()
    
    async with httpx.AsyncClient(http2=True) as client:
        await login(client)
        found = await poll_seats(client, target_ts)
        if found:
            success = await book_seat(client)
            print("🎉 예약 성공!" if success else "⚠️ 예약 실패…")
        else:
            print("⚠️ 좌석을 찾지 못했습니다.")

if __name__ == "__main__":
    asyncio.run(main())
