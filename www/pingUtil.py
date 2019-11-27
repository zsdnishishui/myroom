import subprocess
import re
import os
def getHome():
    return1 = os.system('ping -c1 192.168.1.19')
    if return1:
        return "no"
    else:
        return "yes"