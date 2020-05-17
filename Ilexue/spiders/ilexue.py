# --coding:utf-8--
import importlib
import os
import re
import sys

import demjson
import requests
import scrapy
from purl import URL
from scrapy.http import Request

from IlexueClient import IlexueClient
from Ilexue.items import IlexueItem, IlexueVideoItem
from Ilexue.settings import USER_NAME, PASS_WORD, DEFAULT_REQUEST_HEADERS

importlib.reload(sys)


class Myspider(scrapy.Spider):
    name = 'Ilexue'
    # allowed_domains=['ilexue.yonyou.com']
    base = r'C:/Users/Administrator/Desktop/ilexue_scrapy/Ilexue/info/'
    host = 'ilexue.yonyou.com'
    ilexueSession = {}

    def start_requests(self):
        self.ilexueSession = requests.session()
        client = IlexueClient();
        token = client.ssoLogin(username=USER_NAME, password=PASS_WORD)['token']
        url = 'http://ilexue.yonyou.com/ilexuehome.htm'
        cookies = requests.utils.dict_from_cookiejar(self.ilexueSession.get(url + '?token=' + token).cookies)
        cookie_str = "; ".join([str(x) + "=" + str(y) for x, y in cookies.items()])
        # for cookie in cookies:
        #     cookie_str +=cookie.getValue()getKey()+'='+cookie.getValue()+'; '
        DEFAULT_REQUEST_HEADERS['Cookie'] = cookie_str
        # yield Request('http://ilexue.yonyou.com/Services/CommonService.svc/GetKnowledgeRecommendsList',
        #               callback=self.parseJson,
        #               meta={'header': {'Content-Type': 'text/json', 'Referer': 'http://ilexue.yonyou.com/'},'body':'{"limitp":100}'})
        url = 'http://ilexue.yonyou.com/plan/c588a8f03db5429c89d180941b227a71.html'
        yield Request(url, callback=self.parse)

    def parseJson(self, response):
        resjson = demjson.decode(demjson.decode(response.text))
        for res in resjson:
            if res['knowledgeType'] == 'VideoKnowledge':
                item = IlexueItem()
                siteURL = URL(res['knowledgeUrl']).scheme('http').domain(self.host)
                item['siteURL'] = siteURL.as_string()
                item['onclick'] = ''
                item['pageURL'] = response.request.url
                item['title'] = res['title']
                item['fileName'] = self.base + item['title']
                yield Request(url=item['siteURL'], meta={'item1': item}, callback=self.parseVideoAndDocument)

    def parse(self, response):
        # 创建一个大的list存储所有的item
        items = []
        print(response.request.headers)
        # pattern_html = re.compile(r'<div class="title".*?<a.*?href="(.*?)">(.*?)</a></span></div>', re.S)
        pattern_html = re.compile(r'(/[kng|plan]+/[\S]*?\.htm[l]?.*?)[\'"].*?<span title="(.*?)".*?>.*?</span>', re.S)
        htmls = re.findall(pattern_html, response.text)
        for html in htmls:
            # 创建实例,并转化为字典
            item = IlexueItem()
            siteURL = URL(html[0]).scheme('http').domain(self.host)
            item['id'] = ''
            item['siteURL'] = siteURL.as_string()
            item['onclick'] = ''
            item['pageURL'] = response.request.url
            item['title'] = 'more' if html[1] == '' else html[1]
            item['fileName'] = self.base + item['title']
            items.append(item)
        # pattern_onclick = re.compile(r'onclick="(.*?)".*?>(\w*[·\.\.\.]*)<.*?(span>\(([0-9]+)\))*', re.S)
        # onclicks = re.findall(pattern_onclick, response.text)
        onclicks = re.findall(re.compile(
            r'(id="([\w|-]*)"[^\<|^\>]*)?((onclick="(.*?)")|(href="javascript:void\((.*?)\))).*?>([\w|"]*[·\.\.\.]*)<.*?(span>\(([0-9]+)\))*',
            re.S), response.text)
        for onclick in onclicks:
            if onclick[7] != '' and 'displayData' in onclick[4] and (onclick[9] == '' or onclick[9] == '0'):
                continue
            if 'amp;amp;' in response.request.url:
                response.request.url = response.request.url.replace('amp;', '')
                continue
            # 创建实例,并转化为字典
            item = IlexueItem()
            item['id'] = onclick[1]
            item['siteURL'] = ''
            item['onclick'] = onclick[4]
            item['pageURL'] = response.request.url
            item['title'] = 'more' if onclick[7] == '' else onclick[7]
            item['fileName'] = self.base + item['title']
            items.append(item)

        for item in items:
            # 创建文件夹
            fileName = item['fileName']
            if not os.path.exists(fileName.replace('\"', '')):
                os.makedirs(fileName.replace('\"', ''))
            # 用meta传入下一层
            print(item)
            if item["siteURL"].find('video') > 0 or item['siteURL'].find('document') > 0:
                yield Request(url=item['siteURL'], meta={'item1': item}, callback=self.parseVideoAndDocument)
            elif len(item['onclick']) > 0:
                yield Request(url=item['pageURL'], meta={'item1': item}, callback=self.parse, dont_filter=True)
            else:
                yield Request(url=item['siteURL'], meta={'item1': item}, callback=self.parse)

    def parseVideoAndDocument(self, response):
        item = IlexueVideoItem(response.meta['item1'])
        pattern = re.compile(r'[video|document]+/(.*?).html', re.S)
        item['id'] = re.findall(pattern, item['siteURL'])[1]
        yield item
