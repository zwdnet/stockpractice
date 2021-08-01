# coding:utf-8
# 1000元实盘练习程序
# 测试backtrader，策略文件
# https://algotrading101.com/learn/backtrader-for-backtesting/


import backtrader as bt


class MyStrategy(bt.Strategy):
    def next(self):
        pass
        
        
class PrintClose(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        
    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(dt, txt)
        print(f'{dt.isoformat()} {txt} {self.dataclose[0]}')
        
    def next(self):
        self.log("close", self.datas[0].datetime.date(0))
        
        
# 移动均线策略
class MAcrossover(bt.Strategy):
    params = (('pfast', 5),
                       ('pslow', 20),
                       ('pstock', 10000))

    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(dt, txt)
        # print(f'{dt.isoformat()} {txt} {self.dataclose[0]}')
        
        
    def __init__(self):
        self.order = None
        self.bar_executed = len(self)
        self.slow_sma = list()
        self.fast_sma = list()
        self.crossover = list()
        self.total = 0
        for data in self.datas:
            self.slow_sma.append(bt.indicators.MovingAverageSimple(data, period=self.params.pslow))
            self.fast_sma.append(bt.indicators.MovingAverageSimple(data, period=self.params.pfast))
            self.crossover.append(bt.indicators.CrossOver(self.fast_sma[self.total], self.slow_sma[self.total]))
            self.total += 1
                        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            """
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            """
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        if not self.position:
            # if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
            for i in range(self.total):
                if self.crossover[i] > 0:
                    # self.log(f'BUY CREATE {self.datas[i].close:2f}')
                    self.order = self.buy(data = self.datas[i])
            # elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                elif self.crossover[i] < 0:
                    # self.log(f'SELL CREATE {self.datas[i].close:2f}')
                    self.order = self.sell(data = self.datas[i])
        else:
            if len(self) >= (self.bar_executed + 5):
                # self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()
            
            
class Screener_SMA(bt.Analyzer):
    params = (('period',20), ('devfactor',2),)
    
    def start(self):
        self.bband = {data: bt.indicators.BollingerBands(data, period=self.params.period, devfactor=self.params.devfactor) for data in self.datas}
        
    def stop(self):
        self.rets["over"] = list()
        self.rets["under"] = list()
        
        for data, band in self.bband.items():
            node = data._name, data.close[0], round(band.lines.bot[0], 2)
            if data > band.lines.bot:
                self.rets['over'].append(node)
            else:
                self.rets['under'].append(node)
                
                
class AverageTrueRange(bt.Strategy):
    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(dt, txt)
        print(f'{dt.isoformat()} {txt}')
        
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
    def next(self):
        for data in self.datas:
            dataclose = data.close
            datahigh = data.high
            datalow = data.low
            range_total = 0
            for i in range(-13, 1):
                true_range = datahigh[i] - datalow[i]
                range_total += true_range
            ATR = range_total / 14
            self.log(f'Close: {dataclose[0]:.2f}, ATR: {ATR:.4f}, Code: {data._name}')
        