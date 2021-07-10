# coding:utf-8
# 测试读取ip地址文件


i = 0
with open("serverIP.txt", "rt") as f:
    server = f.readlines()
for s in server:
    # print(s)
    s = s.replace('\n', '').replace('\r', '')
    if s[0] != "#":
        print(s)
        res = s.split("@")
        print(res)