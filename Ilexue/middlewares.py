import pickle
import pickle
import threading
import time

import requests
from purl import URL
from scrapy.http import HtmlResponse
from scrapy.http import TextResponse
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from Ilexue.settings import DEFAULT_REQUEST_HEADERS, enabledMethod


def synchronized(func):
    outer_lock = threading.Lock()

    def synced_func(*args, **kws):
        with outer_lock:
            return func(*args, **kws)

    return synced_func

@synchronized
def process_onclick(self, item, request, result):
    # try:
    #     lock.acquire(timeout=60)
    self.browser.switch_to.window(self.browser.window_handles[0])
    handle = self.browser.current_window_handle
    handles = self.browser.window_handles
    for newhandle in handles:
        if newhandle != handle:
            self.browser.close()
    # 获取当前窗口句柄（窗口A）
    self.browser.header_overrides = DEFAULT_REQUEST_HEADERS
    # self.browser.add_cookie(cookies)
    # while len(self.browser.window_handles) > 1:
    if request.url != self.browser.current_url:
        self.browser.get(request.url)
    req = self.browser.wait_for_request(request.url, timeout=30)
    handle = self.browser.current_window_handle
    # 打开一个新的窗口
    self.didOnlicks.append(URL(request.url).path() + '_' + item['onclick'])
    with open('didOnlicks.data', 'wb') as f:
        # f.write( pickle.dumps(list) )
        pickle.dump(self.didOnlicks, f)
    if item['id'] != '':
        self.browser.find_element_by_id(item['id']).click()
    else:
        self.browser.execute_script(item['onclick'])
    self.browser.wait_for_request(self.browser.last_request.path, timeout=10)
    for i in range(self.timeout):
        if len(self.browser.window_handles) > 1:
            break
        time.sleep(1)
    # self.wait.until((len(self.browser.window_handles) > 1))
    # self.browser.find_element_by_id('xx').click()
    # 获取当前所有窗口句柄（窗口A、B）
    handles = self.browser.window_handles
    # 对窗口进行遍历
    if len(handles) == 1:
        result = HtmlResponse(url=request.url, body=self.browser.page_source, request=request,
                              encoding='utf-8',
                              status=200)
    for newhandle in handles:
        # 筛选新打开的窗口B
        if newhandle != handle:
            # 切换到新打开的窗口B
            self.browser.switch_to.window(newhandle)
            self.browser.wait_for_request(self.browser.last_request.path, timeout=10)
            result = HtmlResponse(url=request.url, body=self.browser.page_source, request=request,
                                  encoding='utf-8',
                                  status=200)
            self.browser.close()
    self.browser.switch_to.window(handle)
    return result


# finally:
#     lock.release()


class CustomDownloaderMiddleware(object):
    def process_request(self, request, spider):
        header = {}
        header.update(DEFAULT_REQUEST_HEADERS)
        header.update(request.meta.get('header') if request.meta.get('header') else {})
        r = requests.post(request.url, headers=header, data=request.meta.get('body'))
        del r.headers['Content-Encoding']
        return TextResponse(url=request.url, body=r.text, request=request, encoding='utf-8', status=200,
                            headers=r.headers)


class ScrapySeleniumDownloaderMiddleware(object):
    def __init__(self, timeout=None, options=None):
        with open('didOnlicks.data', 'wb') as f:
            # data = pickle.loads(f.read())
            try:
                self.didOnlicks = pickle.load(f)  # 跟上面的data = pickle.loads(f.read())语意完全一样。
                print(self.didOnlicks)
            except Exception:
                self.didOnlicks = []

        self.timeout = timeout
        self.options = options
        self.browser = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.browser, self.timeout)
        # 初始化一些基本的变量

    def process_request(self, request, spider):
        try:
            item = request.meta.get('item1')
            # cookies = request.mata.get('cookies')
            if item == None:
                item = {'onclick': ''}
            result = None
            if len(item['onclick']) > 0 and (
                    URL(request.url).path() + '_' + item['onclick']) not in self.didOnlicks and any(
                    str(x) in item['onclick'] for x in enabledMethod):
                result = process_onclick(self, item, request, result)
            elif len(item['onclick']) > 0:
                result = HtmlResponse(url=request.url, status=500, request=request)

            return result
        except Exception:
            return HtmlResponse(url=request.url, status=500, request=request)

            # 生成一个页面的driver对象
            # page = request.mata.get('page')
            # # 这里取出刚刚倒进request中的page数
            # if page == 1:
            #     pass # 直接就不用处理，就直接是这个首页的driver就可以了
            # else:
            #     input_element = self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="mainsrp-pager"]//input[@class="input J_Input"]')))
            #     # 找到输入page的框框
            #     submit_element = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="mainsrp-pager"]//span[@class="btn J_Submit"]')))
            #     # 找到点击的按钮
            #     input_element.clear()
            #     # 清除里面原来可能包含的内容
            #     input_element.send_keys(page)
            #     submit_element.click()
            # # 如果不是等于一，那么还应该在这个找到输入框并输入页码，进行跳转
            # # 将这个driver改成跳转后的driver
            # yield HtmlResponse(url=request.url,body=res.page_source,request=request,encoding='utf-8',status=200)
            # # 这里我们直接返回了经过selenium提取的页面
        # except TimeoutException:
        #     return HtmlResponse(url=request.url,status=500,request=request)
        # HtmlResponse是textResponse的一个子类，它会自动寻找适当的html文件编码，然后返回html类型的数据
        # 注意我们这里返回的是一个response，所以，接下来我们就不会继续调用剩下的中间件的request和exception
        # 的方法了，转而调用所有中间件的response方法

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   options=crawler.settings.get('CHROME_OPTIONS'))

    # 这个类方法用于提取settings中的配置信息
    # 返回一个实例
    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
