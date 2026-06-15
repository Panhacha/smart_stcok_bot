import psycopg2
import os

DB_URL = "postgresql://postgres.gjdjqnffelyxsgzzgpmn:cGz5ehrrgez8YtaB@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def main():
    print("Connecting to Supabase PostgreSQL to add is_active column...")
    conn = psycopg2.connect(DB_URL)
    
    with conn.cursor() as cur:
        # Add is_active column if not exists
        cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")
        print("Column is_active added successfully!")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
