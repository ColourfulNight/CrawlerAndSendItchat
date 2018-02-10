# coding=utf-8
# python version：2.7
# author:sharpdeep

#注意：使用之前必须pip install lxml itchat bs4 pytz APScheduler
import urllib
import urllib2
import logging

import itchat
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as BS
from pytz import utc

# 利用微信接口给好友发送消息
# uname：好友的备注名
# message：要发送的消息内容(必须是字符串)
def sendItchatMsg(uname, message):
    itchat.auto_login(enableCmdQR=True, hotReload=True)
    # 想给谁发信息，先查找到这个朋友,name后填微信备注即可,deepin测试成功
    users = itchat.search_friends(name=uname)
    # 获取好友全部信息,返回一个列表,列表内是一个字典
    # 获取`UserName`,用于发送消息
    userName = users[0]['UserName']
    itchat.send(message, toUserName=userName)
    # print("Success")


# 功能：爬取百度搜索结果页面(正文标题、发布时间和内容快照)
# keyword：百度想要搜索的关键字
def baiduSearchCrawler(keyword):
    baseUrl = 'http://www.baidu.com/s'
    page = 1  # 第几页
    word = keyword  # 搜索关键词

    data = {'wd': word, 'pn': str(page - 1) + '0', 'tn': 'baidurt', 'ie': 'utf-8', 'bsst': '1'}
    data = urllib.urlencode(data)
    url = baseUrl + '?' + data
    count = 0
    contentList = []
    response = 0

    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
    except urllib2.HttpError, e:
        print e.code
        exit(0)
    except urllib2.URLError, e:
        print e.reason
        exit(0)

    html = response.read()
    soup = BS(html, "lxml")
    td = soup.find_all(class_='f')

    for t in td:
        count += 1
        splitLine = "_____________" + "标题" + str(count) + ":" + "____________"
        contentList.append(splitLine)
        contentList.append(str.strip(t.h3.a.get_text().encode("utf-8")))
        contentList.append(str.strip(t.h3.a['href'].encode("utf-8")))

        font_str = t.find_all('font', attrs={'size': '-1'})[0].get_text()
        start = 0  # 起始
        realtime = t.find_all('div', attrs={'class': 'realtime'})
        if realtime:
            realtime_str = realtime[0].get_text()
            start = len(realtime_str)
            contentList.append(str.strip(realtime_str.encode("utf-8")))
        end = font_str.find('...')
        contentList.append(str.strip(font_str[start:end + 3].encode("utf-8")) + '\n')
    return contentList


# 每隔2天的9:30定时执行任务，这里是发送微信
def scheduledTask(myJob):
    # myJob()
    sched = BlockingScheduler(timezone=utc)
    #sched.daemonic = True
    sched.add_job(myJob, 'interval', days=2, hours=9, minutes=30, seconds=0)
    sched.start()


def myJob():
    strList = "\n".join(baiduSearchCrawler("淘宝网"))
    sendItchatMsg("Mary".decode("utf-8"), strList.decode("utf-8"))


if __name__ == '__main__':
    logging.basicConfig()
    daemon = True
    scheduledTask(myJob)
