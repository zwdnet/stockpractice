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
def getData(refresh = False):
    data = pd.DataFrame()
    if refresh == True:
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        print(stock_zh_a_spot_df.info())
        stock_zh_a_spot_df.to_csv("stocks.csv")
        data = stock_zh_a_spot_df
    else:
        data = pd.read_csv("stocks.csv")
    # print(data.head())
    return data
    
    
# 计算一些数据
def analysis(data):
    print("股票池总数:%d" % (len(data)))
    print("平均市盈率:%.2f" % (data.per.mean()))
    print("平均成交量:%.2f" % (data.volume.mean()))
    print("平均成交额:%.2f" % (data.amount.mean()))
    print("平均市净率:%.2f" % (data.pb.mean()))
    print("平均换手率:%.2f" % (data.turnoverratio.mean()))
    # print("平均股东人数:%.2f" % (data.holders.mean()))
    
    
# EDA特征工程
@run.change_dir
def EDA(data):
    bins = 20
    # 股价低于5元的
    smallData = data[data.high < 5.0]
    # 排除ST个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.name.str.contains("ST")]
    # print("排除后", len(smallData))
    # 排除要退市个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.name.str.contains("退")]
    # print("排除后", len(smallData))
    # 排除成交量低于平均成交量的个股
    # 以及换手率低于平均值两倍的个股
    smallData = smallData[(smallData.volume > smallData.volume.mean()) & (smallData.turnoverratio > 2.0*smallData.turnoverratio.mean())]
    print(smallData.head())
    print(smallData.info())
    smallData.trade.plot(kind = "hist", bins = bins)
    plt.savefig("./output/trade.png")
    plt.close()
    plt.figure()
    smallData.volume.plot(kind = "hist", bins = bins)
    plt.savefig("./output/volume.png")
    plt.close()
    plt.figure()
    smallData.changepercent.plot(kind = "hist", bins = bins)
    plt.savefig("./output/changepercent.png")
    plt.close()
    plt.figure()
    smallData.per.plot(kind = "hist", bins = bins)
    plt.savefig("./output/per.png")
    plt.close()
    plt.figure()
    smallData.pb.plot(kind = "hist", bins = bins)
    plt.savefig("./output/pb.png")
    plt.close()
    plt.figure()
    smallData.nmc.plot(kind = "hist", bins = bins)
    plt.savefig("./output/nmc.png")
    plt.close()
    plt.figure()
    smallData.mktcap.plot(kind = "hist", bins = bins)
    plt.savefig("./output/mktcap.png")
    plt.close()
    plt.figure()
    smallData.turnoverratio.plot(kind = "hist", bins = bins)
    plt.savefig("./output/turnoverratio.png")
    plt.close()
    # 计算一些平均数据
    analysis(smallData)
    # 按换手率排序
    newData = smallData.sort_values("turnoverratio").iloc[-100:, :]
    # print(newData.head())
    # print(newData.iloc[:10, :])
    print(newData.name)
    newData.name.to_csv("./output/result.csv")


if __name__ == "__main__":
    init()
    data = getData()
    # print(data.info())
    # print(data[data.high < 10.0])
    EDA(data)
    
    