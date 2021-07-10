# coding:utf-8
# 将程序上传到服务器上执行
import os
import sys
from functools import wraps
import time


# 上传代码至服务器并运行
def run(gpus, server):
    # 上传本目录所有文件再执行指定文件
    if gpus == "all":
        # 清除服务器代码目录里所有源文件以及输出目录中的文件
        s = "ssh ubuntu@" + server + " \"sudo rm -rf ~/code/*.py\""
        os.system(s)
        s = "ssh ubuntu@" + server + " \"sudo rm -rf ~/code/output/*\""
        os.system(s)
        # 将本地目录所有文件上传至容器
        s = "scp -r ./*.py ubuntu@" + server + ":~/code"
        os.system(s)
        # 运行指定代码
        s = "ssh root@" + server +  " -p 2222 \"python /home/code/" + sys.argv[2] + "\""
        print("正在运行代码……\n")
        os.system(s)
        # 将代码目录里所有输出文件传回
        s = "scp -r ubuntu@" + server + ":~/code/output/* ./output/"
        os.system(s)
    # 将所有结果文件传回
    elif gpus == "copy":
        s = "scp -r ubuntu@" + server + ":~/code/output/* ./output/"
        os.system(s)
    # 上传指定文件并执行
    else:
        ## 清除服务器代码目录里所有源文件以及输出目录中的文件
        s = "ssh ubuntu@" + server + " \"sudo rm -rf ~/code/*.py\""
        os.system(s)
        s = "ssh ubuntu@" + server + " \"sudo rm -rf ~/code/output/*\""
        os.system(s)
        # 将本地目录指定文件上传至容器
        s = "scp " + sys.argv[1] + " ubuntu@" + server + ":~/code"
        os.system(s)
        # 运行指定代码
        s = "ssh root@" + server +  " -p 2222 \"python /home/code/" + sys.argv[1] + "\""
        os.system(s)
        # 将代码目录里所有文件传回
        s = "scp -r ubuntu@" + server + ":~/code/output/* ./output/"
        os.system(s)


if __name__ == "__main__":
    gpus = sys.argv[1]
    # 读取服务器IP地址，自己编辑serverIP.txt去
    with open("serverIP.txt", "rt") as f:
        server = f.read()
    run(gpus, server)
        
    
# 工具函数，在上传到服务器上运行时改变当前目录
def change_dir(func):
    @wraps(func)
    def change(*args, **kwargs):
        oldpath = os.getcwd()
        newpath = "/home/code/"
        os.chdir(newpath)
        r = func(*args, **kwargs)
        os.chdir(oldpath)
        return r
    return change
    
    
# 工具函数，计算函数运行时间    
def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{}的运行时间为 : {}秒'.format(func.__module__, func.__name__, end - start))
        return r
    return wrapper
    