# coding:utf-8
# 1000元实盘练习程序''
# 测试定时执行某函


import datetime as dt
import time


def hello():
        print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
      
# 每隔s秒执行一次任务
def run(s):
    while True:
        hello()
        time.sleep(s)


if __name__ == "__main__":
    run(1)
    