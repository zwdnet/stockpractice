# coding:utf-8
# 1000元实盘练习程序
# 工具函数，用于初始化，下载数据，画图等


import pandas as pd
import numpy as np
import efinance as ef
import akshare as ak
import run
import os
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick2_ohlc
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv



# 设置显示环境
def init():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # mpl.rcParams['axes.unicode_minus'] = False
    
    
# 获取股价数据
@run.change_dir
def getData(refresh = True):
    data = pd.DataFrame()
    if refresh == True:
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        # print(stock_zh_a_spot_df.info())
        stock_zh_a_spot_df.to_csv("./stocks.csv")
        data = stock_zh_a_spot_df
    else:
        data = pd.read_csv("./stocks.csv", dtype = {"code":str, "昨日收盘":np.float64})# converters = {'代码':str})
    # print(data.info())
    return data
    
    
# 形成股票池
@run.change_dir
def make_stock_pool(data, highPrice = 5.0):
    # 股价低于highPrice的
    smallData = data[data.最高 < highPrice]
    # 排除ST个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.名称.str.contains("ST")]
    # print("排除后", len(smallData))
    # 排除要退市个股
    # print("排除前", len(smallData))
    smallData = smallData[~ smallData.名称.str.contains("退")]
    # 上市时间太短需排除的股票代码
    discard = ['sh600032', 'sh600905', 'sh601665', 'sh605167', 'sh688425', 'sh688509', 'sh688538', 'sz001208']
    smallData = smallData[~smallData.代码.isin(discard)]
    newData = smallData
    newData.reset_index(drop = True, inplace = True)
    # print(newData.info())
    # print(newData.代码)
    # newData.代码.to_csv("./result.csv")
    
    codes = []
    for code in newData.代码:
        codes.append(code[2:])
    return codes
    
    
# 获取股票池近month个月的日线数据
@run.change_dir
def getRecentData(codes, refresh = False, savePath = "./pooldata/", month = 6):
    # data = pd.read_csv(path, converters = {'代码':str}).代码.values
    new_codes = []
    discard_code = []
    # print(data)
    # 获取股票最近month个月数据
    if refresh == True:
        today = datetime.date.today().strftime("%Y%m%d")
        # print("今天日期:", today)
        months = (datetime.date.today() - relativedelta(months = month)).strftime("%Y%m%d")
        # print("上月日期:", lastmonth)
        k = 0.0
        n = len(codes)
        for i in codes:
            k += 1.0
            print("已下载了", str(k/n*100), "%股票数据\n")
            code = i
            # print(code)
            stock_data = ak.stock_zh_a_hist(symbol = code, start_date = months, end_date = today, adjust = "qfq")
            # 排除上市不足两个月的股票。
            # print("测试", len(stock_data))
            if len(stock_data) > 60:
                # print("大于60")
                new_codes.append(code)
                filename = savePath + new_codes[-1] + ".csv"
                stock_data.to_csv(filename, index = False)
            else:
                discard_code.append(code)
        # print("需排除的股票代码:", discard_code)
        return new_codes
    else:
        return codes
    
    
# 获取指定代码股票历史数据
@run.change_dir
def getStockData(code, path = "./pooldata/", month = 6, refresh = False):
    filename = path + code + ".csv"
    if os.path.exists(filename) and refresh == False:
        data = pd.read_csv(filename)
        data.日期 = pd.to_datetime(data.日期)
        return data
    else:
        today = datetime.date.today().strftime("%Y%m%d")
        # print("今天日期:", today)
        months = (datetime.date.today() - relativedelta(months = month)).strftime("%Y%m%d")
        stock_data = ak.stock_zh_a_hist(symbol = code, start_date = months, end_date = today, adjust = "qfq")
        stock_data.日期 = pd.to_datetime(stock_data.日期)
        stock_data.to_csv(filename, index = False)
        return stock_data
    
    
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
        # print("测试基准", code, type(code))
        # benchmark_data = ak.stock_zh_a_hist(symbol = code, start_date = months, end_date = today, adjust = "qfq")
        benchmark_data = ak.stock_zh_index_daily(symbol = code)
        # benchmark_data.columns = ["开盘", "最高", "最低", "收盘", "成交量"]
        # benchmark_data.rename(index = {"date":"日期"})
        benchmark_data.to_csv(filename)
        data = pd.read_csv(filename)
        data.date = pd.to_datetime(data.date)
        data.columns = ["日期", "开盘", "最高", "最低", "收盘", "成交量"]
        return data
    
    
# 打包整个下载数据，选股过程
@run.change_dir
def Research(refresh = True, month = 6, highPrice = 5.0):
    data = getData(refresh = refresh)
    pool_codes = make_stock_pool(data, highPrice)
    codes = getRecentData(codes = pool_codes, refresh = refresh, month = month)
    getBenchmarkData(month = month, refresh = refresh)
    return codes
    
    
# 画指定股票的k线
@run.change_dir
def drawKLine(code, open = "开盘", high = "最高", low = "最低", close = "收盘", date = "日期", path = "./pooldata/"):
    filename = path + code + ".csv"
    if os.path.exists(filename):
        # 画k线
        data = pd.read_csv(filename)
        # print(data.info())
        fig, ax = plt.subplots(1, 1, figsize=(8,3), dpi=200)
        candlestick2_ohlc(ax,
                opens = data[open].values,
                highs = data[high].values,
                lows = data[ low].values,
                closes = data[close].values,
                width=0.5, colorup="r", colordown="g")
        """
        # 计算均线数据
        data["5"] = data[close].rolling(5).mean()
        data["10"] = data[close].rolling(10).mean()
        data["20"] = data[close].rolling(20).mean()
        data["30"] = data[close].rolling(30).mean()
        # 画均线
        plt.plot(data['5'].values, alpha = 0.5, label='MA5')
        plt.plot(data['10'].values, alpha = 0.5, label='MA10')
        plt.plot(data['20'].values, alpha = 0.5, label='MA20')
        plt.plot(data['30'].values, alpha = 0.5, label='MA30')
        """
        # 设定图例及坐标轴
        plt.legend(loc = "best")
        plt.xticks(ticks =  np.arange(0,len(data)), labels = data[date].values)
        plt.xticks(rotation=90, size=3)

        # 输出图片
        plt.savefig("./output/" + code + ".png")
        plt.close()
    else:
        print("无股票数据")
        
        
# 发送邮件模块
# 参考https://zhuanlan.zhihu.com/p/24180606
# 防止硬编码泄露用户名密码，参考:https://blog.csdn.net/lantian_123/article/details/101518724
# 需在源码目录下自行编辑.env文件，定义USERNAME和PASSWORD的值
def sentMail(title, content):
    # 加载用户名和密码
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    senderAddress = username+"@163.com"
    # 设置服务器所需信息
    mail_host = "smtp.163.com"
    # 用户名
    mail_user = username
    # 密码
    mail_pass = password
    # 邮件发送方地址
    sender = senderAddress
    # 接收方地址
    receivers = [senderAddress]
    
    # 设置邮件信息
    # 邮件内容
    message = MIMEText(content, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = title
    # 发送方信息
    message['From'] = sender 
    # 接受方信息     
    message['To'] = receivers[0]
    
    # 登陆并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        # 连接到服务器
        # smtpObj.connect(mail_host, 465)
        # 登录到服务器
        smtpObj.login(mail_user,mail_pass) 
        # 发送
        smtpObj.sendmail(
            sender,receivers,message.as_string()) 
        # 退出
        smtpObj.quit() 
        print('发送成功')
    except smtplib.SMTPException as e:
        print('发送错误', e) #打印错误
        
        
if __name__ == "__main__":
    init()
    codes = Research(refresh = False)
    print(codes, len(codes))
    data = getStockData(codes[0])
    # print(data.info())
    drawKLine(codes[0])
    