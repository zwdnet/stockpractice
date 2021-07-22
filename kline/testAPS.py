# coding:utf-8
# 1000元实盘练习程序
# 测试APScheduler定时任务


from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


def my_clock():
    print("hello, now is ", datetime.now())


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Chongqing")
    scheduler.add_job(my_clock, "cron", day_of_week = "mon-fri", hour = "9-15", second = "*/5")
    scheduler.start()
    