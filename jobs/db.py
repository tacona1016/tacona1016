# jobs/db.py
import os
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine, text
import re

# 1) DB 경로와 상위 폴더 자동 생성 (Windows 포함)
DB_PATH = os.getenv("DB_PATH", "data/market.sqlite3")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

@contextmanager
def get_conn():
    with engine.begin() as conn:
        yield conn

UPSERT_PRICE = """
INSERT INTO prices(ticker,date,open,high,low,close,adj_close,volume)
VALUES (:ticker,:date,:open,:high,:low,:close,:adj_close,:volume)
ON CONFLICT(ticker,date) DO UPDATE SET
 open=excluded.open,
 high=excluded.high,
 low=excluded.low,
 close=excluded.close,
 adj_close=excluded.adj_close,
 volume=excluded.volume;
"""

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS prices(
  ticker TEXT, date DATE,
  open REAL, high REAL, low REAL, close REAL, adj_close REAL, volume INTEGER,
  PRIMARY KEY(ticker, date)
);
CREATE INDEX IF NOT EXISTS idx_prices_date ON prices(date);

CREATE TABLE IF NOT EXISTS dividends(
  ticker TEXT, date DATE, dividend REAL,
  PRIMARY KEY(ticker, date)
);

CREATE TABLE IF NOT EXISTS splits(
  ticker TEXT, date DATE, split REAL,
  PRIMARY KEY(ticker, date)
);

CREATE TABLE IF NOT EXISTS meta(
  ticker TEXT PRIMARY KEY,
  name TEXT,
  currency TEXT,
  exchange TEXT,
  last_price_update DATE
);
"""

def init_db():
    # 2) 세미콜론을 추가로 붙이지 말고, 문장 단위로 깨끗하게 분리하여 그대로 실행
    statements = [
        s.strip().rstrip(";")  # 끝의 ; 제거
        for s in re.split(r";\s*(?:\r?\n)+", CREATE_SQL.strip())
        if s.strip()
    ]
    with get_conn() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)  # 여기서 ';' 추가 금지!