FROM python:3
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

ADD app /usr/src/app

 

COPY app/requirements.txt ./

COPY app/scrapyd.conf /etc/scrapyd/

RUN pip install --upgrade pip
RUN pip install --default-timeout=100 future
RUN pip install --no-cache-dir -r requirements.txt

 

VOLUME /etc/scrapyd/ /var/lib/scrapyd/


WORKDIR /usr/src/app

COPY app/entrypoint.sh /
EXPOSE 6800
# WORKDIR /usr/src/app/scrapy_app

# CMD ["scrapyd"]
ENTRYPOINT ["bash", "/entrypoint.sh" ]