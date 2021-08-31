# coding:utf-8
# 1000元实盘练习程序
# 统计每日涨跌停数量


import pandas as pd
import numpy as np
import akshare as ak
import run
import tools
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt


# 涨停统计
def up(date = "20210826"):
    try:
        res = ak.stock_em_zt_pool(date=date)
        return len(res)
    except:
        return 0
        
        
# 跌停统计
def down(date = "20210525"):
    try:
        res = ak.stock_em_zt_pool_dtgc(date=date)
        return len(res)
    except:
        return 0
        


# 主函数
@run.change_dir
def main():
    month = 12
    end = datetime.date.today()#.strftime("%Y%m%d")
    start = (datetime.date.today() - relativedelta(months = month))#.strftime("%Y%m%d")
    upnum = []
    downnum = []
    dates = []
    while start < end:
        start += datetime.timedelta(days = 1)
        date = start.strftime("%Y%m%d")
        updata = up(date)
        downdata = down(date)
        # print(date, updata, downdata)
        if updata != 0 and downnum != 0:
            upnum.append(updata)
            downnum.append(downdata)
            dates.append(date)
    results = pd.DataFrame({"date":dates, "up":upnum, "down":downnum})
    print(results.info(), results.head())
    # 画图
    plt.figure()
    results.plot(x = "date", y = ["up", "down"])
    # results.plot(x = "date", y = "down", label = "down")
    plt.legend(loc = "best")
    plt.savefig("./output/updown.jpg")
    plt.close()
    results.to_csv("./output/updown.csv", index = False)


if __name__ == "__main__":
    main()