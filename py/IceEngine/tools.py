import threading
import time
import copy
#特殊字典类
class dic:
    def __init__(self,dict={}):
        for i in dict:
            self[i]=dict[i]
        
    def __getitem__(self,item):
        return self.__dict__[item]
    def __setitem__(self,item,value):
        self.__dict__[item]=value

    def __str__(self):
        return str(self.__dict__)

    def find(self,item):
        for i in self.__dict__:
            if self.__dict__[i] == item:
                return i
        return None

    def __iter__(self):
        return self.__dict__.__iter__()

    def __add__(self,item):
        x=copy.deepcopy(self)
        for i in item:
            x[i]=item[i]
        return x

class enum:
    def __init__(self,enums:list):
        self.dic=dic({})
        for i in range(len(enums)):
            self.dic[enums[i]]=i
    def __getattr__(self,item):
        return self.dic[item]
    __getitem__=__getattr__

def setTimeOut(function,ti):
    def p():
        time.sleep(ti)
        function()
    t=threading.Thread(None,p)
    t.start()
