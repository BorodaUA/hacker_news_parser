import scrapy


class IpTestSpider(scrapy.Spider):
    name = "ip_test"
    start_urls = ["http://atomurl.net/myip/"]

    def parse(self, response):
        ip_address = response.xpath("//*/table[2]/tr[1]/td/font/text()").get()
        user_agent = response.xpath("//*/table[2]/tr[3]/td/text()").get().split(": ")[1]
        result = {"ip_address": ip_address, "user_agent": user_agent}
        yield result
