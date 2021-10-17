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
def addMA(data, ma_short = 1, ma_long = 5):
    data["短期均线"] = pd.Series.rolling(data.收盘, window = ma_short).mean()
    data["长期均线"] = pd.Series.rolling(data.收盘, window = ma_long).mean()
    return data
    
    
# 计算均线在每个点的斜率
def addSlope(data):
    data["短期均线斜率"] = data.短期均线 - data.短期均线.shift(1)
    data["长期均线斜率"] = data.长期均线 - data.长期均线.shift(1)
    return data
    

# 计算日线数据的MACD信号
def addMACD(data):
    dif, dea, macd = talib.MACD(data.收盘, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    # print(macd[:100], signal[:100], hist[:100])
    data["dif"] = dif
    data["dea"] = dea
    data["macd"] = macd
    return data
    
    
# 准备数据
@run.change_dir
def makeData(code, start_date = "20110101", end_date = "20210101", refresh = True):
    data_day = tools.getStockData(code, start_date = start_date, end_date = end_date, refresh = refresh, period = "daily")
    data_week = tools.getStockData(code, start_date = start_date, end_date = end_date, refresh = True, period = "weekly")
    # print(len(data_day), len(data_week))
    # print(data_day.head(), data_week.head())
    data_week = addMA(data_week)
    data_week = addSlope(data_week)
    data_day = addMA(data_day)
    data_day = addSlope(data_day)
    data_day = addMACD(data_day)
    # print(data_day.info(), data_day.head())
    # print(data_week.info(), data_week.head())
    # print(data_week.loc[:, ["日期", "短期均线", "短期均线斜率", "长期均线", "长期均线斜率"]])
    data_choose = data_week[(data_week.短期均线斜率 > 0) & (data_week.长期均线斜率 > 0)]
    # print(data_choose.loc[:, ["日期", "短期均线", "短期均线斜率", "长期均线", "长期均线斜率"]])
    return data_day, data_week
    
    
# 全局变量，回测用的
cash = 1000000 # 初始资金
cash0 = 1000000
commit_rate = 0.0006 # 佣金税收费率
stocks = 0 # 持仓量
cost = 0.0 # 交易成本
value = 0.0 # 股票市值
profit = 0.0 # 净收益
buy_value = 0.0 # 买入后的总资产
sell_value = 0.0 # 卖出后的总资产
# 记录每次交易的结果
td = [] # 持股天数
tp = [] # 每次交易的收益(为负则是亏损)


# 初始化全局变量
def initGlobal():
    global cash, cash0, commit_rate, stocks, cost, value, profit, sell_value, buy_value, td, tp
    cash = 1000000 # 初始资金
    cash0 = 1000000
    commit_rate = 0.0006 # 佣金税收费率
    stocks = 0 # 持仓量
    cost = 0.0 # 交易成本
    value = 0.0 # 股票市值
    profit = 0.0 # 净收益
    buy_value = 0.0 # 买入后的总资产
    sell_value = 0.0 # 卖出后的总资产
    # 记录每次交易的结果
    td = [] # 持股天数
    tp = [] # 每次交易的收益(为负则是亏损)
    
    
# 执行交易，记录结果
def doTrade(date, direct, price):
    global stocks, cash, cost, value, buy_value, sell_value, profit, tp
    # print("交易函数收到参数:", date, direct, price)
    # print("持仓状态", stocks)
    if direct == "buy":
        if stocks == 0:
            stocks = math.floor(cash/(100*price))*100
            if stocks*price*(1+commit_rate) > cash:
                stocks -= 100
            value = stocks*price
            cost = value*commit_rate
            cash = cash - value - cost
            buy_value = cash + value
            # print(date, "以", price, "买入")
            # print(cash, stocks, value)
    elif direct == "sell":
        if stocks != 0:
            value = stocks*price
            cost = value*commit_rate
            cash = cash + value - cost
            value = 0.0
            stocks = 0
            sell_value = cash + value
            profit = sell_value - buy_value
            # print(date, "以", price, "卖出")
            # print(cash, stocks, value)
            tp.append(profit)
    else:
        print("direct参数有误")
    

# 对某只股票某个时间区间进行回测
def test(code, benchdata, start_date = "20110101", end_date = "20210101"):
    initGlobal()
    data_day, data_week = makeData(code, start_date = start_date, end_date = end_date, refresh = False)
    # print(data_day.info(), data_week.info())
    days = data_day["日期"].values
    days_s_slop = data_day["短期均线斜率"].values
    days_l_slop = data_day["长期均线斜率"].values
    days_close = data_day["收盘"].values
    macd = data_day["macd"].values
    dif = data_day["dif"].values
    dea = data_day["dea"].values
    # print(len(days), days[0])
    # data_temp = data_week[data_week.日期 <= days[0]]
    # if len(data_temp) != 0:
    #     print(data_week[data_week.日期 <= days[0]])
    # 全局变量
    global stocks, cash, cost, value, profit, td, tp
    # 回测指标数据
    # cash0 = copy.deepcopy(cash)
    total_cash = [] # 总现金
    total_stock = [] # 总持股数
    total_value = [] # 总持仓市值
    total_profit = [] # 总盈利
    total_cost = [] # 总成本
    
    i = 0
    bIn = False
    bTrade = False
    bd = -1 # 买入时的索引
    buy_price = 0.0 # 买入价格
    stop_loss = 0.05 # 买入止损比例5%
    stop_profit = 0.1 # 止盈比例10%
    highest_price = 0.0 # 交易时的最高价
    stoptimes = 0 # 止损止盈卖出次数
    for day in days:
        # print("bug测试", cash, cash0)
        # 进行交易
        if bTrade == True and bIn == True:
            doTrade(day, "buy", days_close[i])
            bd = i
            buy_price = days_close[i]
            highest_price = buy_price
            bTrade = False
        elif bTrade == True and bIn == False:
            doTrade(day, "sell", days_close[i])
            td.append(i - bd + 1)
            bd = -1
            highest_price = 0.0
            bTrade = False
        # 记录
        total_cash.append(cash)
        total_stock.append(stocks)
        total_value.append(stocks*days_close[i] + cash)
        total_profit.append(stocks*days_close[i] + cash-cash0)
        total_cost.append(cost)
        week = data_week[data_week.日期 <= day]
        if days_close[i] > highest_price:
            highest_price = days_close[i]
        if len(week) == 0:
            i += 1
            continue
        else:
            week = week.iloc[-1, :]
            # print(day, week)
        judge = week["短期均线斜率"] > 0 and week["长期均线斜率"] > 0 and week["短期均线"] > week["长期均线"]
        if judge and bIn == False:
           if i >= 1:
               if macd[i] > 0 and macd[i-1] < 0 and dif[i-1] < dea[i-1] and dif[i] > dea[i]:    
                   # print("买点", day)
                   bIn = True
                   bTrade = True
                   continue
        
        if bIn == True:
            # 判断是否到达止损止盈点
            # 低于买入价，按买入止损
            if days_close[i] < buy_price:
                if (buy_price - days_close[i])/buy_price >= stop_loss:
                    bStop = True
                    stoptimes += 1
                    bIn = False
                    bTrade = True
                    continue
            else: # 高于买入价，按浮盈止盈
                if (highest_price - days_close[i])/highest_price >= stop_profit:
                    bStop = True
                    stoptimes += 1
                    bIn = False
                    bTrade = True
                    continue
            # 判断是否达到出场条件
            if i > 2:
                if (macd[i-2] < 0.0 and macd[i-1] < 0.0 and macd[i] < 0.0):
                   # print("卖点", day
                   bIn = False
                   bTrade = True
        i += 1
        
    # 统计计算回测结果    
    testResult = pd.DataFrame({
        "日期":days,
        "现金":total_cash,
        "股票数量":total_stock,
        "市值":total_value,
        "累积成本":total_cost,
        "累积收益":total_profit,
        "每日市值":total_value
    })
    testResult.set_index(["日期"], inplace = True)
    win_times = len([i for i in tp if i > 0])
    loss_times = len(tp) - win_times
    win_money = sum([i for i in tp if i > 0])
    loss_money = sum([i for i in tp if i < 0])
    if loss_times == 0:
        winvsloss = np.nan         
        wmvslm = np.nan           
    else:
        winvsloss = win_times/loss_times
        wmvslm = abs(win_money)/abs(loss_money)          
    # print("交易次数:", win_times+loss_times, "盈利次>数:", win_times, "亏损次数:", loss_times, "盈利总金额:", win_money, "亏损总金额:", loss_money, "赢率:", winvsloss, "盈亏比:", wmvslm , "平均持股天数:", np.mean(td), "止损止盈卖出次数:", stoptimes)
    # print(testResult.info(), testResult.tail())
    
    # 生成回测返回的数据
    # 要计算的指标:年化收益率，总收益，总成本，胜率，赔率(盈亏比)，平均持仓时间，止盈止损(非计划)卖出次数占比等。
    # 计算每日收益率
    retrate = testResult["每日市值"]/testResult["每日市值"].shift(1) - 1.0
    ret = pd.DataFrame()
    # print(testResult.info())
    ret["日期"] = testResult.index.values
    ret["每日收益率"] = retrate.values
    ret.每日收益率.fillna(0.0, inplace = True)
    # print("每日收益率", len(ret), ret.head())
    
    bench = benchdata[benchdata.日期.isin(ret.日期)]
    bench.每日收益率.fillna(0.0, inplace = True)
    # print("测试", benchdata.日期.isin(ret.日期.values))
    # print(len(bench), len(ret))
    
    ret.set_index(["日期"], inplace = True)
    bench.set_index(["日期"], inplace = True)
    if ret.每日收益率.std() != 0.0:
        riskfact = riskAnaly(ret.每日收益率, bench.每日收益率)
    # 基准总收益率
    benchreturn = bench.收盘.values[-1]/bench.收盘.values[0] - 1.0
    # print("风险回测结果:", riskfact)
    
    result = pd.Series([], dtype='float64')
    result["股票代码"] = code
    result["总收益"] = total_profit[-1]
    result["总收益率"] = total_profit[-1]/cash0
    result["策略基准收益差"] = result.总收益率 - benchreturn
    # print("bug测试", total_profit[-1], cash0, total_profit[-1]/cash0, result["总收益率"])
    result["总成本"] = total_cost[-1]
    if result["总收益"] == 0.0:
        result["成本盈利占比"] = np.nan
    else:
        result["成本盈利占比"] = result["总成本"]/result["总收益"]
    if loss_times == 0:
        result["胜率"] = 0.0
        result["盈亏比"] = 0.0
    else:
        result["胜率"] = win_times/loss_times
        result["盈亏比"] = abs(win_money)/abs(loss_money)
    result["平均持股天数"] = np.mean(td)
    if win_times == 0 and loss_times == 0:
        result["止盈止损占比"] = np.nan
    else:
        result["止盈止损占比"] = stoptimes/(win_times+loss_times)
    if ret.每日收益率.std() != 0.0:
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
def riskAnaly(returns, bk_returns, rf = 0.02, periods = 242, annualize = True, trading_year_days = 242):
    # 计算夏普比率
    _sharpe = quantstats.stats.sharpe(returns = returns, rf = rf, periods = periods, annualize = True, trading_year_days = trading_year_days)
    print("函数内", returns.shape, returns[0], bk_returns.shape, bk_returns[0])
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
    
    
# 画图
@run.change_dir
def drawResults(result):
    # 用均值填充空值
    for column in list(result.columns[result.isnull().sum() > 0]):
        mean_val = result[column].mean()
        result[column].fillna(mean_val, inplace = True)

    draw(result, result.总收益率, "总收益率")
    draw(result, result.成本盈利占比, "成本盈利占比")
    draw(result, result.胜率, "胜率")
    draw(result, result.盈亏比, "盈亏比")
    draw(result, result.平均持股天数, "平均持股天数")
    draw(result, result.止盈止损占比, "止盈止损占比")
    draw(result, result.夏普比率, "夏普比率")
    draw(result, result.调整索提比率, "调整索提比率")
    draw(result, result.α, "α值")
    draw(result, result.β, "β值")
    draw(result, result.策略基准收益差, "策略基准收益差")
    
    
# 具体作画过程
@run.change_dir
def draw(result, data, title, bins = -1):
    plt.figure()
    if bins == -1:
        bins = math.floor(math.sqrt(len(data)))
    data.hist(bins = bins)
    plt.title(title)
    plt.savefig("./output/" + title + ".jpg")
    plt.close()
    print(title)
    print("平均值:", data.mean(), "最大值:", data.max(), "最大值的股票代码", result[data == data.max()].股票代码)
    

    
# 主函数
@run.change_dir
def main():
    tools.init()
    month = 0
    refresh = False
    retest = False
    start_date = "20110101"
    end_date = "20210101"
    codes = tools.Research(refresh = refresh, month = 0, bSelect = False, start_date = start_date, end_date = end_date)
    # 下载沪深300数据
    benchcode = "000300"
    benchmark = tools.getStockData(benchcode, month = 0, refresh = refresh, start_date = start_date, end_date = end_date, adjust = "hfq")
    
    # 计算基准指数的收益率
    benchrate = benchmark["收盘"]/benchmark["收盘"].shift(1) - 1.0
    benchdata = pd.DataFrame()
    benchdata["日期"] = benchmark.日期.values
    benchdata["每日收益率"] = benchrate.values
    benchdata["收盘"] = benchmark["收盘"].values
    # print("基准每日收益率", len(benchdata), benchdata.head())
    
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
            result = test(code = code, benchdata = benchdata)
            test_res = test_res.append(result, ignore_index = True)
        test_res.to_csv(datafilepath, index = False)
    # print(test_res)
    drawResults(test_res)


if __name__ == "__main__":
    main()