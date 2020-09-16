import time
import requests
from bs4 import BeautifulSoup
import json
import os


def appendURL(resp):
    return "http://jwc.bjtu.edu.cn/Admin/UserInfo/Login.aspx?LoginInUIA=" + resp["LoginInUIA"] + \
           "&UserName=" + resp["UserName"] + "&LoginFor="


payload_req = {
    "callCount": "1",
    "c0-scriptName": "__System",
    "c0-methodName": "generateId",
    "c0-id": "0",
    "batchId": "0",
    "instanceId": "0",
    "page": "/meol/jpk/course/layout/newpage/index.jsp/courseId/19268",
    "scriptSessionId": "",
    "windowName": "main"
}


class Util:

    def __init__(self):
        self.course_list = dict()
        self.login_url = "http://jwc.bjtu.edu.cn:82/LoginAjax.aspx"
        self.welcome_url = "http://jwc.bjtu.edu.cn:82/Welcome.aspx"
        self.jump_jwc_url = "http://jwc.bjtu.edu.cn:82/NoMasterJumpPage.aspx?URL=jwcKcpt&amp;FPC=page:jwcKcpt"

        self.kcpt_host_url = "http://cc.bjtu.edu.cn:81/meol/"
        self.kcpt_index_url = "index.jsp"
        self.kcpt_reminder_url = "welcomepage/student/interaction_reminder.jsp"
        self.kcpt_mycourse_url = "lesson/blen.student.lesson.list.jsp"
        self.kcpt_lesson_base_url = "lesson/mainJumpPage.jsp?courseId="
        self.dwr_url = "dwr/call/plaincall/__System.generateId.dwr"  # 我们仍未知道这个玩意儿是干嘛的

        self.my_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate"
        }

        self.data = {"username": 18281011, "password": 37862859, "type": 1, "_": int(round(time.time() * 1000))}
        self.session = requests.Session()
        self.session.headers.update(self.my_header)

    def getReminderContent(self):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_reminder_url)
        if cont.status_code == 200:
            with open("nowReminder.html", "w", encoding="utf-8") as f:
                f.write(cont.text)

    def getCourseList(self):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_mycourse_url)
        # print(cont.headers)
        with open("output/kcpt.html", "w", encoding="utf-8") as f:
            f.write(cont.text)

        soup = BeautifulSoup(cont.text, "html.parser")
        res = soup.find_all("a")
        for item in res:
            attr = item.attrs
            if attr.get("class") is None:
                self.course_list[item.string.strip()] = item["href"].split("=")[-1]

    def getCourseDetail(self, courseID):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_lesson_base_url + courseID)
        txxt = self.session.post(self.kcpt_host_url + self.dwr_url, data=payload_req)
        self.session.cookies.update({"DWRSESSIONID": txxt.text.split('"')[-2]})

        # 这里的cont是主页面 不包含课程简介、课程通知、最新动态

    def login(self):
        response = self.session.post(url=self.login_url, data=self.data)
        self.session.cookies.update(response.cookies)
        response = self.session.get(url=appendURL(json.loads(response.text[1:-1])))

        with open("output/welcome.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # 以上登录了jwc个人中心

        nxturl = self.session.get(self.jump_jwc_url, allow_redirects=False).headers["Location"]
        response = self.session.get(nxturl, allow_redirects=False)
        self.session.cookies.clear()
        self.session.cookies.update(response.cookies)
