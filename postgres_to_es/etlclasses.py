import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ESPerson:
    id: str
    name: str


@dataclass
class ESMovie:
    id: str
    imdb_rating: float
    imdb_tconst: str
    filmtype: str
    genre: list
    title: str
    description: str
    directors_names: list
    actors_names: list
    writers_names: list
    directors: List[ESPerson]
    actors: List[ESPerson]
    writers: List[ESPerson]


@dataclass
class ETLFilmWork:
    id: uuid.UUID
    rating: float
    imdb_tconst: str
    type_name: str
    genres: list
    title: str
    description: str
    directors: list
    actors: list
    writers: list
    modified: datetime


@dataclass
class ETLModifiedID:
    id: uuid.UUID
    modified: datetime


@dataclass
class ETLProducerTable:
    table: str = ''
    field: str = ''
    ptable: str = ''
    pfield: str = ''
    isrelation: bool = True


@dataclass
class ETLEnricherData:
    table: ETLProducerTable
    idlist: list
