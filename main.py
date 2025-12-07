import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import (
    view_regional_sales,
    view_top_selling_games,
    view_sales_by_genre,
    view_sales_by_platform,
    view_publishers,
    conn,
    c
)

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="Video Game Sales Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING & THEME
# ============================================================================
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("🎮 Video Game Sales Analysis Dashboard")
st.markdown("---")
st.subheader("Analisis Mendalam Penjualan Game Global")

# ============================================================================
# SIDEBAR - NAVIGASI
# ============================================================================
st.sidebar.header("📊 Navigasi Dashboard")
page = st.sidebar.radio(
    "Pilih Halaman Analisis:",
    [
        "🏠 Ringkasan Keseluruhan",
        "🌍 Penjualan Regional",
        "🎯 Game Paling Laris",
        "📈 Tren Genre",
        "🖥️ Kinerja Platform",
        "🔗 Korelasi Genre-Platform",
        "🏢 Kinerja Penerbit"
    ]
)

# ============================================================================
# FUNGSI HELPER - FETCH DATA
# ============================================================================
@st.cache_data
def get_regional_sales_data():
    """Ambil data penjualan regional"""
    try:
        c.execute('''
            SELECT 
                r.region_name,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN regions r ON rs.region_id = r.region_id
            WHERE r.region_id IS NOT NULL
            GROUP BY r.region_id, r.region_name
            ORDER BY total_sales DESC
        ''')
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Region', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching regional sales: {e}")
        return pd.DataFrame()

@st.cache_data
def get_top_games_data(limit=15):
    """Ambil data top N games terlaris"""
    try:
        c.execute('''
            SELECT 
                g.game_name,
                p.publisher_name,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
            JOIN games g ON gr.game_id = g.game_id
            JOIN publishers p ON g.publisher_id = p.publisher_id
            GROUP BY g.game_id, g.game_name, p.publisher_id, p.publisher_name
            ORDER BY total_sales DESC
            LIMIT %s
        ''', (limit,))
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Game', 'Publisher', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching top games: {e}")
        return pd.DataFrame()

@st.cache_data
def get_genre_sales_data():
    """Ambil data penjualan per genre"""
    try:
        c.execute('''
            SELECT 
                ge.genre_name,
                COUNT(DISTINCT g.game_id) AS game_count,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
            JOIN games g ON gr.game_id = g.game_id
            JOIN game_genres gg ON g.game_id = gg.game_id
            JOIN genres ge ON gg.genre_id = ge.genre_id
            GROUP BY ge.genre_id, ge.genre_name
            ORDER BY total_sales DESC
        ''')
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Genre', 'Game Count', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        df['Game Count'] = pd.to_numeric(df['Game Count'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching genre sales: {e}")
        return pd.DataFrame()

@st.cache_data
def get_platform_sales_data():
    """Ambil data penjualan per platform"""
    try:
        c.execute('''
            SELECT 
                pl.platform_name,
                pl.platform_code,
                COUNT(DISTINCT gr.game_id) AS game_count,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
            JOIN platforms pl ON gr.platform_id = pl.platform_id
            GROUP BY pl.platform_id, pl.platform_name, pl.platform_code
            ORDER BY total_sales DESC
        ''')
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Platform', 'Code', 'Game Count', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        df['Game Count'] = pd.to_numeric(df['Game Count'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching platform sales: {e}")
        return pd.DataFrame()

@st.cache_data
def get_genre_platform_sales_data():
    """Ambil data penjualan genre per platform"""
    try:
        c.execute('''
            SELECT 
                pl.platform_name,
                ge.genre_name,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
            JOIN games g ON gr.game_id = g.game_id
            JOIN platforms pl ON gr.platform_id = pl.platform_id
            JOIN game_genres gg ON g.game_id = gg.game_id
            JOIN genres ge ON gg.genre_id = ge.genre_id
            GROUP BY pl.platform_id, pl.platform_name, ge.genre_id, ge.genre_name
            ORDER BY pl.platform_name, total_sales DESC
        ''')
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Platform', 'Genre', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching genre-platform sales: {e}")
        return pd.DataFrame()

@st.cache_data
def get_publisher_sales_data(limit=15):
    """Ambil data penjualan per penerbit"""
    try:
        c.execute('''
            SELECT 
                p.publisher_name,
                p.country,
                COUNT(DISTINCT g.game_id) AS game_count,
                ROUND(SUM(rs.sales_in_millions)::numeric, 2) AS total_sales
            FROM regional_sales rs
            JOIN game_releases gr ON rs.game_release_id = gr.game_release_id
            JOIN games g ON gr.game_id = g.game_id
            JOIN publishers p ON g.publisher_id = p.publisher_id
            WHERE p.publisher_id IS NOT NULL
            GROUP BY p.publisher_id, p.publisher_name, p.country
            ORDER BY total_sales DESC
            LIMIT %s
        ''', (limit,))
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Publisher', 'Country', 'Game Count', 'Total Sales (Millions)'])
        df['Total Sales (Millions)'] = pd.to_numeric(df['Total Sales (Millions)'], errors='coerce')
        df['Game Count'] = pd.to_numeric(df['Game Count'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching publisher sales: {e}")
        return pd.DataFrame()

# ============================================================================
# HALAMAN 1: RINGKASAN KESELURUHAN
# ============================================================================
if page == "🏠 Ringkasan Keseluruhan":
    st.header("📊 Ringkasan Keseluruhan")
    
    try:
        # Key Metrics
        c.execute('SELECT SUM(sales_in_millions) FROM regional_sales')
        total_sales = c.fetchone()[0] or 0
        
        c.execute('SELECT COUNT(DISTINCT game_id) FROM games')
        total_games = c.fetchone()[0] or 0
        
        c.execute('SELECT COUNT(DISTINCT publisher_id) FROM publishers')
        total_publishers = c.fetchone()[0] or 0
        
        c.execute('SELECT COUNT(DISTINCT platform_id) FROM platforms')
        total_platforms = c.fetchone()[0] or 0
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Total Penjualan Global",
                f"${total_sales:,.2f}M",
                "Dalam Jutaan Dolar"
            )
        
        with col2:
            st.metric(
                "🎮 Total Games",
                f"{total_games:,}",
                "Judul Game Unik"
            )
        
        with col3:
            st.metric(
                "🏢 Total Publishers",
                f"{total_publishers:,}",
                "Perusahaan Penerbit"
            )
        
        with col4:
            st.metric(
                "🖥️ Total Platforms",
                f"{total_platforms:,}",
                "Platform/Konsol"
            )
        
        st.markdown("---")
        
        # Quick Stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Top 5 Games Terlaris")
            top5_games = get_top_games_data(5)
            if not top5_games.empty:
                st.dataframe(top5_games, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("🌍 Top 5 Region Penjualan")
            regional_data = get_regional_sales_data()
            if not regional_data.empty:
                top5_regions = regional_data.head(5)
                st.dataframe(top5_regions, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Error loading summary: {e}")

# ============================================================================
# HALAMAN 2: PENJUALAN REGIONAL
# ============================================================================
elif page == "🌍 Penjualan Regional":
    st.header("🌍 Analisis Penjualan Regional")
    st.markdown("**Pertanyaan:** Bagaimana distribusi total penjualan antar benua?")
    st.markdown("**Narasi Kunci:** Menyoroti wilayah dominan dan wilayah yang memiliki potensi pertumbuhan.")
    
    st.markdown("---")
    
    regional_data = get_regional_sales_data()
    
    if not regional_data.empty:
        col1, col2 = st.columns(2)
        
        # Bar Chart Horizontal (OPTIMAL untuk Penjualan Regional)
        with col1:
            fig_bar_h = px.bar(
                regional_data.sort_values('Total Sales (Millions)', ascending=True),
                y='Region',
                x='Total Sales (Millions)',
                title='📊 Total Penjualan per Region',
                color='Total Sales (Millions)',
                color_continuous_scale='Blues',
                text='Total Sales (Millions)',
                orientation='h',
                labels={'Total Sales (Millions)': 'Penjualan (M$)'}
            )
            fig_bar_h.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
            fig_bar_h.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig_bar_h, use_container_width=True)
        
        # Donut Chart untuk Market Share
        with col2:
            fig_pie = px.pie(
                regional_data,
                names='Region',
                values='Total Sales (Millions)',
                title='🥧 Market Share per Region',
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Sankey Chart untuk menunjukkan aliran penjualan (visualisasi alternatif)
        fig_sunburst = go.Figure(go.Sunburst(
            labels=['Total'] + regional_data['Region'].tolist(),
            parents=[''] + ['Total'] * len(regional_data),
            values=[regional_data['Total Sales (Millions)'].sum()] + regional_data['Total Sales (Millions)'].tolist(),
            marker=dict(
                colorscale='Blues',
                cmid=regional_data['Total Sales (Millions)'].median()
            )
        ))
        fig_sunburst.update_layout(title='🌍 Hierarchical View Penjualan Regional', height=500)
        st.plotly_chart(fig_sunburst, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Data Penjualan Regional")
        regional_data_sorted = regional_data.sort_values('Total Sales (Millions)', ascending=False)
        regional_data_sorted['Persentase'] = (
            regional_data_sorted['Total Sales (Millions)'] / 
            regional_data_sorted['Total Sales (Millions)'].sum() * 100
        ).round(2)
        st.dataframe(regional_data_sorted, use_container_width=True, hide_index=True)
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        top_region = regional_data.loc[regional_data['Total Sales (Millions)'].idxmax()]
        st.markdown(f"""
        - **Wilayah Dominan:** {top_region['Region']} dengan penjualan ${top_region['Total Sales (Millions)']:,.2f}M
        - **Total Penjualan Global:** ${regional_data['Total Sales (Millions)'].sum():,.2f}M
        - **Rata-rata Penjualan Per Region:** ${regional_data['Total Sales (Millions)'].mean():,.2f}M
        """)
    
    else:
        st.warning("Tidak ada data penjualan regional yang ditemukan.")

# ============================================================================
# HALAMAN 3: GAME PALING LARIS
# ============================================================================
elif page == "🎯 Game Paling Laris":
    st.header("🎯 Game Paling Laris Secara Global")
    st.markdown("**Pertanyaan:** Game mana yang menghasilkan pendapatan global tertinggi?")
    st.markdown("**Narasi Kunci:** Menampilkan juara penjualan, memberikan fokus pada nama game dan angka penjualan.")
    
    st.markdown("---")
    
    top_games = get_top_games_data(20)
    
    if not top_games.empty:
        # Lollipop Chart (OPTIMAL untuk ranking) - Urutkan descending
        top_games_sorted = top_games.sort_values('Total Sales (Millions)', ascending=True)
        fig_lollipop = go.Figure(data=[
            go.Scatter(
                x=top_games_sorted['Total Sales (Millions)'],
                y=top_games_sorted['Game'],
                mode='markers+lines',
                marker=dict(
                    size=12,
                    color=top_games_sorted['Total Sales (Millions)'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Sales (M$)")
                ),
                line=dict(width=2, color='darkred'),
                text=top_games_sorted['Publisher'],
                customdata=top_games_sorted['Total Sales (Millions)'],
                hovertemplate='<b>%{y}</b><br>Publisher: %{text}<br>Sales: $%{customdata:.2f}M<extra></extra>'
            )
        ])
        fig_lollipop.update_layout(
            title='🍭 Top 20 Games Terlaris (Lollipop Chart)',
            xaxis_title='Total Penjualan (Juta $)',
            yaxis_title='Game Title',
            height=700,
            hovermode='closest',
            plot_bgcolor='rgba(240,240,240,0.5)',
            yaxis=dict(categoryorder='total ascending')
        )
        st.plotly_chart(fig_lollipop, use_container_width=True)
        
        st.markdown("---")
        
        # Bar Chart Alternative (hapus, diganti dengan insight summary)
        st.markdown("---")
        
        # Sorted Bar Chart untuk perbandingan
        fig_bar = px.bar(
            top_games.sort_values('Total Sales (Millions)', ascending=True),
            y='Game',
            x='Total Sales (Millions)',
            color='Total Sales (Millions)',
            color_continuous_scale='Reds',
            text='Total Sales (Millions)',
            title='📊 Perbandingan Penjualan Top 20 Games',
            labels={'Total Sales (Millions)': 'Penjualan (M$)'},
            hover_data=['Publisher']
        )
        fig_bar.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
        fig_bar.update_layout(height=700, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Top 20 Games")
        top_games_display = top_games.copy()
        top_games_display['Ranking'] = range(1, len(top_games_display) + 1)
        st.dataframe(
            top_games_display[['Ranking', 'Game', 'Publisher', 'Total Sales (Millions)']],
            use_container_width=True,
            hide_index=True
        )
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        top_game = top_games.iloc[0]
        st.markdown(f"""
        - **Game Terlaris:** {top_game['Game']} dengan penjualan ${top_game['Total Sales (Millions)']:,.2f}M
        - **Publisher:** {top_game['Publisher']}
        - **Total Penjualan Top 5 Games:** ${top_games.head(5)['Total Sales (Millions)'].sum():,.2f}M
        - **Rata-rata Penjualan Top 20:** ${top_games['Total Sales (Millions)'].mean():,.2f}M
        """)
    
    else:
        st.warning("Tidak ada data game yang ditemukan.")

# ============================================================================
# HALAMAN 4: TREN GENRE
# ============================================================================
elif page == "📈 Tren Genre":
    st.header("📈 Analisis Tren Genre")
    st.markdown("**Pertanyaan:** Genre mana yang paling populer dan menghasilkan penjualan tertinggi secara global?")
    st.markdown("**Narasi Kunci:** Menunjukkan porsi pasar setiap genre dalam total penjualan.")
    
    st.markdown("---")
    
    genre_data = get_genre_sales_data()
    
    if not genre_data.empty:
        col1, col2 = st.columns(2)
        
        # Donut Chart untuk Market Share (OPTIMAL)
        with col1:
            fig_donut = px.pie(
                genre_data,
                names='Genre',
                values='Total Sales (Millions)',
                title='🥧 Genre Market Share',
                hole=0.4
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10)
            st.plotly_chart(fig_donut, use_container_width=True)
        
        # Treemap (OPTIMAL untuk hierarchical view)
        with col2:
            fig_treemap = go.Figure(go.Treemap(
                labels=genre_data['Genre'].tolist(),
                parents=[''] * len(genre_data),
                values=genre_data['Total Sales (Millions)'].tolist(),
                marker=dict(
                    colorscale='RdYlGn',
                    cmid=genre_data['Total Sales (Millions)'].median(),
                    colorbar=dict(title="Sales (M$)")
                ),
                textposition='middle center',
                hovertemplate='<b>%{label}</b><br>Sales: $%{value:.2f}M<extra></extra>'
            ))
            fig_treemap.update_layout(
                title='🗺️ Genre Sales Distribution (Treemap)',
                height=500,
                font=dict(size=11)
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
        
        st.markdown("---")
        
        # Bar Chart untuk perbandingan detail
        fig_bar = px.bar(
            genre_data.sort_values('Total Sales (Millions)', ascending=True),
            y='Genre',
            x='Total Sales (Millions)',
            color='Total Sales (Millions)',
            color_continuous_scale='Viridis',
            text='Total Sales (Millions)',
            title='📊 Ranking Genre berdasarkan Penjualan',
            labels={'Total Sales (Millions)': 'Penjualan (M$)'},
            hover_data=['Game Count']
        )
        fig_bar.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
        fig_bar.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Penjualan per Genre")
        genre_data_sorted = genre_data.sort_values('Total Sales (Millions)', ascending=False)
        genre_data_sorted['Persentase'] = (
            genre_data_sorted['Total Sales (Millions)'] / 
            genre_data_sorted['Total Sales (Millions)'].sum() * 100
        ).round(2)
        st.dataframe(genre_data_sorted, use_container_width=True, hide_index=True)
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        top_genre = genre_data.loc[genre_data['Total Sales (Millions)'].idxmax()]
        st.markdown(f"""
        - **Genre Terpopuler:** {top_genre['Genre']} dengan penjualan ${top_genre['Total Sales (Millions)']:,.2f}M
        - **Jumlah Game:** {int(top_genre['Game Count'])} game
        - **Total Penjualan Semua Genre:** ${genre_data['Total Sales (Millions)'].sum():,.2f}M
        - **Rata-rata Penjualan per Genre:** ${genre_data['Total Sales (Millions)'].mean():,.2f}M
        """)
    
    else:
        st.warning("Tidak ada data genre yang ditemukan.")

# ============================================================================
# HALAMAN 5: KINERJA PLATFORM
# ============================================================================
elif page == "🖥️ Kinerja Platform":
    st.header("🖥️ Analisis Kinerja Platform")
    st.markdown("**Pertanyaan:** Platform mana yang mendominasi pasar saat ini atau selama periode tertentu?")
    st.markdown("**Narasi Kunci:** Membandingkan kekuatan pasar antar konsol/PC.")
    
    st.markdown("---")
    
    platform_data = get_platform_sales_data()
    
    if not platform_data.empty:
        col1, col2 = st.columns(2)
        
        # Bar Chart Horizontal (OPTIMAL untuk platform comparison)
        with col1:
            fig_bar = px.bar(
                platform_data.sort_values('Total Sales (Millions)', ascending=True),
                y='Platform',
                x='Total Sales (Millions)',
                color='Total Sales (Millions)',
                color_continuous_scale='Blues',
                text='Total Sales (Millions)',
                title='📊 Platform Market Performance',
                labels={'Total Sales (Millions)': 'Penjualan (M$)'},
                hover_data=['Code', 'Game Count']
            )
            fig_bar.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
            fig_bar.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Bubble Chart (Games Count vs Sales) - lebih informatif
        with col2:
            fig_bubble = px.scatter(
                platform_data,
                x='Game Count',
                y='Total Sales (Millions)',
                size='Total Sales (Millions)',
                color='Total Sales (Millions)',
                color_continuous_scale='Blues',
                text='Platform',
                title='🔵 Platform Efficiency: Games Count vs Sales',
                labels={'Game Count': 'Jumlah Game', 'Total Sales (Millions)': 'Total Sales (M$)'},
                size_max=60
            )
            fig_bubble.update_traces(textposition='top center', textfont_size=10)
            fig_bubble.update_layout(height=500, hovermode='closest')
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Kinerja Platform")
        platform_data_sorted = platform_data.sort_values('Total Sales (Millions)', ascending=False)
        platform_data_sorted['Persentase'] = (
            platform_data_sorted['Total Sales (Millions)'] / 
            platform_data_sorted['Total Sales (Millions)'].sum() * 100
        ).round(2)
        st.dataframe(platform_data_sorted, use_container_width=True, hide_index=True)
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        top_platform = platform_data.loc[platform_data['Total Sales (Millions)'].idxmax()]
        st.markdown(f"""
        - **Platform Dominan:** {top_platform['Platform']} dengan penjualan ${top_platform['Total Sales (Millions)']:,.2f}M
        - **Jumlah Game:** {int(top_platform['Game Count'])} game
        - **Total Penjualan Semua Platform:** ${platform_data['Total Sales (Millions)'].sum():,.2f}M
        - **Rata-rata Penjualan per Platform:** ${platform_data['Total Sales (Millions)'].mean():,.2f}M
        """)
    
    else:
        st.warning("Tidak ada data platform yang ditemukan.")

# ============================================================================
# HALAMAN 6: KORELASI GENRE-PLATFORM
# ============================================================================
elif page == "🔗 Korelasi Genre-Platform":
    st.header("🔗 Analisis Korelasi Genre-Platform")
    st.markdown("**Pertanyaan:** Genre apa yang paling laris di Platform tertentu?")
    st.markdown("**Narasi Kunci:** Mengidentifikasi kecocokan pasar (misalnya, Sports mendominasi di PS5, Strategy di PC).")
    
    st.markdown("---")
    
    genre_platform_data = get_genre_platform_sales_data()
    
    if not genre_platform_data.empty:
        # Get top platforms - convert to numeric first
        genre_platform_data['Total Sales (Millions)'] = pd.to_numeric(genre_platform_data['Total Sales (Millions)'], errors='coerce')
        top_platforms = genre_platform_data.groupby('Platform')['Total Sales (Millions)'].sum().nlargest(10).index.tolist()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            selected_platform = st.selectbox(
                "Pilih Platform untuk Detail Genre:",
                top_platforms
            )
        
        with col2:
            show_all = st.checkbox("Tampilkan Semua Platform")
        
        st.markdown("---")
        
        if show_all:
            platforms_to_show = genre_platform_data['Platform'].unique()
            title_suffix = "Semua Platform"
        else:
            platforms_to_show = [selected_platform]
            title_suffix = f"{selected_platform}"
        
        # Grouped Bar Chart (lebih baik dari stacked untuk perbandingan)
        filtered_data = genre_platform_data[genre_platform_data['Platform'].isin(platforms_to_show)]
        
        fig_grouped = px.bar(
            filtered_data,
            x='Platform',
            y='Total Sales (Millions)',
            color='Genre',
            title=f'📊 Genre Sales Distribution - {title_suffix}',
            labels={'Total Sales (Millions)': 'Penjualan (M$)'},
            barmode='group',
            height=600
        )
        fig_grouped.update_layout(hovermode='x unified', legend=dict(title='Genre'))
        st.plotly_chart(fig_grouped, use_container_width=True)
        
        st.markdown("---")
        
        # Detail untuk selected platform
        selected_data = genre_platform_data[genre_platform_data['Platform'] == selected_platform].sort_values('Total Sales (Millions)', ascending=True)
        
        if not selected_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart untuk genre ranking di selected platform
                fig_bar = px.bar(
                    selected_data,
                    y='Genre',
                    x='Total Sales (Millions)',
                    color='Total Sales (Millions)',
                    color_continuous_scale='Purples',
                    text='Total Sales (Millions)',
                    title=f'📊 Genre Ranking di {selected_platform}',
                    labels={'Total Sales (Millions)': 'Penjualan (M$)'}
                )
                fig_bar.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
                fig_bar.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Donut untuk market share di selected platform
            with col2:
                fig_pie = px.pie(
                    selected_data,
                    names='Genre',
                    values='Total Sales (Millions)',
                    title=f'🥧 Genre Market Share di {selected_platform}',
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Genre-Platform Sales")
        display_data = genre_platform_data.sort_values('Total Sales (Millions)', ascending=False)
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        
        platform_genre_combo = genre_platform_data.loc[genre_platform_data['Total Sales (Millions)'].idxmax()]
        st.markdown(f"""
        - **Best Genre-Platform Combo:** {platform_genre_combo['Genre']} di {platform_genre_combo['Platform']} 
          dengan penjualan ${platform_genre_combo['Total Sales (Millions)']:,.2f}M
        - **Total Kombinasi Unik:** {len(genre_platform_data)} kombinasi
        - **Platform dengan Keragaman Genre Terbesar:** {genre_platform_data.groupby('Platform')['Genre'].nunique().idxmax()}
        """)
    
    else:
        st.warning("Tidak ada data korelasi genre-platform yang ditemukan.")

# ============================================================================
# HALAMAN 7: KINERJA PENERBIT
# ============================================================================
elif page == "🏢 Kinerja Penerbit":
    st.header("🏢 Analisis Kinerja Penerbit")
    st.markdown("**Pertanyaan:** Publisher mana yang paling sukses dalam hal volume penjualan?")
    st.markdown("**Narasi Kunci:** Membandingkan performa publisher secara langsung.")
    
    st.markdown("---")
    
    publisher_data = get_publisher_sales_data(20)
    
    if not publisher_data.empty:
        # Bar Chart (PRIMARY - untuk ranking)
        fig_bar = px.bar(
            publisher_data.sort_values('Total Sales (Millions)', ascending=True),
            y='Publisher',
            x='Total Sales (Millions)',
            color='Total Sales (Millions)',
            color_continuous_scale='Greens',
            text='Total Sales (Millions)',
            title='📊 Top 20 Publishers by Sales Volume',
            labels={'Total Sales (Millions)': 'Penjualan (M$)'},
            hover_data=['Country', 'Game Count']
        )
        fig_bar.update_traces(textposition='outside', texttemplate='$%{x:.2f}M')
        fig_bar.update_layout(height=700, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bubble Chart: Games Count vs Sales (untuk efficiency analysis)
            fig_bubble = px.scatter(
                publisher_data,
                x='Game Count',
                y='Total Sales (Millions)',
                size='Total Sales (Millions)',
                color='Total Sales (Millions)',
                color_continuous_scale='Greens',
                text='Publisher',
                title='🔵 Publisher Efficiency: Games vs Sales',
                labels={'Game Count': 'Jumlah Game Dirilis', 'Total Sales (Millions)': 'Total Sales (M$)'},
                hover_data=['Country'],
                size_max=50
            )
            fig_bubble.update_traces(textposition='top center', textfont_size=9)
            fig_bubble.update_layout(height=500, hovermode='closest')
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Top 5 publishers pie
        with col2:
            top5_pub = publisher_data.head(5)
            total_top5 = top5_pub['Total Sales (Millions)'].sum()
            others = publisher_data.iloc[5:]['Total Sales (Millions)'].sum()
            
            pie_data = pd.concat([
                top5_pub[['Publisher', 'Total Sales (Millions)']],
                pd.DataFrame({'Publisher': ['Others'], 'Total Sales (Millions)': [others]})
            ])
            
            fig_pie = px.pie(
                pie_data,
                names='Publisher',
                values='Total Sales (Millions)',
                title='🥧 Market Share: Top 5 vs Others',
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Detail Top 20 Publishers")
        pub_display = publisher_data.copy()
        pub_display['Ranking'] = range(1, len(pub_display) + 1)
        pub_display_sorted = pub_display.sort_values('Total Sales (Millions)', ascending=False)
        pub_display_sorted['Persentase'] = (
            pub_display_sorted['Total Sales (Millions)'] / 
            pub_display_sorted['Total Sales (Millions)'].sum() * 100
        ).round(2)
        st.dataframe(
            pub_display_sorted[['Ranking', 'Publisher', 'Country', 'Game Count', 'Total Sales (Millions)', 'Persentase']],
            use_container_width=True,
            hide_index=True
        )
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        top_pub = publisher_data.iloc[0]
        st.markdown(f"""
        - **Publisher Terbaik:** {top_pub['Publisher']} ({top_pub['Country']}) dengan penjualan ${top_pub['Total Sales (Millions)']:,.2f}M
        - **Jumlah Game:** {int(top_pub['Game Count'])} game
        - **Total Penjualan Top 5 Publishers:** ${publisher_data.head(5)['Total Sales (Millions)'].sum():,.2f}M
        - **Rata-rata Penjualan per Publisher:** ${publisher_data['Total Sales (Millions)'].mean():,.2f}M
        - **Efisiensi Tertinggi:** {publisher_data.assign(efficiency=publisher_data['Total Sales (Millions)']/publisher_data['Game Count']).nlargest(1, 'efficiency')['Publisher'].values[0]}
        """)
    
    else:
        st.warning("Tidak ada data publisher yang ditemukan.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Video Game Sales Analysis Dashboard | Data sourced from PostgreSQL Database</p>
    <p>Built with Streamlit & Plotly | Last Updated: December 2025</p>
</div>
""", unsafe_allow_html=True)
