-- Создаём отдельную схему для контента, чтобы ничего не перемешалось с сущностями Django
CREATE SCHEMA IF NOT EXISTS content;

-- Убраны актёры, жанры, режиссёры и сценаристы, так как они находятся с этой таблицей в отношении m2m 
-- Произведения с сериями подразумеваются сериалы, если это не сериал то в соответсвующих полях NULL
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    imdb_tconst TEXT NOT NULL,
    imdb_pconst TEXT, -- Для произведений с сериями (родительское произведение)
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    end_date DATE, -- Для произведений с сериями дата выхода последней серии 
    certificate TEXT, -- Возрастные ограничения
    file_path TEXT,
    rating FLOAT, -- Рейтинг imdb
    season_number INTEGER, -- Для произведений с сериями номер сезона 
    episode_number INTEGER, -- Для произведений с сериями номер серии 
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Информация о жанрах
CREATE TABLE IF NOT EXISTS content.film_genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    migrated_from TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    UNIQUE (name)
);

-- m2m-таблица для связывания кинопроизведений с жанрами
CREATE TABLE IF NOT EXISTS content.film_work_genre (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    migrated_from TEXT,
    created_at timestamp with time zone,
    FOREIGN KEY (film_work_id) REFERENCES content.film_work (id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES content.film_genre (id) ON DELETE CASCADE
);

-- Обязательно проверяется уникальность жанра и кинопроизведения, чтобы не появлялось дублей
CREATE UNIQUE INDEX film_work_genre_ind ON content.film_work_genre (film_work_id, genre_id);

-- Информация о типах
CREATE TABLE IF NOT EXISTS content.film_type (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    UNIQUE (name)
);

-- m2m-таблица для связывания кинопроизведений с типами
CREATE TABLE IF NOT EXISTS content.film_work_type (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    type_id uuid NOT NULL,
    created_at timestamp with time zone,
    FOREIGN KEY (film_work_id) REFERENCES content.film_work (id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES content.film_type (id) ON DELETE CASCADE
);

-- Обязательно проверяется уникальность типа и кинопроизведения, чтобы не появлялось дублей
CREATE UNIQUE INDEX film_work_type_ind ON content.film_work_type (film_work_id, type_id);

-- Обобщение для актёра, режиссёра и сценариста
CREATE TABLE IF NOT EXISTS content.film_person (
    id uuid PRIMARY KEY,
    imdb_nconst TEXT, 
    full_name TEXT NOT NULL,
    birth_date DATE,
    death_date DATE,
    migrated_from TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- m2m-таблица для связывания кинопроизведений с участниками
CREATE TABLE IF NOT EXISTS content.film_work_person (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    migrated_from TEXT,
    created_at timestamp with time zone,
    FOREIGN KEY (film_work_id) REFERENCES content.film_work (id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES content.film_person (id) ON DELETE CASCADE
);

-- Обязательно проверяется уникальность кинопроизведения, человека и роли человека, чтобы не появлялось дублей
-- Один человек может быть сразу в нескольких ролях (например, сценарист и режиссёр)
CREATE UNIQUE INDEX film_work_person_role_ind ON content.film_work_person (film_work_id, person_id, role);
