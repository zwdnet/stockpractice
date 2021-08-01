# coding:utf-8
# 1000元实盘练习程序
# 测试backtrader
# https://algotrading101.com/learn/backtrader-for-backtesting/


import pandas as pd
import backtrader as bt
import run
import tools
import strategy as st
from backtest import BackTest


# 数据转换
@run.change_dir
def data_transform(code):
    data_df = tools.getStockData(code)
    data = bt.feeds.PandasData(
        dataname=data_df,
        name=code,
        fromdate=data_df.日期[0],
        todate=data_df.日期[len(data_df) - 1],
        datetime='日期',
        open='开盘',
        high='最高',
        low='最低',    
        close='收盘',
        volume='成交量',
        openinterest=-1
    )
    return data
    
    
# backtrader初始化
def init_bt(codes, teststrategy):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000.0)
    cerebro.broker.setcommission(0.0006)
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    # cerebro.optstrategy(teststrategy, pfast=range(5, 20), pslow=range(20, 21))
    for code in codes:
        data = data_transform(code)
        cerebro.adddata(data, name = code)
    cerebro.addstrategy(teststrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
    # cerebro.addanalyzer(st.Screener_SMA)
    return cerebro

@run.change_dir
def main():
    tools.init()
    codes = tools.Research(refresh = False, month = 60, highPrice = 10.0)
    test_res = pd.DataFrame()
    for code in codes[:10]:
        backtest = BackTest(codes = [code], strategy = st.MAcrossover)
        results = backtest.getResults()
        
    
    
if __name__ == "__main__":
    # main()
    backtest = BackTest(codes = ["002166"], strategy = st.MAcrossover)
    backtest.drawResults()
    results = backtest.getResults()
    print(results)
