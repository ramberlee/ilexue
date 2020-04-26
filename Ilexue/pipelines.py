# -*- coding: utf-8 -*-
import _thread
import importlib
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

import requests
import sys

from Ilexue.IlexueClient import IlexueClient
from Ilexue.settings import USER_NAME, PASS_WORD
from Ilexue.util.UniQueue import UniQueue

importlib.reload(sys)
#sys.setdefaultencoding('utf-8')


class IlexuePipeline(object):

    def process_item(self, item, spider):
        id = item['id']
        path = item.path
        # fileName=item['fileName']

        # image=requests.get(detailURL)
        IlexueClient().uniQueue.put(item)
        if not os.path.isfile(path):
            f = open(path, 'ab')
            f.write(bytes('id,siteUrl\n','utf-8'))
        else:
            f = open(path, 'ab')
        str = '\n' + id + ','+item['siteURL']
        f.write(bytes(str, 'utf-8'))
        f.close()
        print(str)
        return item
