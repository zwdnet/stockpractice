# coding:utf-8
# 1000元实盘练习程序
# 用历史新高新低比值作为买入卖出点的策略
# 根据《阿佩尔均线操盘术》第六章


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
import sys


# 主程序
@run.change_dir
def main():
    tools.init()
    makeData(refresh = False, reGenerate = False)
    # testData()
    
    
# 准备数据
@run.change_dir
def makeData(refresh = True, reGenerate = False):
    codes = tools.Research(refresh = refresh, bSelect = False)
    startdate = "20100101"
    enddate = "20211231"
    researchData = tools.getBenchmarkData(refresh = False, start_date = startdate, end_date = enddate)
    # print(researchData.info())
    
    if reGenerate == True:
    
        datas = []
        allcodes = []
        for code in codes[:10]:
            data = tools.getStockData(code, refresh = False, start_date = startdate, end_date = enddate)
            data["代码"] = code
            datas.append(data)
            allcodes.append(code)
            # print(code, len(data))
            # print(data.iloc[0:5, :])
            # print("测试", data[data.日期 == "2020-11-11"].index[0])
            # print(data.info())
            # close = data.收盘[:100]
            # maxClose = close.max()
            # maxIdx = close.idxmax()
            # print(maxClose, maxIdx)
        # print(len(datas), sys.getsizeof(datas))
        # print(datas[0].info())
    
        results = pd.DataFrame(columns = ["日期", "代码", "结果"])
        year = 242 # 一年的交易日天数
        i = 0
        total = len(researchData)*len(datas)
        maxClose = {}
        minClose = {}
        maxIndex = {}
        minIndex = {}
        for code in allcodes:
            maxClose[code] = -1
            minClose[code] = -1
            maxIndex[code] = -1
            minIndex[code] = -1
        for date in researchData.日期:
            tmpRes = 100
            for data in datas:
                i += 1
                print("进行了",i/total*100.0,"%")
                tmp = data[data.日期 == date]
                if len(tmp) == 0:
                    # print("测试a")
                    tmpRes = -100
                else:
                    # print("测试b")
                    code = tmp.代码.values[0]
                    ind = tmp.index[0]
                    if ind < year: # 交易日不足一年
                        tmpRes = 0
                    else:
                        close = data.收盘[ind-year:ind]
                        # 之前没有保存过最大值或最大值在第一个位置
                        if maxIndex[code] <= 0:
                            maxIdx = close.idxmax()
                            maxIndex[code] = maxIdx
                            maxClose[code] = data.收盘[maxIdx]
                        # 之前没有保存过最小值或最小值在第一个位置
                        if minIndex[code] <= 0:
                            minIdx = close.idxmin()
                            minIndex[code] = minIdx
                            minClose[code] = data.收盘[minIdx]
                        # 比较最近一个数据与历史数据
                        nowclose = data.收盘[ind]
                        if nowclose > maxClose[code]:
                            maxClose[code] = nowclose
                            maxIndex[code] = ind
                        if nowclose < minClose[code]:
                            minClose[code] = nowclose
                            minIndex[code] = ind
                        # 年内新高
                        if maxIndex[code] == ind:
                            tmpRes = 1
                        # 年内新低
                        elif minIndex[code] == ind:
                            tmpRes = -1
                        else:
                            tmpRes = 0
                # if len(tmp) != 0:
                    # print(len(tmp), tmp.代码)
                
                    # print(type(code), date.date(), code, tmpRes)
                    # res = {"日期":date, "代码":code, "结果":tmpRes}
                    # print(res)
                    # results.loc[i] = [date, code, tmpRes]
                    results = results.append({"日期":date, "代码":code, "结果":tmpRes}, ignore_index = True)
        # print(results.info(), results.head())
        # print(results.代码)
        results.to_csv("HLresults.csv", index = False)
        # res = pd.read_csv("HLresults.csv")
        # print(res.info())
        # print(res.head())
    data = generateData(researchData)
    # data["指标"] = data.NH/(data.NH + data.NL)
    print(data.info(), data.describe(), data.head())
    print(data[data["指标"] > 0.0])
    
    
    
# 生成NH,HL数据
@run.change_dir
def generateData(researchData):
    res = pd.read_csv("HLresults.csv")
    res.日期 = pd.to_datetime(res.日期)
    # print(res.head())
    # print(res[res.结果]==1)
    # print(res[res.结果 == 1 and res.日期 == "2011-01-06"])
    # input("按任意键继续")
    data = pd.DataFrame()
    for date in researchData.日期:
        NH = res[res.结果 == 1]
        NL = res[res.结果 == -1]
        # print(NL.count())
        # input("按任意键继续")
        NHnum = 0
        NLnum = 0
        for today in NH.日期:
            if date.date().__eq__(today.date()):
                NHnum += 1
        for today in NL.日期:
            if date.date().__eq__(today.date()):
                NLnum += 1
        # print(date.date(), NHnum, NLnum)
    #    for resDate in res.日期:
    #        if date.date()==resDate:
    #            print(date.date(), resDate, res[resDate == date.date()].结果.values)
        if NHnum == 0 and NLnum == 0:
            indicate = 0.0
        else:
            indicate = NHnum/(NHnum + NLnum)
        if NHnum != 0 and NLnum != 0:
            print("出现有意义的指标", date.date())
        data = data.append({"日期":date.date(), "NH":NHnum, "NL":NLnum, "指标":indicate}, ignore_index = True)
        data.日期 = pd.to_datetime(data.日期)
    return data
    
    
# 测试数据生成结果
@run.change_dir
def testData():
    res = pd.read_csv("HLresults.csv")
    print(res.describe(), res.info()) 
    
    
if __name__ == "__main__":
    main()