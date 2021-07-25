# coding:utf-8
# 1000元实盘练习程序
# 测试求极值
# 参考https://blog.csdn.net/weijifen000/article/details/80070520


import numpy as np 
import pylab as pl
import matplotlib.pyplot as plt
import scipy.signal as signal
import run


@run.change_dir
def main():
    x=np.array([
    0, 6, 25, 20, 15, 8, 15, 6, 0, 6, 0, -5, -15, -3, 4, 10, 8, 13, 8, 10, 3,
    1, 20, 7, 3, 0 ])
    plt.figure(figsize=(16, 4))
    plt.plot(np.arange(len(x)), x)
    print(x[signal.argrelextrema(x, np.greater)])
    print(signal.argrelextrema(x, np.greater))
    print(x[signal.argrelextrema(x, np.less)])
    print(signal.argrelextrema(x, np.less))

    plt.plot(signal.argrelextrema(x, np.greater)[0], x[signal.argrelextrema(x, np.greater)], 'o')
    plt.plot(signal.argrelextrema(x, np.less)[0], x[signal.argrelextrema(x, np.less)], '+')
    plt.savefig("./output/testextrem.png")


if __name__ == "__main__":
    main()