FROM python:3-alpine as base

FROM base as builder

RUN mkdir /install
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --prefix=/install -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add libpq
COPY db/db.sqlite /etl/db/
COPY db/get_imdb_data.sh /etl/db/
COPY *.py /etl/
WORKDIR /etl