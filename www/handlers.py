#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
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
from orm import execute
from motor import zheng,fan,stopC
from picamera import PiCamera
import time,threading
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pingUtil import getHome
from predict import get_winstate
from killps import kill_video
__author__ = 'zhou'

' url handlers '





import RPi.GPIO as GPIO
import Adafruit_DHT
# 输入邮件地址, 口令和POP3服务器地址:
email = '**' #你的email 的地址
from_addr = '**' #你的email 的地址
password = '**' #你的email 的密码
to_addr = '***' #email 的目的地址
smtp_server = '**' #smtp服务器 的地址
pop3_server = '**' #pop3服务器 的地址
chuang_state=None
deng_state=None
def init_deng_state():
    '''
        灯的初始状态
    '''
    global deng_state
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    if GPIO.input(12)==1:
        deng_state='open'
    else:
        deng_state='close'
def init_chuang_state():
    '''
        窗帘的初始状态，是用tensorflow来判断的，这个地点也是此项目的亮点
    '''
    global chuang_state
    img_url=take_camera()
    win_state=get_winstate(img_url)
    if win_state =='chuang_close':
        chuang_state='close'
    if win_state =='chuang_open':
        chuang_state='open'
    print('+++++++++++window_state++++++++++++++'+chuang_state)
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
    return  addr,value
async def sch_job():
    '''
    定时查询邮件的任务，参考的是廖雪峰的网站
    '''
    server = poplib.POP3(pop3_server)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    #print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    #print(mails)
    
    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    resp, lines, octets = server.retr(index)
    
    # lines存储了邮件的原始文本的每一行,
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)
    fro,sub=print_info(msg)
    #print(sub)
    if "1053604549@qq.com"==fro:
        if "枕边头套"==sub:
            server.dele(index)
        if "关灯"==sub:
            await api_register_user()
            server.dele(index)
        if "开灯"==sub:
            await api_register_users()
            server.dele(index)
        if "开窗"==sub:
            chuangkan()
            file_url=take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "关窗"==sub:
            chuangguan()
            file_url=take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "房间"==sub:
            file_url=take_camera()
            server.dele(index)
            sendEmailFile(file_url)
        if "关窗开灯"==sub:
            chuangguan()
            await api_register_users()
            file_url=take_camera()
            server.dele(index)
            sendEmailFile(file_url)
    # 关闭连接:
    server.quit()
@get('/api/run')
async def run():
    '''
        记录跑步的时间，这是我的个人生活
    '''
    await execute('insert into run_rec(state)values(?)',('run'))
    return "success"
@get('/api/camera')
async def camera():
    '''
        拍照，并在浏览器上显示
    '''
    file_url=take_camera()
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
    r0 = requests.get("http://192.168.1.3:5000/shutdown")
    return "success"
@get('/api/kanchuang')
async def kanchuang():
    '''
     控制窗户
    '''
    if chuang_state=='close':
        t = threading.Thread(target=chuangkan, name='LoopThread0')
        t.start()
        t.join
    if chuang_state=='open':
        t = threading.Thread(target=chuangguan, name='LoopThread0')
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
@get('/api/shutDown')
async def api_register_user():
    '''
        关灯
    '''
    GPIO.output(12, GPIO.LOW)
    await execute('insert into light(state)values(?)', ('close'))
    global deng_state
    deng_state='close'
    return "success"
@get('/api/open')
async def api_register_users():
    '''
        开灯
    '''
    GPIO.output(12, GPIO.HIGH)
    await execute('insert into light(state)values(?)', ('open'))
    global deng_state
    deng_state='open'
    return "success"
@get('/api/deng')
async def deng_caozuo():
    global deng_state
    if deng_state=='close':
        GPIO.output(12, GPIO.HIGH)
        await execute('insert into light(state)values(?)', ('open'))
        deng_state='open'
    else:
        GPIO.output(12, GPIO.LOW)
        await execute('insert into light(state)values(?)', ('close'))
        deng_state='close'
    return "success"
@get('/api/showTem')
async def api_register_userss():
    '''
    爬取天气
    '''
    out_temp,out_hum=getWeather()
    hum_index = out_hum.index("%")
    out_hum=out_hum[3:hum_index]
    sensor=Adafruit_DHT.DHT11
    gpio=17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    await execute('insert into temp_hum(temp,humidity,out_tem,out_hum)values(?,?,?,?)', (temperature, humidity,out_temp,out_hum))
    return {
        'Temp': temperature,
        'Humidity': humidity,
        'outTemp': out_temp,
        'outHumidity': out_hum
        }
@get('/api/getTem')
async def getTem():
    '''
    获取室内温度与湿度
    '''
    sensor=Adafruit_DHT.DHT11
    gpio=17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    await execute('insert into temp_hum(temp,humidity)values(?,?)', (temperature, humidity))
    return {
        '温度': temperature,
        '湿度': humidity
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
def getWeather():
    htmlData = request.urlopen("https://tianqi.moji.com/weather/china/shandong/huaiyin-district").read().decode('utf-8')
    soup = BeautifulSoup(htmlData, 'html.parser')
    weather = soup.find('div',attrs={'class':"wea_weather clearfix"})
    temp1 = weather.find('em').get_text()#当前温度
    temp2 = weather.find('b').get_text()
    AQI = soup.select(".wea_alert.clearfix > ul > li > a > em")[0].get_text()
    H = soup.select(".wea_about.clearfix > span")[0].get_text()#湿度
    S = soup.select(".wea_about.clearfix > em")[0].get_text()#风速
    return temp1,H
def start_sch():
    sched = AsyncIOScheduler()
    sched.add_job(sch_job, 'cron', hour='8-20', minute="*/10",id='my_job_id')
    sched.add_job(sendEmail,'cron',hour='22', minute="30",args=["枕边头套"],id='my_job_id2')
    sched.add_job(getHome_job,'cron',day_of_week='mon-fri',hour='17-19', minute="*/1",id='my_job_id3')
    sched.start()    
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
    time.sleep(9.5)
    stopC()
    global chuang_state
    chuang_state='open'
def chuangguan():
    fan()
    time.sleep(9)
    stopC()
    global chuang_state
    chuang_state='close'
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
    file_url=""
    with PiCamera() as camera:
        time.sleep(0.1)
        camera.resolution = (320, 240)
        file_url = "/home/pi/img/"+str(int(time.time()))+".jpg"
        camera.capture(file_url)
    return file_url
async def getHome_job():
    if chuang_state=="open":
        if "yes" == getHome(): 
            chuangguan()
            await api_register_users()
def videoCmd():
    val = os.system("python3.7 /home/pi/videoTest/pistreaming-master/server.py")