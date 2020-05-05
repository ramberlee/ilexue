import _thread
import time

from scrapy.cmdline import execute

# 为线程定义一个函数
from IlexueClient import IlexueClient

#execute(['scrapy', 'crawl', 'Ilexue'])

def scrapy(threadName, delay):
    count = 0
    while count < 200:
        execute(['scrapy', 'crawl', 'Ilexue'])
        time.sleep(delay)
        count += 1
        print("%s: %s" % (threadName, time.ctime(time.time())))


# 为线程定义一个函数
def ilexue(threadName, delay):
    count = 0
    IlexueClient().study()
    while count < 50:
        time.sleep(delay)
        count += 1
        print("%s: %s" % (threadName, time.ctime(time.time())))


# 创建两个线程
try:
    _thread.start_new_thread(ilexue, ("Thread-2", 21600,))
    #scrapy("Thread-1", 3600)
except Exception as e:
    print(e)
    print("Error: 无法启动线程")

while 1:
    pass
