#! -*- coding:utf-8 -*-
from crawling.spiders.redis_spider import RedisSpider
from scrapy import Request


class TitleSpider(RedisSpider):
    name = "title"

    def __init__(self, *args, **kwargs):
        super(TitleSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        fd = open("crawling\spiders\url_1w.txt", "r")
        lines = fd.readlines()
        data = {"appid": "testapp", "crawlid": "andy", "spiderid": "title"}
        for line in lines:
           yield Request(line, callback=self.parse, meta=data, dont_filter=True)

    def parse(self, response):
        print response.title
        print response.url

