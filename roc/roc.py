# coding:utf-8
# 1000元实盘练习程序
# 计算ROC指标策略


import numpy as np
import pandas as pd
import akshare as ak
import tools
import run
from datetime import datetime
import datetime as dt
import matplotlib.pyplot as plt


# 研究ROC指标
@run.change_dir
def roc():
    codes = tools.Research(refresh = False, bSelect = False)
    # print(len(codes))
    data = tools.getStockData(codes[0])
    # print(data.info())
    # print(data.head())
    start_date = "2014-01-01"
    end_date = "2016-12-31"
    StartDate = start_date
    # print(data[data.日期 == start_date].涨跌幅.values)
    # 获取股价数据
    datas = []
    for code in codes[:100]:
        data = tools.getStockData(code)
        datas.append(data)
    # print(datas[0])
    dates = []
    ups = []
    downs = []
    totals = []
    while start_date < end_date:
        upnum = 0
        downnum = 0
        totalnum = 0
        i = 0

        for code in codes[:100]:
            # data = tools.getStockData(code)
            data = datas[i]
            i += 1
            updown = data[data.日期 == start_date].涨跌幅.values
            # print(updown)
            if len(updown) != 0:
                totalnum += 1
                if updown[0] > 0.0:
                    upnum += 1
                elif updown[0] < 0.0:
                    downnum += 1
        if totalnum != 0:
            dates.append(start_date)
            ups.append(upnum)
            downs.append(downnum)
            totals.append(totalnum)
        start_date = (datetime.strptime(start_date, "%Y-%m-%d").date() + dt.timedelta(days = 1)).strftime("%Y-%m-%d")
        print(start_date, end_date, upnum, downnum, totalnum)
    results = pd.DataFrame({"date":dates, "up":ups, "down":downs, "total":totals})
    results.set_index("date", inplace = True, drop = True)
    
    # 计算ROC指标
    # 变化率指标(ROC) = 100 - 100/(1+x日平均上涨数/x日平均下跌数)，x一般取10。
    results["up10"] = results.up.rolling(window = 10).mean()
    results["down10"] = results.down.rolling(window = 10).mean()
    results["ROC"] = 100-100/(1+results.up10/results.down10)
    # 删除有空值的行
    results.dropna(axis = 0, how = "any", inplace = True)
    
    print(results.info())
    print(results.tail())
    
    results.to_csv("./output/ROC.csv", index = False)
    
    # 画图
    index = results.index.values
    start_date = datetime.strptime(index[0], "%Y-%m-%d").date().strftime("%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date().strftime("%Y%m%d")
    print(start_date, end_date)
    df300 = tools.getStockData("000300", refresh = True, start_date = start_date, end_date = end_date)
    print(df300.head())
    # n = len(results)
    # for date in index:
    #     print(df300[date])
    # data = df300[df300.日期 in index]
    # print(data)
    plt.figure()
    ax = plt.subplot(211)
    df300.plot(x = "日期", y = "收盘", ax = ax)
    ax = plt.subplot(212)
    results.plot(y = "ROC", ax = ax)
    plt.savefig("./output/ROC.jpg")
    plt.close()


def main():
    tools.init()
    roc()
    

if __name__ == "__main__":
    main()