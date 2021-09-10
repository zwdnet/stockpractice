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
    # marketTest(refresh = False, retest = False)
    # select(refresh = True)
    haigui_decise(code = "600622", date = "2021-09-08", buyprice = 2.86)
    

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
    
    
# 判断海龟策略进场条件
@run.change_dir
def bIn(code, refresh, month):
    data = tools.getStockData(code, month = month, refresh = refresh, adjust = "qfq")
    # 计算参数
    # 20日内最高价
    period = 20
    # data["high"] = data.最高.rolling(period).max().shift(-1).values
    high = []
    j = 0
    for i in range(-len(data), 0):
        if j < period:
            high.append(np.nan)
            j += 1
            continue
        high.append(data.最高.values[i - period:i].max())
    # print(len(high))
    data["high"] = high
    # 计算均线值
    ma5 = data.收盘.rolling(5).mean().values
    ma20 = data.收盘.rolling(20).mean().values
    ma30 = data.收盘.rolling(30).mean().values
    ma60 = data.收盘.rolling(60).mean().values
    data["ma5"] = ma5
    data["ma20"] = ma20
    data["ma30"] = ma30
    data["ma60"] = ma60
    # print(code)
    # print(high, ma5, ma20, ma30, ma60)
    # 划分数据
    # data = data.iloc[-month*22:, :]
    # print(data.high, data.ma5, data.ma20, data.ma30, data.ma60)
    data["入场"] = data.收盘 > data.high
    res = data[data.入场 == True]
    # print(data.loc[:, ["high", "收盘", "入场"]])
    # plt.figure()
    # data.plot(x = "日期", y = ["high", "收盘", "ma5", "ma20", "ma30", "ma60"])
    # plt.savefig("./output/"+code+".jpg")
    if len(res) != 0:
        result = res.tail(1)
        # print(code)
        # print(result)
        if result.ma5.values[0] > result.ma20.values[0] and result.ma5.values[0] > result.ma30.values[0] and result.ma5.values[0] > result.ma60.values[0]:
            return None
        else:
            return result.日期.values[0], res.tail(1).high.values[0]
    else:
        return None
    # print(data.info())
    # print(data.head())
    # print(res.iloc)
    # print(data.describe())
    
    
# 用海龟法则选股进场
@run.change_dir
def select(refresh = False):
    month = 12
    codes = tools.Research(refresh = refresh, month = month, highPrice = 3.0, bSelect = True, path = "./stockdata/", drop_days = 20*month)
    n = len(codes)
    print(n)
    i = 0
    results = pd.DataFrame(columns = ["股票代码", "突破时间", "突破价格"])
    for code in codes:
        i += 1.0
        print("研究进度:", i/n*100, "%")
        res = bIn(code, refresh = refresh, month = month)
        if res is not None:
            results = results.append({"股票代码":code, "突破时间":res[0], "突破价格":res[1]}, ignore_index = True)
    results = results.sort_values(by = "突破时间")
    print(results)
    
    
# 计算海龟交易法的加仓，出场，止损点
@run.change_dir
def haigui_decise(code, date, buyprice = 0.0):
    month = 1
    data = tools.getStockData(code, month = month, refresh = True, adjust = "qfq")
    # 计算AR值
    # data = data[data.日期 <= date]
    n = len(data)
    data = data.loc[n-21:n-1, ["收盘", "最高", "最低"]]
    print(data)
    AR = []
    for i in range(n-1, n-21, -1):
        x1 = data.最高[i] - data.最低[i]
        x2 = np.abs(data.最高[i] - data.收盘[i-1])
        x3 = np.abs(data.最低[i] - data.收盘[i-1])
        x = max(x1, x2, x3)
        AR.append(x)
    ATR = np.mean(AR)
    low10 = data.最低.values[-10:].min()
    print(ATR, low10)
    if buyprice == 0.0:
        price = data.收盘.values[-1]
    else:
        price = buyprice
    addPrice1 = price + 0.5*ATR # 加仓价1
    addPrice2 = addPrice1 + 0.5*ATR # 加仓价2
    addPrice3 = addPrice2 + 0.5*ATR # 加仓价3
    outPrice = low10 # 出场价
    stopPrice = price - 2.0*ATR # 止损价
    print("加仓价格1:", addPrice1, "加仓价格2:", addPrice2, "加仓价格3:", addPrice3, "出场价格:", outPrice, "止损价格:", stopPrice)
    
    

if __name__ == "__main__":
    tools.init()
    main()
