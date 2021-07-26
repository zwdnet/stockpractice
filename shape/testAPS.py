# coding:utf-8
# 1000元实盘练习程序
# 测试APScheduler定时任务


from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


def taskA():
    print("TaskA, now is ", datetime.now())
    
    
def taskB():
    print("TaskB, now is ", datetime.now())


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Chongqing")
    scheduler.add_job(taskA, "cron", day_of_week = "mon-fri", second = "*/5")
    scheduler.add_job(taskB, "cron", day_of_week = "mon-fri", second = "*/10")
    scheduler.start()
    