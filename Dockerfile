FROM python:3.8.3-alpine
#
RUN mkdir /usr/src/hacker_news_parser
WORKDIR /usr/src/hacker_news_parser
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#
RUN apk update
RUN apk add  \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    libressl-dev \
    libffi-dev \
    zeromq-dev \
    libxml2-dev \
    libxslt-dev \
    g++ \
    unzip \
    git
#
COPY . /usr/src/hacker_news_parser
RUN pip install -r requirements.txt
#
EXPOSE 80
EXPOSE 6800
EXPOSE 6900
#
ENTRYPOINT ["sh", "run_server.sh"]