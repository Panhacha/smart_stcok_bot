import psycopg2

DB_URL = "postgresql://postgres.gjdjqnffelyxsgzzgpmn:cGz5ehrrgez8YtaB@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def main():
    print("Connecting to Supabase PostgreSQL to add 'delete' to transaction_type enum...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        try:
            cur.execute("ALTER TYPE transaction_type ADD VALUE 'delete';")
            print("Successfully added 'delete' to transaction_type enum.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("'delete' enum value already exists.")
            else:
                print(f"Error adding enum value: {e}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
