from config import conn

c = conn.cursor()
c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = c.fetchall()
print(f'Tables in Supabase: {len(tables)}')
for t in tables:
    print(f'  - {t[0]}')
c.close()
conn.close()
