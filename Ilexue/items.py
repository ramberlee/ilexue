# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
import os

class IlexueItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    siteURL = scrapy.Field()
    onclick = scrapy.Field()
    pageURL = scrapy.Field()
    detailURL = scrapy.Field()
    title = scrapy.Field()
    fileName = scrapy.Field()
    path = scrapy.Field()


class IlexueVideoItem(IlexueItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    path = scrapy.Field()
    path = r'C:/Users/Administrator/Desktop/ilexue_scrapy/Ilexue/videourl/url.csv'
    id = scrapy.Field()
