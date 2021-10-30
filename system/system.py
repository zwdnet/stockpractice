# coding:utf-8
# 1000元实盘练习程序
# 三重滤网交易系统实现


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import run
import tools
import talib
import math
import copy
import os
import quantstats


# 给股价数据增加均线
def add_ma(data, ma_short = 1, ma_long = 5):
    data["短期均线"] = pd.Series.rolling(data.收盘, window = ma_short).mean()
    data["长期均线"] = pd.Series.rolling(data.收盘, window = ma_long).mean()
    return data
    
    
# 计算均线在每个点的斜率
def add_slope(data):
    data["短期均线斜率"] = data.短期均线 - data.短期均线.shift(1)
    data["长期均线斜率"] = data.长期均线 - data.长期均线.shift(1)
    return data
    

# 计算日线数据的MACD信号
def add_macd(data):
    dif, dea, macd = talib.MACD(data.收盘, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    data["dif"] = dif
    data["dea"] = dea
    data["macd"] = macd
    return data
    
    
# 准备数据
@run.change_dir
def make_data(code, start_date = "20110101", end_date = "20210101", refresh = True):
    data_day = tools.getStockData(code, start_date = start_date, end_date = end_date, refresh = refresh, period = "daily")
    data_week = tools.getStockData(code, start_date = start_date, end_date = end_date, refresh = True, period = "weekly")
    data_week = add_ma(data_week)
    data_week = add_slope(data_week)
    data_day = add_ma(data_day)
    data_day = add_slope(data_day)
    data_day = add_macd(data_day)
    # data_choose = data_week[(data_week.短期均线斜率 > 0) & (data_week.长期均线斜率 > 0)]

    return data_day, data_week
    
    
# 计算并保存交易数据
class Broker():
    def __init__(self):
        self.init_data()
        
    def init_data(self):
        self._cash = 1000000 # 初始资金
        self._cash_init = 1000000
        self._commit_rate = 0.0006 # 佣金税收费率
        self._stocks = 0 # 持仓量
        self._cost = 0.0 # 交易成本
        self._value = 0.0 # 股票市值
        self._profit = 0.0 # 净收益
        self._buy_value = 0.0 # 买入后的总资产
        self._sell_value = 0.0 # 卖出后的总资产
        self._stoptimes = 0 # 止盈止损次数
        # self._date = None # 交易日期
        # 记录每次交易的结果
        self._hold_days = [] # 持股天数
        self._trade_profit = [] # 每次交易的收益(为负则是亏损)
        
        # 回测指标数据
        self._total_cash = [] # 总现金
        self._total_stock = [] # 总持股数
        self._total_value = [] # 总持仓市值
        self._total_profit = [] # 总盈利
        self._total_cost = [] # 总成本
        
    # 执行交易，记录结果
    def do_trade(self, direct, price, hold_days = -1, bStop = False):
        # 买入
        if direct == "buy":
            if self._stocks == 0:
                stocks = math.floor(self._cash/(100*price*(1+self._commit_rate)))*100
                if stocks*price*(1 + self._commit_rate) > self._cash:
                    stocks -= 100
            self._stocks = stocks
            self._value = self._stocks * price
            self._cost = self._value * self._commit_rate
            self._cash = self._cash - self._value - self._cost
            self._buy_value = self._cash + self._value
        # 卖出
        elif direct == "sell":
            if self._stocks != 0:
                self._value = self._stocks * price
                self._cost = self._value * self._commit_rate
                self._cash = self._cash + self._value - self._cost
                self._value = 0.0
                self._stocks = 0
                self._sell_value = self._cash + self._value
                self._profit = self._sell_value - self._buy_value
                self._trade_profit.append(self._profit)
                self._hold_days.append(hold_days)
                if bStop == True:
                    self._stoptimes += 1
        else:
            print("direct参数有误")
            
    # 记录交易数据
    def make_record(self, price):
        self._total_cash.append(self._cash)
        self._total_stock.append(self._stocks)
        self._total_value.append(self._stocks * price + self._cash)
        self._total_profit.append(self._stocks * price + self._cash - self._cash_init)
        self._total_cost.append(self._cost)
        
    # 返回回测指标
    def _get_results(self, days):
        # 统计计算回测结果    
        testResult = pd.DataFrame({
            "日期":days,
            "现金":self._total_cash,
            "股票数量":self._total_stock,
            "市值":self._total_value,
            "累积成本":self._total_cost,
            "累积收益":self._total_profit,
            "每日市值":self._total_value,
            "止盈止损次数":self._stoptimes
            })
        testResult.set_index(["日期"], inplace = True)
        return testResult
        
    # 生成回测数据
    def make_test_data(self, bench_data, code, days):
        testResult = self._get_results(days)
        result = pd.Series([], dtype='float64')
        result["股票代码"] = code
        returns, bench = self._daily_return_data(testResult, bench_data)
        result = self._risk_data(returns, bench, result)
        result = self._trade_data(result, testResult)
        result = self._profit_data(testResult, bench, result)
    
        return result
        
    # 生成收益率数据
    def _daily_return_data(self, testResult, bench_data):
        # 计算每日收益率
        profit_rate = testResult["每日市值"]/testResult["每日市值"].shift(1) - 1.0
        returns = pd.DataFrame()
        returns["日期"] = testResult.index.values
        returns["每日收益率"] = profit_rate.values
        returns.每日收益率.fillna(0.0, inplace = True)
    
        bench = bench_data[bench_data.日期.isin(returns.日期)]
        bench.每日收益率.fillna(0.0, inplace = True)
    
        returns.set_index(["日期"], inplace = True)
        bench.set_index(["日期"], inplace = True)
    
        return returns, bench
        
    # 计算风险回测指标
    def _risk_data(self, returns, bench, result):
        if returns.每日收益率.std() != 0.0:
            riskfact = self._risk_analyse(returns.每日收益率, bench.每日收益率)
            result["夏普比率"] = riskfact.夏普比率
            result["信息比例"] = riskfact.信息比例
            result["索提比率"] = riskfact.索提比率
            result["调整索提比率"] = riskfact.调整索提比率
            result["skew值"] = riskfact.skew值
            result["_calmar"] = riskfact._calmar
            result["α"] = riskfact.α
            result["β"] = riskfact.β
        else:
            result["夏普比率"] = 0.0
            result["信息比例"] = 0.0
            result["索提比率"] = 0.0
            result["调整索提比率"] = 0.0
            result["skew值"] = 0.0
            result["_calmar"] = 0.0
            result["α"] = 0.0
            result["β"] = 0.0
        
        return result
        
    # 计算各种回测指标
    def _risk_analyse(self, returns, bk_returns, rf = 0.02, periods = 242, annualize = True, trading_year_days = 242):
        # 计算夏普比率
        _sharpe = quantstats.stats.sharpe(returns = returns, rf = rf, periods = periods, annualize = True, trading_year_days = trading_year_days)
        # 计算αβ值
        _alphabeta = quantstats.stats.greeks(returns, bk_returns, periods = periods)
        # 计算信息比率
        _info = quantstats.stats.information_ratio(returns, bk_returns)
        # 索提比率
        _sortino = quantstats.stats.sortino(returns = returns, rf = 0.02, periods = periods, annualize = True, trading_year_days = trading_year_days)
        # 调整索提比率
        _adjustSt = quantstats.stats.adjusted_sortino(returns = returns, rf = rf, periods = periods, annualize = True, trading_year_days = trading_year_days)
        # skew值
        _skew = quantstats.stats.skew(returns = returns)
        # calmar值
        _calmar = quantstats.stats.calmar(returns = returns)
    
        results = pd.Series({
            "夏普比率": _sharpe,
            "α": _alphabeta[0],
            "β": _alphabeta[1],
            "信息比例": _info,
            "索提比率": _sortino,
            "调整索提比率": _adjustSt,
            "skew值": _skew,
            "_calmar": _calmar
        })
        return results
        
    # 生成交易数据
    def _trade_data(self, result, testResult):
        # 计算生成回测结果
        trade_profit = self._trade_profit
        win_times = len([i for i in trade_profit if i > 0])
        loss_times = len(trade_profit) - win_times
        win_money = sum([i for i in trade_profit if i > 0])
        loss_money = sum([i for i in trade_profit if i < 0])
        if loss_times == 0:
            winvsloss = np.nan         
            wmvslm = np.nan           
        else:
            winvsloss = win_times/loss_times
            wmvslm = abs(win_money)/abs(loss_money)
    
        if loss_times == 0:
            result["胜率"] = 0.0
            result["盈亏比"] = 0.0
        else:
            result["胜率"] = win_times/loss_times
            result["盈亏比"] = abs(win_money)/abs(loss_money)
        result["平均持股天数"] = np.mean(self._hold_days)
        if win_times == 0 and loss_times == 0:
            result["止盈止损占比"] = np.nan
        else:
            result["止盈止损占比"] = testResult["止盈止损次数"].values[0]/(win_times+loss_times)
        
        return result
        
    # 计算收益指标
    def _profit_data(self, testResult, bench, result):
        result["总收益"] = testResult["累积收益"][-1]
        result["总收益率"] = testResult["累积收益"][-1]/self._cash_init
        # 基准总收益率
        benchreturn = bench.收盘.values[-1]/bench.收盘.values[0] - 1.0
        result["策略基准收益差"] = result.总收益率 - benchreturn
        result["总成本"] = testResult["累积成本"][-1]
        if result["总收益"] == 0.0:
            result["成本盈利占比"] = np.nan
        else:
            result["成本盈利占比"] = result["总成本"]/result["总收益"]
        
        return result
        
        
# 封装回测过程
class Trade:
    def __init__(self):
        self._bIn = False
        self._bTrade = False
        self._buy_days = -1 # 买入时的索引
        self._buy_price = 0.0 # 买入价格
        self._stop_loss = 0.05 # 买入止损比例5%
        self._stop_profit = 0.1 # 止盈比例10%
        self._highest_price = 0.0 # 交易时的最高价
        self._bStop = False # 是否止盈止损

        
    # 具体交易过程
    def doTrade(self, broker, i, price):
        if self._bTrade == True and self._bIn == True:
            broker.do_trade("buy", price)
            self._buy_days = i
            self._buy_price = price
            self._highest_price = self._buy_price
            self._bTrade = False
        elif self._bTrade == True and self._bIn == False:
            broker.do_trade("sell", price, hold_days = i - self._buy_days + 1, bStop = self._bStop)
            # trade.append_hold_days(i - buy_days + 1)
            self._buy_days = -1
            self._highest_price = 0.0
            self._bTrade = False
            self._bStop = False
        
        
    # 记录最高价
    def record_highest_price(self, price):
        if price > self._highest_price:
            self._highest_price = price
        

    # 第一层滤网，周线层面上判断       
    def level1(self, week):
        judge = week["短期均线斜率"] > 0 and week["长期均线斜率"] > 0 and week["短期均线"] > week["长期均线"]
        return judge
    
    
    # 第二层滤网，日线层面上判断
    def level2(self, macd, dif, dea, i):
        return macd[i] > 0 and macd[i-1] < 0 and dif[i-1] < dea[i-1] and dif[i] > dea[i]
    
    
    # 止损
    def b_stop_loss(self, price):
        return (self._buy_price - price)/self._buy_price >= self._stop_loss
    
    
    # 止盈
    def b_stop_profit(self, price):
        return (self._highest_price - price)/self._highest_price >= self._stop_profit
    

    # 出场
    def b_out(self, macd, i):
        return (macd[i-2] < 0.0 and macd[i-1] < 0.0 and macd[i] < 0.0)
        
        
    # 具体策略
    def step(self, i, price, week, macd, dif, dea):
        judge = self.level1(week)
        if judge and self._bIn == False:
            if i >= 1:
                if self.level2(macd, dif, dea, i):    
                    # print("买点", day)
                    self._bIn = True
                    self._bTrade = True
                    return
        
        if self._bIn == True:
        # 判断是否到达止损止盈点
            # 低于买入价，按买入止损
            if price < self._buy_price:
                if self.b_stop_loss(price):
                    self._bStop = True
                    self._bIn = False
                    self._bTrade = True
                    return
            else: # 高于买入价，按浮盈止盈
                if self.b_stop_profit(price):
                    self._bStop = True
                    self._bIn = False
                    self._bTrade = True
                    return
            # 判断是否达到出场条件
            if i > 2:
                if self.b_out(macd, i):
                    # print("卖点", day
                    self._bIn = False
                    self._bTrade = True

        
# 实际进行回测过程
def test_process(data_day, data_week, broker):
    days, days_s_slop, days_l_slop, days_close, macd, dif, dea = make_temp_data(data_day, data_week)
    i = 0
    trade = Trade()
    
    for day in days:
        # print("bug测试", cash, cash_init)
        # 进行交易
        trade.doTrade(broker, i, days_close[i])

        broker.make_record(days_close[i])
        week = data_week[data_week.日期 <= day]
        trade.record_highest_price(days_close[i])
        if len(week) == 0:
            i += 1
            continue
        else:
            week = week.iloc[-1, :]
            # print(day, week)
        trade.step(i, days_close[i], week, macd, dif, dea)
        i += 1


# 生成临时数据
def make_temp_data(data_day, data_week):
    days = data_day["日期"].values
    days_s_slop = data_day["短期均线斜率"].values
    days_l_slop = data_day["长期均线斜率"].values
    days_close = data_day["收盘"].values
    macd = data_day["macd"].values
    dif = data_day["dif"].values
    dea = data_day["dea"].values
    return days, days_s_slop, days_l_slop, days_close, macd, dif, dea


# 对某只股票某个时间区间进行回测
def backtest(code, bench_data, start_date = "20110101", end_date = "20210101"):
    broker = Broker()
    data_day, data_week = make_data(code, start_date = start_date, end_date = end_date, refresh = False)
    test_process(data_day, data_week, broker)
    return broker.make_test_data(bench_data, code, data_day["日期"].values)
    
    
# 画图
@run.change_dir
def draw_results(result):
    # 用均值填充空值
    for column in list(result.columns[result.isnull().sum() > 0]):
        mean_val = result[column].mean()
        result[column].fillna(mean_val, inplace = True)

    drawing_process(result, result.总收益率, "总收益率")
    drawing_process(result, result.成本盈利占比, "成本盈利占比")
    drawing_process(result, result.胜率, "胜率")
    drawing_process(result, result.盈亏比, "盈亏比")
    drawing_process(result, result.平均持股天数, "平均持股天数")
    drawing_process(result, result.止盈止损占比, "止盈止损占比")
    drawing_process(result, result.夏普比率, "夏普比率")
    drawing_process(result, result.调整索提比率, "调整索提比率")
    drawing_process(result, result.α, "α值")
    drawing_process(result, result.β, "β值")
    drawing_process(result, result.策略基准收益差, "策略基准收益差")
    
    
# 具体作画过程
@run.change_dir
def drawing_process(result, data, title, bins = -1):
    plt.figure()
    if bins == -1:
        bins = math.floor(math.sqrt(len(data)))
    data.hist(bins = bins)
    plt.title(title)
    plt.savefig("./output/" + title + ".jpg")
    plt.close()
    print(title)
    print("平均值:", data.mean(), "最大值:", data.max(), "最大值的股票代码", result[data == data.max()].股票代码)
    
    
# 获取市场最新股票代码
def get_codes(refresh, start_date, end_date, month = 0, bSelect = False):
    codes = tools.Research(refresh = refresh, month = month, bSelect = bSelect, start_date = start_date, end_date = end_date)
    codes = codes[:]
    return codes
    
    
# 获取基准数据并计算基准收益率
def get_bench(refresh, month, start_date, end_date):
    # 下载沪深300数据
    benchcode = "000300"
    benchmark = tools.getStockData(benchcode, month = month, refresh = refresh, start_date = start_date, end_date = end_date, adjust = "hfq")
    
    # 计算基准指数的收益率
    benchrate = benchmark["收盘"]/benchmark["收盘"].shift(1) - 1.0
    bench_data = pd.DataFrame()
    bench_data["日期"] = benchmark.日期.values
    bench_data["每日收益率"] = benchrate.values
    bench_data["收盘"] = benchmark["收盘"].values
    
    return bench_data
    
    
# 进行回测
@run.change_dir
def do_backtest(retest, codes, bench_data):
    datafilepath = "./backtest.csv"
    # print(codes[:10], len(codes))
    if os.path.exists(datafilepath) and retest == False:
        test_res = pd.read_csv(datafilepath, converters = {'股票代码':str})
    else:
        test_res = pd.DataFrame()
        n = len(codes)
        i = 0
        for code in codes:
            i += 1.0
            print("回测进度:", i/n*100, "%")
            result = backtest(code = code, bench_data = bench_data)
            test_res = test_res.append(result, ignore_index = True)
        test_res.to_csv(datafilepath, index = False)
        
    return test_res

    
# 主函数
@run.change_dir
def main():
    tools.init()
    month = 0
    refresh = False
    retest = False
    start_date = "20110101"
    end_date = "20210101"
    codes = get_codes(refresh = refresh, month = month, start_date = start_date, end_date = end_date)
    bench_data = get_bench(refresh = refresh, month = month, start_date = start_date, end_date = end_date)
    test_res = do_backtest(retest = retest, codes = codes, bench_data = bench_data)
    # print(test_res)
    draw_results(test_res)


if __name__ == "__main__":
    main()