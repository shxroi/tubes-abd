import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Koneksi ke database Supabase PostgreSQL
try:
    conn = psycopg2.connect(
        host=os.getenv("SUPABASE_HOST", "aws-1-ap-south-1.pooler.supabase.com"),
        port=os.getenv("SUPABASE_PORT", "5432"),
        user=os.getenv("SUPABASE_USER", "postgres.sdzgspgymazncfktpcrp"),
        password=os.getenv("SUPABASE_PASSWORD", "postgres"),
        dbname=os.getenv("SUPABASE_DB", "postgres"),
        sslmode="require"  # Supabase memerlukan SSL
    )
    print("✅ Koneksi Supabase PostgreSQL berhasil!")
except psycopg2.Error as e:
    print(f"❌ Gagal terhubung ke Supabase: {e}")
    raise

# Membuat cursor
c = conn.cursor()

# ============================
# Fungsi ambil data dari tabel
# ============================

def view_games():
    """Menampilkan semua games dengan informasi publisher"""
    query = '''
        SELECT 
            g.game_id, 
            g.game_name, 
            p.publisher_name
        FROM games g
        JOIN publishers p ON g.publisher_id = p.publisher_id
        ORDER BY g.game_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_games_with_genres():
    """Menampilkan games dengan genre-genrenya"""
    query = '''
        SELECT 
            g.game_id,
            g.game_name,
            STRING_AGG(ge.genre_name, ', ') AS genres,
            p.publisher_name
        FROM games g
        JOIN publishers p ON g.publisher_id = p.publisher_id
        LEFT JOIN game_genres gg ON g.game_id = gg.game_id
        LEFT JOIN genres ge ON gg.genre_id = ge.genre_id
        GROUP BY g.game_id, g.game_name, p.publisher_name
        ORDER BY g.game_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_game_releases():
    """Menampilkan rilis game per platform"""
    query = '''
        SELECT 
            gr.game_release_id,
            g.game_name,
            pl.platform_name,
            pl.platform_code,
            gr.release_year,
            p.publisher_name
        FROM game_releases gr
        JOIN games g ON gr.game_id = g.game_id
        JOIN platforms pl ON gr.platform_id = pl.platform_id
        JOIN publishers p ON g.publisher_id = p.publisher_id
        ORDER BY gr.release_year DESC, g.game_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_regional_sales():
    """Menampilkan data penjualan regional"""
    query = '''
        SELECT 
            rs.sale_id,
            g.game_name,
            pl.platform_code,
            r.region_name,
            rs.sales_in_millions,
            gr.release_year
        FROM regional_sales rs
        JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
        JOIN games g ON gr.game_id = g.game_id
        JOIN platforms pl ON gr.platform_id = pl.platform_id
        JOIN regions r ON rs.region_id = r.region_id
        ORDER BY rs.sales_in_millions DESC
    '''
    c.execute(query)
    return c.fetchall()

def view_top_selling_games(limit=10):
    """Menampilkan top N games berdasarkan total penjualan"""
    query = '''
        SELECT 
            g.game_name,
            p.publisher_name,
            SUM(rs.sales_in_millions) AS total_sales
        FROM regional_sales rs
        JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
        JOIN games g ON gr.game_id = g.game_id
        JOIN publishers p ON g.publisher_id = p.publisher_id
        GROUP BY g.game_id, g.game_name, p.publisher_name
        ORDER BY total_sales DESC
        LIMIT %s
    '''
    c.execute(query, (limit,))
    return c.fetchall()

def view_sales_by_region():
    """Menampilkan total penjualan per region"""
    query = '''
        SELECT 
            r.region_name,
            SUM(rs.sales_in_millions) AS total_sales
        FROM regional_sales rs
        JOIN regions r ON rs.region_id = r.region_id
        GROUP BY r.region_id, r.region_name
        ORDER BY total_sales DESC
    '''
    c.execute(query)
    return c.fetchall()

def view_sales_by_platform():
    """Menampilkan total penjualan per platform"""
    query = '''
        SELECT 
            pl.platform_name,
            pl.platform_code,
            COUNT(DISTINCT gr.game_id) AS game_count,
            SUM(rs.sales_in_millions) AS total_sales
        FROM regional_sales rs
        JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
        JOIN platforms pl ON gr.platform_id = pl.platform_id
        GROUP BY pl.platform_id, pl.platform_name, pl.platform_code
        ORDER BY total_sales DESC
    '''
    c.execute(query)
    return c.fetchall()

def view_sales_by_genre():
    """Menampilkan total penjualan per genre"""
    query = '''
        SELECT 
            ge.genre_name,
            COUNT(DISTINCT g.game_id) AS game_count,
            SUM(rs.sales_in_millions) AS total_sales
        FROM regional_sales rs
        JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
        JOIN games g ON gr.game_id = g.game_id
        JOIN game_genres gg ON g.game_id = gg.game_id
        JOIN genres ge ON gg.genre_id = ge.genre_id
        GROUP BY ge.genre_id, ge.genre_name
        ORDER BY total_sales DESC
    '''
    c.execute(query)
    return c.fetchall()

def view_publishers():
    """Menampilkan semua publishers"""
    query = '''
        SELECT publisher_id, publisher_name, country, founded_year
        FROM publishers
        ORDER BY publisher_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_platforms():
    """Menampilkan semua platforms"""
    query = '''
        SELECT platform_id, platform_code, platform_name, manufacturer, release_year
        FROM platforms
        ORDER BY platform_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_genres():
    """Menampilkan semua genres"""
    query = '''
        SELECT genre_id, genre_name, description
        FROM genres
        ORDER BY genre_name ASC
    '''
    c.execute(query)
    return c.fetchall()

def close_connection():
    """Menutup koneksi database"""
    c.close()
    conn.close()
    print("Koneksi database ditutup.")