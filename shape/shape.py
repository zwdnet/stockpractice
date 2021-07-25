# coding:utf-8
# 1000元实盘练习程序
# 用程序识别技术形态
"""
参考文献:ANDREW W. LO, HARRY MAMAYSKY, AND JIANG WANG.Foundations of Technical Analysis:Computational Algorithms, Statistical Inference, and Empirical Implementation.TEIE JOURNAL OF FINANCE VOL. LV. NO. 4 AUGUST 2000.
"""


import pandas as pd
import numpy as np
import run
import tools
import os
from pyGRNN import GRNN
import matplotlib.pyplot as plt
from sklearn.model_selection import  GridSearchCV
from sklearn.metrics import mean_squared_error as MSE
import scipy.signal as signal


# 识别股价序列数据中的技术形状
@run.change_dir
def shape(code, shapeName):
    if shapeName not in ("头肩顶", "头肩底", "三角顶", "三角底", "矩形顶", "矩形底", "顶部扩散", "底部扩散"):
        print("输入的形态名称有误")
        return []
    path = "./pooldata/"
    filename = path + code + ".csv"
    if os.path.exists(filename):
        data = tools.getStockData(code)
        rawdata = data.收盘.values
        # print(code, data.info())
        best_sigma = doSearch(code, rawdata)
        sigma = 0.3*best_sigma
        model = doGRNN(code, sigma, rawdata)
        x = np.arange(len(rawdata))
        y = model.predict(x.reshape(-1, 1))
        results = searchShape(y, shapeName)
        results["代码"] = code
        if len(results) != 0:
#            print(results)
#            print(results.位置)
#            print(len(results) - 1)
            pos = results.位置.values
#            print(results.位置)
#            print(pos)
#            print(data.loc[pos, ["日期"]])
            results.insert(0, "日期", data.loc[pos, ["日期"]].values)
        # print(results)
        return results
    else:
        print("无此股票数据\n")
        
        
# 在给定数据上寻找技术形态
def searchShape(y, shapeName):
    l = 35
    d = 3
    n = len(y)
    results = pd.DataFrame(columns = ["名称", "位置"])
    names = []
    pos = []
    # print(results.info())
    for t in range(n - l - d):
        window = []
        for k in range(t, t+l+d):
            window.append(y[k])
        maxExtrem, minExtrem = findExtrem(window)
        # print(maxExtrem, minExtrem)
        if maxExtrem is not None and minExtrem is not None:
            ts = judgeShape(maxExtrem, minExtrem, y)
            # print(ts)
            if ts == shapeName:
                names.append(ts)
                pos.append(t+l+d)
    results["名称"] = names
    results["位置"] = pos
    # print(results)
    return results
        
        
# 找到给定窗口内的极值
def findExtrem(data):
    data = np.array(data)
    maxExtrem = signal.argrelextrema(data, np.greater)
    minExtrem = signal.argrelextrema(data, np.less)
    # print(len(maxExtrem[0]), len(minExtrem[0]))
    if len(maxExtrem[0]) + len(minExtrem[0]) == 5:
        return (maxExtrem[0], minExtrem[0])
    else:
        return (None, None)
        
        
# 根据窗口内的极值情况，判断技术形态
def judgeShape(maxExtrem, minExtrem, y):
    # 计算E1……E5的位置，并根据E1的类型区分顶底
    bBottom = True
    # E1为极大值
    if maxExtrem[0] < minExtrem[0]: 
        # print(len(maxExtrem), len(minExtrem))
        E1 = maxExtrem[0]
        E2 = minExtrem[0]
        E3 = maxExtrem[1]
        E4 = minExtrem[1]
        E5 = maxExtrem[2]
        bBottom = False
    # E1为极小值
    else: 
        # print(len(maxExtrem), len(minExtrem))
        E1 = minExtrem[0]
        E2 = maxExtrem[0]
        E3 = minExtrem[1]
        E4 = maxExtrem[1]
        E5 = minExtrem[2]
        bBottom = True
        
    # 判断技术形态
    shape = ""
    #顶部形态
    if bBottom == False:
        # """ 暂时先注释掉
        # print("1")
        # 头肩顶 HS
        if HS(E1, E2, E3, E4, E5, y):
            shape = "头肩顶"
            return shape
        # 顶部扩散
        if BTOP(E1, E2, E3, E4, E5, y):
            shape = "顶部扩散"
            return shape
        # 三角顶
        if TTOP(E1, E2, E3, E4, E5, y):
            shape = "三角顶"
            return shape
        # 矩形顶
        if RTOP(E1, E2, E3, E4, E5, y):
            shape = "矩形顶"
            return shape
        #"""
        return shape
    # 底部形态
    else:
        # print("2")
        # 头肩底
        if IHS(E1, E2, E3, E4, E5, y):
            shape = "头肩底"
            return shape
        #""" 暂时先注释掉
        # 底部扩散
        if BBOT(E1, E2, E3, E4, E5, y):
            shape = "底部扩散"
            return shape
        # 三角底
        if TBOT(E1, E2, E3, E4, E5, y):
            shape = "三角底"
            return shape
        # 矩形底
        if RBOT(E1, E2, E3, E4, E5, y):
            shape = "矩形顶"
            return shape
        #"""
    return shape
    
        
        
# 判断头肩顶
def HS(E1, E2, E3, E4, E5, y):
    """
    ①E1是一个极大值。
    ②E3>E1，E3>E5。
    ③E1和E5在其平均值的1.5倍范围内。
    ④E2和E4在其平均值的1.5倍范围内。
    """
    # print(11)
    if y[E3] > y[E1] and y[E3] > y[E5]:
        # print("1a")
        mean15 = (y[E1] + y[E5])/2.0
        if y[E1] < 1.5*mean15 and y[E1] > mean15/1.5  and y[E5] < 1.5*mean15 and y[E5] > mean15/1.5:
            # print("1b")
            mean24 = (y[E2] + y[E4])/2.0
            if y[E2] < 1.5*mean24 and y[E2] > mean24/1.5  and y[E4] < 1.5*mean24 and y[E4] > mean24/1.5:
                # print("1c")
                return True
    return False
    
    
# 判断头肩底
def IHS(E1, E2, E3, E4, E5, y):
    """
    ①E1是一个极小值。
    ②E3<E1，E3<E5。
    ③E1和E5在其平均值的1.5倍范围内。
    ④E2和E4在其平均值的1.5倍范围内。
    """
    # print("22")
    if y[E3] < y[E1] and y[E3] < y[E5]:
        # print("2a")
        mean15 = (y[E1] + y[E5])/2.0
        if y[E1] < 1.5*mean15 and y[E1] > mean15/1.5  and y[E5] < 1.5*mean15 and y[E5] > mean15/1.5:
            # print("2b")
            mean24 = (y[E2] + y[E4])/2.0
            if y[E2] < 1.5*mean24 and y[E2] > mean24/1.5  and y[E4] < 1.5*mean24 and y[E4] > mean24/1.5:
                # print("2c")
                return True
    return False
    
    
# 判断顶部扩散
def BTOP(E1, E2, E3, E4, E5, y):
    """
    ①E1是极大值。
    ②E1<E3<E5
    ③E2>E4
    """
    if y[E1] < y[E3] and y[E3] < y[E5]:
        if y[E2] > y[E4]:
            return True
    return False
    
    
# 判断底部扩散
def BBOT(E1, E2, E3, E4, E5, y):
    """
    ①E1是极小值。
    ②E1>E3>E5
    ③E2<E4
    """
    if y[E1] > y[E3] and y[E3] > y[E5]:
        if y[E2] > y[E4]:
            return True
    return False
    
    
# 判断三角顶
def TTOP(E1, E2, E3, E4, E5, y):
    """
    ①E1是极大值。
    ②E1>E3>E5
    ③E2<E4
    """
    if y[E1] > y[E3] and y[E3] > y[E5]:
        if y[E2] < y[E4]:
            return True
    return False
    
    
# 判断三角底
def TBOT(E1, E2, E3, E4, E5, y):
    """
    ①E1是极小值。
    ②E1<E3<E5
    ③E2>E4
    """
    if y[E1] < y[E3] and y[E3] < y[E5]:
        if y[E2] > y[E4]:
            return True
    return False
    
    
# 判断矩形顶
def RTOP(E1, E2, E3, E4, E5, y):
    """
    ①E1是极大值。
    ②顶和底与它们的均值偏离均在75%以内。
    ③最低的高点>最高的低点。
    """
    yMax = np.array([y[E1], y[E3], y[E5]])
    yMin = np.array([y[E2], y[E4]])
    meanMax = yMax.mean()
    meanMin = yMax.min()
    minTop = yMax.min()
    maxBot = yMin.max()
    if y[E1] > 0.75*meanMax and y[E1] < 1.75*meanMax and y[E3] > 0.75*meanMax and y[E3] < 1.75*meanMax and y[E5] > 0.75*meanMax and y[E5] < 1.75*meanMax and y[E2] > 0.75*meanMin and y[E2] < 1.75*meanMin and y[E4] > 0.75*meanMin and y[E4] < 1.75*meanMin:
        if minTop > maxBot:
            return True
    return False
    
    
# 判断矩形底
def RBOT(E1, E2, E3, E4, E5, y):
    """
    ①E1是极小值。
    ②顶和底与它们的均值偏离均在75%以内。
    ③最低的高点>最高的低点。
    """
    yMax = np.array([y[E2], y[E4]])
    yMin = np.array([y[E1], y[E3], y[E5]])
    meanMax = yMax.mean()
    meanMin = yMax.min()
    minTop = yMax.min()
    maxBot = yMin.max()
    if y[E1] > 0.75*meanMin and y[E1] < 1.75*meanMin and y[E3] > 0.75*meanMin and y[E3] < 1.75*meanMin and y[E5] > 0.75*meanMin and y[E5] < 1.75*meanMin and y[E2] > 0.75*meanMax and y[E2] < 1.75*meanMax and y[E4] > 0.75*meanMax and y[E4] < 1.75*meanMax:
        if minTop > maxBot:
            return True
    return False
    
        
# 进行网格搜索最佳参数
@run.change_dir
def doSearch(code, data):
    x = np.arange(len(data))
    IGRNN = GRNN()
    params_IGRNN = {'kernel':["RBF"],
                'sigma' : list(np.arange(0.1, 10, 0.01)),
                'calibration' : ['None']
                 }
    grid_IGRNN = GridSearchCV(estimator=IGRNN,
                          param_grid=params_IGRNN,                           scoring='neg_mean_squared_error',
                          cv=5,
                          verbose=1
                          )
    grid_IGRNN.fit(x.reshape(-1, 1), data)
    best_model = grid_IGRNN.best_estimator_
    y_pred = best_model.predict(x.reshape(-1, 1))
    mse_IGRNN = MSE(data, y_pred)
#    print(mse_IGRNN)
#    print("最佳参数:", grid_IGRNN.best_params_)
    # draw(code, x, data, [data, y_pred])
    return grid_IGRNN.best_params_["sigma"]
    
    
# 用给定参数估计实际识别用的曲线
@run.change_dir
def doGRNN(code, sigma, data):
    x = np.arange(len(data))
    grnn = GRNN(kernel = "RBF", sigma = sigma, calibration = None)
    grnn.fit(x.reshape(-1, 1), data)
    y_pred = grnn.predict(x.reshape(-1, 1))
    # draw(code + "实际拟合曲线", x, data, [data, y_pred], "code:" + code + " params: " + str(sigma))
    return grnn
    
    
# 绘制原始数据和拟合后的数据
@run.change_dir
def draw(name, x, datas, lines, title = ""):
    plt.figure()
    plt.scatter(x, datas, s = 10, marker = "p", c = "y")
    plt.plot(x, lines[0], label = "real")
    plt.plot(x, lines[1], c = "r", label = "pred")
    plt.title(title)
    plt.legend(loc = "best")
    filename = "./output/" + name + "拟合结果.png"
    plt.savefig(filename)
    plt.close()
    
    
# 主程序
@run.change_dir
def main():
    # 先初始化，准备数据
    tools.init()
    codes = tools.Research(refresh = False, month = 6)
    # print(codes, len(codes))
    data = tools.getStockData(codes[0])
    # print(data.info())
    # tools.drawKLine(codes[0])
    # 搞定，开始识别
    i = 0
    n = len(codes)
    lastResults = pd.DataFrame()
    shapeName = "头肩底"
    for code in codes:
        print("已经完成", float(i)/n)
        i = i+1
        result = shape(code, shapeName)
        if len(result) != 0:
            # print(result)
            lastResults = lastResults.append(result.iloc[-1], ignore_index = True)
    lastResults.drop("位置", axis = 1, inplace = True)
    lastResults.sort_values(by = "日期", inplace = True)
    print("最终结果:\n", lastResults)
    lastResults.to_csv(shapeName + ".csv")    


if __name__ == "__main__":
    main()
