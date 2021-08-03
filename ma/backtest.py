# coding:utf-8
# 1000元实盘练习程序
# 封装backtrader回测过程


import pandas as pd
import backtrader as bt
import run
import tools
import strategy as st
import matplotlib.pyplot as plt
# 文档地址: https://github.com/ranaroussi/quantstats
import quantstats
import imgkit
import os
from PIL import Image



# 封装BackTrader回测过程的类
class BackTest:
    def __init__(self, codes, strategy, cash = 1000, commission = 0.0006, stake = 100, riskfree = 0.0):
        self.cash = cash
        self.commission = commission
        self.codes = codes
        self.strategy = strategy
        self.stake = stake
        self.cerebro = None
        self.results = None
        self.totalTrade = None
        self.rf = riskfree
        self.initBT()
        
    # 初始化BackTrader
    def initBT(self):
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.setcommission(self.commission)
        self.cerebro.addsizer(bt.sizers.SizerFix, stake = self.stake)
        # 准备数据
        for code in self.codes:
            data = self.data_transform(code)
            self.cerebro.adddata(data, name = code)
        self.cerebro.addstrategy(self.strategy)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name = "TA")
            
    # 数据转换
    @run.change_dir
    def data_transform(self, code):
        data_df = tools.getStockData(code)
        data = bt.feeds.PandasData(
            dataname=data_df,
            name=code,
            fromdate=data_df.日期[0],
            todate=data_df.日期[len(data_df) - 1],
            datetime='日期',
            open='开盘',
            high='最高',
            low='最低',    
            close='收盘',
            volume='成交量',
            openinterest=-1
        )
        return data
            
    # 运行回测
    def __run(self):
        # print("正在执行回测")
        self.results = self.cerebro.run()
        portfolio_stats = self.results[0].analyzers.getbyname('PyFolio')
        self.returns, self.positions, self.transactions, self.gross_lev = portfolio_stats.get_pf_items()
        self.returns.index = self.returns.index.tz_convert(None)
        self.totalTrade = self.results[0].analyzers.getbyname("TA").get_analysis()
        # print("测试", self.totalTrade.get_analysis()["total"]["total"])
        # print("回测执行完毕")
        
    # 获取回测结果
    def getResults(self):
        if self.results is None:
            self.__run()
        # print("测试", self.codes[0])
        results = pd.Series(
        {
         "股票代码":self.codes[0],
         "交易次数":self.totalTrade["total"]["total"],
         "胜率":quantstats.stats.win_rate(returns = self.returns),
         "胜负比率":quantstats.stats.profit_ratio(returns = self.returns),
         "赢率":quantstats.stats.win_loss_ratio(returns = self.returns),
         "平均收益":quantstats.stats.avg_win(returns = self.returns),
         "平均损失":quantstats.stats.avg_loss(returns = self.returns),
         "年化收益率":quantstats.stats.cagr(returns = self.returns, rf = self.rf),
         "期末收益率":self.returns[-1],
         "夏普比例":quantstats.stats.sharpe(returns = self.returns, rf = self.rf),
         "索提比例":quantstats.stats.sortino(returns = self.returns, rf = self.rf),
         "调整索提比例":quantstats.stats.adjusted_sortino(returns = self.returns, rf = self.rf),
          "skew":quantstats.stats.skew(returns = self.returns),
          "calmar":quantstats.stats.calmar(returns = self.returns),
          "最大回撤":quantstats.stats.max_drawdown(prices = self.returns)})
        # 获取交易成本
        # self.results[0].analyzers.TA.print()
        results.name = self.codes[0]
        # results.index.name = "股票代码"
        return results
        
    # 制作回测报告
    @run.change_dir
    def __drawReport(self, filename = "backtestStat.png", bDraw = False):
        if self.results is None:
            self.__run()
        
        if bDraw:
            quantstats.reports.html(self.returns, output='./output/stats.html', title='SMA Sentiment', rf = self.rf)
            imgkit.from_file("./output/stats.html", "./output/" + filename, options = {"xvfb": ""})
            # 压缩图片文件
            im = Image.open("./output/" + filename)
            im.save("./output/" + filename, quality=0.05)
            os.system("rm ./output/stats.html")
        
    # 作图画出回测结果
    @run.change_dir
    def drawResults(self, filename = "backtestRes.png"):
        if self.results is None:
            self.__run()
        self.cerebro.plot()
        plt.savefig("./output/" + filename)
        self.__drawReport(bDraw = True)
        
        
if __name__ == "__main__":
    # main()
    backtest = BackTest(codes = ["002166"], strategy = st.MAcrossover)
    backtest.drawResults()
    results = backtest.getResults()
    print(results)
        