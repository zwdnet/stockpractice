# coding:utf-8
# 1000元实盘练习程序
# 回测锤子线选股策略，策略文件


import backtrader as bt
import talib
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import run


class ChuiziStrategy(bt.Strategy):
    params = (('period', 5),
                       ('rate', 0.1),
                       ('stopup', 0.2),
                       ('stopdown', 0.1))
    
    def __init__(self):
        self.order = None
        self.orefs = list()
        self.days = 0
        self.开盘 = self.datas[0].open
        self.最高 = self.datas[0].high
        self.最低 = self.datas[0].low
        self.收盘 = self.datas[0].close
        self.成交量 = self.datas[0].volume
        self.成交量均线 = bt.indicators.MovingAverageSimple(self.成交量, period=self.params.period)
        # 计算是否为锤子形态
        self.result = bt.talib.CDLHAMMER(self.开盘, self.最高, self.最低, self.收盘)
        
    # 判断是否是买点
    def judgeBuy(self):
        # 出现锤子线且放量，买点
        if self.result[0] != 0 and self.成交量[0] > (1+self.params.rate)*self.成交量均线[0]:
            return 1
        return -1
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            # print(self.data.datetime.date(0))
            # print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # print("交易失败!")
            self.order = None
        
    def next(self):
        # print(self.datas[0].datetime.date(0), self.result[0], self.成交量均线[0], self.judgeBuy(), self.成交量[0]/self.成交量均线[0])
        self.days += 1
        if self.order:
            return
            
        if not self.position:
            if self.judgeBuy() == 1:
                p1 = self.datas[0].close
                p2 = p1*(1+self.params.stopup) # 止盈价
                p3 = p1*(1-self.params.stopdown) # 止损价
                buy_ord = self.buy_bracket(limitprice = p2, stopprice = p3, exectype = bt.Order.Market)
            """
                self.order = self.buy(data = self.datas[0])
                self.days = 0
        elif self.days >= 20:
            self.order = self.sell(data = self.datas[0])
            self.days = 0

            """
            """
                p1 = self.datas[0].close
                p2 = p1*(1+0.2) # 止盈20%
                p3 = p1*(1-0.1) # 止损10%
                valid = datetime.timedelta(1000)
                o1 = self.buy(exectype=bt.Order.Market,
                                  valid = valid,
                                  price=p1,
                                  transmit=False)
                o2 = self.sell(exectype=bt.Order.Stop,
                                   valid = valid,
                                   price=p2,
                                   parent=o1,
                                   transmit=False)
                o3 = self.sell(exectype=bt.Order.Stop,
                                   valid = valid,
                                   price=p3,
                                   parent=o1,
                                   transmit=False)
                self.ores = [o1.ref, o2.ref, o3.ref]
                """
                
    def stop(self):
        self.order = self.close()
        # print("期末资产金额:", self.broker.getvalue(), "参数:", "成交量均线周期:", self.params.period, "成交量比例:", self.params.rate, "止盈比例:", self.params.stopup, "止损比例:", self.params.stopdown)
        
        
# 判断牛熊指标策略，来自《阿佩尔均线操盘术》        
class CYBStrategy(bt.Strategy):
    def __init__(self):
        self.strategy = pd.read_csv("./strategy.csv")
        self.strategy.日期 = pd.to_datetime(self.strategy.日期)
        self.close = self.datas[0].close
        self.n = 0
        self.order = None
        
        
    def next(self):
        if self.order:
            return
        # print(self.broker.cash, self.datas[0].close[0])
        diff = self.datas[0].datetime.date(0) - self.strategy.日期[self.n].date()
        # if self.n > 60:
        #    print(diff.days, self.datas[0].datetime.date(0), self.strategy.日期[self.n].date())
        #    input("按任意键继续")
        if diff.days >= 0:
            if self.strategy.buy[self.n] == 1 and not self.position:
                self.order = self.buy(data = self.datas[0])
            elif self.strategy.buy[self.n] == 2 and self.position:
                self.order = self.sell(data = self.datas[0])
            if self.n < len(self.strategy) - 1:
                self.n += 1
                
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            print(self.data.datetime.date(0))
            print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print("交易失败!", order.status)
            self.order = None
            
    def stop(self):
        self.order = self.close()
        
        
# 均线策略
class MA(bt.Strategy):
    params = (('period', 30),)
    
    def __init__(self):
        self.order = None
        self.收盘 = self.datas[0].close
        self.ma = bt.indicators.MovingAverageSimple(self.收盘, period=self.params.period)
        
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.收盘[0] > self.ma[0]:
                self.order = self.buy(data = self.datas[0])
        else:
            if self.收盘[0] < self.ma[0]:
                self.order = self.sell(data = self.datas[0])
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            # print(self.data.datetime.date(0))
            # print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print("交易失败!", order.status)
            self.order = None
            
    def stop(self):
        self.order = self.close()
        
        
# 三重动量择时策略
class ThreeMovement(bt.Strategy):
    params = (("ma1", 5),
              ("ma2", 15),
              ("ma3", 25),
              ("rate", 0.04))
              
    def __init__(self):
        self.order = None
        self.close = self.datas[0].close
        self.price = []
        self.indicators = []
        self.rateline = []
        self.i = 0
        
    def next(self):
        if self.order:
            return
        # 计算指标
        self.ma1 = (self.close[0] - self.close[-self.params.ma1])/self.close[-self.params.ma1]
        self.ma2 = (self.close[0] - self.close[-self.params.ma2])/self.close[-self.params.ma2]
        self.ma3 = (self.close[0] - self.close[-self.params.ma3])/self.close[-self.params.ma3]
        indicator = self.ma1 + self.ma2 + self.ma3
        self.price.append(self.close[0])
        scale = 3000
        baseline = self.params.rate*scale
        self.indicators.append(indicator*scale)
        self.rateline.append(baseline)
        # 计算信号
        if self.i < self.params.ma3:
            self.i += 1
            return
        signal = 0
        # 由下向上突破基准，买入
        if self.indicators[-2] <= baseline and self.indicators[-1] > baseline:
            signal = 1
        # 由上向下突破基准，卖出
        elif self.indicators[-2] > baseline and self.indicators[-1] <= baseline:
            signal = 2
            
        # 根据持仓情况决策
        if not self.position and signal == 1:
            self.order = self.buy(data = self.datas[0])
        if self.position and signal == 2:
            self.order = self.sell(data = self.datas[0])
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            # print(self.data.datetime.date(0))
            # print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print("交易失败!", order.status)
            self.order = None
        
    @run.change_dir    
    def stop(self):
        self.order = self.close()
        plt.plot(self.price, label = "股价")
        plt.plot(self.indicators, label = "指标")
        plt.plot(self.rateline, label = "基线")
        plt.legend(loc = "best")
        plt.savefig("./output/var.jpg")
        
        
# 测试backtrader框架用的策略        
class TestBT(bt.Strategy):
    def __init__(self):
        self.order = None
        self.close = self.datas[0].close
        
    def start(self):
        self.order = self.buy(data = self.datas[0])
        
    def next(self):
        if self.order:
            return
            
        if not self.position:
            self.order = self.buy()
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.order = None
            # print(self.data.datetime.date(0))
            # print("买入"*order.isbuy() or "卖出\n")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print("交易失败!", order.status)
            self.order = None
            
    def notify_fund(self, cash, value, fundvalue, shares):
        # print("策略测试进行中, ",cash, value, fundvalue, shares, self.close[0])
        pass
        
    def notify_order(self, order):
        # print("交易信息", order.executed.size, order.executed.price)
        pass
            
    def stop(self):
        self.order = self.close()