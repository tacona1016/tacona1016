# yfinance → SQLite → Streamlit (Minimal Template)

자동 수집(batch)으로 SQLite에 적재하고, Streamlit 대시보드에서 읽는 **최소 동작 리포 템플릿**입니다.

## 구성

```
repo/
├─ app/
│  └─ streamlit_app.py
├─ jobs/
│  ├─ fetch_and_load.py
│  └─ db.py
├─ data/
│  └─ market.sqlite3        # 최초 실행 후 생성
├─ .github/workflows/
│  └─ fetch.yml             # (선택) GitHub Actions 배치
├─ .env.example
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## 로컬에서 실행

1) 의존성 설치

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) 환경 파일 생성

```bash
cp .env.example .env
# 필요한 값 수정 (티커, 시작일 등)
```

3) 최초 DB 생성 및 적재

```bash
python jobs/fetch_and_load.py
```

4) 대시보드 실행

```bash
streamlit run app/streamlit_app.py
```

## 스케줄 자동화 (선택)

- GitHub Actions의 cron은 **UTC 기준**입니다. 한국시간 오전 09:00에 맞추려면 UTC 00:00에 실행.
- 저장소 Settings → Secrets and variables → Actions에서 `TICKERS`, `DEFAULT_START` 등을 Secrets로 등록하세요.

## 참고

- yfinance는 인증키가 필요 없습니다.
- 테이블은 `(ticker, date)`를 PK로 하는 upsert로 증분 적재합니다.
- 데이터가 늘면 `VACUUM` 또는 월별 스냅샷을 고려하세요.
