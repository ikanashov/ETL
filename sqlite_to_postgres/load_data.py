import time

from csvmovies import CsvMovies

from postgresmovies import NewMovies

from sqlitemovies import SQLiteMoviesDB


def load_from_sqlite():
    sqlite_movies = SQLiteMoviesDB().get_all_movies()
    csv_movies = CsvMovies()
    postgres_movies = NewMovies()

    [csv_movies.add_or_get_film_work(movie) for movie in sqlite_movies]

    filmgenres = csv_movies.generate_csv(csv_movies.filmgenres)
    filmpersons = csv_movies.generate_csv(csv_movies.filmpersons)
    filmtypes = csv_movies.generate_csv(csv_movies.filmtypes)
    filmworks = csv_movies.generate_csv(csv_movies.filmworks)
    filmworkgenres = csv_movies.generate_csv(csv_movies.filmworkgenres)
    filmworktypes = csv_movies.generate_csv(csv_movies.filmworktypes)
    filmworkpersons = csv_movies.generate_csv(csv_movies.filmworkpersons)

    postgres_movies.drop_film_genre_index()
    postgres_movies.drop_film_type_index()
    postgres_movies.drop_film_person_index()

    postgres_movies.copy_to_table_from_csv('film_genre', filmgenres)
    postgres_movies.copy_to_table_from_csv('film_person', filmpersons)
    postgres_movies.copy_to_table_from_csv('film_type', filmtypes)
    postgres_movies.copy_to_table_from_csv('film_work', filmworks)
    postgres_movies.copy_to_table_from_csv('film_work_genre', filmworkgenres)
    postgres_movies.copy_to_table_from_csv('film_work_type', filmworktypes)
    postgres_movies.copy_to_table_from_csv('film_work_person', filmworkpersons)

    postgres_movies.create_film_genre_index()
    postgres_movies.create_film_type_index()
    postgres_movies.create_film_person_index()


if __name__ == '__main__':
    start = time.time()
    load_from_sqlite()
    end = time.time()
    print('Read tsv imdb files and write to postgres: ', (end-start), 'sec')
