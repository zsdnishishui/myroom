#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'通过ping我的手机的ip来判断我是不是到家了'

__author__ = 'zhou'

import subprocess
import re
import os
def getHome():
    return1 = os.system('ping 192.168.1.6 -c1')
    if return1:
        return "no"
    else:
        return "yes"