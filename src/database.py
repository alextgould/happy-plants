import sqlite3

# PLACEHOLDER CODE (ChatGPT)

if False:

    def store_data(df, db_path="rainfall.db"):
        conn = sqlite3.connect(db_path)
        df.to_sql("rainfall", conn, if_exists="append", index=False)
        conn.close()

    def get_historical_data(db_path="rainfall.db"):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM rainfall", conn)
        conn.close()
        return df