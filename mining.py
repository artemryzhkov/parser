import sqlite3
import pandas as pd

conn = sqlite3.connect("ya.db")

cursor = conn.cursor()

df = pd.read_sql_query("SELECT * FROM data", conn)
df.head()
conn.commit()