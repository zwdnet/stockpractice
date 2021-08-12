# coding:utf-8
# 1000元实盘练习程序
# 回测锤子线选股策略，策略文件


import backtrader as bt
import talib
import numpy as np
import datetime


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
        