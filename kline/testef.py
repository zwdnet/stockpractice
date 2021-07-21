# coding:utf-8
# 1000元实盘练习程序
# 测试efinance获取股票数据


import efinance as ef
import pandas as pd
import numpy as np
import kline


if __name__ == "__main__":
    kline.init()
    code = "600166"
    
    # 获取单只股票基本信息
    stock_info = ef.stock.get_base_info(code)
    print(stock_info)
    
    # 获取指定时间段日k线数据
    beg = "20210101"
    end = "20210720"
    df = ef.stock.get_quote_history(code, beg = beg, end = end)
    print(df.info(), df.head())
    
    # 获取多只股票指定时间段日K线数据
    codes = ["600616", "600256"]
    df = ef.stock.get_quote_history(code, beg = beg, end = end)
    print(df.info(), df.head(), df[df["股票代码"] == "600256"])
    
    # 获取单只股票5分钟k线数据
    df = ef.stock.get_quote_history(code, beg = beg, end = end, klt = 5)
    print(df.info(), df.head())
    
    # 获取单只股票60分钟k线数据
    df = ef.stock.get_quote_history(code, klt = 60)
    print(df.info(), df.head(), df.tail())