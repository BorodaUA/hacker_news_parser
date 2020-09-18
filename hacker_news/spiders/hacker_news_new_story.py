import json
import os
import sys
import glob
import scrapy
import logging
from scrapy import Request, signals
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

load_dotenv()


class HackerNewsNewStorySpider(scrapy.Spider):
    name = "hacker_news_new_story"

    def __init__(self, **kwargs):
        self.list_of_items = []
        pid = str(os.getpid())
        try:
            self.process_name = glob.glob(
                f"/usr/src/hacker_news_parser/{self.name}*"
            )[0]
            process_time = os.stat(self.process_name)[-1]
            process_time = datetime.fromtimestamp(process_time)
            process_time = datetime.strftime(
                process_time, "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
            if datetime.now() - datetime.fromisoformat(process_time) >= timedelta(minutes=5):
                logging.debug('file created more then 5 min ago')
                os.unlink(self.process_name)
                self.process_name = None
            self.marker = True
        except IndexError:
            logging.debug('No process of this spider')
            self.process_name = None
        if not self.process_name:
            with open(f'{self.name}-{pid}.txt', 'w+') as f:
                f.close()
                self.marker = False
    

    def db_connect(self):
        self.hn_db_url = os.environ.get("HACKER_NEWS_DATABASE_URI")
        self.Base = automap_base()
        self.engine = create_engine(self.hn_db_url)
        self.Base.prepare(self.engine, reflect=True)
        self.HackerNewsNewStory = self.Base.classes.hacker_news_new_story
        self.Base.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine,)
        )
        self.HackerNewsNewStory.query = self.Base.session.query_property()
        self.session = self.Base.session
        return {
            'HackerNewsNewStory': self.HackerNewsNewStory, 
            'session': self.session 
            }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        try:
            db_info = self.db_connect()
            self.HackerNewsNewStory = db_info['HackerNewsNewStory']
            self.session = db_info['session']

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
                found_item = self.HackerNewsNewStory.query.filter(
                    self.HackerNewsNewStory.hn_id == i["hn_id"]
                ).first()
                #
                if found_item:
                    self.HackerNewsNewStory.query.filter(
                        self.HackerNewsNewStory.hn_id == i["hn_id"]
                    ).update(
                        {
                            "parsed_time": datetime.strftime(
                                datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
                            )[:-3],
                            # "hn_url": i["hn_url"],
                            "hn_id": i["hn_id"],
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
                    data = self.HackerNewsNewStory(**i)
                    self.session.add(data)
            #
            self.session.commit()
            self.session.close()
        except OperationalError:
            logging.debug('No database found.')
        except AttributeError:
            logging.debug('No tables found.')
        try:
            self.process_name = glob.glob(
                f"/usr/src/hacker_news_parser/{self.name}*"
            )[0]
            os.unlink(self.process_name)
            logging.debug('Succesful spider run, closing spider.')
        except IndexError:
            logging.debug('No file found to delete.')

    def start_requests(self):
        if self.marker == True:
            logging.debug('Runtime file found, closing spider.')
        else:
            try:
                db_info = self.db_connect()
                self.HackerNewsNewStory = db_info['HackerNewsNewStory']
                yield Request(
                    url="https://hacker-news.firebaseio.com/v0/newstories.json",
                    callback=self.parse,
                    dont_filter=True,
                )
            except OperationalError:
                logging.debug('No database found.')
            except AttributeError:
                logging.debug('No tables found.')

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
            result_dict["hn_id"] = scrape_item.get("id")
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
