# coding:utf-8
# 1000元实盘练习程序
# 用历史数据进行回测


import numpy as np
import pandas as pd
import akshare as ak
import sys
import run
import matplotlib.pyplot as plt
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
def getChuizi(codes):
    code = codes[2:]
    filename = "./histdata/" + code + ".csv"
    # print(filename)
    if os.path.exists(filename):
        data = pd.read_csv(filename)
        # print(data.info())
        result = talib.CDLHAMMER(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
        pos = ()
        pos = list(np.nonzero(result))
        return pos[0]
    else:
        return []
        
        
# 回测，买入后gap天内最大涨幅超过rate%为赢
# 最大跌幅超过rate%为输，其余为中性。
@run.change_dir
def backtest(codes):
    gap = 5
    rate = 0.05
    total = 0 # 找到的锤子形态总数
    win = 0 # 在锤子线出现后的gap个交易日最高涨幅超过rate%的次数
    fail = 0 # 在锤子线出现后的gap个交易日最高跌幅超过rate%的次数
    print("回测")
    for code in codes:
        poses = getChuizi(code)
        if len(poses) != 0:
        # if poses.size > 0:
            for pos in poses:
                filename = "./histdata/" + code[2:] + ".csv"
                # print(filename)
                if os.path.exists(filename):
                    data = pd.read_csv(filename)
                    length = len(data) # 交易日总数
                    # 基准价 出现锤子形当天的收盘价
                    basePrice = data.收盘[pos]
                    # 找其后gap个交易日的最低/最高价
                    high = basePrice
                    low = basePrice
                    # print(basePrice)
                    for t in range(gap):
                        now = pos+t
                        if now >= length:
                            break
                        if data.最高[now] > high:
                            high = data.最高[now]
                        if data.最低[now] < low:
                            low = data.最低[now]
                    # 判断回测结果
                    total += 1.0
                    if high/basePrice > 1.0+rate:
                        win += 1.0
                    if low/basePrice < 1.0-rate:
                        fail += 1.0
                    # print(high, low, basePrice)

    print("赢率:%f 赔率:%f 平率:%f" % (win/total, fail/total, (total - win - fail)/total))


if __name__ == "__main__":
    init()
    codes = getCodes(refresh = False)
    print(codes)
    # getStockData(codes)
    result = getChuizi(codes[0])
    print(result)
    backtest(codes)