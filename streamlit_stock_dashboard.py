import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")

# ---------- 사이드바 ----------
st.sidebar.title("📌 대시보드 설정")
ticker = st.sidebar.selectbox("종목 선택", ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"])
start_date = st.sidebar.date_input("시작일", date.today() - timedelta(days=180))
end_date = st.sidebar.date_input("종료일", date.today())

# ---------- 데이터 가져오기 ----------
data = yf.download(ticker, start=start_date, end=end_date)
data["MA20"] = data["Close"].rolling(window=20).mean()
data["MA50"] = data["Close"].rolling(window=50).mean()

# ---------- 헤더 ----------
st.title(f"📊 {ticker} 주식 데이터 대시보드")
st.markdown(f"기간: **{start_date}** ~ **{end_date}**")

# ---------- 가격 + 이동평균 차트 ----------
st.subheader("📉 종가 + 이동 평균")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(data.index, data["Close"], label="종가", linewidth=2)
ax.plot(data.index, data["MA20"], label="MA 20", linestyle="--")
ax.plot(data.index, data["MA50"], label="MA 50", linestyle=":")
ax.set_ylabel("가격 ($)")
ax.legend()
st.pyplot(fig)

# ---------- 거래량 차트 ----------
st.subheader("📦 거래량")
fig2, ax2 = plt.subplots(figsize=(12, 2.5))
ax2.bar(data.index, data["Volume"], color="gray")
ax2.set_ylabel("Volume")
st.pyplot(fig2)

# ---------- 테이블 ----------
st.subheader("🧾 최근 데이터")
st.dataframe(data.tail(10).style.format({"Close": "{:.2f}", "Volume": "{:,}"}))
