FROM germey/scrapyd:latest

RUN mkdir /db

ADD . /usr/src/app

RUN mv /usr/src/app/db.sqlite3 /db


WORKDIR /usr/src/app/scrapy_app

EXPOSE 6800

CMD ["scrapyd"]