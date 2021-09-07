# coding:utf-8
# 1000元实盘练习程序
# 封装backtrader回测过程


import pandas as pd
import backtrader as bt
import run
import tools
import matplotlib.pyplot as plt
# 文档地址: https://github.com/ranaroussi/quantstats
import quantstats
import imgkit
import os
from PIL import Image
import math
import pyfolio as pf


# 基准测试类   
# 买入持有策略
class BmStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        # self.bBuy = False
        self.dataclose = self.datas[0].close
        self.cheat_on_open = False
        
    def start(self):
        if self.cheat_on_open:
            self.order = self.buy(data = self.datas[0])
 
    def next(self):
        if self.order:
            return
        if not self.position:
            cash = self.broker.get_cash()
            stock = math.ceil((cash/self.dataclose[0] - 100)/100)*100
            # print("回测基准策略", stock, cash, self.dataclose[0], stock*self.dataclose[0])
            self.order = self.buy(size = stock, price = self.datas[0].close) 
                
            # self.bBuy = True
            
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
                stock = math.ceil((cash/self.dataclose[0] - 100)/100)*100*0.90
                self.order = self.buy(size = stock, price = self.datas[0].close)
                # print("现金不足，新购入数量为:", stock)
                return
            else:
                print("交易被拒绝\n")
            
            self.order = None
            
    def notify_fund(self, cash, value, fundvalue, shares):
        # print("基准测试进行中, ",cash, value, fundvalue, shares)
        pass
 
    def stop(self):
        self.order = self.close()


# 封装BackTrader回测过程的类
class BackTest:
    def __init__(self, codes, strategy, benchmark = None, month = 0, path = "./pooldata/", cash = 1000, commission = 0.0006, stake = 100, riskfree = 0.0, refresh = False, bOpt = False, bData = False, data = None, cheat_on_open = False, start_date = "19000101", end_date = "21000101", days = 242, Sizer = None):
        self.cash = cash # 资金量
        self.totalcash = cash  # 总现金
        self.commission = commission # 手续费比率
        self.codes = codes  # 股票或指数代码
        self.strategy = strategy # 策略
        self.stake = stake # 交易规模
        self.cerebro = None  # 回测类
        self.results = None  # 回测结果
        self.bm_results = None # 基准回测结果
        self.totalTrade = None # 交易次数
        self.bm = None  # 基准类
        self.benchmark = benchmark # 基准数据，由调用者提供
        self.rf = riskfree # 无风险收益率
        self.month = month # 回测月数，如为0则需定义起始日期
        self.path = path # 数据文件保存路径
        self.refresh = refresh # 是否下载更新数据
        self.bOpt = bOpt # 是否进行参数优化
        self.bData = bData # 是否由调用者直接提供数据
        self.data = data # 调用者提供的数据
        self.cheat_on_open = cheat_on_open # 是否开启开盘即买入作弊模式
        self.start = start_date # 回测开始日期
        self.end = end_date # 回测结束日期
        self.days = days # 每年的交易天数，用于计算回测指标，按中国股市默认为242天/年
        self.Sizer = Sizer # 头寸规模
        self.initBT()
        
    # 初始化BackTrader
    def initBT(self):
        self.cerebro = bt.Cerebro(cheat_on_open = self.cheat_on_open)
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.setcommission(self.commission)
        if self.Sizer is None:
            self.cerebro.addsizer(bt.sizers.SizerFix, stake = self.stake)
        else:
            self.cerebro.addsizer(self.Sizer)
        # 准备数据
        for code in self.codes:
            if self.bData == True and self.data is not None:
                data_df = self.data
            else:
                data_df = tools.getStockData(code = code, path = self.path, month = self.month, refresh = self.refresh, start_date = self.start, end_date = self.end)
            # print("测试输出数据大小", len(data_df))
            data = self.data_transform(code, data_df)
            self.cerebro.adddata(data, name = code)
        if self.bOpt == False:
            self.cerebro.addstrategy(self.strategy)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name = "TA")
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name = "TR")
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name = "SQN")
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name = "Returns", tann = self.days)
        # 初始化基准数据
        self.bm = bt.Cerebro(cheat_on_open = self.cheat_on_open)
        self.bm.broker.setcash(self.cash)
        self.bm.broker.setcommission(self.commission)
        self.bm.addsizer(bt.sizers.SizerFix, stake = self.stake)
        # 准备数据
        # print("基准数据", self.benchmark.info())
        data = self.data_transform("BenchMark", self.benchmark)
        self.bm.adddata(data, name = "BenchMark")
        # 添加策略和分析器
        self.bm.addstrategy(BmStrategy)
        self.bm.addanalyzer(bt.analyzers.TimeReturn, _name = "TR")
        
        
    # 参数优化
    def optRun(self, *args, **kwargs):
        if self.bOpt:
            self.cerebro.optstrategy(self.strategy, *args, **kwargs)
            runs = self.cerebro.run()
            finial_results = []
            params_name = list(runs[0][0].params._getkeys())
            params_num = len(params_name)
            # print(params_name)
            for run in runs:
                for strategy in run:
                    returns, positions, transactions, gross_lev = list(strategy.analyzers)[0].get_pf_items()
                    returns.index = returns.index.tz_convert(None)
                    ar = quantstats.stats.cagr(returns = returns, rf = self.rf)
                    params_value = strategy.params._getvalues()
                    temp = [0]*(params_num+1)
                    for i in range(params_num):
                        temp[i] = (params_name[i], params_value[i])
                    temp[params_num] = ar
                    finial_results.append(temp)
            sort_results = sorted(finial_results, key=lambda x: x[params_num], reverse=True)
            # print("测试:", sort_results[:5])
            return sort_results
        return 0
        
            
    # 数据转换
    @run.change_dir
    def data_transform(self, code, data_df):
        # print(code, data_df.info())
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
        self._SQN = self.results[0].analyzers.SQN.get_analysis()["sqn"]
        self._Returns = self.results[0].analyzers.Returns.get_analysis()
        
        # print("测试", self.totalTrade.get_analysis()["total"]["total"])
        # print("回测执行完毕")
        # 运行基准回测
        self.bm_results = self.bm.run()
        self.ret = pd.Series(self.results[0].analyzers.TR.get_analysis())
        self.bm_ret = pd.Series(self.bm_results[0].analyzers.TR.get_analysis())
        # 累积收益
        self._cumRet = ((1+self.ret).cumprod() - 1)[-1]
        # 计算风险指标
        self.__riskAnalyzer()
        # print("策略收益序列:", self.returns)
        # print("分析器返回收益策略:", self.ret)

        
    # 计算风险分析
    def __riskAnalyzer(self):
        # print("测试", self.ret.head(), self.bm_ret)
        # 计算夏普比率
        if self.ret.std() == 0.0:
            self._sharpe = 0.0
        else:
            self._sharpe = quantstats.stats.sharpe(returns = self.ret, rf = self.rf, periods = self.days, annualize = True, trading_year_days = self.days)
        # 计算αβ值
        self._alphabeta = quantstats.stats.greeks(self.ret, self.bm_ret, periods = self.days)
        # 计算信息比率
        self._info = quantstats.stats.information_ratio(self.ret, self.bm_ret)
        # 索提比率
        self._sortino = quantstats.stats.sortino(returns = self.ret, rf = self.rf, periods = self.days, annualize = True, trading_year_days = self.days)
        # 调整索提比率
        self._adjustSt = quantstats.stats.adjusted_sortino(returns = self.ret, rf = self.rf, periods = self.days, annualize = True, trading_year_days = self.days)
        # skew值
        self._skew = quantstats.stats.skew(returns = self.ret)
        # calmar值
        self._calmar = quantstats.stats.calmar(returns = self.ret)
        
        
    # 获取回测结果
    def getResults(self):
        if self.results is None:
            self.__run()
        # print("测试", self.codes[0])
        cost = abs(self.transactions.value).sum() * self.commission
        results = pd.Series(
        {
         "股票代码":self.codes[0],
         "交易次数":self.totalTrade["total"]["total"],
         "胜率": quantstats.stats.win_rate(returns = self.returns),
         "盈亏率比": quantstats.stats.profit_ratio(returns = self.ret),
         "盈亏比": quantstats.stats.win_loss_ratio(returns = self.ret),
         "盈亏次数比": quantstats.stats.profit_factor(returns = self.ret),
         "平均收益": quantstats.stats.avg_win(returns = self.returns),
         "平均损失": quantstats.stats.avg_loss(returns = self.returns),
         "年化收益率": self._Returns["rnorm"], 
         "累积收益":self._cumRet,
         "收益标准差": self.ret.std(),
         "交易成本":cost,
         "收益占交易成本的比例":self.totalcash/self._cumRet/cost,
         "夏普比例":self._sharpe,
         "索提比例":self._sortino,
         "调整索提比例":self._adjustSt,
         "skew":self._skew,
         "calmar":self._calmar,
         "Alpha":self._alphabeta.alpha,
         "Beta":self._alphabeta.beta,
         "信息比率":self._info,
         "SQN":self._SQN,
         "最大回撤": quantstats.stats.max_drawdown(prices = self.returns)})
        results.name = self.codes[0]
        return results
        
    # 制作回测报告
    @run.change_dir
    def __drawReport(self, filename = "backtestStat.jpg", bDraw = False):
        if self.results is None:
            self.__run()
        
        if bDraw:
            quantstats.reports.html(self.returns, benchmark = self.bm_ret, rf = self.rf, output='./output/stats.html', title='BackTest Results', trading_year_days = self.days)
            imgkit.from_file("./output/stats.html", "./output/" + filename, options = {"xvfb": ""})
            # 压缩图片文件
            im = Image.open("./output/" + filename)
            im.save("./output/" + filename)
            # im.save("./output/" + filename, quality=0.05)
            os.system("rm ./output/stats.html")
        
    # 作图画出回测结果
    @run.change_dir
    def drawResults(self, filename = "backtestRes.jpg"):
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
        