# coding:utf-8
# 1000元实盘练习程序
# 测试判断牛熊的指标
# 根据《阿佩尔均线操盘术》第二章


import pandas as pd
import numpy as np
import akshare as ak
import run
import tools
import efinance as ef
import datetime, quandl
import matplotlib.pyplot as plt
import os
from backtest import BackTest
import strategy as st


# 根据输入数据计算指标
def preprocess(data, data_name1, data_name2):
    data["Index"] = data[data_name1]/data[data_name2]
    # 移动均数
    data["Index_ma"] = data["Index"].rolling(window = 10).mean()
    # 计算是否为牛市
    data["niu"] = -1
    for i in range(len(data)):
        if data.Index[i] > data.Index_ma[i]:
            data.niu[i] = 1
    # 计算买卖点
    # 0为中性，1为买入，2为卖出
    data["buy"] = 0
    for i in range(1, len(data)):
        if data["buy"][i-1] == 1 and data["niu"][i] == 1: # 已买入且还是牛市，持有
            data["buy"][i] = 1
        elif data["buy"][i-1] != 1 and data["niu"][i] == 1: # 在牛市且没有买入，则买入
            data["buy"][i] = 1
        elif data["buy"][i-1] != 1 and data["niu"][i] == -1: # 没买入且还是熊市，观望
            data["buy"][i] == 0
        elif data["buy"][i-1] == 1 and data["niu"][i] == -1: # 已买入且在熊市，则卖出
            data["buy"][i] = 2
    new_data = data.set_index(data.日期, inplace = False, drop = True)
    new_data = new_data.drop("日期", axis = 1)
    return new_data
    
    
# 画图
@run.change_dir
def draw(data, stockname, scale = 2000):
    data.Index.plot(ylabel = "index")
    data.Index_ma.plot(ylabel = "index_ma")
    plt.legend(loc = "best")
    plt.savefig("./output/index_ma.jpg")
    plt.close()
    plt.figure()
    index = data.Index*scale
    index_ma = data.Index_ma*scale
    stock = data.loc[:,[stockname]]
#    index.plot(ylabel = "index")
#    index_ma.plot(ylabel = "index_ma")
#    stock = data.loc[:,[stockname]]
#    stock.plot(ylabel = stockname)
    plt.plot(index, label = "index")
    plt.plot(index_ma, label = "index_ma")
    plt.plot(stock, label = stockname)
    plt.legend(loc = "best")
    plt.savefig("./output/" + stockname + ".jpg")
    plt.close()


# 先研究美股
@run.change_dir
def us_stock():
    # 加载数据，数据预处理
    ndq = pd.read_csv("./us_ndq.csv")
    spx = pd.read_csv("./us_spx.csv", thousands = ',')
    print(ndq.head(), spx.head(), ndq.info(), spx.info())
    ndq = ndq.iloc[-53:, :].reset_index(drop = True)
    ndq_index = ndq["Index Value"]
    # spx.Close = spx.Close.replace(',', '')
    # print(spx.Close.replace(',', ''))
    spx_index = spx.Close
    spx_index = pd.Series(spx_index.values[::-1]).reset_index(drop = True)
    # print(ndq_index, spx_index)
    data = pd.DataFrame({"ndq" : ndq_index,
                                            "spx" : spx_index})
    data = preprocess(data, "ndq", "spx")
    # 计算指标
    
    print(data.info(), data.tail())
    draw(data, "ndq", scale = 3000)
    
    
# 再研究A股
@run.change_dir
def cn_stock():
    # 准备数据
    filename = ["./cyb_data.csv", "./hs_data.csv"]
    if os.path.exists(filename[0]) and os.path.exists(filename[1]):
        cyb_data = pd.read_csv(filename[0])
        hs_data = pd.read_csv(filename[1])
    else:
        cyb_code = "sz399006"
        hs_code = "sh000300"
        cyb_data = ef.stock.get_quote_history(cyb_code[2:])
        hs_data = ef.stock.get_quote_history(hs_code[2:])
        cyb_data.to_csv(filename[0], index = False)
        hs_data.to_csv(filename[1], index = False)
    
    hs_data = hs_data.iloc[-len(cyb_data):, :]
    print(cyb_data.head(), hs_data.head())
    cyb_data = cyb_data.iloc[::5, :]
    hs_data = hs_data.iloc[::5, :]
    print(cyb_data.info(), hs_data.info())
    print(cyb_data.head(), cyb_data.tail())
    cyb_index = cyb_data.收盘.reset_index(drop = True)
    hs_index = hs_data.收盘.reset_index(drop = True)
    print(cyb_index.head(), hs_index.head())
    
    date = cyb_data.日期.reset_index(drop = True)
    print(len(cyb_data), len(date))
    data = pd.DataFrame({"创业板" : cyb_index,
                         "沪深300" : hs_index,
                         "日期" : date
                         })
    data = preprocess(data, "创业板", "沪深300")
    data.to_csv("./strategy.csv")
    print(data.info(), data)
    draw(data, "创业板", scale = 1500)
    
    
# 对策略进行回测
@run.change_dir
def backTest(refresh = False):
    start = "2010-06-01"
    end = "2021-08-13"
    month = 135
    code = "399006" # 创业板指数
    benchmark = tools.getBenchmarkData(month = month,  refresh = refresh, path = "./stockdata/")
    backtest = BackTest(codes = [code], strategy = st.CYBStrategy, benchmark = benchmark, month = month, cash = 1000000, refresh = refresh, path = "./stockdata/")
    results = backtest.getResults()
    print(results)
    backtest.drawResults(code + "result")
    

if __name__ == "__main__":
    tools.init()
    # us_stock()
    # cn_stock()
    backTest(refresh = False)
    
    