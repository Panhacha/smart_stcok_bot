import psycopg2
import os

DB_URL = "postgresql://postgres.gjdjqnffelyxsgzzgpmn:cGz5ehrrgez8YtaB@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def main():
    print("Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql)
        print("Schema executed successfully!")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
