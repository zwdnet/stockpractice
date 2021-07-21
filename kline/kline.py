# coding:utf-8
# 1000元实盘练习程序
# 研究k线形态

import numpy as np
import pandas as pd
import akshare as ak
import sys
import run
import matplotlib.pyplot as plt

from mplfinance.original_flavor import candlestick2_ohlc
import os
import datetime
from dateutil.relativedelta import relativedelta
import talib


# 设置显示环境
def init():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)


# 获取股票池近一个月的日线数据
@run.change_dir
def getRecentData(path = "result.csv", refresh = False, savePath = "./data/"):
    data = pd.read_csv(path, converters = {'code':str}).代码.values
    codes = []
    # print(data)
    # 获取股票最近一个月数据
    if refresh == True:
        today = datetime.date.today().strftime("%Y%m%d")
        # print("今天日期:", today)
        lastmonth = (datetime.date.today() - relativedelta(months = 1)).strftime("%Y%m%d")
        # print("上月日期:", lastmonth)
        for i in data:
            codes.append(i[2:])
            stock_data = ak.stock_zh_a_hist(symbol = codes[-1], start_date = lastmonth, end_date = today, adjust = "qfq")
            filename = savePath + codes[-1] + ".csv"
            # 改造数据
            # stock_data.index = pd.DatetimeIndex(data.index)
            # stock_data.rename(columns={'日期':'Date', '开盘':'Open'})
            stock_data.to_csv(filename)
    else:
        for i in data:
            codes.append(i[2:])
    return codes
    
    
# 画指定股票的k线
@run.change_dir
def drawKLine(code, open = "开盘", high = "最高", low = "最低", close = "收盘", date = "日期", path = "./data/"):
    filename = path + code + ".csv"
    if os.path.exists(filename):
        # 画k线
        data = pd.read_csv(filename)
        # print(data.info())
        fig, ax = plt.subplots(1, 1, figsize=(8,3), dpi=200)
        candlestick2_ohlc(ax,
                opens = data[open].values,
                highs = data[high].values,
                lows = data[ low].values,
                closes = data[close].values,
                width=0.5, colorup="r", colordown="g")
        # 计算均线数据
        data["5"] = data[close].rolling(5).mean()
        data["10"] = data[close].rolling(10).mean()
        data["20"] = data[close].rolling(20).mean()
        data["30"] = data[close].rolling(30).mean()
        # 画均线
        plt.plot(data['5'].values, alpha = 0.5, label='MA5')
        plt.plot(data['10'].values, alpha = 0.5, label='MA10')
        plt.plot(data['20'].values, alpha = 0.5, label='MA20')
        plt.plot(data['30'].values, alpha = 0.5, label='MA30')
        # 设定图例及坐标轴
        plt.legend(loc = "best")
        plt.xticks(ticks =  np.arange(0,len(data)), labels = data[date].values)
        plt.xticks(rotation=90, size=3)

        # 输出图片
        plt.savefig("./output/" + code + ".png")
        plt.close()
    else:
        print("无股票数据")
        
        
# 检测k线有无method所定义的形态
@run.change_dir
def test(codes, method):
    print("检测k线形态")
    results = {}
    for code in codes:
        date = []
        filename = "./data/" + code + ".csv"
        if os.path.exists(filename):
            data = pd.read_csv(filename)
            # print(data.info())
            result = method(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
            pos = ()
            pos = list(np.nonzero(result))
            if len(pos[0]) != 0:
                date.append(data.日期[pos[0][-1]])
                results[code] = date
    return results
    
    
# 获取指定股票代码集合的k线符合method形态的位置
def getPosition(codes, method):
    for name, method in methods.items():
        results = test(codes, method)
        # 按日期降序排序，最近的日期排最前
        results = sorted(results.items(),key = lambda x:x[1],reverse = True)
        print(name, results)


if __name__ == "__main__":
    init()
    codes = getRecentData(refresh = False)
    # print(codes)
    # drawKLine(codes[0])
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
    results = getPosition(codes, methods)