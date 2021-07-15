# coding:utf-8
# 1000元实盘练习程序
# 用历史数据进行回测


import numpy as np
import pandas as pd
import akshare as ak
import sys
import run
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import datetime
from dateutil.relativedelta import relativedelta
import talib


# 设置显示环境
def init():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)


# 获取所有股票代码
@run.change_dir
def getCodes(refresh = True):
    data = pd.DataFrame()
    if refresh == True:
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        # print(stock_zh_a_spot_df.info())
        stock_zh_a_spot_df.to_csv("stocks.csv")
        data = stock_zh_a_spot_df
        data.代码.to_csv("codes.csv")
        return data.代码.values
    else:
        codes = pd.read_csv("codes.csv")
        return codes.代码.values
        # data = pd.read_csv("stocks.csv", converters = {'代码':str})
    # print(data.head())
    
    
# 根据代码获取股票2020年的历史数据
@run.change_dir
def getStockData(codes):
    i = 0.0
    n = float(len(codes))
    for c in codes:
        code = c[2:]
        startDate = "20200101"
        endDate = "20201231"
        stockdata = ak.stock_zh_a_hist(symbol = code, start_date = startDate, end_date = endDate, adjust = "qfq")
        if len(stockdata != 0):
            i = i+1.0
            print(code, i/n)
            filename = "./histdata/" + code + ".csv"
            stockdata.to_csv(filename)
        else:
            n = n - 1.0
        
        
# 找到锤子线形态
@run.change_dir
def getPosition(codes, method):
    code = codes[2:]
    filename = "./histdata/" + code + ".csv"
    # print(filename)
    if os.path.exists(filename):
        data = pd.read_csv(filename)
        # print(data.info())
        result = method(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
        pos = ()
        pos = list(np.nonzero(result))
        return pos[0]
    else:
        return []
        
        
#  进行一轮回测
@run.change_dir
def doTest(gap, rate, codes, method):
    total = 0 # 找到的形态总数
    win = 0 # 在形态出现后的gap个交易日最高涨幅超过rate%的次数
    fail = 0 # 在形态出现后的gap个交易日最高跌幅超过rate%的次数
    for code in codes:
        poses = getPosition(code, method)
        if len(poses) != 0:
        # if poses.size > 0:
            for pos in poses:
                filename = "./histdata/" + code[2:] + ".csv"
                # print(filename)
                if os.path.exists(filename):
                    data = pd.read_csv(filename)
                    length = len(data) # 交易日总数
                    # 基准价 出现形态当天的收盘价
                    basePrice = data.收盘[pos]
                    # 找其后gap个交易日的最低/最高价
                    high = basePrice
                    low = basePrice
                    # print(basePrice)
                    ph = 0
                    pl = 0
                    for t in range(gap):
                        now = pos+t
                        if now >= length:
                            break
                        if data.最高[now] > high:
                            high = data.最高[now]
                            ph = t
                        if data.最低[now] < low:
                            low = data.最低[now]
                            pl = t
                    # 判断回测结果
                    total += 1.0
                    if high/basePrice > 1.0+rate and ph < pl:
                        win += 1.0
                    if low/basePrice < 1.0-rate and pl < ph:
                        fail += 1.0
    return (win, fail, total)
        
        
# 回测，买入后gap天内最大涨幅超过rate%为赢
# 最大跌幅超过rate%为输，其余为中性。
@run.change_dir
def doBacktest(codes, method):
    gap = 10 # 回测时长
    rate = 0.05 # 回测收益率
    win, fail, total = doTest(gap, rate, codes, method)
                    # print(high, low, basePrice)
    # print(win, fail, total)

    print("赢率:%f 赔率:%f 平率:%f" % (win/total, fail/total, (total - win - fail)/total))
    
    
# 回测过程
@run.change_dir
def backtest(codes):
    print("开始回测")
    methods = {
        "锤子线":talib.CDLHAMMER,
        "启明星":talib.CDLMORNINGDOJISTAR,
        "看涨吞没":talib.CDLENGULFING,
        "旭日东升":talib.CDLPIERCING,
        "低位孕线":talib.CDLHARAMI,
        "塔形底":talib.CDLBREAKAWAY,
        "红三兵":talib.CDL3WHITESOLDIERS,
        "上升三法":talib.CDLRISEFALL3METHODS
    }
    for name, method in methods.items():
        print(method.__name__)
        doBacktest(codes, method)
        
        
# 改变回测时间，涨跌幅比例两个条件，回测
@run.change_dir
def multiBacktest(codes, method):
    results = pd.DataFrame(columns = ("gap", "rate", "win"))
    print(results.info())
    gaps = []
    rates = []
    win_rates = []
    for gap in range(3, 20):
        for rate in np.arange(0.05, 0.06, 0.01):
            win, fail, total = doTest(gap, rate, codes, method)
            win_rate = win/total
            gaps.append(gap)
            rates.append(rate)
            win_rates.append(win_rate)
            print(gap, rate, win_rate)
    results.gap = gaps
    results.rate = rates
    results.win = win_rates
    print(results)
    draw(results, method.__name__)
    
    
# 画回测时间长度，涨跌幅与盈利概率的关系图
@run.change_dir
def draw(results, name):
    x = results.gap.values
    y = results.rate.values
    z = results.win.values
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    
    ax.scatter(x, y, z)
    plt.savefig("./output/" + name + ".png")
    plt.close()
    
    fig = plt.figure()
    plt.plot(z)
    plt.savefig("./output/tdres.png")
    plt.close()
                        

if __name__ == "__main__":
    init()
    codes = getCodes(refresh = False)
    print(codes)
    # getStockData(codes)
    method = talib.CDLHAMMER
    result = getPosition(codes[0], method)
    print(result)
    # doBacktest(codes, method)
    # backtest(codes)
    multiBacktest(codes, talib.CDLBREAKAWAY)
    