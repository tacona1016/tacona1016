import os, sys, datetime as dt
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import text
from db import get_conn, init_db, UPSERT_PRICE

load_dotenv()
init_db()

TICKERS = [x.strip().upper() for x in os.getenv('TICKERS', 'AAPL,MSFT,TSLA,GC=F,SI=F').split(',') if x.strip()]
DEFAULT_START = os.getenv('DEFAULT_START', '2015-01-01')

def get_last_date(conn, ticker):
    r = conn.exec_driver_sql('SELECT MAX(date) FROM prices WHERE ticker = ?', (ticker,)).fetchone()
    return r[0] if r else None

def fetch_prices(ticker, start, end):
    hist = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)
    if hist.empty:
        return pd.DataFrame(columns=['ticker','date','open','high','low','close','adj_close','volume'])
    df = hist.reset_index().rename(columns={
        'Date':'date','Open':'open','High':'high','Low':'low',
        'Close':'close','Adj Close':'adj_close','Volume':'volume'
    })
    df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)
    df['ticker'] = ticker
    return df[['ticker','date','open','high','low','close','adj_close','volume']]

def upsert_prices(conn, df):
    if df.empty:
        return 0
    rows = df.to_dict(orient='records')
    for row in rows:
        conn.execute(text(UPSERT_PRICE), row)
    return len(rows)

def main():
    today = dt.date.today()
    end = (today + dt.timedelta(days=1)).isoformat()
    total = 0
    with get_conn() as conn:
        for t in TICKERS:
            last = get_last_date(conn, t)
            start = (pd.to_datetime(last) + pd.Timedelta(days=1)).date().isoformat() if last else DEFAULT_START
            df = fetch_prices(t, start, end)
            total += upsert_prices(conn, df)
            conn.exec_driver_sql(
                'INSERT INTO meta(ticker,last_price_update) VALUES(?,?) '
                'ON CONFLICT(ticker) DO UPDATE SET last_price_update=excluded.last_price_update',
                (t, today.isoformat())
            )
    print(f'upserted rows: {total}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
