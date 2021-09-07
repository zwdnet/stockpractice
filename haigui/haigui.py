# coding:utf-8
# 1000元实盘练习程序
# 实现海龟交易策略回测


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
import math
from scipy import stats


class TestSizer(bt.Sizer):
    params = (('stake', 1),)
    
    
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:          
            return self.p.stake        
        position = self.broker.getposition(data)        
        if not position.size:            
            return 0        
        else:            
            return position.size        
        return self.p.stakeclass 
    
    
class HaiguiStrategy(bt.Strategy):
    params = ( ('maperiod', 15), ('printlog', False), )
    
    
    def log(self, txt, dt = None, doprint = False):
        if self.params.printlog and doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            
            
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
        self.order = None
        self.buyprice = 0.0
        self.buycomm = 0.0
        self.newstake = 0.0
        self.buytime = 0.0
        
        # 计算参数
        self.DonchianHi = bt.indicators.Highest(self.datahigh(-1), period=20, subplot=False)
        self.DonchianLo = bt.indicators.Lowest(self.datalow(-1), period=10, subplot=False)
        self.TR = bt.indicators.Max((self.datahigh(0)- self.datalow(0)), abs(self.dataclose(-1) -   self.datahigh(0)), abs(self.dataclose(-1)  - self.datalow(0) ))
        self.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=14, subplot=True)
        
        # 上下突破
        self.CrossoverHi = bt.ind.CrossOver(self.dataclose(0), self.DonchianHi)
        self.CrossoverLo = bt.ind.CrossOver(self.dataclose(0), self.DonchianLo)
        
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:            
            return

        if order.status in [order.Completed]:            
            if order.isbuy():               
                self.log(                    
                'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %                   
                (order.executed.price,
                order.executed.value, order.executed.comm), doprint=True)              
                self.buyprice = order.executed.price              
                self.buycomm = order.executed.comm            
            else:             
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm), doprint=True)
                self.buyprice = order.executed.price              
                self.buycomm = order.executed.comm                             
                self.bar_executed = len(self)       
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:           
            self.log('Order Canceled/Margin/Rejected')        
        self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed: 
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))
        
        
    def next(self):
        if self.order:
            return
        # 入场
        if self.CrossoverHi > 0 and self.buytime == 0:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.buytime = 1
            self.order = self.buy()
        # 加仓
        elif self.datas[0].close >self.buyprice+0.5*self.ATR[0] and self.buytime > 0 and self.buytime < 5:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.order = self.buy()
            self.buytime = 1
        # 出场
        elif self.CrossoverLo < 0 and self.buytime > 0:            
            self.order = self.sell()            
            self.buytime = 0
        #止损        
        elif self.datas[0].close < (self.buyprice - 2*self.ATR[0]) and self.buytime > 0:           
            self.order = self.sell()
            self.buytime = 0
            
    
    def stop(self): 
        self.log('(MA Period %2d) Ending Value %.2f'% (self.params.maperiod, self.broker.getvalue()), doprint=True)
    
    
# 主程序
@run.change_dir
def main(refresh = True):
    # test(refresh = refresh)
    marketTest(refresh = False, retest = False)
    

# 对某只股票回测
@run.change_dir    
def test(refresh = True):
    month = 120
    code = "600658"
    benchmark = tools.getBenchmarkData(month = month,  refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = HaiguiStrategy, benchmark = benchmark, month = month, cash = 10000000, refresh = refresh, path = "./stockdata/", bOpt = False, Sizer = TestSizer)
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    
    
# 对整个市场回测
@run.change_dir
def marketTest(refresh = False, retest = False):
    month = 120
    codes = tools.Research(refresh = refresh, month = month, highPrice = 5.0, bSelect = False, path = "./stockdata/")
    benchmark = tools.getBenchmarkData(month = month, refresh = refresh)
    datafilepath = "./backtest.csv"
    if os.path.exists(datafilepath) and retest == False:
        test_res = pd.read_csv(datafilepath, converters = {'股票代码':str})
    else:
        test_res = pd.DataFrame()
        n = len(codes)
        i = 0
        for code in codes:
            i += 1.0
            print("回测进度:", i/n*100, "%", code)
            backtest = BackTest(codes = [code], strategy = HaiguiStrategy, benchmark = benchmark, month = month, cash = 10000000, refresh = refresh, path = "./stockdata/", Sizer = TestSizer)
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
    plt.savefig("./output/test_winrate.png")
    plt.close()
    plt.figure()
    test_res["年化收益率"][np.isinf(test_res["年化收益率"])] = 0
    test_res.年化收益率.plot(kind = "kde")
    plt.legend(loc = "best")
    plt.savefig("./output/test_ar.png")
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
    main()
