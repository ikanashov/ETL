FROM python:3.9-alpine as base

FROM base as builder

RUN mkdir /install
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --prefix=/install -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add libpq
COPY db/db.sqlite /sqlite_to_pg/db/
COPY db/get_imdb_data.sh /sqlite_to_pg/db/
COPY *.py /sqlite_to_pg/
WORKDIR /sqlite_to_pg