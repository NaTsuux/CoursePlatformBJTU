import requests
from bs4 import BeautifulSoup
import json
import data
import os


def appendURL(resp):
    return "http://jwc.bjtu.edu.cn/Admin/UserInfo/Login.aspx?LoginInUIA=" + resp["LoginInUIA"] + \
           "&UserName=" + resp["UserName"] + "&LoginFor="


def ptoFile(name, content, encod='utf-8'):
    with open("output/" + name, "w", encoding=encod) as f:
        f.write(content)


payload_req = {
    "callCount": "1",
    "c0-scriptName": "__System",
    "c0-methodName": "generateId",
    "c0-id": "0",
    "batchId": "0",
    "instanceId": "0",
    "page": "/meol/jpk/course/layout/newpage/index.jsp/courseId/",
    "scriptSessionId": "",
    "windowName": "main"
}


def init_payload_req(courseId):
    res = payload_req.copy()
    res['page'] = res['page'] + str(courseId)
    return res


def getInput(low: int, high: int):
    t = int(input())
    while t <= low or t > high:
        print("输入错误 请再输入一次")
        t = int(input())
    return t


class Node:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class Util:

    def __init__(self):
        self.course_list = []
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

        self.reserveName = ['课程作业', '教学日历', '教学大纲']

        self.data = data.cdata
        self.session = requests.Session()
        self.session.headers.update(self.my_header)

    def getReminderContent(self):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_reminder_url)
        if cont.status_code == 200:
            ptoFile("nowReminder.html", cont.text)

    def getCourseList(self):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_mycourse_url)

        soup = BeautifulSoup(cont.text, "html.parser")
        res = soup.find_all("a")
        for item in res:
            attr = item.attrs
            if attr.get("class") is None:
                self.course_list.append(Node(item.string.strip(), item["href"].split("=")[-1]))
        return self.course_list

    def getCourseDetail(self, courseID):
        cont = self.session.get(self.kcpt_host_url + self.kcpt_lesson_base_url + courseID)
        txxt = self.session.post(self.kcpt_host_url + self.dwr_url, data=init_payload_req(courseID))
        self.session.cookies.update({"DWRSESSIONID": txxt.text.split('"')[-2]})

        detailHref = []

        soup = BeautifulSoup(cont.text, "html.parser")

        course_title = soup.find(class_="course_title").string.strip()
        print("现在所在的课程位置为: " + course_title)

        tmenu = soup.find_all("a", target="mainFrame")
        for item in tmenu:
            if item.string is None:
                cname = item.find('span').string.strip()
            else:
                cname = item.string.strip()
            if cname in self.reserveName and len(detailHref) < 3:
                detailHref.append(Node(cname, item['href']))

        # for item in detailHref:
        #     print(item.name + ' ' + item.data)

        i = 1
        print('请选择获取的内容')
        for item in detailHref:
            print(str(i) + ' ' + item.name)
            i += 1
        t = getInput(0, len(detailHref))

        selectedContent = self.session.get(cont.url[:cont.url.rfind('/')] + '/' + detailHref[t - 1].data)
        if selectedContent.status_code != 200:
            return False

        soup = BeautifulSoup(selectedContent.text, 'html.parser')
        ptoFile("kcpt.html", selectedContent.text)
        if t == 1:
            ptoFile("jxdg.html", soup.find('input')['value'], selectedContent.apparent_encoding)
        elif t == 2:
            content = soup.find('input')['value']
            # content = content[content.find('</p>') + 4:]
            ptoFile("jxrl.html", content, selectedContent.apparent_encoding)
        elif t == 3:
            # 还剩解析课程作业没有写 麻了
            pass
        else:
            print('orz')
            exit(0)

    def login(self):
        response = self.session.post(url=self.login_url, data=self.data)
        if json.loads(response.text[1:-1])['result'] == 2:
            return False

        self.session.cookies.update(response.cookies)
        response = self.session.get(url=appendURL(json.loads(response.text[1:-1])))

        with open("output/welcome.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # 以上登录了jwc个人中心

        nxturl = self.session.get(self.jump_jwc_url, allow_redirects=False).headers["Location"]
        response = self.session.get(nxturl, allow_redirects=False)
        self.session.cookies.clear()
        self.session.cookies.update(response.cookies)
        return True

    def printCourseList(self):
        i = 1
        for item in self.course_list:
            print(str(i) + ': ' + item.name)
            i += 1
