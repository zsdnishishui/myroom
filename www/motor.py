# -*- coding: utf-8 -*-                 #通过声明可以在程序中书写中文
import RPi.GPIO as GPIO                 #引入RPi.GPIO库函数命名为GPIO
import time   

# BOARD编号方式，基于插座引脚编号
GPIO.setmode(GPIO.BOARD)                #将GPIO编程方式设置为BOARD模式
GPIO.setwarnings(False)
#接口定义
INT1 = 29                               #将L298 INT1口连接到树莓派Pin11
INT2 = 31                           #将L298 INT2口连接到树莓派Pin12
#INT3 = 33                              #将L298 INT3口连接到树莓派Pin13
#INT4 = 35                              #将L298 INT4口连接到树莓派Pin15
ENA = 36
#ENB = 37
#输出模式
GPIO.setup(INT1,GPIO.OUT)
GPIO.setup(INT2,GPIO.OUT)
#GPIO.setup(INT3,GPIO.OUT)
#GPIO.setup(INT4,GPIO.OUT)
GPIO.setup(ENA,GPIO.OUT)
#GPIO.setup(ENB,GPIO.OUT)
freq = 60
speed = 100
#pwm = GPIO.PWM(ENA, freq)           # 设置向ENA输入PWM脉冲信号，频率为freq并创建PWM对象
#pwm.start(speed)
def zheng(): 
    GPIO.output(ENA,GPIO.HIGH)
    GPIO.output(INT1,GPIO.HIGH)
    GPIO.output(INT2,GPIO.LOW)
    #pwm.ChangeDutyCycle(speed)
    #while True:
        #pwm.ChangeDutyCycle(speed)
    
def stopC(): 
    GPIO.output(ENA,GPIO.LOW)
def fan(): 
    GPIO.output(ENA,GPIO.HIGH)
    GPIO.output(INT1,GPIO.LOW)
    GPIO.output(INT2,GPIO.HIGH)
#zheng()
#stop()
#fan()