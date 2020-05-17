import _thread
import csv
import json
import os
import re
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue

import demjson
import execjs
import requests
from PyEvalJS import Runtime

from Ilexue.settings import CSVDIR, USER_NAME, PASS_WORD


def learnCourse(courseinfo):
    IlexueClient().learnCourse(courseinfo)


class IlexueClient(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.pool = ThreadPoolExecutor(max_workers=3)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with IlexueClient._instance_lock:
                if not hasattr(cls, '_instance'):
                    IlexueClient._instance = super().__new__(cls)
                    _thread.start_new_thread(IlexueClient._instance.startLearning, ())
        return IlexueClient._instance

    casURL = 'https://euc.diwork.com/cas/login?sysid=diwork&mode=light&service=https%3A%2F%2Fwww.diwork.com' \
             '%2Flogin_light%3Fyhtdesturl%3D%2Fyhtssoislogin%26yhtrealservice%3Dhttps%3A%2F%2Fwww.diwork.com&locale' \
             '=zh_CN '
    getServiceInfoWithDetailURL = 'https://www.diwork.com/service/getServiceInfoWithDetail?serviceCode=9b37bced' \
                                  '-1f9e-4adc-944d-a95d438334f9&serviceType=0&tm='
    studySubmitURL = "https://api-qidatestin.yunxuetang.cn/v1/study/submit?encryption="
    updateprogressURL = 'https://api-qidatestin.yunxuetang.cn/v1/study/updateprogress'
    createActionLogURL = 'http://ilexue.yonyou.com/kng/services/KngComService.svc/CreateActionLog'
    getEncryptRequestURL = 'http://ilexue.yonyou.com/kng/services/KngComService.svc/GetEncryptRequest'
    ilexueInfo = {}
    uniQueue = Queue()
    mysession = requests.session()
    studyingCouses = set()
    studyedCouses = set()
    courses = []

    def startLearning(self):
        # pool = Pool(3)  # 创建拥有3个进程数量的进程池
        # testFL:要处理的数据列表，run：处理testFL列表中数据的函数
        # client.ssoLogin(USER_NAME, PASS_WORD)
        while 1:
            if not self.uniQueue.empty():
                item = self.uniQueue.get_nowait()
                self.pool.submit(learnCourse, item)
            time.sleep(3)

    def ssoLogin(self, username, password):
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        res = requests.post(self.casURL, data=self.getSsoRaw(username, password), headers=header)
        print("casURL-info:" + str(res.text))
        try:
            info = res.json()
        except  Exception as e:
            info = {'data': res.text}
        pattern = re.compile(r'[a-zA-z]+://[^\s]*[\w]', re.S)
        ssoLoginurl = re.search(pattern, info['data']).group(0)
        res = requests.get(ssoLoginurl, headers=header)
        print("ssoLoginurl-info:" + str(res.text))
        yht_access_token = res.cookies['yht_access_token']
        header['Content-Type'] = r'application/x-www-form-urlencoded;charset=UTF-8'
        header['Cookie'] = r'yht_access_token=' + yht_access_token
        res = requests.get(self.getServiceInfoWithDetailURL + str(int(time.time())), headers=header,
                           cookies=res.cookies)
        print("getServiceInfoWithDetailURL-info:" + str(res.text))
        try:
            ilexueSsoInfo = res.json()
        except  Exception as e:
            ilexueSsoInfo = {'data': res.text}
        ilexuetokenURL = ilexueSsoInfo['data']['url']
        print(ilexuetokenURL)
        res = requests.get(ilexuetokenURL)
        self.mysession.get(ilexuetokenURL)
        try:
            ilexueInfo = res.json()
        except  Exception as e:
            ilexueInfo = {'data': res.text}
        pattern = re.compile(r'"(ucloud--cluster--[^\s]*)"', re.S)
        print(ilexueInfo)
        token = re.search(pattern, ilexueInfo['data']).group(1)
        self.ilexueInfo = ilexueInfo
        self.ilexueInfo['token'] = token
        self.ilexueInfo['Cookie'] = res.request._cookies
        return self.ilexueInfo

    def getSsoRaw(self, username, password):
        data1 = open(os.path.dirname(__file__) + '/Ilexue/js/security.min.js', 'r', encoding='utf8').read()
        data2 = open(os.path.dirname(__file__) + '/Ilexue/js/interface.js', 'r', encoding='utf8').read()
        runtime = Runtime()
        runtime.compile(data1 + '\n' + data2)
        return runtime.call('getraw', username, password)

    def learnCourse(self, courseinfo):
        header = {
            'token': self.ilexueInfo['token']
        }
        id = courseinfo['id']
        course = {
            "knowledgeId": '',
            "masterId": "",
            "masterType": courseinfo["mastertype"],
            "packageId": '',
            "pageSize": 1,
            "studySize": 1,
            "studyTime": 120,
            "type": 0 if courseinfo['siteURL'].find('video') > 0 else 1 if courseinfo['siteURL'].find(
                'video') > 0 else '',
            "offLine": False,
            "end": False,
            "care": True,
            "deviceId": "",
            "studyChapterIds": "",
            "viewSchedule": 121.105073 if courseinfo['siteURL'].find('video') > 0 else 1,
        }
        ids = id.split('_')
        ids0 = ids[0]
        if len(ids) > 1:
            ids1 = ids[1]
            packageId = ids0[0:8] + "-" + ids0[8:12] + "-" + ids0[12:16] + "-" + ids0[16:20] + "-" + ids0[20:]
            course['packageId'] = packageId if not course['masterType'] else ''
            course['masterId'] = packageId if course['masterType'] else ''
            course['knowledgeId'] = ids1[0:8] + "-" + ids1[8:12] + "-" + ids1[12:16] + "-" \
                                    + ids1[16:20] + "-" + ids1[20:]
        else:
            course['packageId'] = ''
            course['knowledgeId'] = ids0[0:8] + "-" + ids0[8:12] + "-" + ids0[12:16] + "-" \
                                    + ids0[16:20] + "-" + ids0[20:]
        try:
            print(courseinfo)
            print(requests.get(courseinfo['siteURL'], headers=header,
                               cookies=self.ilexueInfo['Cookie']))
            progress = self.updateprogress(course, header, self.ilexueInfo['Cookie'])
            print(progress)
            if progress.__contains__('error') and progress['error']['key'] == 'global.token.invalid':
                self.ssoLogin(USER_NAME, PASS_WORD)
            standardStudyHours = int(progress["standardstudyhours"]) - int(progress["actualstudyhours"])
            course['pageSize'] = progress['studypagesize']
            course['studySize'] = progress['studypagesize']
            course['viewSchedule'] = int(progress['viewSchedule']) \
                if progress['knowledgetype'] == 'DocumentKnowledge' else progress['viewSchedule']
            createactionLogJson = {
                'kngId': course['knowledgeId'],
                'bachNo': "",
                'type': 'play',
                'context': "开始播放时间：0，用户开始播放事件，(vediolength)视频总时长：" + str(progress['standardstudyhours'])
            }
            self.createActionLog(createactionLogJson, header)
            gap = 2
            count = int(standardStudyHours / gap) + 1
            for i in range(1, count):
                time.sleep(60 * gap)
                result = {"X-Application-Context": ''}
                while result["X-Application-Context"] == '' or (
                        "qidaapi:prod:10000" != result["X-Application-Context"]):
                    res = requests.post(self.studySubmitURL + self.getEncryptRequest(id, course),
                                        data=json.dumps(course),
                                        headers=header)
                    try:
                        result['X-Application-Context'] = res.headers['X-Application-Context']
                    except Exception as e:
                        result = {'data': res.text, "X-Application-Context": ''}
                    print(
                        str(i * 2) + "-knowledgeId:" + course["knowledgeId"] + '-siteURL:' + courseinfo["siteURL"])
                    print(result)
            print("结束:" + time.ctime(time.time()) + "++++" + str(standardStudyHours) + "-knowledgeId:" + course[
                "knowledgeId"])
            self.studyedCouses.add(courseinfo['id'])
        except Exception as e:
            print(e)

    def updateprogress(self, data, header, cookie):
        header['Content-Type'] = 'application/json'
        print("updateprogress:"+self.updateprogressURL+"<>data:"+json.dumps(data))
        res = requests.post(self.updateprogressURL, data=json.dumps(data), headers=header, cookies=cookie)
        try:
            info = res.json()
        except Exception as e:
            info = {'data': res.text}
        print("updateprogress-info:" + str(info))
        return info

    def createActionLog(self, data, header):
        header['Content-Type'] = 'application/json'
        print("createActionLog:" + self.createActionLogURL + "<>data:" + json.dumps(data))
        res = requests.post(self.createActionLogURL, data=json.dumps(data), headers=header)
        try:
            info = res.json()
        except Exception as e:
            info = {'data': res.text}
        print("createActionLog-info:" + str(info))
        return info

    def getEncryptRequest(self, id, data):
        header = {
            'Content-Type': 'application/json',
            'Referer': "http://ilexue.yonyou.com/kng/course/package/video/" + id + ".html" if id.find(
                '_') > -1 else "http://ilexue.yonyou.com/kng/view/video/" + id + ".html"

        }
        bodyjson = {
            'body': json.dumps(data, separators=(',', ':'))
        }
        res = requests.post(self.getEncryptRequestURL, data=json.dumps(bodyjson, separators=(',', ':')), headers=header)
        try:
            info = res.json()
        except Exception as e:
            info = {'data': res.text}
        if isinstance(info, str):
            info = demjson.decode(info)
        print("getEncryptRequest-info:" + str(info))
        return info['Data']

    def study(self):
        self.ssoLogin(USER_NAME, PASS_WORD)
        coursesReader = self.importCsv(CSVDIR)
        self.pool.submit(self.cleanCsv, coursesReader)
        for course in self.courses:
            self.learnCourse(
                courseinfo=course)

    def cleanCsv(self, coursesReader):
        # 清理url.csv
        while len(self.studyedCouses) < len(self.studyingCouses):
            csvdata = open(os.path.dirname(__file__) + CSVDIR, 'w', encoding='utf8')
            csvWriter = csv.DictWriter(csvdata, fieldnames=coursesReader.fieldnames)
            csvWriter.writeheader()
            for courseTmp in self.courses:
                if not self.studyedCouses.__contains__(courseTmp['id']):
                    csvWriter.writerow(courseTmp)
            csvdata.close()
            time.sleep(60*10)

    def importCsv(self, CSVDIR):
        csvdata = open(os.path.dirname(__file__) + CSVDIR, 'r', encoding='utf8')
        csvReader = csv.DictReader(csvdata)
        for course in csvReader:
            if not self.studyingCouses.__contains__(course.get('id')):
                self.courses.append(course)
            self.studyingCouses.add(course.get('id'))
        csvdata.close()
        return csvReader


def main():
    IlexueClient().study()


if __name__ == "__main__":
    main()
