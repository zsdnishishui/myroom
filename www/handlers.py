#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from aiohttp import web
from multiprocessing import Process
from email import encoders
from email.header import Header, decode_header
from email.mime.text import MIMEText
from email.parser import Parser
from email.utils import parseaddr, formataddr
import poplib
import re, time, json, logging, hashlib, base64, asyncio, os
import smtplib
from urllib import request
import time
import aiomysql
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import requests
from coroweb import get, post
from orm import execute, select
from motor import zheng, fan, stopC, zheng2, fan2, stop2
from picamera import PiCamera
import time, threading
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pingUtil import getHome
from predict import get_winstate
from killps import kill_video, kill_natapp
from models import User
import pytz

__author__ = 'zhou'

' url handlers '

import RPi.GPIO as GPIO
import Adafruit_DHT

import sys
from sys import path
path.append('/home/pi')
import config_default
# 输入邮件地址, 口令和POP3服务器地址:
email_config = config_default.config['email']

email = email_config['email'] #你的email 的地址
from_addr = email_config['from_addr'] #你的email 的地址
password = email_config['password'] #你的email 的密码
to_addr = email_config['to_addr'] #email 的目的地址
smtp_server = email_config['smtp_server'] #smtp服务器 的地址
pop3_server = email_config['pop3_server'] #pop3服务器 的地址
chuang_state = None
deng_state = None
sched = None
COOKIE_NAME = 'awesession'
_COOKIE_KEY = "configs.session.secret"


# 计算加密cookie:
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user['id'], user['passwd'], expires, _COOKIE_KEY)
    L = [user['id'], expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    user = None
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        logging.info("-----------------" + uid)
        if uid == '1':
            user = {'id': '1', 'passwd': '123456'}
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user['passwd'], expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user['passwd'] = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


def init_deng_state():
    '''
        灯的初始状态
    '''
    global deng_state
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    if GPIO.input(12) == 1:
        deng_state = 'open'
    else:
        deng_state = 'close'


def init_chuang_state():
    '''
        窗帘的初始状态，是用tensorflow来判断的，这个地点也是此项目的亮点
    '''
    global chuang_state
    img_url = take_camera()
    win_state = get_winstate(img_url)
    if win_state == 'chuang_close':
        chuang_state = 'close'
    if win_state == 'chuang_open':
        chuang_state = 'open'
    print('+++++++++++window_state++++++++++++++' + chuang_state)


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def print_info(msg, indent=0):
    value = decode_str(msg.get('Subject', ''))
    hdr, addr = parseaddr(msg.get('From', ''))
    return addr, value


@get('/api/schJob')
async def sch_job():
    '''
    定时查询邮件的任务，参考的是廖雪峰的网站
    '''
    server = poplib.POP3(pop3_server)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    # print(mails)

    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    resp, lines, octets = server.retr(index)

    # lines存储了邮件的原始文本的每一行,
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)
    fro, sub = print_info(msg)
    # print(sub)
    if "1053604549@qq.com" == fro:
        if "枕边头套" == sub:
            server.dele(index)
        if "关灯" == sub:
            await api_register_user()
            server.dele(index)
        if "开灯" == sub:
            await api_register_users()
            server.dele(index)
        if "开窗" == sub:
            chuangkan()
            file_url = take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "关窗" == sub:
            chuangguan()
            file_url = take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "房间" == sub:
            file_url = take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "关窗开灯" == sub:
            chuangguan()
            await api_register_users()
            file_url = take_camera()
            server.dele(index)
            sendEmailFile(file_url)
    # 关闭连接:
    server.quit()


@get('/api/shutdownlinux')
def shutdownlinux():
    os.system("sudo shutdown -h now")


@get('/api/test')
def test():
    logging.info("test---test")


@get('/api/run')
async def run():
    '''
        记录跑步的时间，这是我的个人生活
    '''
    await execute('insert into run_rec(state)values(?)', ('run'))
    return "success"


@post('/api/login')
def login(*, username, passwd):
    logging.info(username + '-------------------------------' + passwd)
    if username == '001' and passwd == '123456':
        user = {'username': '001', 'passwd': '123456', 'id': '1', 'state': 'success'}
        r = web.Response()
        r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        user['passwd'] = '******'
        r.content_type = 'application/json'
        r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
        return r
    return "error"


@get('/signin')
def signin():
    return "login"


@get('/api/camera')
async def camera():
    '''
        拍照，并在浏览器上显示
    '''
    file_url = take_camera()
    import base64
    img_stream = ''
    with open(file_url, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream)

    return img_stream


@get('/api/shutdown')
async def shutdown():
    '''
        用requests模块，发送关闭计算机的指令
    '''
    r0 = requests.get("http://W4HUDGN5ZEIGEHX:5000/shutdown")
    return "success"


@get('/api/kanchuang')
async def kanchuang():
    '''
     控制窗户
    '''
    t = threading.Thread(target=chuangkan, name='LoopThread0')
    t.start()
    t.join
    return "success"


@get('/api/guanchuang')
async def guanchuang():
    t = threading.Thread(target=chuangguan, name='LoopThread1')
    t.start()
    t.join
    return "success"


@get('/api/stop')
async def stop():
    stopC()
    return "success"


@get('/api/stopKong')
async def stopKong():
    '''t = threading.Thread(target=stop2, name='LoopThread0')
    t.start()
    t.join'''
    stop2();
    return "success"


@get('/api/openKong')
async def openKong():
    zheng2()
    return "success"


@get('/api/closeKong')
async def closeKong():
    fan2()
    return "success"


@get('/api/kongKong')
async def kongKong():
    t = threading.Thread(target=kongtiao, name='kongtiao')
    t.start()
    t.join

    return "success"


@get('/api/shutDown')
async def api_register_user():
    '''
        关灯
    '''
    GPIO.output(12, GPIO.LOW)
    await execute('insert into light(state)values(?)', ('close'))
    global deng_state
    deng_state = 'close'
    return "success"


@get('/api/open')
async def api_register_users():
    '''
        开灯
    '''
    GPIO.output(12, GPIO.HIGH)
    await execute('insert into light(state)values(?)', ('open'))
    global deng_state
    deng_state = 'open'
    return "success"


@get('/api/deng')
async def deng_caozuo():
    global deng_state
    if deng_state == 'close':
        GPIO.output(12, GPIO.HIGH)
        await execute('insert into light(state)values(?)', ('open'))
        deng_state = 'open'
    else:
        GPIO.output(12, GPIO.LOW)
        await execute('insert into light(state)values(?)', ('close'))
        deng_state = 'close'
    return "success"


@get('/api/taideng')
async def taideng():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, GPIO.HIGH)
    time.sleep(4)
    GPIO.output(16, GPIO.LOW)
    return "success"


@get('/api/showTem')
async def api_register_userss():
    res = await select('select temp,humidity,out_tem,out_hum from temp_hum order by add_time desc limit 1', ());
    return json.dumps(res[0])


@get('/api/getTem')
def getTem():
    '''
    获取室内温度与湿度
    '''
    sensor = Adafruit_DHT.DHT11
    gpio = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    return {
        '温度': int(temperature),
        '湿度': int(humidity)
    }


@get('/api/openVideo')
async def openVideo():
    '''
    打开摄像头的进程，这个进程启动的是https://github.com/waveform80/pistreaming这个项目，
    用进程来启动而不是用线程来启动这个项目，是因为进程能够，用代码来关闭
    '''
    p = Process(target=videoCmd)
    p.start()
    return "success"


@get('/api/stopVideo')
async def stopVideo():
    '''
    杀掉摄像的进程
    '''
    kill_video()
    return "success"


@get('/api/stopNatapp')
async def stopNatapp():
    newRoomUrl()
    return "success"


@get('/api/pauseSch')
async def pauseSch():
    '''
    暂停任务
    '''
    pause_sch()
    return "success"


def getWeather():
    htmlData = request.urlopen("https://tianqi.moji.com/weather/china/shandong/lixia-district").read().decode('utf-8')
    soup = BeautifulSoup(htmlData, 'html.parser')
    weather = soup.find('div', attrs={'class': "wea_weather clearfix"})
    temp1 = weather.find('em').get_text()  # 当前温度
    temp2 = weather.find('b').get_text()
    AQI = soup.select(".wea_alert.clearfix > ul > li > a > em")[0].get_text()
    H = soup.select(".wea_about.clearfix > span")[0].get_text()  # 湿度
    S = soup.select(".wea_about.clearfix > em")[0].get_text()  # 风速
    return temp1, H


def start_sch():
    global sched
    sched = AsyncIOScheduler()
    #    sched.add_job(sch_job, 'cron', hour='8-20', minute="*/10",id='my_job_id')
    #    sched.add_job(sendEmail,'cron',hour='22', minute="30",args=["枕边头套"],id='my_job_id2')
    sched.add_job(newRoomUrl, 'cron', hour='9', minute="30", timezone=pytz.utc, id='my_job_id6')
    sched.add_job(tem_job, 'cron', minute="*/30", id='my_job_id5')
    sched.add_job(resume_job, 'cron', hour='9', minute="30", timezone=pytz.utc, id='my_job_id4')
    sched.add_job(getHome_job, 'cron', day_of_week='mon-fri', hour='10-12', minute="*/1", timezone=pytz.utc,
                  id='my_job_id3')
    sched.add_job(delMyUrl, 'cron', hour='15', timezone=pytz.utc, id='my_job_id7')
    sched.add_job(cpufengshan, 'cron', minute="*/10", id='my_job_id8')
    sched.start()


def cpufengshan():
    file = open("/sys/class/thermal/thermal_zone0/temp")
    # 读取结果，并转换为浮点数
    temp = float(file.read()) / 1000
    logging.info("cputemp++++++++" + str(temp))
    if temp > 60:
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.HIGH)
    elif temp < 46:
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.LOW)


def delMyUrl():
    server = poplib.POP3(pop3_server)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    resp, mails, octets = server.list()
    index = len(mails)
    resp, lines, octets = server.retr(index)
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    msg = Parser().parsestr(msg_content)
    fro, sub = print_info(msg)
    if "1053604549@qq.com" == fro and sub.startswith("http://"):
        server.dele(index)
    # 关闭连接:
    server.quit()


def pause_sch():
    sched.get_job('my_job_id3').pause()


def resume_job():
    sched.get_job('my_job_id3').resume()


async def tem_job():
    '''
    爬取天气
    '''
    out_temp, out_hum = getWeather()
    hum_index = out_hum.index("%")
    out_hum = out_hum[3:hum_index]
    sensor = Adafruit_DHT.DHT11
    gpio = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    await execute('insert into temp_hum(temp,humidity,out_tem,out_hum)values(?,?,?,?)',
                  (temperature, humidity, out_temp, out_hum))


def sendEmail(suc):
    msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
    msg['From'] = _format_addr('你是谁  <%s>' % from_addr)
    msg['To'] = _format_addr('你是谁  <%s>' % to_addr)
    msg['Subject'] = Header(suc, 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(0)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def chuangkan():
    zheng()
    time.sleep(16)
    stopC()

def chuangguan():
    fan()
    time.sleep(12)
    stopC()


def sendEmailFile(url):
    msg = MIMEMultipart()
    msg['From'] = _format_addr('你是谁  <%s>' % from_addr)
    msg['To'] = _format_addr('你是谁  <%s>' % to_addr)
    msg['Subject'] = Header('myroom', 'utf-8').encode()
    msg.attach(MIMEText('<html><body><h1>Hello</h1>' +
                        '<p><img src="cid:0"></p>' +
                        '</body></html>', 'html', 'utf-8'))
    # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
    with open(url, 'rb') as f:
        # 设置附件的MIME和文件名，这里是png类型:
        mime = MIMEBase('image', 'jpg', filename='test.jpg')
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename='test.jpg')
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        msg.attach(mime)
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(0)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def take_camera():
    file_url = ""
    with PiCamera() as camera:
        time.sleep(0.5)
        camera.resolution = (320, 240)
        file_url = "/home/pi/img/" + str(int(time.time())) + ".jpg"
        camera.capture(file_url)
    return file_url


async def getHome_job():
    if deng_state == "close":
        if "yes" == getHome():
            await api_register_users()


def videoCmd():
    val = os.system("python3.7 /home/pi/web/www/server.py")


def kongtiao():
    zheng2()
    time.sleep(1)
    stop2()
    time.sleep(0.5)
    fan2()
    time.sleep(1)
    stop2()


def newRoomUrl():
    url = ""
    index_url = ""
    file_data = ""
    file_url = "/home/pi/natapp/myvideo/"
    html_url = "/home/pi/natapp/"
    file_html = '/home/pi/web/www/static/index.html'
    kill_natapp()
    if (os.path.exists(html_url + 'nohup.out')):
        os.remove(html_url + 'nohup.out')
    os.system("nohup " + html_url + "natapp > " + html_url + "nohup.out &")
    time.sleep(1)
    if (os.path.exists(file_url + 'nohup.out')):
        os.remove(file_url + 'nohup.out')
    os.system("nohup " + file_url + "natapp > " + file_url + "nohup.out &")
    time.sleep(1)
    with open(html_url + 'nohup.out', 'r') as f:
        text_lines = f.readlines()
        for line in text_lines:
            if line.find("established at") > 0:
                index_url = line.split("established at")[1].strip()
    with open(file_url + 'nohup.out', 'r') as f:
        text_lines = f.readlines()
        for line in text_lines:
            if line.find("established at") > 0:
                url = line.split("established at")[1].strip()
    logging.info("+++++++" + index_url)
    with open(file_html, 'r', encoding="utf-8") as f:
        text_lines = f.readlines()
        for line in text_lines:
            if line.find("//update") > 0:
                line = "var videoUrl ='" + url + "';//update\n"
                logging.info(line)
            file_data += line
    with open(file_html, "w", encoding="utf-8") as f:
        f.write(file_data)
    sendEmail(index_url)