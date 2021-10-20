# coding:utf-8
# 1000元实盘练习程序
# 服务器端监控程序


import numpy as np
import pandas as pd
import akshare as ak
import efinance as ef
import run
import tools
import talib
import os
import datetime
import time
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil.relativedelta import relativedelta


# 制作报告邮件内容
@run.change_dir
def makeContent(date, name, code):
    # print("测试", code)
    filename = "./data2/" + code[2:] + ".csv"
    # print(filename)
    if os.path.exists(filename):
        data = pd.read_csv(filename)
        # print(data.info(), data.tail())
        lastestdata = ef.stock.get_latest_stock_info([code[2:]])
        price = lastestdata.最新价.values[0]
        # print(code, date, name, price)
        date = date.strftime('%Y-%m-%d %H:%M')
        title = "报告:" + code[2:] + "出现" + name + "的情况!"
        content = "股票" + code[2:] + "在" + date + "出现" + name + "的情况。股票现价" + str(price)
        return (title, content)
    else:
        return ("", "")
        
    
# 进行一次止损价检测
def taskA(buyPrice, codes):
    filename = "./HighPrice.txt"
    highPrice = 0
    date = datetime.datetime.now()
    for code in codes:
        lastestdata = ef.stock.get_latest_quote([code[2:]])
        lastPrice = lastestdata.最新价.values[0]
        # 5%止损
        if lastPrice <= buyPrice*0.95 and lastPrice != 0.0:
            name = "到达止损价"
            print(lastPrice, buyPrice*0.95)
            title, content = makeContent(date, name, code)
            if title != "" and content != "":
                tools.sentMail(title, content)
        # 10%止盈
        if os.path.exists(filename):
            HighPrice = np.loadtxt(filename)
            if HighPrice.size <= 0:
                HighPrice = lastPrice
        else:
            HighPrice = lastPrice
            
        if HighPrice <= lastPrice:
            HighPrice = lastPrice
            np.savetxt(filename, np.array([HighPrice]))
            
        if lastPrice <= 0.9*HighPrice:
            name = "到达止盈价"
            print(lastPrice, HighPrice*0.9)
            title, content = makeContent(date, name, code)
            if title != "" and content != "":
                tools.sentMail(title, content)
    print(date, "执行了一次止损价格检测，最新股价:", lastPrice)
    
    
# 判断出场情况
def taskB(codes):
    date = datetime.datetime.now()
    for code in codes:
        data = tools.getStockData(code[2:], month = 3, refresh = True, path = "./data" period = "daily")
        data = addMACD(data)
        macd = data["macd"].values
        if macd[-1] < 0.0 and macd[-2] < 0.0:
            name = "出现卖出条件"
            print(date, data.日期.values[-1])
            title, content = makeContent(date, name, code)
            if title != "" and content != "":
                tools.sentMail(title, content)
    print(date, "执行了一次出场检测")
        
        
        
# 计算日线数据的MACD信号
def addMACD(data):
    dif, dea, macd = talib.MACD(data.收盘, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    # print(macd[:100], signal[:100], hist[:100])
    data["dif"] = dif
    data["dea"] = dea
    data["macd"] = macd
    return data
    

# 每间隔s分钟监控codes股票形态和止损价(1分钟)
def run(codes, s, buyPrice):
    scheduler = BlockingScheduler(timezone="Asia/Chongqing")
    scheduler.add_job(taskA, "cron", day_of_week = "mon-fri", hour = "9-15", minute = "*/"+str(1), args = [buyPrice, codes])
    scheduler.add_job(taskB, "cron", day_of_week = "mon-fri", hour = "9-15", minute = "30", args = [codes])
    scheduler.start()


if __name__ == "__main__":
    code = "sz000428"
    codes = [code]
    s = 10
    buyPrice = 3.68
    run(codes, s, buyPrice)
    
