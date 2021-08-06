# coding:utf-8
# 1000元实盘练习程序
# 研究A股收益与CPI的关系


import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import run
import tools
import os
# import datetime


# 获取并处理数据
@run.change_dir
def dataprocess():
    # 日期范围为201205-202104
    start = "2012-05"
    end = "2021-04"
    # 获取cpi数据
    filename = "./cpi.csv"
    if os.path.exists(filename):
        cpi = pd.read_csv(filename, index_col = "date")
        cpi.index = pd.to_datetime(cpi.index)
    else:
        cpi = ak.macro_china_cpi_monthly()
        cpi.index.name = "date"
        cpi.to_csv(filename)
    cpi_M = cpi.to_period('M')
    cpi_M = cpi_M[cpi_M.index >= "2012-06"]
    cpi_M = cpi_M[cpi_M.index <= end]
    # print(cpi_M.head())
    # 获取A股数据
    filename = "./hs300.csv"
    if os.path.exists(filename):
        hs300 = pd.read_csv(filename, index_col = "date")
        hs300.index = pd.to_datetime(hs300.index).strftime("%Y-%m-%d")
        hs300.index = pd.to_datetime(hs300.index)
        # hs300.index = hs300.index.dt.normalize()
    else:
        hs300 = ak.stock_zh_index_daily(symbol = "sh510300")
        hs300.to_csv(filename)
    hs300_M = hs300.to_period('M')
    hs300_M = hs300_M[~hs300_M.index.duplicated(keep='first')]
    hs300_M = hs300_M[hs300_M.index >= start]
    hs300_M = hs300_M[hs300_M.index <= "2021-03"]
    # print(len(cpi_M), len(hs300_M))
    return (cpi_M, hs300_M)


# 计算股票的月度实际收益率和货币贬值情况
@run.change_dir
def getResults():
    tools.init()
    cpi, hs300 = dataprocess()
    # 计算沪深300月度收益率
    ret = []
    for i in range(1, len(hs300)):
        ret.append(((hs300.close[i] - hs300.close[i-1])/hs300.close[i-1]))
    cpi_values = cpi.values/100.0
    returns = []
    money = [1.0]
    for i in range(len(ret)):
        tmp = ret[i] - cpi_values[i]
        returns.append(tmp[0])
        money.append(money[i]*(1+cpi_values[i])[0])
    results = pd.Series(returns, index = cpi.index[:-1], name = "实际月度收益率")
    moneys = pd.Series(money, index = cpi.index, name = "货币贬值")
    # print(moneys)
    return results, moneys, cpi
    
    
@run.change_dir
def main():
    results, moneys, cpi = getResults()
    results.plot()
    plt.ylabel(results.name)
    plt.savefig("./output/monthret.jpg")
    plt.close()
    # 假设期初投入1元，计算每月的资产净值。
    value = [1*(1+results[0])]
    for i in range(1, len(results)):
        value.append(value[i-1]*(1+results[i]))
    # print(value)
    values = pd.Series(value, index = results.index, name = "月度金额")
    values.plot()
    #moneys.plot()
    plt.legend(loc = "best")
    plt.savefig("./output/monthvalue.jpg")
    plt.close()
    # 实际收益率和cpi画到一起
    plt.figure()
    ax = results.plot()
    cpi = cpi/100.0
    cpi.plot(ax = ax)
    plt.savefig("./output/valuevscpi.jpg")
    

if __name__ == "__main__":
    main()
    