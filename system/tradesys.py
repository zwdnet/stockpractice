# coding:utf-8
# 1000元实盘练习程序
# 三重滤网交易系统实盘选股程序


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import run
import tools
import talib
import math
import os


# 选股，根据交易系统入场规则选择合适入场的股票
@run.change_dir
def Select(refresh = True, highPrice = 10.0, month = 3):
    # 定义需要的常量
    stop_loss = 0.05 # 买入止损比例5%
    stop_profit = 0.1 # 止盈比例10%
    # 获取符合筛选条件的股票的代码
    codes = tools.Research(refresh = refresh, month = month, highPrice = highPrice, bSelect = True, path = "./tradedata/")
    # 找买点
    n = len(codes)
    print("测试", n)
    t = 0
    result = pd.DataFrame()
    for code in codes:
        print("研究进程:", t/n*100, "%")
        t += 1
        # 准备股票数据
        data_day, data_week = makeData(code = code, month = month, refresh = refresh)
        days = data_day["日期"].values
        days_s_slop = data_day["短期均线斜率"].values
        days_l_slop = data_day["长期均线斜率"].values
        days_close = data_day["收盘"].values
        macd = data_day["macd"].values
        dif = data_day["dif"].values
        dea = data_day["dea"].values
        i = 0
        for day in days:
            week = data_week[data_week.日期 < day]
            if len(week) == 0:
                i += 1
                continue
            # print(day, week.日期.values[-1], week.短期均线斜率.values[-1])
            # 一重滤网
            judge = week["短期均线斜率"].values[-1] > 0 and week["长期均线斜率"].values[-1] > 0 and week["短期均线"].values[-1] > week["长期均线"].values[-1]
            # 二重滤网
            if judge:
                if macd[i] > 0 and macd[i-1] < 0 and dif[i-1] < dea[i-1] and dif[i] > dea[i]:
                    result = result.append({"股票代码":code, "买点日期":day}, ignore_index = True)
            i += 1
    print("测试", result)
    result = result.sort_values(by = "买点日期")
    print(result)
    
    
# 给股价数据增加均线
def addMA(data, ma_short = 1, ma_long = 5):
    data["短期均线"] = pd.Series.rolling(data.收盘, window = ma_short).mean()
    data["长期均线"] = pd.Series.rolling(data.收盘, window = ma_long).mean()
    return data
    
    
# 计算均线在每个点的斜率
def addSlope(data):
    data["短期均线斜率"] = data.短期均线 - data.短期均线.shift(1)
    data["长期均线斜率"] = data.长期均线 - data.长期均线.shift(1)
    return data
    

# 计算日线数据的MACD信号
def addMACD(data):
    dif, dea, macd = talib.MACD(data.收盘, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    # print(macd[:100], signal[:100], hist[:100])
    data["dif"] = dif
    data["dea"] = dea
    data["macd"] = macd
    return data
    
    
# 准备数据
@run.change_dir
def makeData(code, month, refresh = True):
    data_day = tools.getStockData(code, month = month, refresh = refresh, period = "daily", path = "./tradedata/")
    data_week = tools.getStockData(code, month = month, refresh = refresh, period = "weekly", path = "./tradedata/")
    # print(len(data_day), len(data_week))
    # print(data_day.head(), data_week.head())
    data_week = addMA(data_week)
    data_week = addSlope(data_week)
    data_day = addMA(data_day)
    data_day = addSlope(data_day)
    data_day = addMACD(data_day)
    # print(data_day.info(), data_day.head())
    # print(data_week.info(), data_week.head())
    # print(data_week.loc[:, ["日期", "短期均线", "短期均线斜率", "长期均线", "长期均线斜率"]])
    # data_choose = data_week[(data_week.短期均线斜率 > 0) & (data_week.长期均线斜率 > 0)]
    # print(data_choose.loc[:, ["日期", "短期均线", "短期均线斜率", "长期均线", "长期均线斜率"]])
    return data_day, data_week
    

# 主程序
def main():
    tools.init()
    Select(refresh = False)


if __name__ == "__main__":
    main()