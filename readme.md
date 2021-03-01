# hacker_news_parser
A parser for https://news.ycombinator.com/ , that stores data in the [postgres_server](https://github.com/BorodaUA/postgres_server), and part of the [webportal](https://github.com/BorodaUA/webportal) project.

## How to use:
### Local development mode:
1. Clone the repo
2. Create .env file inside the repo with following data:
    - HACKER_NEWS_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres database
3. To access local Scrapydweb web iterface use [this](http://localhost:6900/) address 