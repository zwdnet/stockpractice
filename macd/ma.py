# coding:utf-8
# 1000元实盘练习程序
# 测试判断牛熊的指标
# 根据《阿佩尔均线操盘术》第二章


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
import strategy as st
    
    
# 对策略进行回测
@run.change_dir
def backTest(refresh = False):
    month = 15*12
    code = "000300" # 沪深300指数
    benchmark = tools.getBenchmarkData(month = month,  refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = st.MA, benchmark = benchmark, month = month, cash = 1000000, refresh = refresh, path = "./stockdata/", bOpt = False)
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    # res = backtest.optRun(period = range(5,200))
    # print("测试c", res)
    
    

if __name__ == "__main__":
    tools.init()
    backTest(refresh = False)
    
    