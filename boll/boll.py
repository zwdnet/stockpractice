# coding:utf-8
# 1000元实盘练习程序
# 日线布林带选股


import pandas as pd
import numpy as np
import akshare as ak
import run
import tools
import efinance as ef
import datetime, quandl
import matplotlib.pyplot as plt
import os
from backtest import BackTest
import backtrader as bt
import talib


# 主程序
@run.change_dir
def main(refresh = False):
    month = 12
    codes = tools.Research(refresh = refresh, month = month, highPrice = 10.0, lowPrice = 5.0, bSelect = True, drop_days = 60)
    n = len(codes)
    print(n)
    chosecodes = []
    i = 0
    for code in codes:
        print("研究进度:", i/n)
        i += 1
        data = tools.getStockData(code, month = month, refresh = refresh, adjust = "qfq")
        upper,middle,lower=talib.BBANDS(data.收盘.values, timeperiod=20, nbdevup=2, nbdevdn=2, matype=1)
        data["upper"] = upper
        data["middle"] = middle
        data["lower"] = lower
        # print(data.info(), data.收盘.values[-1], data.lower.values[-1])
        if data.收盘.values[-1] < data.lower.values[-1]:
            chosecodes.append(code)
    return chosecodes
    
    
if __name__ == "__main__":
    tools.init()
    codes = main(refresh = False)
    print(codes)