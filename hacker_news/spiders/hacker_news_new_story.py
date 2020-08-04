import json
import os
import scrapy
import logging
from scrapy.exceptions import CloseSpider
from scrapy import Request, signals
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
from sqlalchemy.exc import InternalError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from hacker_news.models import hn_db

load_dotenv()


class HackerNewsNewStorySpider(scrapy.Spider):
    name = "hacker_news_new_story"

    def __init__(self, **kwargs):
        #
        self.hn_db_url = os.environ.get("HACKER_NEWS_DATABASE_URI")
        self.postges_db_url = os.environ.get("POSTGRES_DATABASE_URI")
        #
        if not database_exists(self.hn_db_url):
            self.db_name = os.environ.get("HACKER_NEWS_DATABASE_NAME")
            self.engine = create_engine(self.postges_db_url)
            with self.engine.connect() as conn:
                conn.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                conn.execute(
                    f"CREATE DATABASE {self.db_name} ENCODING 'utf8' TEMPLATE template1"
                )
        #
        hn_engine = create_engine(self.hn_db_url)
        hn_db.Base.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=hn_engine,)
        )
        hn_db.Base.query = hn_db.Base.session.query_property()
        hn_db.Base.metadata.create_all(hn_engine)
        #
        self.list_of_items = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        sorted_list_of_items = sorted(
            self.list_of_items, key=lambda k: k["item_order"], reverse=True
        )
        for i in sorted_list_of_items:
            #
            i["parsed_time"] = datetime.strftime(
                datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
            #
            i["origin"] = "hacker_news"
            #
            found_item = hn_db.HackerNewsNewStory.query.filter(
                hn_db.HackerNewsNewStory.id == i["id"]
            ).first()
            #
            if found_item:
                hn_db.HackerNewsNewStory.query.filter(
                    hn_db.HackerNewsNewStory.id == i["id"]
                ).update(
                    {
                        "parsed_time": datetime.strftime(
                            datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
                        )[:-3],
                        # "hn_url": i["hn_url"],
                        "id": i["id"],
                        "deleted": i["deleted"],
                        "type": i["type"],
                        "by": i["by"],
                        "time": i["time"],
                        "text": i["text"],
                        "dead": i["dead"],
                        "parent": i["parent"],
                        "poll": i["poll"],
                        "kids": i["kids"],
                        "url": i["url"],
                        "score": i["score"],
                        "title": i["title"],
                        "parts": i["parts"],
                        "descendants": i["descendants"],
                    }
                )
            else:
                i.pop("item_order")
                data = hn_db.HackerNewsNewStory(**i)
                hn_db.Base.session.add(data)
        #
        hn_db.Base.session.commit()
        hn_db.Base.session.close()

    def start_requests(self):
        yield Request(
            url="https://hacker-news.firebaseio.com/v0/newstories.json",
            callback=self.parse,
            dont_filter=True,
        )

    def parse(self, response):
        self.resp = json.loads(response.text)
        for item in enumerate(self.resp):
            url = f"https://hacker-news.firebaseio.com/v0/item/{item[1]}.json"
            yield Request(
                url=url,
                callback=self.item_parse,
                dont_filter=True,
                meta={"item_order": item[0], "value": item[1]},
            )

    def item_parse(self, response):
        scrape_item = json.loads(response.text)
        if scrape_item:
            result_dict = {}
            item_order = response.meta.get("item_order")
            #
            result_dict["item_order"] = item_order
            #
            # result_dict["parse_dt"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            #
            # result_dict["hn_url"] = "https://news.ycombinator.com/item?id=" + str(
            #     scrape_item.get("id", None)
            # )
            #
            result_dict["id"] = scrape_item.get("id")
            result_dict["deleted"] = scrape_item.get("deleted")
            result_dict["type"] = scrape_item.get("type")
            result_dict["by"] = scrape_item.get("by")
            result_dict["time"] = scrape_item.get("time")
            result_dict["text"] = scrape_item.get("text")
            result_dict["dead"] = scrape_item.get("dead")
            result_dict["parent"] = scrape_item.get("parent")
            result_dict["poll"] = scrape_item.get("poll")
            result_dict["kids"] = scrape_item.get("kids")
            result_dict["url"] = scrape_item.get("url")
            result_dict["score"] = scrape_item.get("score")
            result_dict["title"] = scrape_item.get("title")
            result_dict["parts"] = scrape_item.get("parts")
            result_dict["descendants"] = scrape_item.get("descendants")
            #
            self.list_of_items.append(result_dict)
        else:
            logging.debug("No items to parse, skipping.")
