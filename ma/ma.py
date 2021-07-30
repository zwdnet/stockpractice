# coding:utf-8
# 1000元实盘练习程序
# 均线突破策略实现


import tools
import pandas as pd
import numpy as np
import run
import matplotlib.pyplot as plt


# 给股价数据增加均线
def addMA(data, ma_short = 5, ma_long = 20):
    data["短期均线"] = pd.Series.rolling(data.收盘, window = ma_short).mean()
    data["长期均线"] = pd.Series.rolling(data.收盘, window = ma_long).mean()
    return data
    
    
# 根据股价数据检测买入卖出点
@run.change_dir
def check(data):
    buy = []
    sell = []
    for i in range(1, len(data)):
        # print(i, data.短期均线[i-1], data.长期均线[i-1], data.短期均线[i], data.长期均线[i])
        # 短期均线上穿长期均线，买点
        if data.短期均线[i-1] < data.长期均线[i-1] and data.短期均线[i] > data.长期均线[i]:
            buy.append(i)
        # 短期均线下穿长期均线，卖点
        elif data.短期均线[i-1] > data.长期均线[i-1] and data.短期均线[i] < data.长期均线[i]:
            sell.append(i)
#    print("买点", buy, data.iloc[buy].日期)
#    print("卖点", sell, data.iloc[sell].日期)
#    plt.figure()
#    plt.plot(data.收盘)
#    plt.plot(data.短期均线, label = "short")
#    plt.plot(data.长期均线, label = "long")
#    plt.legend(loc = "best")
#    plt.savefig("./output/ma.png")
#    plt.close()
    return (buy, sell)
    
    
# 在股票池中寻找今天出现买点的股票
@run.change_dir
def findBuy(codes):
    results = []
    i = 0
    n = len(codes)
    for code in codes:
        print("正在检查第%d只股票，一共有%d只股票" % (i, n))
        i += 1
        data = tools.getStockData(code)
        data = addMA(data)
        buy = check(data)[0]
        # 今天出现买点的股票
        if len(buy) != 0 and buy[-1] == len(data) - 1:
            results.append(code)
    return results
    

if __name__ == "__main__":
    # 先初始化，准备数据
    tools.init()
    codes = tools.Research(refresh = False, month = 12, highPrice = 10.0)
#    print(len(codes), codes[0])
#    data = tools.getStockData(codes[0])
#    print(data.info())
#    data = addMA(data, ma_short = 5, ma_long = 30)
#    print(data.info())
#    check(data)
    results = findBuy(codes)
    print("今日出现买点的股票代码:", results)
    