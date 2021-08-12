# coding:utf-8
# 1000元实盘练习程序
# 在K线选股的过程中增加用成交量辅助判断


import numpy as np
import pandas as pd
import tools
import run
import backtrader as bt
import datetime
import matplotlib.pyplot as plt
from backtest import BackTest
import talib
import os


# 判断量能的函数
def judge(value, mean, rate = 0.1):
    result = -2
    if value > mean*(1+rate): # 放量
        result = 1
    elif value < mean*(1-rate): # 缩量
        result = -1
    else: # 平量
        result = 0
    return result


# 在数据中增加成交量的均线，并判断量能
def addMA(data, period = 5, rate = 0.1):
    data["成交量均线"] = pd.Series.rolling(data.成交量, window = period).mean()
    # 成交量大于均值的110%为放量，值为1，低于均值的90%为缩量，值为-1，否则为平量，值为0
    data["量能"] = data.apply(lambda x: judge(x.成交量, x.成交量均线, rate=rate), axis = 1)
    return data


# 检测k线有无method所定义的形态
@run.change_dir
def test(codes, method, month):
    print("检测k线形态")
    results = {}
    date = []
    for code in codes:
        data = tools.getStockData(code=code, month = month)
        data = addMA(data, rate = 0.2)
        # data = data.iloc[-5:, :]
        # print(code, data.tail())
        result = method(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
        pos = ()
        pos = list(np.nonzero(result))
        if len(pos[0]) != 0:
            if data.量能[pos[0][-1]] == 1: # 用成交量辅助判断
                date.append(data.日期[pos[0][-1]])
                results[code] = date
        date = []
#        print(code, results[code])
#        input("按任意键继续")
    return results
    
    
# 获取指定股票代码集合的k线符合method形态的位置
def getPosition(codes, methods, month):
    for name, method in methods.items():
        results = test(codes, method, month)
        # 按日期降序排序，最近的日期排最前
        results = sorted(results.items(),key = lambda x:x[1],reverse = True)
        print(name, results)


# 主函数
@run.change_dir
def main(refresh = False, month = 6):
    # 先初始化，准备数据
    tools.init()
    codes = tools.Research(refresh = refresh, month = month, highPrice = 10.0)
    benchmark = tools.getBenchmarkData(month = month, refresh = refresh)
    print(len(codes))
    methods = {
    "锤子线":talib.CDLHAMMER
    }
    """
    methods = {
        "锤子线":talib.CDLHAMMER,
        "启明星":talib.CDLMORNINGDOJISTAR,
        "看涨吞没":talib.CDLENGULFING,
        "旭日东升":talib.CDLPIERCING,
        "低位孕线":talib.CDLHARAMI,
        "塔形底":talib.CDLBREAKAWAY,
        "红三兵":talib.CDL3WHITESOLDIERS,
        "上升三法":talib.CDLRISEFALL3METHODS
    }"""
    results = getPosition(codes, methods, month)


if __name__ == "__main__":
    main(refresh = False, month = 1)
    