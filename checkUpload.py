# encoding=utf8
import requests
import json
import time
import datetime
import pytz
import re
import sys
import argparse
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import io
import os
from bs4 import BeautifulSoup
import PIL
import pytesseract
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"


def sendMail(sub, body):
    smtp_server = 'smtp.qq.com'
    from_mail = 'michael3400@foxmail.com'
    mail_pass = 'qfwksoqbkhzqbege'
    to_mail = '791813400@qq.com'
    from_name = 'sad'
    subject = sub

    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = Header("小橙子", 'utf-8')
    msg['To'] = Header(','.join(to_mail))
    # msg = '\n'.join(mail)
    try:
        s = smtplib.SMTP_SSL('smtp.qq.com', 465)
        s.login(from_mail, mail_pass)
        s.sendmail(from_mail, to_mail, msg.as_string())
        s.quit()
    except smtplib.SMTPException as e:
        print("Error: " + e)


class Report(object):
    def __init__(self, stuid, password, data_path, emer_person, relation, emer_phone):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path
        self.emer_person = emer_person
        self.relation = relation
        self.emer_phone = emer_phone

    def report(self):
        loginsuccess = False
        retrycount = 5
        while (not loginsuccess) and retrycount:
            session = self.login()
            cookies = session.cookies
            getform = session.get("https://weixine.ustc.edu.cn/2020")
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retrying...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False

        # 自动出校报备
        tips = ["行程卡", "安康码", "核酸报告"]
        flag = [False, False, False, False]
        data = session.get("https://weixine.ustc.edu.cn/2020/upload/xcm").text
        soup = BeautifulSoup(data, 'html.parser')
        pattern = re.compile("202[0-9]-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        token = soup.find_all(
            "p", {"style": "clear: both"})
        # flag = False
        print(token)
        for i in range(3):
            if pattern.search(token[i].text) is not None:
                date = pattern.search(token[i].text).group()
                print("Latest Update: " + date)
                date = date + " +0800"
                reporttime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
                print("Updatetime : " + format(reporttime))
                timenow = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                print("Nowtime : " + format(timenow))
                delta = timenow - reporttime
                delta_nega = reporttime - timenow
                print("Delta is ")
                print(delta)
                print("Delta_Negative is ")
                print(delta_nega)
                if delta.days < 6 or delta_nega.days < 6:
                    flag[i] = True
                    print("这周" + tips[i] + "上传过了")
                else:
                    print("您本周" + tips[i] + "没上传")
        if flag[0] == True and flag[1] == True and flag[2] == True:
            flag[3] = True
            print("您本周已全部上传!")
        else:
            print("您本周有未上传项目!")
        return flag[3]

    def login(self):
        retries = Retry(total=5,
                        backoff_factor=0.5,
                        status_forcelist=[500, 502, 503, 504])
        s = requests.Session()
        s.mount("https://", HTTPAdapter(max_retries=retries))
        s.headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        r = s.get(url, params={"service": CAS_RETURN_URL})
        x = re.search(r"""<input.*?name="CAS_LT".*?>""", r.text).group(0)
        cas_lt = re.search(r'value="(LT-\w*)"', x).group(1)

        CAS_CAPTCHA_URL = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
        r = s.get(CAS_CAPTCHA_URL)
        img = PIL.Image.open(io.BytesIO(r.content))
        pix = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = pix[i, j]
                if g >= 40 and r < 80:
                    pix[i, j] = (0, 0, 0)
                else:
                    pix[i, j] = (255, 255, 255)
        lt_code = pytesseract.image_to_string(img).strip()

        data = {
            'model': 'uplogin.jsp',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '1',
            'button': '',
            'CAS_LT': cas_lt,
            'LT': lt_code
        }
        s.post(url, data=data)

        print("lt-code is {}, login...".format(lt_code))
        return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    parser.add_argument('emer_person', help='emergency person', type=str)
    parser.add_argument('relation', help='relationship between you and he/she', type=str)
    parser.add_argument('emer_phone', help='phone number', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path,
                         emer_person=args.emer_person, relation=args.relation, emer_phone=args.emer_phone)
    ret = autorepoter.report()
    if ret != False:
        # sendMail("小橙子的健康上传提醒", "小橙子提醒您本周项目都传好啦！")
        print("传完了")
    else:
        sendMail("小橙子的健康上传提醒", "小橙子提醒您本周有项目没上传，请及时上传~")
        print("有东西没传")
