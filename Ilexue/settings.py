# -*- coding: utf-8 -*-
# Scrapy settings for Ilexue project

BOT_NAME = 'Ilexue'
SPIDER_MODULES = ['Ilexue.spiders']
NEWSPIDER_MODULE = 'Ilexue.spiders'
MIDDLEWARES_MODULES = ['Ilexue.middlewares']

SELENIUM_TIMEOUT=3
enabledMethod = ['GetDateForMap','displayMore','openURL','displayData','window.open']

USER_NAME = 'lihrd@yonyou.com'
PASS_WORD = 'lhr8182281'
CSVDIR = '/Ilexue/videourl/url.csv'

RANDOMIZE_DOWNLOAD_DELAY = True
ROBOTSTXT_OBEY = False
AUTOTHROTTLE_START_DELAY = 30
AUTOTHROTTLE_MAX_DELAY = 120
# 默认是16，一次可以请求的最大次数
CONCURRENT_REQUESTS = 1
# 下载延迟
DOWNLOAD_DELAY = 240
COOKIES_ENABLED = True
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept': '*/*',
    # 'Accept-Encoding': 'gzip, deflate',
    # 'Connection': 'keep-alive',
    'Cookie': r'ELEARNING_00008=5741d938-86b1-4638-a342-292fd7399e8c; XXTOWN_COOKIE_00018=35a1eb12-7592-48a2-9688-1563ccb6d2f5; ELEARNING_00006=41E130158283DDB0B1265A28A974F392DFF9C11AA9FF93A48A74028CE74765FD5D26DF3B2F17C9709BC307F0F774CA3F83972B57C20C9EDA02AB964FAF3A8E3200FB47BF8534D5F215FE5CA8B56886950A3155ECE9230C05465C505002AAF8FFC7DD3151013BC4DB7495D09777D6F869A94F2FEAA2E521624577D6545AE2F5C309C5D33090ED898CC98E388DB2E2758AB3ED2539C62D9A75B371159EDBDF784D34ECDCD359495632F8C963A7836EE368C2631CB2F169B0B9365E5C77; ELEARNING_00022=%5b%5d; COOKIE_LANGAGES=zh; ELEARNING_00999=y2betsbh0nv2gaammsz24qfh; route=d30a443a0e4a29f54a49230418e9a82f; TY_SESSION_ID=cda83fa6-0f0e-4cba-960f-c99165f6fe69; ELEARNING_00003=StudyMenuGroup; .ASPXAUTH=2FDEEDB1B7D8D0CD4DDAD3594A0D5EE42C4D978FCAF4711E904EDF10B876E62A7109FFF5666251DD8DFB576782A8952A900AD8110CE0185CA3C393BE6CD47A9B8AE674FAC6140696A229E907BE67AF5A238D4DEAC084A5029DAF77B51CA215702864CDF67FACDCDAB1489CA5D9380E2CCB1E1ED331CE0CDC5F90DB7044D09AFC937955BD2A6F8E4AC9999A75; ELEARNING_00018=kEWTaJi27uTd9D18eKs0p7jUqZWy4hXX/72h/hh/moIA2r5aBkVC9E5lneCVM7pYbdQwVatCFXG7VhJqiByyl/U3BQy39178eAJTfv23+IAUBg7hFGgGhJK188L55bnuyV2jTysr0G+wTldtjKBq5tomy9ul/sPhnu8/Zxb/LEYvNS2wWvTKm2+831CaE232ltKuu50mmdB673O/GTu+ogohplI6ymzQrQTpVOTyUIQ=; ELEARNING_00024=ucloud--cluster--AAAAAK5kpfvxrL4qEfuTuV4n28Olv-3zTV3PCBwh9T1kfjQiwZtmqs3YRoNNhS2HzFhQNSWeKQb8lBKdFRtNizaxxaf_XoMSd-nlp1m420amtD8Gs9BacJaUClUWHZEvuGRRs7H-KWz5jXadkcCoJA9JV9A'
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'Ilexue.middlewares.ScrapySeleniumDownloaderMiddleware': 90,
    'Ilexue.middlewares.CustomDownloaderMiddleware': 544
}

ITEM_PIPELINES = {'Ilexue.pipelines.IlexuePipeline': 300}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DEPTH_LIMIT = 500
