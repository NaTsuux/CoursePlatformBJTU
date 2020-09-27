from util import Util
from util import getInput

if __name__ == "__main__":
    try:
        core = Util()
        print("欢迎使用QAQ菜逼课程平台自助系统 请输入账号密码(或许不用orz)")

        while not core.login():
            print("密码错了 这里还需要安排一下重新输入密码")
            core.login()

        core.getCourseList()
        core.printCourseList()

        t = getInput(0, len(core.course_list))

        core.getCourseDetail(core.course_list[t - 1].data)
    except KeyboardInterrupt:
        print('已断开qaq')
        exit(0)
