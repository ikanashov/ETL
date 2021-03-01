import time

from imdbmovies import IMDBMovies


if __name__ == '__main__':
    start = time.time()
    print('loading data from imdb...')
    imdb = IMDBMovies()
    imdb.load_data_from_tsv()
    end = time.time()
    print('load data from tsv imdb files and write to postgres: ', (end-start), 'sec')
