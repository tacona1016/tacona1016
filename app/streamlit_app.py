import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DB_PATH = os.getenv('DB_PATH', 'data/market.sqlite3')
engine = create_engine(f'sqlite:///{DB_PATH}', future=True)

st.set_page_config(page_title='Market Dashboard', layout='wide')

@st.cache_data(ttl=300)
def load_prices(ticker, start, end):
    q = '''
    SELECT date, open, high, low, close, adj_close, volume
    FROM prices
    WHERE ticker=:ticker AND date BETWEEN :start AND :end
    ORDER BY date
    '''
    with engine.connect() as conn:
        df = pd.read_sql(q, conn, params={'ticker': ticker, 'start': start, 'end': end})
    if df.empty:
        return df
    df['date'] = pd.to_datetime(df['date'])
    return df

st.title('📈 Market Dashboard (SQLite)')

with engine.connect() as conn:
    try:
        tickers = pd.read_sql('SELECT ticker FROM meta ORDER BY ticker', conn)['ticker'].tolist()
    except Exception:
        tickers = []

col1, col2, col3 = st.columns([2,1,1])
ticker = col1.selectbox('Ticker', options=tickers or ['AAPL'])
start = col2.date_input('Start', value=pd.to_datetime('2022-01-01'))
end = col3.date_input('End', value=pd.to_datetime('today'))

if start > end:
    st.error('Start가 End보다 늦을 수 없습니다.')
else:
    df = load_prices(ticker, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    if df.empty:
        st.info('선택한 범위에 데이터가 없습니다. 먼저 배치 잡을 실행하거나 기간을 늘려보세요.')
    else:
        st.line_chart(df.set_index('date')['close'])
        st.bar_chart(df.set_index('date')['volume'])
        st.dataframe(df.tail(20))
