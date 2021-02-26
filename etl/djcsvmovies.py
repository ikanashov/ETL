import csv
import io
import uuid
from datetime import date, datetime, timezone

from etlclasses import DJFilmGenre, DJFilmPerson, DJFilmType, DJFilmWork
from etlclasses import DJFilmWorkGenre, DJFilmWorkPerson
from etlclasses import MoviesGenre, MoviesPerson, MoviesToPostgres
from etlclasses import imdb_name_basics, imdb_to_postgres

from imdbmovies import IMDBMovies


class DJCsvMovies:
    filmgenres: dict = {}
    filmpersons: dict = {}
    filmtypes: dict = {}
    filmworks: dict = {}
    filmworkgenres: dict = {}
    filmworkpersons: dict = {}

    def get_or_add_film_genre(self, genre: MoviesGenre) -> DJFilmGenre:
        try:
            filmgenre = self.filmgenres[genre.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmgenre = (now, now, str(uuid.uuid4()), genre.name, genre.name, f'from id = {genre.migrated_from}')
            self.filmgenres[genre.name] = filmgenre
        finally:
            return DJFilmGenre(*filmgenre)

    def get_or_add_film_person(self, person: MoviesPerson, imdb_person: imdb_name_basics) -> DJFilmPerson:
        try:
            filmperson = self.filmpersons[person.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            id = str(uuid.uuid4())
            try:
                nconst = imdb_person.nconst
            except AttributeError:
                nconst = '\\N'
            try:
                birth_date = date(int(imdb_person.birthyear), 1, 1)
            except (ValueError, TypeError, AttributeError):
                birth_date = '\\N'
            try:
                death_date = date(int(imdb_person.deathyear), 1, 1)
            except (ValueError, TypeError, AttributeError):
                death_date = '\\N'
            filmperson = (
                now,
                now,
                id,
                person.name,
                nconst,
                birth_date, death_date,
                f'imported from old_id = {person.migrated_from}'
            )
            self.filmpersons[person.name] = filmperson
        finally:
            return DJFilmPerson(*filmperson)

    def get_or_add_film_type(self, imdb_data: imdb_to_postgres) -> DJFilmType:
        try:
            filmtype = self.filmtypes[imdb_data.titletype]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmtype = (now, now, str(uuid.uuid4()), imdb_data.titletype, imdb_data.titletype)
            self.filmtypes[imdb_data.titletype] = filmtype
        finally:
            return DJFilmType(*filmtype)

    def add_film_work(self, movie: MoviesToPostgres, imdb_data: imdb_to_postgres) -> DJFilmWork:
        now = datetime.now(timezone.utc)
        filmuuid = str(uuid.uuid4())
        film_type = self.get_or_add_film_type(imdb_data)
        type_id = film_type.id
        creation_date = date(int(imdb_data.startyear), 1, 1)
        try:
            end_date = date(int(imdb_data.endyear), 1, 1)
        except (ValueError, TypeError):
            end_date = '\\N'
        certificate = ''
        if imdb_data.isadult:
            certificate = 'Adult'
        if imdb_data.season_number:
            season_number = imdb_data.season_number
        else:
            season_number = '\\N'
        if imdb_data.episode_number:
            episode_number = imdb_data.episode_number
        else:
            episode_number = '\\N'
        filmwork = (
            now, now, filmuuid, imdb_data.tconst, imdb_data.pconst,
            movie.title, movie.plot,
            creation_date, end_date, certificate, '', movie.imdb_rating,
            season_number, episode_number, type_id
        )
        self.filmworks[filmuuid] = filmwork
        return DJFilmWork(*filmwork)

    def add_genre_film_work(self, migrated_from: str, film_work_id: str, genre_id: str) -> DJFilmWorkGenre:
        gfwuuid = str(uuid.uuid4())
        genrefilmwork = (
            gfwuuid, migrated_from, datetime.now(timezone.utc),
            film_work_id, genre_id
        )
        self.filmworkgenres[gfwuuid] = genrefilmwork
        return DJFilmWorkGenre(*genrefilmwork)

    def add_person_film_work(
            self, role: str, film_work_id: str, person_id: str, migrated_from: str) -> DJFilmWorkPerson:
        pfwuuid = str(uuid.uuid4())
        personfilmwork = (
            pfwuuid, migrated_from, datetime.now(timezone.utc),
            role, film_work_id, person_id
        )
        self.filmworkpersons[pfwuuid] = personfilmwork
        return DJFilmWorkPerson(*personfilmwork)

    def add_or_get_film_work(self, movie: MoviesToPostgres) -> DJFilmWork:
        imdb_data = IMDBMovies().get_imdb_movie_by_id(movie.id)
        new_film_work = self.add_film_work(movie, imdb_data)
        for genre in movie.genres:
            filmgenre = self.get_or_add_film_genre(genre)
            self.add_genre_film_work(movie.id, new_film_work.id, filmgenre.id)
        for person in movie.persons:
            imdb_person = IMDBMovies().get_imdb_person_by_name(person.name, person.role, movie.id)
            filmperson = self.get_or_add_film_person(person, imdb_person)
            self.add_person_film_work(person.role, new_film_work.id, filmperson.id, movie.id)
        return new_film_work

    def generate_csv(self, tabledict: dict) -> io.StringIO:
        csvtable = io.StringIO()
        tablewriter = csv.writer(csvtable, delimiter='|',)
        for key in tabledict:
            tablewriter.writerow(tabledict[key])
        csvtable.seek(0)
        return csvtable
