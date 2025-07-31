#!/usr/bin/env python
# coding: utf-8

# In[50]:


import pandas as pd
import yfinance as yf
import seaborn as sns
import os
sns.set_theme(style="darkgrid")


# In[62]:


from sqlalchemy import create_engine, text

# DB 파일 생성 및 연결
engine = create_engine("sqlite:///mydb.sqlite")


# In[65]:


query_text = """select * from stock where 1=1 and
                Ticker in ('Gold', 'Silver')
                """
query = text(query_text)
with engine.connect() as conn:
    df = pd.read_sql(query, con=engine)


# In[67]:


df = pd.pivot_table(df, index='Date', columns='Ticker', values='value', observed=True).reset_index()


# In[69]:


df['Gold/Silver'] = df['Gold']/df['Silver']


# In[71]:


import streamlit as st
# Streamlit 차트
st.title("📈 금/은 비율 추이")
st.line_chart(df.set_index("Date")["Gold/Silver"])

