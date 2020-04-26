#!coding=utf-8
import time
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pickle
 
class IlexueSpider(object):
    def __init__(self,username):
        self.username = username
        self.driver = webdriver.Firefox()
        self.set_cookie()
        self.driver.get(url='http://ilexue.yonyou.com/ilexuehome.htm')
        self.is_login()
    def is_login(self):
        '''判断当前是否登陆'''
        #self.driver.refresh()
        html = self.driver.page_source
        if html.find(self.username) == -1: #利用用户名判断是否登陆
            # 没登录 ,则手动登录
            self.login()
        else:
            #已经登录  尝试访问搜索记录，可以正常访问
            
            #time.sleep(30)  # 延时看效果
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ilexuehome_layout")))
            print("正在获取网页数据...")
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            self.driver.close()

            #request = urllib.request.Request(url, headers=header)
            #html = urllib.request.urlopen(request)
            #bsObj = BeautifulSoup(html, "html.parser")
            #print(html.read())
            #print(bsObj)
            fhandle = open("./diwork.html", "wb")
            fhandle.write(bytes(bsObj.get_text(),'utf8'))
            fhandle.close()
 
    def login(self):
        '''登陆'''
        #time.sleep(20) #等待手动登录
        del self.driver.header_overrides
        self.driver.get(url='https://www.diwork.com')
        element = WebDriverWait(self.driver,60,1).until(EC.presence_of_element_located((By.XPATH,'//img[@src="https://file-cdn.yonyoucloud.com/workbench-image-path-applicationIcon/f8e43748-089e-486d-a4d0-a89190f97260/original_15FF5455-1A8A-4BCC-B595-05048C442AB2.jpg"]')))
        element.click()
        time.sleep(5)
        #print(self.driver.get_cookies())
        n = self.driver.window_handles # 获取当前页句柄
        self.driver.switch_to.window (n[1])
        #print(self.driver.get_cookies())
        self.driver.get(url='http://ilexue.yonyou.com/ilexuehome.htm')
        #WebDriverWait(self.driver,60,1).until(EC.presence_of_element_located((By.ID,'hylIndex0')))
        #time.sleep(5)
        self.save_cookie()
     
    def save_cookie(self):
        '''保存cookie'''
        # 将cookie序列化保存下来
        print(self.driver.get_cookies())
        pickle.dump(self.driver.get_cookies(), open("cookies.ilexue", "wb"))
 
    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            cookies = pickle.load(open("cookies.ilexue", "rb"))
            print(cookies)
            cookie_str=''
            for cookie in cookies:
                cookie_str=cookie_str+cookie.get('name')+'='+cookie.get('value')+';'
                cookie_dict = {
                    #"domain": ".baidu.com",  # 火狐浏览器不用填写，谷歌要需要
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                #self.driver.add_cookie(cookie_dict)
            print(cookie_str)
            header = {
                'Cookie': cookie_str,
            }
            self.driver.header_overrides = header
        except Exception as e:
            print(e)
 
 
if __name__ == '__main__':
 
    IlexueSpider('李杭燃') # 你的名称
