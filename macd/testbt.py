# coding:utf-8
# 1000元实盘练习程序
# 测试backtrader回测结果是否正确


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
import pyfolio as pf
from scipy import stats


# 制造虚拟的股价数据
@run.change_dir
def makeData():
    date = pd.date_range("1/1/2021", "1/10/2021")
    priceA = [1.0, 1.1, 1.2, 1.3, 0.5, 0.8, 0.4, 0.6, 1.0, 1.2]
    priceB = [1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09]
    # for i in range(len(date)):
    #     priceA.append(price + 2*i)
    #     priceB.append(price + i)
    print(priceA, priceB)
    data = pd.DataFrame({"日期": date,
                         "开盘": priceA,
                         "收盘": priceA,
                         "最高": priceA,
                         "最低": priceA,
                         "成交量": priceA
    })
    
    bench = pd.DataFrame({"日期": date,
                         "开盘": priceB,
                         "收盘": priceB,
                         "最高": priceB,
                         "最低": priceB,
                         "成交量": priceB
    })
    
    return (data, bench)
    
    
# 进行回测
@run.change_dir
def backtest():
    # month = 0
    # code = "600519"
    # refresh = True
    # data, bench = makeData()
    # start_date = "2009-01-01"
    # end_date = "2009-01-18"
    # bench = tools.getBenchmarkData(code = "000001", refresh = refresh, start_date = start_date, end_date = end_date)
    # print("测试基准数据:", bench.info())
    code = "test"
    data, bench = makeData()
    backtest = BackTest(codes = [code], strategy = st.TestBT, benchmark = bench, cash = 1, commission = 0.0, riskfree = 0.0, stake = 1,refresh = False, path = "./stockdata/", bOpt = False, bData = True, data = data, cheat_on_open = True)
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    
    
# 手撸代码计算回测指标
def bk_indicator(data, bench, rf = 0.0, days = 252.0):
    data.set_index("日期", drop = True, inplace = True)
    bench.set_index("日期", drop = True, inplace = True)
    # print(data, bench)
    data_ret = data.收盘.pct_change().fillna(0).tz_localize(None)
    bench_ret = bench.收盘.pct_change().fillna(0).tz_localize(None)
    print("手算验证")
    # print("收益率数据:", data_ret, bench_ret)
    
    # res = pf.create_interesting_times_tear_sheet(returns = data_ret, benchmark_rets = bench_ret, return_fig = True)
    # with open("test.jpg", "wb") as res:
    #     res.write(res.img)
    
    # 计算累积收益率
    n = len(data)
    RcA = (data.收盘[n-1] - data.收盘[0])/data.收盘[0]
    RcB = (bench.收盘[n-1] - bench.收盘[0])/bench.收盘[0]
    print("累积收益率", RcA, RcB)
    
    # 计算年化收益率
    RaA = pow(1 + RcA, days/n) - 1
    RaB = pow(1 + RcB, days/n) - 1
    print("年化收益率", RaA, RaB)
    
    # 计算最大回撤值
    MDA = ((data.收盘.cummax() - data.收盘)/data.收盘.cummax()).max()
    MDB = ((bench.收盘.cummax() - bench.收盘)/bench.收盘.cummax()).max()
    print("最大回撤:", MDA, MDB)
    
    # 计算β值
    # covAB = np.cov(data_ret, bench_ret)
    covAB = data_ret.cov(bench_ret)
    print("协方差", covAB)
    varB = np.var(bench_ret, ddof = 1)
    beta = covAB/varB
    print("策略β值:", beta)
    
    # 计算α值
    x = data_ret.values
    y = bench_ret.values
    b, a, r_value, p_value, std_err = stats.linregress(x, y)
    alpha = round(a*days, 4)
    beta2 = round(b*days, 4)
    print("α:", alpha, "β:", beta2)
    
    # 另一种计算α的方法
    alpha = RaA - (rf + beta*(RaB - rf))
    print(alpha)
    
    # 计算夏普比率
    # rf = 0.03
    rf = (1+rf)**(1/days) - 1.0
    exReturn = data_ret - rf
    sharpe = exReturn.mean() / exReturn.std() * np.sqrt(days)#np.sqrt(len(exReturn)) * exReturn.mean() / exReturn.std()
    print("夏普比率:", sharpe)
    
    # 计算信息比率
    ex_return = data_ret - bench_ret
    information = np.sqrt(len(ex_return)) * ex_return.mean() / ex_return.std()
    print("信息比率:", information)
    
    
# 自己算验证结果
@run.change_dir
def test():
    data, bench = makeData()
    bk_indicator(data, bench)
    
    
# 用文章https://mp.weixin.qq.com/s?__biz=MzUyMDk1MDY2MQ==&mid=2247483991&idx=1&sn=7e2a54011706fd88ff7cef2007f840d8&chksm=f9e3c4bdce944daba8cdd20fa7ca26704381779159f2aa25e66a2d1f527590e29c906df9a697&scene=21#wechat_redirect 的例子验证
@run.change_dir
def realTest():
    stock_code = "000006"
    bench_code = "510300"
    start_date = "20200106"
    end_date = "20200531"
    data = tools.getStockData(code = stock_code, path = "./stockdata/", refresh = True, start_date = start_date, end_date = end_date)
    bench = tools.getBenchmarkData(code = bench_code, refresh = True, start_date = start_date, end_date = end_date)
    bk_indicator(data, bench)
    
    
# 用大一点的数据进行回测
@run.change_dir
def backtest_more():
    # month = 12
    code = "600658"
    refresh = True
    # data, bench = makeData()
    start_date = "20150101"
    end_date = "20160601"
    bench = tools.getBenchmarkData(code = "000300", refresh = refresh, start_date = start_date, end_date = end_date)
    print(bench.info())
    backtest = BackTest(codes = [code], strategy = st.TestBT, benchmark = bench, cash = 4700, riskfree = 0.02, stake = 100, refresh = refresh, path = "./stockdata/", bOpt = False, bData = False, cheat_on_open = True, start_date = start_date, end_date = end_date)
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    

if __name__ == "__main__":
    tools.init()
    # backtest()
    # test()
    # realTest()
    backtest_more()