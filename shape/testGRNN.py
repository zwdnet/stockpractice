# coding:utf-8
# 1000元实盘练习程序
# 测试用pyGRNN进行Nadaraya-Watson Estimator


import numpy as np
from pyGRNN import GRNN
import matplotlib.pyplot as plt
import run
from sklearn.model_selection import  GridSearchCV
from sklearn.metrics import mean_squared_error as MSE


# 画图
@run.change_dir
def draw(name, x, datas, lines, title = ""):
    plt.figure()
    plt.scatter(x, datas, s = 10, marker = "p", c = "y")
    plt.plot(x, lines[0], label = "real")
    plt.plot(x, lines[1], c = "r", label = "pred")
    plt.title(title)
    plt.legend(loc = "best")
    filename = "./output/" + name + ".png"
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    # 产生数据
    x = np.arange(0, 2*np.pi, 0.05)
    # print(x)
    y = np.sin(x)
    noise = np.random.normal(size = len(x))
    data = y + 0.5*noise
    guess1 = x
    draw("test0", x, data, [y, guess1])
    
    IGRNN = GRNN()
    params_IGRNN = {'kernel':["RBF"],
                'sigma' : list(np.arange(0.1, 4, 0.01)),
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
    print(mse_IGRNN)
    print("最佳参数:", grid_IGRNN.best_params_)
    draw("test1", x, data, [y, y_pred])
    
    sigma = [0.1, 0.3, 0.5, 2.0]
    i = 2
    for s in sigma:
        grnn = GRNN(kernel = "RBF", sigma = s, calibration = None)
        grnn.fit(x.reshape(-1, 1), data)
        y_pred = grnn.predict(x.reshape(-1, 1))
        name = "test" + str(i)
        i += 1
        draw(name, x, data, [y, y_pred], "var = " + str(s))
        