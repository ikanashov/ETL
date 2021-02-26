-- Создаем схему для загрузки данных из imdb 
CREATE SCHEMA IF NOT EXISTS imdb;

-- Contains the following information for names
CREATE TABLE IF NOT EXISTS imdb.name_basics (
    nconst TEXT PRIMARY KEY,
    primaryName TEXT NOT NULL,
    birthYear TEXT,
    deathYear TEXT,
    primaryProfession TEXT,
    knownForTitles TEXT
);

-- Contains the following information for titles
CREATE TABLE IF NOT EXISTS imdb.title_basics (
    tconst TEXT PRIMARY KEY,
    titleType TEXT NOT NULL,
    primaryTitle TEXT NOT NULL,
    originalTitle TEXT NOT NULL,
    isAdult BOOLEAN,
    startYear TEXT,
    endYear TEXT,
    runtimeMinutes INTEGER,
    genres TEXT
);

-- Contains the tv episode information
CREATE TABLE IF NOT EXISTS imdb.title_episode (
    tconst TEXT PRIMARY KEY,
    parentTconst TEXT NOT NULL,
    seasonNumber INTEGER,
    episodeNumber INTEGER
);

-- Создаем индекс для поиска произведений и актеров по имени
CREATE INDEX imdb_name_basics_name ON imdb.name_basics (primaryName);
CREATE INDEX imdb_title_basics_title ON imdb.title_basics (primaryTitle);