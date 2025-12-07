-- ============================================================================
-- Database Schema for Video Game Sales Analysis (PostgreSQL Version) - REVISED
-- ============================================================================
-- Author: Gemini/Kelompok 7
-- Date: 2025-12-06
-- Description: Normalized database schema resolving M:N relationships and sales structure.
-- ============================================================================

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS Regional_Sales CASCADE;
DROP TABLE IF EXISTS Regions CASCADE; -- Tabel baru
DROP TABLE IF EXISTS Game_Releases CASCADE; -- Tabel baru
DROP TABLE IF EXISTS Game_Genres CASCADE; -- Tabel baru
DROP TABLE IF EXISTS Games CASCADE;
DROP TABLE IF EXISTS Publishers CASCADE;
DROP TABLE IF EXISTS Platforms CASCADE;
DROP TABLE IF EXISTS Genres CASCADE;

-- ============================================================================
-- 1. GENRES TABLE
-- ============================================================================
CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE Genres IS 'Stores unique game genres (Action, RPG, Strategy, etc.)';

-- ============================================================================
-- 2. PLATFORMS TABLE
-- ============================================================================
CREATE TABLE Platforms (
    platform_id SERIAL PRIMARY KEY,
    platform_code VARCHAR(10) NOT NULL UNIQUE,
    platform_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50),
    release_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE Platforms IS 'Stores gaming platforms and consoles';

-- ============================================================================
-- 3. PUBLISHERS TABLE
-- ============================================================================
CREATE TABLE Publishers (
    publisher_id SERIAL PRIMARY KEY,
    publisher_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50),
    founded_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE Publishers IS 'Stores game publishing companies';

-- ============================================================================
-- 4. GAMES TABLE (JUDUL UNIK)
-- ============================================================================
-- Stores individual game information (one entry per unique title, regardless of platform)
CREATE TABLE Games (
    game_id SERIAL PRIMARY KEY,
    game_name VARCHAR(255) NOT NULL UNIQUE, -- Game name is now UNIQUE
    publisher_id INT NOT NULL,
    -- Removed: platform_id, genre_id
    
    CONSTRAINT fk_games_publisher 
        FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
COMMENT ON TABLE Games IS 'Main table storing unique video game titles.';

-- ============================================================================
-- 5. GAME_GENRES TABLE (JUNCTION TABLE M:N)
-- ============================================================================
-- Resolves the Many-to-Many relationship between Games and Genres
CREATE TABLE Game_Genres (
    game_id INT NOT NULL,
    genre_id INT NOT NULL,
    
    PRIMARY KEY (game_id, genre_id),
    
    CONSTRAINT fk_gg_game
        FOREIGN KEY (game_id) REFERENCES Games(game_id)
        ON DELETE CASCADE -- If a game is deleted, delete its genre links
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_gg_genre
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
        ON DELETE RESTRICT -- Do not delete a genre if games are still linked to it
        ON UPDATE CASCADE
);
COMMENT ON TABLE Game_Genres IS 'Links games to one or more genres.';

-- ============================================================================
-- 6. GAME_RELEASES TABLE (JUNCTION TABLE M:N)
-- ============================================================================
-- Resolves the Many-to-Many relationship between Games and Platforms, 
-- and stores release-specific information (like release year on that platform)
CREATE TABLE Game_Releases (
    game_release_id SERIAL PRIMARY KEY,
    game_id INT NOT NULL,
    platform_id INT NOT NULL,
    release_year INT, -- The specific year this game was released on this platform
    
    UNIQUE (game_id, platform_id), -- A game can only be released once per platform in the data
    
    CONSTRAINT fk_gr_game
        FOREIGN KEY (game_id) REFERENCES Games(game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_gr_platform
        FOREIGN KEY (platform_id) REFERENCES Platforms(platform_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
COMMENT ON TABLE Game_Releases IS 'Links games to platforms and stores platform-specific release data.';

-- ============================================================================
-- 7. REGIONS TABLE (NORMALISASI WILAYAH)
-- ============================================================================
-- Stores regional codes for sales analysis (e.g., NA, EU, ASIA)
CREATE TABLE Regions (
    region_id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL UNIQUE, -- e.g., 'NA', 'EU', 'GLOBAL'
    region_name VARCHAR(50) NOT NULL UNIQUE
);
COMMENT ON TABLE Regions IS 'Stores regional codes for sales data normalisation.';

-- ============================================================================
-- 8. REGIONAL_SALES TABLE (MODEL BARIS-PER-WILAYAH)
-- ============================================================================
-- Stores sales data for each game/platform/region combination
CREATE TABLE Regional_Sales (
    sale_id SERIAL PRIMARY KEY,
    -- Kunci Asing merujuk ke Game_Releases (yang mencakup Game dan Platform)
    game_release_id INT NOT NULL,
    region_id INT NOT NULL, 
    sales_in_millions NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (game_release_id, region_id), -- Penjualan unik per rilis per wilayah
    
    CONSTRAINT fk_rs_release
        FOREIGN KEY (game_release_id) REFERENCES Game_Releases(game_release_id)
        ON DELETE CASCADE -- Jika rilis game dihapus, hapus data penjualannya
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_rs_region
        FOREIGN KEY (region_id) REFERENCES Regions(region_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
        
    CONSTRAINT chk_sales_positive 
        CHECK (sales_in_millions >= 0)
);
COMMENT ON TABLE Regional_Sales IS 'Stores regional sales data (millions) per game release.';

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_game_name ON Games(game_name);
CREATE INDEX idx_gr_game_platform ON Game_Releases(game_id, platform_id);
CREATE INDEX idx_rs_sales_region ON Regional_Sales(region_id, sales_in_millions DESC);
CREATE INDEX idx_rs_sales_game_release ON Regional_Sales(game_release_id);