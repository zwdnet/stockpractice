# coding:utf-8
# 策略模式测试
# 参考《人人都懂设计模式》


from abc import ABCMeta, abstractmethod


class IVehicle(metaclass = ABCMeta):
    """交通工具的抽象类"""
    
    @abstractmethod
    def running(self):
        pass
        

class SharedBicycle(IVehicle):
    """共享单车"""
    def running(self):
        print("骑共享单车", end = '')
        
        
class ExpressBus(IVehicle):
    """公交"""
    def running(self):
        print("坐公交车", end = '')
        
        
class Subway(IVehicle):
    """坐地铁"""
    def running(self):
        print("坐地铁", end = '')
        
        
class Classmate:
    """同学聚餐"""
    def __init__(self, name, vechicle):
        self.__name = name
        self.__vechicle = vechicle
        
    def attendTheDinner(self):
        print(self.__name + " ", end = '')
        self.__vechicle.running()
        print(" 来聚餐")
        
        
# 测试Classmate类
def testTheDinner():
    sharedBicycle = SharedBicycle()
    joe = Classmate("joe", sharedBicycle)
    joe.attendTheDinner()
    expressBus = ExpressBus()
    helen = Classmate("helen", expressBus)
    helen.attendTheDinner()
    subway = Subway()
    ruby = Classmate("ruby", subway)
    ruby.attendTheDinner()


if __name__ == "__main__":
    testTheDinner()