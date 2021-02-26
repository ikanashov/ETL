import csv
import io
import uuid
from datetime import date, datetime, timezone

from etlclasses import MoviesGenre, MoviesPerson, MoviesToPostgres
from etlclasses import film_genre, film_person, film_type, film_work
from etlclasses import film_work_genre, film_work_person, film_work_type
from etlclasses import imdb_name_basics, imdb_to_postgres

from imdbmovies import IMDBMovies


class CsvMovies:
    filmgenres: dict = {}
    filmpersons: dict = {}
    filmtypes: dict = {}
    filmworks: dict = {}
    filmworkgenres: dict = {}
    filmworkpersons: dict = {}
    filmworktypes: dict = {}

    def get_or_add_film_genre(self, genre: MoviesGenre) -> film_genre:
        try:
            filmgenre = self.filmgenres[genre.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmgenre = (str(uuid.uuid4()), genre.name, genre.name, f'from id = {genre.migrated_from}', now, now)
            self.filmgenres[genre.name] = filmgenre
        finally:
            return film_genre(*filmgenre)

    def get_or_add_film_person(self, person: MoviesPerson, imdb_person: imdb_name_basics) -> film_person:
        try:
            filmperson = self.filmpersons[person.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            id = str(uuid.uuid4())
            try:
                nconst = imdb_person.nconst
            except AttributeError:
                nconst = None
            try:
                birth_date = date(int(imdb_person.birthyear), 1, 1)
            except (ValueError, TypeError, AttributeError):
                birth_date = None
            try:
                death_date = date(int(imdb_person.deathyear), 1, 1)
            except (ValueError, TypeError, AttributeError):
                death_date = None
            filmperson = (
                id,
                nconst,
                person.name,
                birth_date, death_date,
                f'imported from old_id = {person.migrated_from}',
                now,
                now
            )
            self.filmpersons[person.name] = filmperson
        finally:
            return film_person(*filmperson)

    def get_or_add_film_type(self, imdb_data: imdb_to_postgres) -> film_type:
        try:
            filmtype = self.filmtypes[imdb_data.titletype]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmtype = (str(uuid.uuid4()), imdb_data.titletype, imdb_data.titletype, now, now)
            self.filmtypes[imdb_data.titletype] = filmtype
        finally:
            return film_type(*filmtype)

    def add_film_work(self, movie: MoviesToPostgres, imdb_data: imdb_to_postgres) -> film_work:
        now = datetime.now(timezone.utc)
        filmuuid = str(uuid.uuid4())
        try:
            creation_date = date(int(imdb_data.startyear), 1, 1)
        except (ValueError, TypeError):
            creation_date = None
        try:
            end_date = date(int(imdb_data.endyear), 1, 1)
        except (ValueError, TypeError):
            end_date = None
        certificate = ''
        if imdb_data.isadult:
            certificate = 'Adult'
        filmwork = (
            filmuuid, imdb_data.tconst, imdb_data.pconst,
            movie.title, movie.plot,
            creation_date, end_date, certificate, '', movie.imdb_rating,
            imdb_data.season_number, imdb_data.episode_number,
            now, now)
        self.filmworks[filmuuid] = filmwork
        return film_work(*filmwork)

    def add_genre_film_work(self, genre: film_work_genre) -> film_work_genre:
        gfwuuid = str(uuid.uuid4())
        genrefilmwork = (
            gfwuuid,
            genre.film_work_id, genre.genre_id,
            genre.migrated_from, datetime.now(timezone.utc)
        )
        self.filmworkgenres[gfwuuid] = genrefilmwork
        return film_work_genre(*genrefilmwork)

    def add_person_film_work(
            self, role: str, film_work_id: str, person_id: str, migrated_from: str) -> film_work_person:
        pfwuuid = str(uuid.uuid4())
        personfilmwork = (
            pfwuuid,
            film_work_id, person_id, role,
            migrated_from, datetime.now(timezone.utc)
        )
        self.filmworkpersons[pfwuuid] = personfilmwork
        return film_work_person(*personfilmwork)

    def add_type_film_work(self, film_work_id: str, type_id: str) -> film_work_type:
        tfwuuid = str(uuid.uuid4())
        typefilmwork = (
            tfwuuid,
            film_work_id,
            type_id,
            datetime.now(timezone.utc)
        )
        self.filmworktypes[tfwuuid] = typefilmwork
        return film_work_type(*typefilmwork)

    def add_or_get_film_work(self, movie: MoviesToPostgres) -> film_work:
        imdb_data = IMDBMovies().get_imdb_movie_by_id(movie.id)
        new_film_work = self.add_film_work(movie, imdb_data)
        film_type = self.get_or_add_film_type(imdb_data)
        self.add_type_film_work(new_film_work.id, film_type.id)
        for genre in movie.genres:
            filmgenre = self.get_or_add_film_genre(genre)
            self.add_genre_film_work(film_work_genre(None, new_film_work.id, filmgenre.id, movie.id, None))
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
