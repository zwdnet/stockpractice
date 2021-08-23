# coding:utf-8
# 1000元实盘练习程序
# 实现MACD找买点的策略
# 根据《阿佩尔均线操盘术》第八章


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
import sys
import talib
import backtrader as bt
import math
from scipy import stats


# 主程序
@run.change_dir
def main(refresh = False):
    code = "600658"
    data = tools.getStockData(code = code, month = 12, refresh = refresh)
    print(data.info())
    # df = pd.DataFrame()
    data["macd"], data["macdsignal"], data["macdhist"] = talib.MACD(data.收盘.values)
    plt.figure()
    data.macd = 10*data.macd
    data.macdsignal = 10*data.macdsignal
    data.macdhist = 10*data.macdhist
    data[["收盘", "macd", "macdsignal", "macdhist"]].plot()
    plt.savefig("./output/macd.jpg")
    plt.close()
    
    
# MACD策略
class MACD(bt.Strategy):
    params = (('buy_short', 12), #买入短周期
              ('buy_long', 26), #买入长周期
              ('sell_short', 24),#卖出短周期
              ('sell_long', 52),#卖出长周期
              ('signal_period', 9)) #信号周期
    
    def __init__(self):
        self.order = None
        self.收盘 = self.datas[0].close
        self.buymacd = bt.talib.MACD(self.收盘, fastperiod=self.params.buy_short,slowperiod=self.params.buy_long, signalperiod=self.params.signal_period)
        self.sellmacd = bt.talib.MACD(self.收盘, fastperiod=self.params.sell_short, slowperiod=self.params.sell_long, signalperiod=self.params.signal_period)
        
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.buymacd.macdhist[0] > 0.0 and self.收盘[0] != 0.0:
                cash = self.broker.get_cash()
                stock = math.ceil((cash/self.收盘[0]-100)/100)*100
                self.order = self.buy(size = stock, price = self.datas[0].close)
                # print(cash, stock, self.收盘[0],  stock*self.datas[0].close)
        else:
            if self.sellmacd.macdhist[0] < 0.0:
                # print("卖出前")
                # self.display()
                self.order = self.sell(size = self.position.size, price = self.datas[0].close)
                # print("卖出后")
                # self.display()
                
                
            # print(self.sellmacd.macdhist[0])
            
    # 输出信息
    def display(self):
        print("现金", self.broker.get_cash(), "持仓", self.position.size, "市值", self.broker.getvalue(), "现价", self.收盘[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            #print(self.data.datetime.date(0))
            #print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.status == order.Canceled:
                print("交易被取消\n")
            elif order.status == order.Margin:
                # 现金不足，重新计算购入数量
                cash = self.broker.get_cash()
                stock = math.ceil((cash/self.收盘[0] - 100)/100)*100*0.90
                self.order = self.buy(size = stock, price = self.datas[0].close)
                # print("现金不足，新购入数量为:", stock)
                return
            else:
                print("交易被拒绝\n")
            
            self.order = None
            
    def stop(self):
        self.order = self.close()

    
    
# 回测MACD策略
@run.change_dir
def backTest(refresh = False):
    month = 60
    code = "600658"
    benchmark = tools.getBenchmarkData(month = month,  refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = MACD, benchmark = benchmark, month = month, cash = 10000000, refresh = refresh, path = "./stockdata/", bOpt = True)
    # results = backtest.getResults()
    # print(results)
    # backtest.drawResults(code + "result")
    res = backtest.optRun(buy_short = [6, 10], buy_long = [18, 26, 30], sell_short = [18, 30], sell_long = [54, 60], signal_period = [9, 18, 27])
    print("测试c", res)
    
    
# 对整个市场回测
@run.change_dir
def marketTest(refresh = False, retest = False):
    month = 12
    codes = tools.Research(refresh = refresh, month = month, highPrice = 10.0)
    benchmark = tools.getBenchmarkData(month = month, refresh = refresh)
    datafilepath = "./backtest.csv"
    if os.path.exists(datafilepath) and retest == False:
        test_res = pd.read_csv(datafilepath, converters = {'股票代码':str})
    else:
        test_res = pd.DataFrame()
        n = len(codes)
        i = 0
        for code in codes[:10]:
            i += 1.0
            print("回测进度:", i/n*100, "%")
            backtest = BackTest(codes = [code], strategy = MACD, benchmark = benchmark, month = month, cash = 10000000, refresh = refresh, path = "./stockdata/")
            results = backtest.getResults()
            test_res = test_res.append(results)
        test_res.to_csv(datafilepath, index = False)
    # print(test_res.describe())
    # print(test_res.股票代码)
    print(test_res.info())
    print(test_res.describe())
    
    test_res = test_res.fillna(method='ffill') 
    test_res = test_res.fillna(method='bfill')
    plt.figure()
    test_res.胜率.plot(kind = "kde")
    plt.savefig("./output/test_res1.png")
    plt.close()
    plt.figure()
    test_res["年化收益率"][np.isinf(test_res["年化收益率"])] = 0
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
        


if __name__ == "__main__":
    tools.init()
    # main(refresh = False)
    # backTest(refresh = True)
    marketTest(refresh = False, retest = False)