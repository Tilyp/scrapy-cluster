#! -*-coding:utf-8 -*-
from crawling.spiders.redis_spider import RedisSpider
from crawling.items import RawResponseItem, RenrenItem
from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.http import Request
import time
import redis

class TaoCheSpider(RedisSpider):
    name = "taocheSpider"
    root_url = "http://www.taoche.com"
    rconn = redis.Redis("10.4.255.129", 6379)

    def __init__(self, *args, **kwargs):
        super(TaoCheSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        self._logger.debug("crawled url {}".format(response.request.url))
        cur_depth = 0
        if 'curdepth' in response.meta:
            cur_depth = response.meta['curdepth']

        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = response.request.headers
        # item["body"] = response.body
        item["body"] = "asdfsdfsdfsdfsdfsdf"
        item["links"] = []
        hxs = Selector(response)
        cityList = hxs.xpath('//div[@class="header-city-province-text"]/a')
        for city in cityList:
            link = city.xpath('@href').extract()[0]
            cityName = city.xpath("text()").extract()[0]
            yield Request(url=link, meta={"city": cityName}, callback=self.parse_url, dont_filter=True)

    def parse_url(self, response):
        html =BeautifulSoup(response.body.decode("utf-8"), "lxml")
        car_list = html.find("div", class_="car_list")
        img_stop = car_list.find_all('div', class_="img_stop")
        cityname = response.meta["city"]
        for img in img_stop:
            detail_url = img.find("a")['href']
            lines = cityname + "--" + detail_url
            self.rconn.lpush("yiche:detailurl", lines)
        next_page = html.find("a", class_="pages-next")
        if next_page:
            next_url = next_page['href']
            if next_url == "javascript:;":
                pass
            else:
                yield Request(next_url, meta={"city": cityname}, callback=self.parse, dont_filter=True)
