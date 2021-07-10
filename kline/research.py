# coding:utf-8
# 1000元实盘练习程序
# 筛选股票


import numpy as np
import pandas as pd
import akshare as ak
import sys
import run
import matplotlib.pyplot as plt


# 设置显示环境
def init():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)


# 获取股价数据
def getData(refresh = True):
    data = pd.DataFrame()
    if refresh == True:
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        print(stock_zh_a_spot_df.info())
        stock_zh_a_spot_df.to_csv("stocks.csv")
        data = stock_zh_a_spot_df
    else:
        data = pd.read_csv("stocks.csv", converters = {'代码':str})
    # print(data.head())
    return data
    
    
# 计算一些数据
def analysis(data):
    print("股票池总数:%d" % (len(data)))
    print("平均成交量:%.2f" % (data.成交量.mean()))
    print("平均成交额:%.2f" % (data.成交额.mean()))
    
    
# EDA特征工程
@run.change_dir
def EDA(data):
    bins = 20
    # 股价低于5元的
    smallData = data[data.最高 < 5.0]
    # 排除ST个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.名称.str.contains("ST")]
    # print("排除后", len(smallData))
    # 排除要退市个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.名称.str.contains("退")]
    # print("排除后", len(smallData))
    # 排除成交量低于平均成交量的个股
    smallData = smallData[(smallData.成交量 > smallData.成交量.mean())]
    print(smallData.head())
    print(smallData.info())
    smallData.最新价.plot(kind = "hist", bins = bins)
    plt.savefig("./output/trade.png")
    plt.close()
    plt.figure()
    smallData.成交量.plot(kind = "hist", bins = bins)
    plt.savefig("./output/volume.png")
    plt.close()
    plt.figure()
    smallData.涨跌幅.plot(kind = "hist", bins = bins)
    plt.savefig("./output/changepercent.png")
    plt.close()
    # 计算一些平均数据
    analysis(smallData)
    # 按成交量排序
    newData = smallData.sort_values("成交量").iloc[-100:, :]
    # print(newData.head())
    # print(newData.iloc[:10, :])
    newData.reset_index(drop = True, inplace = True)
    print(newData.info())
    print(newData.代码)
    newData.代码.to_csv("result.csv", index = False)


if __name__ == "__main__":
    init()
    data = getData(refresh = True)
    # print(data.info())
    # print(data[data.high < 10.0])
    EDA(data)
    # getRecentData()
    
    