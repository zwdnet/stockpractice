# coding:utf-8
# 1000元实盘练习程序
# 回测均线突破策略


import numpy as np
import pandas as pd
import tools
import run
import backtrader as bt
import datetime
import matplotlib.pyplot as plt
from backtest import BackTest
import strategy as st
import os
from scipy import stats


# 回测主函数 refresh是否重新加载数据 
# retest是否重新回测
@run.change_dir
def main(refresh = False, retest = False):
    # 先初始化，准备数据
    tools.init()
    codes = tools.Research(refresh = refresh, month = 60, highPrice = 10.0)
    benchmark = tools.getBenchmarkData(month = 60, refresh = refresh)
    # print(benchmark.head())
    datafilepath = "./backtest.csv"
    if os.path.exists(datafilepath) and retest == False:
        test_res = pd.read_csv(datafilepath, converters = {'股票代码':str})
    else:
        test_res = pd.DataFrame()
        n = len(codes)
        i = 0
        for code in codes:
            i += 1.0
            print("回测进度:", i/n*100, "%")
            backtest = BackTest(codes = [code], strategy = st.MAcrossover, benchmark = benchmark)
            results = backtest.getResults()
            test_res = test_res.append(results)
        test_res.to_csv(datafilepath, index = False)
    # print(test_res.describe())
    # print(test_res.股票代码)
    print(test_res.info())
    
    plt.figure()
    test_res.胜率.plot(kind = "kde")
    plt.savefig("./output/test_res1.png")
    plt.close()
    plt.figure()
    test_res.年化收益率.plot(kind = "kde")
    plt.legend(loc = "best")
    plt.savefig("./output/test_res2.png")
    print(test_res.head())
    print(test_res[test_res.年化收益率 >= 0.7])
    # 按年化收益率排序
    test_res.sort_values(by = "年化收益率", inplace = True, ascending = False)
    # 前10名
    print(test_res.head(10).loc[:, ["股票代码", "年化收益率"]])
    # 研究交易次数与年化收益率的相关性
    # 剔除年化收益率绝对值大于40%的数据
    new_res = test_res[np.abs(test_res.年化收益率) < 0.4]
    trades = new_res.交易次数.values
    gets = new_res.年化收益率.values
    plt.figure()
    plt.scatter(trades, gets)
    plt.xlabel("交易次数")
    plt.ylabel("年化收益率")
    plt.savefig("./output/tradevsget.png")
    # 计算交易次数与年化收益率的相关系数
    r, p = stats.pearsonr(trades, gets)
    print("交易次数与年化收益率的相关系数为:%6.3f，概率为:%6.3f" % (r, p))
    # 研究交易次数与胜率的关系
    trades = test_res.交易次数.values
    winrates = test_res.胜率.values
    plt.figure()
    plt.scatter(trades, winrates)
    plt.xlabel("交易次数")
    plt.ylabel("胜率")
    plt.savefig("./output/tradevswinrates.png")
    # 计算交易次数与胜率的相关系数
    r, p = stats.pearsonr(trades, winrates)
    print("交易次数与胜率的相关系数为:%6.3f，概率为:%6.3f" % (r, p))
    # 画alpha，beta值分布图
    plt.figure()
    test_res.Alpha.plot(kind = "kde")
    plt.ylabel("α")
    plt.savefig("./output/alpha.png")
    plt.close()
    plt.figure()
    test_res.Beta.plot(kind = "kde")
    plt.ylabel("β")
    plt.savefig("./output/beta.png")
    plt.close()
    
    
@run.change_dir
def main2():
    tools.init()
    codes = ["003035", "300703"]
    results = pd.DataFrame()
    for code in codes:
        backtest = BackTest(codes = [code], strategy = st.MAcrossover)
        res = backtest.getResults()
        results = results.append(res)
    filename = "./strtest.csv"
    print("a", results)
    results.to_csv(filename, index = False)
    res2 = pd.read_csv(filename, converters = {'股票代码':str})
    print("b", res2)
    
    
# 测试，增加计算alpha等指标
@run.change_dir
def main3(refresh = False):
    tools.init()
    code = "002348"
    benchmark = tools.getBenchmarkData(month = 60, refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = st.MAcrossover, benchmark = benchmark, month = 60, refresh = refresh, path = "./stockdata/")
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    
    
if __name__ == "__main__":
    # main(refresh = False, retest = False)
    # main2()
    main3(refresh = False)