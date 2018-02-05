#! -*-coding:utf-8 -*-
from crawling.spiders.redis_spider import RedisSpider
from crawling.items import RawResponseItem, RenrenItem
from bs4 import BeautifulSoup
from scrapy.http import Request
import time

class RenrenCheSpider(RedisSpider):
    name = "renrenSpider"
    root_url = "https://www.renrenche.com"

    def __init__(self, *args, **kwargs):
        super(RenrenCheSpider, self).__init__(*args, **kwargs)


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
        item["body"] = response.body
        # item["body"] = "asdfsdfsdfsdfsdfsdf"
        item["links"] = []

        soup = BeautifulSoup(response.body.decode("utf-8"), "lxml")
        citys = soup.find("div", class_="area-city-letter").find_all("a")
        for city in citys:
            cityspell = city['href']
            cityname = city.get_text(strip=True)
            link = self.root_url + cityspell + "ershouche/"
            req = Request(link, meta={"city": cityname}, callback=self.parse_list, dont_filter=True)
            if 'useragent' in response.meta and response.meta['useragent'] is not None:
                req.headers['User-Agent'] = response.meta['useragent']
            yield req
            self.logger.info(req)
        yield item


    def parse_list(self, response):
        html = BeautifulSoup(response.body.decode("utf-8"), "lxml")
        thumbnail = html.find("ul", class_="row-fluid list-row js-car-list") \
              .find_all("a", class_="thumbnail")
        data = {"city": response.meta['city']}
        for thum in thumbnail:
            links = self.root_url + thum["href"]
            links = links.replace("http:", "https:")
            links = links.replace("m.renrenche", "www.renrenche")
            yield Request(links, meta=data, callback=self.parse_detail, dont_filter=True)
        next_page = html.find("ul", class_="pagination js-pagination")
        if next_page:
            next_url = next_page.find_all("a")[-1]["href"]
            if next_url != "javascript:void(0);":
                next_link = self.root_url + next_url
                yield Request(next_link, meta=data, callback=self.parse_list, dont_filter=True)


    def parse_detail(self, response):
        html = BeautifulSoup(response.body.decode("utf-8"), "lxml")
        breadcrumb = html.find("p", class_="detail-breadcrumb-tagP").find_all('a')
        brand = breadcrumb[2].get_text(strip=True)  # 品牌
        models = breadcrumb[3].get_text(strip=True)  # 车型
        location = response.meta['city']
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 当前时间
        container = html.find("div", class_="right-container")
        new_price = container.find('p', class_="price detail-title-right-tagP").get_text(strip=True)  # 二手车报价
        old_span = container.find('div', class_="new-car-price detail-title-right-tagP").find("span")
        old_price = old_span.get_text(strip=True)  # 新车报价
        ul = container.find('ul', class_="row-fluid list-unstyled box-list-primary-detail").find_all('li')
        registration_time = ul[0].find('strong').get_text(strip=True)  # 上牌时间
        mileage = ul[1].find('strong').get_text(strip=True)  # 行驶里程
        registration_adr = ul[-1].find('strong')['licensed-city']  # 上牌地
        renItem = RenrenItem()
        if brand:
            renItem['brand'] = brand    
        if models:
            renItem['models'] = models
        if new_price:
            renItem['new_price'] = new_price
        if old_price:
            renItem['old_price'] = old_price
        if registration_time:
            renItem['reg_time'] = registration_time
        if registration_adr:
            renItem['reg_adr'] = registration_adr
        if mileage:
            renItem['mileage'] = mileage
        renItem['current_time'] = current_time
        renItem['location'] = location
        renItem['url'] = response.url
        yield renItem


