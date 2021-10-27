# coding:utf-8
# 1000元实盘练习程序
# 对实盘训练数据进行分析


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import run
import tools
import quantstats
import imgkit
import os
from PIL import Image


# 计算各种回测指标
def riskAnaly(returns, bk_returns, rf = 0.02, periods = 242, annualize = True, trading_year_days = 242):
    # 计算夏普比率
    _sharpe = quantstats.stats.sharpe(returns = returns, rf = rf, periods = periods, annualize = True, trading_year_days = trading_year_days)
    print("函数内", returns.shape, bk_returns.shape)
    # 计算αβ值
    #_alphabeta = quantstats.stats.greeks(returns, bk_returns, periods = periods)
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
        #"α": _alphabeta[0],
        #"β": _alphabeta[0],
        "信息比例": _info,
        "索提比率": _sortino,
        "调整索提比率": _adjustSt,
        "skew值": _skew,
        "_calmar": _calmar
    })
    
    # 调用库画图
    filename = "test_res.jpg"
    quantstats.reports.html(returns, benchmark = bk_returns, output='./output/stats.html', title='BackTest Results', trading_year_days = 242)
    imgkit.from_file("./output/stats.html", "./output/" + filename, options = {"xvfb": ""})
    # 压缩图片文件
    im = Image.open("./output/" + filename)
    im.save("./output/" + filename)
    os.system("rm ./output/stats.html")
    
    return results
    
    
# 计算交易指标
def tradeAnaly(trade_data):
    winTimes = len(trade_data[trade_data.交易结果 == "盈利"])
    loseTimes = len(trade_data[trade_data.交易结果 == "亏损"])
    # print(winTimes, loseTimes)
    # 计算胜率
    winRate = winTimes/len(trade_data)
    print("胜率", winRate)
    winMoney = trade_data[trade_data.交易结果 == "盈利"].盈利金额.sum()
    loseMoney = trade_data[trade_data.交易结果 == "亏损"].盈利金额.sum()
    # print(winMoney, loseMoney)
    # 计算盈亏比
    winloseRate = abs(winMoney)/abs(loseMoney)
    print("盈亏比:", winloseRate)
    results = pd.Series(
        {"胜率": winRate,
         "盈亏比": winloseRate
        }
    )
    return results


@run.change_dir
def main():
    tools.init()
    # 读取数据
    invent_data = pd.read_csv("./收益数据.csv", index_col = "日期", parse_dates = ["日期"])
    trade_data = pd.read_csv("./交易记录.csv")
    print(invent_data.info(), invent_data.head(), invent_data.tail())
    print(trade_data.info(), trade_data.head(), trade_data.tail())
    
    # 画图
    invent_data.账户收益额.plot()
    plt.ylabel("账户收益额")
    plt.savefig("./output/gets.jpg")
    plt.close()
    
    # 计算收益率数据
    invent_data["账户收益率"] = (1000+invent_data["账户收益额"])/(1000+invent_data["账户收益额"].shift(1)) - 1.0
    print(invent_data.head())
    
    # 下载沪深300数据
    code = "000300"
    hs300_data = tools.getStockData(code, path = "./", month = 0, refresh = True, start_date = "20210708", end_date = "20211026", adjust = "hfq")
    print(hs300_data.info())
    
    # 计算基准指数的收益率
    invent_data["基准指数值"] = hs300_data.收盘.values
    invent_data["基准收益率"] = invent_data["基准指数值"]/invent_data["基准指数值"].shift(1) - 1.0
    print(invent_data.head())
    
    # 数据归一化
    invent_data["归一化账户收益额"] = ((invent_data["账户收益额"] - invent_data["账户收益额"].min())/(invent_data["账户收益额"].max() - invent_data["账户收益额"].min()))
    invent_data["归一化基准指数值"] = ((invent_data["基准指数值"] - invent_data["基准指数值"].min())/(invent_data["基准指数值"].max() - invent_data["基准指数值"].min()))
    
    # 画图比较一下
    invent_data.plot(y = ["归一化账户收益额", "归一化基准指数值"])
    plt.savefig("./output/meVSmarket.jpg")
    plt.close()
    invent_data.plot(y = ["账户收益率", "基准收益率"])
    plt.savefig("./output/rateVS.jpg")
    plt.close()
    
    # 计算回测指标
    print(len(invent_data.账户收益率), len(invent_data.基准收益率))
    results = riskAnaly(returns = invent_data.账户收益率, bk_returns = invent_data.基准收益率)
    print(results)
    
    # 计算交易指标
    results = tradeAnaly(trade_data)
    print(results)
    
    # 画成本占盈利的比例
    invent_data["成本盈利占比"] = invent_data.累计成本/invent_data.账户收益额
    invent_data.plot(y = ["成本盈利占比"])
    plt.savefig("./output/costVSgets.jpg")
    plt.close()
    

if __name__ == "__main__":
    main()