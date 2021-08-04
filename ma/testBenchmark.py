# coding:utf-8
# 1000元实盘练习程序
# 测试下载基准数据


import pandas as pd
import numpy as np
import efinance as ef
import akshare as ak
import run
import os
import datetime
from dateutil.relativedelta import relativedelta



# 获取基准数据，默认为沪深300ETF
@run.change_dir
def getBenchmarkData(code = "sh510300", path = "./", month = 6, refresh = False):
    filename = path + "bench.csv"
    if os.path.exists(filename) and refresh == False:
        data = pd.read_csv(filename)
        data.date = pd.to_datetime(data.date)
        data.columns = ["日期", "开盘", "最高", "最低", "收盘", "成交量"]
        return data
    else:
        today = datetime.date.today().strftime("%Y%m%d")
        # print("今天日期:", today)
        months = (datetime.date.today() - relativedelta(months = month)).strftime("%Y%m%d")
        print("测试基准", code, type(code))
        # benchmark_data = ak.stock_zh_a_hist(symbol = code, start_date = months, end_date = today, adjust = "qfq")
        benchmark_data = ak.stock_zh_index_daily(symbol = code)
        benchmark_data.to_csv(filename)
        return benchmark_data
        
        
if __name__ == "__main__":
    data = getBenchmarkData(path = "./testdata/", month = 60)
    print(data.info())
    print(data.head())
    