FROM python:3.8.3-alpine
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add  \
        libressl-dev \
        musl-dev \
        libffi-dev \
        zeromq-dev \
        libxml2-dev \
        libxslt-dev
COPY . /usr/src/app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python", "keep_on.py"]