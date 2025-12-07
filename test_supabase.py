from config import conn
import pandas as pd

c = conn.cursor()

# Test 1: Check games count
c.execute("SELECT COUNT(*) FROM games")
games_count = c.fetchone()[0]
print(f"✅ Total Games: {games_count}")

# Test 2: Check genres
c.execute("SELECT COUNT(*) FROM genres")
genres_count = c.fetchone()[0]
print(f"✅ Total Genres: {genres_count}")

# Test 3: Check regional sales
c.execute("SELECT COUNT(*) FROM regional_sales")
sales_count = c.fetchone()[0]
print(f"✅ Total Regional Sales Records: {sales_count}")

# Test 4: Sample query - Top 5 games
query = '''
    SELECT 
        g.game_name,
        p.publisher_name,
        SUM(rs.sales_in_millions)::numeric AS total_sales
    FROM regional_sales rs
    JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
    JOIN games g ON gr.game_id = g.game_id
    JOIN publishers p ON g.publisher_id = p.publisher_id
    GROUP BY g.game_id, g.game_name, p.publisher_id, p.publisher_name
    ORDER BY total_sales DESC
    LIMIT 5
'''
df = pd.read_sql(query, conn)
print(f"\n✅ Top 5 Games (Sample Query):")
print(df.to_string(index=False))

c.close()
conn.close()
print("\n✅ All tests passed! Supabase connection is working correctly!")
