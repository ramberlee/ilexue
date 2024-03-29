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
from bs4 import BeautifulSoup
import re

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
    createActionLogURL = 'http://youlexue.yonyou.com/kng/services/KngComService.svc/CreateActionLog'
    getEncryptRequestURL = 'http://youlexue.yonyou.com/kng/services/KngComService.svc/GetEncryptRequest'
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
        # res = requests.post(self.casURL, data=self.getSsoRaw(username, password), headers=header)
        res = self.mysession.post(self.casURL, data=self.getSsoRaw(username, password), headers=header)
        print("casURL-info:" + str(res.text))
        try:
            info = res.json()
        except  Exception as e:
            info = {'data': res.text}
        pattern = re.compile(r'[a-zA-z]+://[^\s]*[\w]', re.S)
        ssoLoginurl = re.search(pattern, info['data']).group(0)
        # res = requests.get(ssoLoginurl, headers=header)
        res = self.mysession.get(ssoLoginurl, headers=header)
        print("ssoLoginurl-info:" + str(res.text))
        yht_access_token = res.cookies['yht_access_token']
        header['Content-Type'] = r'application/x-www-form-urlencoded;charset=UTF-8'
        header['Cookie'] = r'yht_access_token=' + yht_access_token
        # res = requests.get(self.getServiceInfoWithDetailURL + str(int(time.time())), headers=header,
        #                    cookies=res.cookies)
        res = self.mysession.get(self.getServiceInfoWithDetailURL + str(int(time.time())), headers=header)
        print("getServiceInfoWithDetailURL-info:" + str(res.text))
        try:
            ilexueSsoInfo = res.json()
        except  Exception as e:
            ilexueSsoInfo = {'data': res.text}
        ilexuetokenURL = ilexueSsoInfo['data']['url']
        print(ilexuetokenURL)
        # res = requests.get(ilexuetokenURL)
        res = self.mysession.get(ilexuetokenURL)
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
        # runtime = Runtime()
        runtime = execjs.compile(data1 + '\n' + data2)
        return runtime.call('getraw', username, password)

    def learnCourse(self, courseinfo):
        header = {
            'token': self.ilexueInfo['token']
        }
        matchObj  = re.match('.*\\/([\\S]+).html', courseinfo['siteURL'])
        id = matchObj.group(1)
        course = {
            "knowledgeId": '',
            "masterId": "",
            "masterType": 'Plan' if courseinfo['siteURL'].find('/plan/') > 0 else '',
            "packageId": '',
            "pageSize": 1,
            "studySize": 1,
            "studyTime": 120,
            "type": 0 if courseinfo['siteURL'].find('video') > 0 else 1 if courseinfo['siteURL'].find(
                'document') > 0 else '',
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
            # pagehtml = requests.get(courseinfo['siteURL'], headers=header,
            #                    cookies=self.ilexueInfo['Cookie'])
            pagehtml = self.mysession.get(courseinfo['siteURL'], headers=header)
            # print(pagehtml.text)
            print(courseinfo['siteURL'])
            soup = BeautifulSoup(pagehtml.text, "lxml")
            progress = self.updateprogress(course, header, self.ilexueInfo['Cookie'])
            print(progress)
            if progress.__contains__('error') and progress['error']['key'] == 'global.token.invalid':
                self.ssoLogin(USER_NAME, PASS_WORD)
            standardStudyHours = int(progress["standardstudyhours"]) - int(progress["actualstudyhours"])
            course['pageSize'] = progress['studypagesize'] if progress['studypagesize'] != 0 else course['pageSize']
            course['studySize'] = progress['studypagesize'] if progress['studypagesize'] != 0 else course['studySize']
            course['viewSchedule'] = int(course['viewSchedule']) \
                if progress['knowledgetype'] == 'DocumentKnowledge' else course['viewSchedule']
            # if progress['knowledgetype'] != 'DocumentKnowledge':
            #     createactionLogJson = {
            #         'kngId': course['knowledgeId'],
            #         'bachNo': soup.find('input',id='hidBachNo').get('value') if soup.find('input',id='hidBachNo') != None else '',
            #         'type': 'play',
            #         'context': "开始播放时间：0，用户开始播放事件，(vediolength)视频总时长：" + str(progress['standardstudyhours'])
            #     }
            #     knows = re.findall(re.compile(r'"fileFullUrl":"(\S*?)".*?,"videoKeyId":"(\S*?)"', re.S), pagehtml.text)
            #     knowfile = knows[0][0]
            #     knowfilekey = knows[0][1]
            #     print("knowfile:"+knowfile+"<>knowfilekey:"+knowfilekey)
            #     self.createActionLog(createactionLogJson, header)
            #     print(self.mysession.get(
            #         "https://drm.media.baidubce.com:8888/v1/sdk-player/user/web/play?videoUrl="+knowfile+"&videoHeight=undefined&videoWidth"
            #                                                                                              "=undefined&playerHeight=100%25&playerWidth=100%25&duration=&size=&startPosition=0&service=vod"
            #                                                                                              "&time="+str.replace(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),' ','%20')+'18'+"&sessionTime="+str(int(time.time()))+"&env=%7B%22flashVersion%22%3A0%2C"
            #                                                                                                                                                                                                                                         "%22cyberPlayerVersion%22%3A%223.4.0%22%2C%22ak%22%3A%22b57e71d512c64ac39543b585ea3f32b1%22%2C"
            #                                                                                                                                                                                                                                         "%22provider%22%3A%22videojs%22%2C%22config%22%3A%22%22%7D&sendTime="+str.replace(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),' ','%20')))
            #     print(self.mysession.get("http://api-component.yxt.com/v1/authex/bce/valid?f="+knowfile+"&m="+knowfilekey+"&e"
            #                                                                                                               "="+str(int(time.time()))+"&k=abc"))
            gap = 2
            count = int(standardStudyHours / gap) + 1
            startsec = time.time()
            for i in range(1, count):
                time.sleep(60 * gap)
                if progress['knowledgetype'] != 'DocumentKnowledge':
                    createactionLogJson = {
                        'kngId': course['knowledgeId'],
                        'bachNo': soup.find('input', id='hidBachNo').get('value') if soup.find('input', id='hidBachNo') is not None else '',
                        'type': 'play',
                        'context': "开始播放时间：0，用户开始播放事件，(vediolength)视频总时长：" + str(progress['standardstudyhours'])
                    }
                    knows = re.findall(re.compile(r'"fileFullUrl":"(\S*?)".*?,"videoKeyId":"(\S*?)"', re.S),
                                       pagehtml.text)
                    knowfile = knows[0][0]
                    knowfilekey = knows[0][1]
                    print("knowfile:" + knowfile + "<>knowfilekey:" + knowfilekey)
                    self.createActionLog(createactionLogJson, header)
                    print(self.mysession.get(
                        "https://drm.media.baidubce.com:8888/v1/sdk-player/user/web/play?videoUrl=" + knowfile + "&videoHeight=undefined&videoWidth"
                                                                                                                 "=undefined&playerHeight=100%25&playerWidth=100%25&duration=&size=&startPosition=0&service=vod"
                                                                                                                 "&time=" + str.replace(
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ' ',
                            '%20') + '18' + "&sessionTime=" + str(
                            int(time.time())) + "&env=%7B%22flashVersion%22%3A0%2C"
                                                "%22cyberPlayerVersion%22%3A%223.4.0%22%2C%22ak%22%3A%22b57e71d512c64ac39543b585ea3f32b1%22%2C"
                                                "%22provider%22%3A%22videojs%22%2C%22config%22%3A%22%22%7D&sendTime=" + str.replace(
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ' ', '%20')))
                    print(self.mysession.get(
                        "http://api-component.yxt.com/v1/authex/bce/valid?f=" + knowfile + "&m=" + knowfilekey + "&e"
                                                                    "=" + str(int(time.time())) + "&k=abc"))
                    course['viewSchedule'] = round(course['viewSchedule'] + time.time()-startsec,6)
                result = {"X-Application-Context": ''}
                while result["X-Application-Context"] == '' or (
                        "qidaapi:prod:10000" != result["X-Application-Context"]):
                    encrypt = self.getEncryptRequest(id, course)
                    res = self.mysession.post(self.studySubmitURL + encrypt,
                                              data=json.dumps(course),
                                              headers=header)
                    print(self.studySubmitURL + encrypt + "<>" + json.dumps(course))
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
        # res = requests.post(self.updateprogressURL, data=json.dumps(data), headers=header, cookies=cookie)
        res = self.mysession.post(self.updateprogressURL, data=json.dumps(data), headers=header)
        try:
            info = res.json()
        except Exception as e:
            info = {'data': res.text}
        print("updateprogress-info:" + str(info))
        return info

    def createActionLog(self, data, header):
        header['Content-Type'] = 'application/json'
        print("createActionLog:" + self.createActionLogURL + "<>data:" + json.dumps(data))
        res = self.mysession.post(self.createActionLogURL, data=json.dumps(data), headers=header)
        try:
            info = res.json()
        except Exception as e:
            info = {'data': res.text}
        print("createActionLog-info:" + str(info))
        return info

    def getEncryptRequest(self, id, data):
        header = {
            'Content-Type': 'application/json',
            'Referer': "http://youlexue.yonyou.com/kng/course/package/video/" + id + ".html" if id.find(
                '_') > -1 else "http://youlexue.yonyou.com/kng/view/video/" + id + ".html"

        }
        bodyjson = {
            'body': json.dumps(data, separators=(',', ':'))
        }
        res = self.mysession.post(self.getEncryptRequestURL, data=json.dumps(bodyjson, separators=(',', ':')), headers=header)
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
            csvdata = open(os.path.dirname(__file__) + CSVDIR, 'r', encoding='utf8')
            csvReader = csv.DictReader(csvdata)
            for course in csvReader:
                if not self.studyingCouses.__contains__(course.get('id')):
                    self.courses.append(course)
                self.studyingCouses.add(course.get('id'))
            csvdata.close()
            csvdata = open(os.path.dirname(__file__) + CSVDIR, 'w', encoding='utf8')
            csvWriter = csv.DictWriter(csvdata, fieldnames=coursesReader.fieldnames)
            csvWriter.writeheader()
            for courseTmp in self.courses:
                if not self.studyedCouses.__contains__(courseTmp['id']):
                    csvWriter.writerow(courseTmp)
            csvdata.close()
            # 1点退出
            if int("01") == int(time.strftime('%H',time.localtime(time.time()))):
                os._exit(0)
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
