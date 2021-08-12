# coding:utf-8
# 1000元实盘练习程序
# 回测成交量辅助判断锤子线策略程序


import pandas as pd
import numpy as np
import talib
import tools
import run
import backtrader as bt
from backtest import BackTest
import strategy as st


# 回测主函数
@run.change_dir
def main(refresh = False, retest = False):
    # 先初始化，准备数据
    tools.init()
    code = "600658"
    benchmark = tools.getBenchmarkData(month = 60, refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = st.ChuiziStrategy, benchmark = benchmark, month = 60, refresh = refresh, path = "./stockdata/")
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    
    
# 调参实验
def main2(refresh = False):
    # 先初始化，准备数据
    tools.init()
    code = "600658"
    benchmark = tools.getBenchmarkData(month = 60, refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = st.ChuiziStrategy, benchmark = benchmark, month = 60, refresh = refresh, path = "./stockdata/", bOpt = True)
    results = backtest.optRun(period = range(5,10), rate = np.arange(0.1, 0.5, 0.1), stopup = np.arange(0.05, 0.5, 0.05), stopdown = np.arange(0.05, 0.1, 0.05))
    # results = backtest.optRun(period = range(5,10))
    print("调参结果:")
    print(results[:5])


if __name__ == "__main__":
    # main(refresh = False)
    main2(refresh = False)
    