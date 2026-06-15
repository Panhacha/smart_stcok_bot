import psycopg2

DB_URL = "postgresql://postgres.gjdjqnffelyxsgzzgpmn:cGz5ehrrgez8YtaB@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def main():
    print("Connecting to Supabase PostgreSQL to add 'is_active' to branches table...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        try:
            cur.execute("ALTER TABLE branches ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
            print("Successfully added 'is_active' to branches.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("'is_active' column already exists.")
            else:
                print(f"Error adding column: {e}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
