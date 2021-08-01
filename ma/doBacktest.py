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


class SmaCross(bt.Strategy):
    def log(self, txt, dt = None, doPrint = False):
        if doPrint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            
    def __init__(self):
        # 初始化数据
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
            
        # 五日均线
        self.sma5 = bt.indicators.SimpleMovingAverage(self.datas[0], period=5)
        # 二十日均线
        self.sma20 = bt.indicators.SimpleMovingAverage(self.datas[0], period=20)
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
                
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            self.bar_executed = len(self)
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
                
        self.order = None
            
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
            
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm),doPrint=True)
        
    def next(self):
        self.log("close %.2f" % self.dataclose[0])
        if self.order:
            return
            
        if not self.position:
            if self.sma5[0] > self.sma20[0]:
                self.order = self.buy()
        else:
            if self.sma5[0] < self.sma20[0]:
                self.order = self.sell()
                
    def stop(self):
        self.log(u'(金叉死叉有用吗) Ending Value %.2f' % (self.broker.getvalue()), doPrint=True)


@run.change_dir
def main():
    # 先初始化，准备数据
    tools.init()
    codes = tools.Research(refresh = False, month = 12, highPrice = 10.0)
    test_res = pd.DataFrame()
    n = len(codes)
    i = 0
    for code in codes:
        i += 1.0
        print("回测进度:", i/n*100)
        backtest = BackTest(codes = [code], strategy = st.MAcrossover)
        results = backtest.getResults()
        test_res = test_res.append(results)
    print(test_res.describe())
    plt.figure()
    test_res.胜率.plot(kind = "kde")
    test_res.年化收益率.plot(kind = "kde")
    plt.legend(loc = "best")
    plt.savefig("./output/test_res.png")
    
    
if __name__ == "__main__":
    main()
    