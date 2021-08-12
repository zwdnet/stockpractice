# coding:utf-8
# 1000元实盘练习程序
# 测试talib


import pandas as pd
import numpy as np
import talib
import tools


if __name__ == "__main__":
    data = pd.DataFrame({"开盘":[8.9, 2.0], "最高":[9.05, 3.0], "最低":[8.81, 1.0], "收盘":[8.94, 2.0]})
    data = data.iloc[[0],:]
    print(data)
    res = talib.CDLHAMMER(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
    print(res)
    code = "600491"
    month = 1
    stockdata = tools.getStockData(code=code, month = month)
    n = len(stockdata)
    for i in range(n):
        data = stockdata.iloc[0:i+1, :]
        print("数据长度", len(data.开盘), data.开盘.values)
        res = talib.CDLHAMMER(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
        print(i, res)
    data = stockdata.iloc[[n-1], :]
    print(data)
    res = talib.CDLHAMMER(data.开盘.values, data.最高.values, data.最低.values, data.收盘.values)
    print(res)
    