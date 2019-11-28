#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'杀掉进程'

__author__ = 'zhou'

import os,signal
def kill_video():
    out=os.popen("ps aux").read()
    for line in out.splitlines():
        #print(line)
        if 'server.py' in line:
            pid = int(line.split()[1])
            os.kill(pid,signal.SIGKILL)

def kill(pid):
    try:
        a = os.kill(pid, signal.SIGKILL)
        print('已杀死pid为%s的进程,　返回值是:%s' % (pid, a))

    except OSError:
        print('没有如此进程!!!')