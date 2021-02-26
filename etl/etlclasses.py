import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class MoviesGenre:
    name: str
    migrated_from: str


@dataclass
class MoviesPerson:
    role: str
    name: str
    migrated_from: str


@dataclass
class Movies:
    id: str
    genre: str
    director: str
    writer: str
    title: str
    plot: str
    ratings: str
    imdb_rating: str
    writers: str


@dataclass
class MoviesToPostgres:
    id: str
    genres: List[MoviesGenre]
    persons: List[MoviesPerson]
    title: str
    plot: str
    imdb_rating: float


@dataclass
class film_genre:
    id: uuid.UUID
    name: str
    description: str
    migrated_from: str
    created_at: datetime
    updated_at: datetime


@dataclass
class DJFilmGenre:
    created: datetime
    modified: datetime
    id: uuid.UUID
    name: str
    description: str
    migrated_from: str


@dataclass
class film_person:
    id: uuid.UUID
    imdb_nconst: str
    full_name: str
    birth_date: datetime.date
    death_date: datetime.date
    migrated_from: str
    created_at: datetime
    updated_at: datetime


@dataclass
class DJFilmPerson:
    created: datetime
    modified: datetime
    id: uuid.UUID
    full_name: str
    imdb_nconst: str
    birth_date: datetime.date
    death_date: datetime.date
    migrated_from: str


@dataclass
class film_type:
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class DJFilmType:
    created: datetime
    modified: datetime
    id: uuid.UUID
    name: str
    description: str


@dataclass
class film_work:
    id: uuid.UUID
    imdb_tconst: str
    imdb_pconst: str
    title: str
    description: str
    creation_date: datetime.date
    end_date: datetime.date
    certificate: str
    file_path: str
    rating: float
    season_number: int
    episode_number: int
    created_at: datetime
    updated_at: datetime


@dataclass
class DJFilmWork:
    created: datetime
    modified: datetime
    id: uuid.UUID
    imdb_tconst: str
    imdb_pconst: str
    title: str
    description: str
    creation_date: datetime.date
    end_date: datetime.date
    certificate: str
    file_path: str
    rating: float
    season_number: int
    episode_number: int
    type_id: uuid.UUID


@dataclass
class film_work_genre:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    migrated_from: str
    created_at: datetime


@dataclass
class DJFilmWorkGenre:
    id: uuid.UUID
    migrated_from: str
    created: datetime
    film_work_id: uuid.UUID
    genre_id: uuid.UUID


@dataclass
class film_work_person:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    migrated_from: str
    created_at: datetime


@dataclass
class DJFilmWorkPerson:
    id: uuid.UUID
    migrated_from: str
    created: datetime
    role: str
    film_work_id: uuid.UUID
    person_id: uuid.UUID


@dataclass
class film_work_type:
    id: uuid.UUID
    film_work_id: uuid.UUID
    type_id: uuid.UUID
    created_at: datetime


@dataclass
class imdb_name_basics:
    nconst: str
    primaryname: str
    birthyear: datetime.date
    deathyear: datetime.date
    primaryprofession: str
    knownfortitles: str


@dataclass
class imdb_title_basics:
    tconst: str
    titletype: str
    primarytitle: str
    originaltitle: str
    isadult: bool
    startyear: str
    endyear: str
    runtimeminutes: int
    genres: str


@dataclass
class imdb_title_episode:
    tconst: str
    parenttconst: str
    season_number: int
    episode_number: int


@dataclass
class imdb_to_postgres:
    tconst: str
    pconst: str
    titletype: str
    primarytitle: str
    isadult: bool
    startyear: str
    endyear: str
    season_number: int
    episode_number: int
