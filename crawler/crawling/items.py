# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class RawResponseItem(Item):
    appid = Field()
    crawlid = Field()
    url = Field()
    response_url = Field()
    status_code = Field()
    status_msg = Field()
    response_headers = Field()
    request_headers = Field()
    body = Field()
    links = Field()
    attrs = Field()
    success = Field()
    exception = Field()



class RenrenItem(Item):
    brand = Field()
    models = Field()
    new_price = Field()
    old_price = Field()
    reg_time = Field()
    reg_adr = Field()
    mileage = Field()
    current_time = Field()
    location = Field()
    url = Field()
