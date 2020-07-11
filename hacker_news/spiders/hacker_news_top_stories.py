import scrapy


class HackerNewsTopStoriesSpider(scrapy.Spider):
    name = 'hacker_news_top_stories'
    start_urls = ['http://atomurl.net/myip/']

    def parse(self, response):
        print(response.text)
