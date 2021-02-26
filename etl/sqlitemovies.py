import json
import sqlite3
from typing import List

from etlclasses import Movies, MoviesGenre, MoviesPerson, MoviesToPostgres


class SQLiteMoviesDB:
    SQLITEBASE = 'db/db.sqlite'
    SQLGETALLMOVIES = 'SELECT * FROM movies'
    SQLGETONEMOVIE = 'SELECT * FROM movies where id = ?'
    SQLGETACTORSBYMOVIESID = ('SELECT "actor", actors.name, movie_actors.actor_id '
                              'FROM movie_actors '
                              'JOIN actors ON actors.id = movie_actors.actor_id '
                              'WHERE actors.name != "N/A" and movie_id = ?')
    SQLGETWRITERBYID = 'SELECT name FROM writers WHERE id = ?'

    def __init__(self):
        self.moviedbconn = sqlite3.connect(self.SQLITEBASE)

    def get_all_movies(self) -> MoviesToPostgres:
        cursor = self.moviedbconn.cursor()
        try:
            cursor.execute(self.SQLGETALLMOVIES)
            row = cursor.fetchone()
            while row:
                movie = Movies(*row)
                yield MoviesToPostgres(
                    movie.id,
                    self.get_genres_by_movie(movie),
                    self.get_persons_by_movie(movie),
                    movie.title,
                    movie.plot,
                    self.rating_to_float(movie.imdb_rating),
                    )
                row = cursor.fetchone()
        finally:
            cursor.close

    def get_one_movie(self, movie_id: str) -> MoviesToPostgres:
        cursor = self.moviedbconn.cursor()
        try:
            cursor.execute(self.SQLGETONEMOVIE, (movie_id,))
            row = cursor.fetchone()
        finally:
            cursor.close
        movie = Movies(*row)
        return MoviesToPostgres(
            movie.id,
            self.get_genres_by_movie(movie),
            self.get_persons_by_movie(movie),
            movie.title,
            movie.plot,
            self.rating_to_float(movie.imdb_rating),
            )

    def get_actors_by_movie(self, movie: Movies) -> List[MoviesPerson]:
        cursor = self.moviedbconn.cursor()
        try:
            cursor.execute(self.SQLGETACTORSBYMOVIESID, (movie.id,))
            actors = []
            actor = cursor.fetchone()
            while actor:
                actors.append(actor)
                actor = cursor.fetchone()
        finally:
            cursor.close()
        actors = list(set(actors))
        actors = [MoviesPerson(*actor) for actor in actors]
        return actors

    def get_writers_by_movie(self, movie: Movies) -> List[MoviesPerson]:
        if (movie.writer != ''):
            writers = [('writer', self.get_writer_by_id(movie.writer), movie.writer)]
        else:
            writers = [
                ('writer', self.get_writer_by_id(writer['id']), writer['id'])
                for writer in json.loads(movie.writers)
                ]
        writers = list(set(writers))
        writers = [MoviesPerson(*writer) for writer in writers]
        return writers

    def get_directors_by_movie(self, movie: Movies) -> List[MoviesPerson]:
        directors = [
            ('director', director.replace('(co-director)', ''), movie.id)
            for director in movie.director.split(', ')
           ]
        directors = list(set(directors))
        directors = [MoviesPerson(*director) for director in directors]
        return directors

    def get_writer_by_id(self, writer_id: str) -> str:
        cursor = self.moviedbconn.cursor()
        try:
            cursor.execute(self.SQLGETWRITERBYID, (writer_id,))
            writer = cursor.fetchone()[0]
        finally:
            cursor.close()
        return writer

    def get_persons_by_movie(self, movie: Movies):
        persons = []
        persons.extend(self.get_directors_by_movie(movie))
        persons.extend(self.get_writers_by_movie(movie))
        persons.extend(self.get_actors_by_movie(movie))
        persons = [person for person in persons if person.name != 'N/A']
        return persons

    def get_genres_by_movie(self, movie: Movies) -> List[MoviesGenre]:
        genres = [MoviesGenre(genre, movie.id) for genre in movie.genre.split(', ')]
        return genres

    def rating_to_float(self, imdb_rating: str) -> float:
        try:
            return float(imdb_rating)
        except ValueError:
            return 0.0
