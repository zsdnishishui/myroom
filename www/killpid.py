import os
import sys
import string 
import psutil
import signal
#print os.getpid()
def getAllPid():
    pid_dict={}
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        pid_dict[pid]=p.name()
        print("pid-%d,pname-%s" %(pid,p.name()))
    return pid_dict

def kill(pid):
    try:
        kill_pid = os.kill(pid, signal.SIGABRT)
        print('已杀死pid为%s的进程,　返回值是:%s' % (pid, kill_pid))
    except Exception as e:
        print('没有如此进程!!!')
 
if __name__ == '__main__':
  dic=getAllPid()
  for t in dic.keys():
      if dic[t]=="360se.exe":
          kill(t)