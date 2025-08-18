import pandas as pd
import psycopg2
import yfinance as yf
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import warnings

# 모든 경고 무시
warnings.filterwarnings("ignore")
load_dotenv()

host = os.environ["SUPABASE_HOST"]
port = os.environ.get("SUPABASE_PORT", 5432)
db   = os.environ["SUPABASE_DB"]
user = os.environ["SUPABASE_USER"]
pw   = os.environ["SUPABASE_PASSWORD"]

url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}?sslmode=require"
engine = create_engine(url, connect_args={"sslmode":"require"}, pool_pre_ping=True)

with engine.begin() as conn:
    df_test = pd.read_sql("SELECT * FROM stock_data", engine)

ticker_alias = pd.read_excel(".." + os.sep + "stock_list.xlsx")
df = pd.merge(df_test, ticker_alias, on = 'ticker', how='inner')
df = pd.pivot_table(df, index = 'date', columns = 'alias', values = "close").reset_index()
df = df[df.nasdaq.notna()]

for col in df.columns:
    if col == "date":
        pass
    else :
        df[f"{col}_monthly"] = df[col].pct_change(21)

df['금/은'] = df['금']/df['은']

df = pd.melt(df, id_vars = 'date').dropna()

with engine.begin() as conn:
    df.to_sql("stock_addp", con=conn, if_exists="replace", index=False)
    print('DB saved')