# myroom

一、项目介绍

   1.用树莓派控制卧室中的设备的项目。在本项目中，我主要控制的有窗帘、电灯、电脑、室内温湿度、摄像头。
   2.控制的方式有页面按键控制、siri语音控制、邮件远程控制。

二、用到的一些技术
    
   python + 爬虫 + 异步io框架 + 定时框架 Apscheduler + tensorflow + mysql + 前端的基础知识 + linux的基本操作

三、主要技术详解
    
   1.python 
   
   (1) 廖雪峰 的官方网站 就足够了。[参考](https://www.liaoxuefeng.com/wiki/1016959663602400)
      
   2.定时框架 Apscheduler
   
   (1) [参考](http://www.sohu.com/a/322257169_120104204)
   
   (2) [参考](https://blog.csdn.net/blueheart20/article/details/70219490)
   
   3.tensorflow
    
   (1) 电脑安装和树莓派安装只看官网就够了 [参考](https://www.tensorflow.org/install)
    
   (2) 训练模型，因为我只需要判断窗帘是关闭还是打开的状态，所以我训练的是二分类模型 [参考](https://tf.wiki/zh/basic/tools.html)
   
   (3) 训练好模型之后，把模型复制到树莓派上，用摄像头拍照并识别窗帘的状态
   
   4.树莓派
   
   (1)远程 用的是putty
   
   (2)GPIO  [参考](https://lingshunlab.com/raspberry-pi-description.html)
   
   (3)其它电子配件 
   
   Ⅰ温湿度传感器 [参考](http://shumeipai.nxez.com/2018/05/16/dht11-temperature-and-humidity-sensor-raspberry-pi.html)
   
   Ⅱ电机控制器 L298N电机驱动板 [参考](https://blog.csdn.net/weixin_43073852/article/details/83085306)
   
   Ⅲ 继电器 [参考](https://blog.csdn.net/iteye_9422/article/details/82650149)
   
   Ⅳ 摄像头 
   
   (4)摄像头 
   
   Ⅰ照片 [参考](https://blog.csdn.net/u012005313/article/details/70244747)
   
   Ⅱ视频 [参考](https://github.com/waveform80/pistreaming)
   
   5.siri语音识别
   
   手机安装快捷指令app，用语音发送树莓派控制指令或用siri读出返回的结果

![image](https://github.com/zsdnishishui/uploadImg/blob/master/chuang.png)
![image](https://github.com/zsdnishishui/uploadImg/blob/master/zongcheng.png)
![image](https://github.com/zsdnishishui/uploadImg/blob/master/shouji.png)
          
