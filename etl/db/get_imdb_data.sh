#!/bin/sh

# Скачиваем необходимые файлы IMDb data set
wget -c -t 5 https://datasets.imdbws.com/name.basics.tsv.gz

wget -c -t 5 https://datasets.imdbws.com/title.basics.tsv.gz

wget -c -t 5 https://datasets.imdbws.com/title.episode.tsv.gz

gzip -df name.basics.tsv.gz

gzip -df title.basics.tsv.gz

gzip -df title.episode.tsv.gz
