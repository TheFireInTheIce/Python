import threading
import time
import copy
# 特殊字典类


class dic:
    def __init__(self, dict=None):
        self.dict = {}
        # 如果传入参数
        if dict != None:
            # 将参数赋值给自己
            for i in dict:
                self[i] = dict[i]

    def __setattr__(self, item, value):
        if item == 'dict':
            super().__setattr__(item, value)
            return
        self.dict[item] = value

    def __getattr__(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return None

    def __getitem__(self, item):
        return self.dict[item]

    def __setitem__(self, item, value):
        self.dict[item] = value

    def __str__(self):
        s = "dic:{"
        for i in self.dict:
            if type(self.dict[i]) == list:
                s += i+": "+listToStr(self.dict[i])+", "
            else:
                s += i+": "+str(self.dict[i])+", "
        s = s[:-2]
        s += "}"
        return s

    def find(self, item):
        for i in self.dict:
            if self.dict[i] == item:
                return i
        return None

    def has(self, item):
        return item in self.dict

    def __iter__(self):
        return self.dict.__iter__()

    def __add__(self, item):
        x = dic()
        for i in self.dict:
            x[i] = self[i]
        for i in item:
            x[i] = item[i]
        return x


class enum:
    def __init__(self, enums: list):
        self.dic = dic({})
        for i in range(len(enums)):
            self.dic[enums[i]] = i

    def __getattr__(self, item):
        return self.dic[item]
    __getitem__ = __getattr__


def setTimeOut(function, ti):
    def p():
        time.sleep(ti)
        function()
    t = threading.Thread(None, p)
    t.start()


def listToStr(listO):
    s = '['
    if len(listO) != 0:
        for i in range(len(listO)-1):
            s += str(listO[i])+', '
        s += str(listO[-1])
    s += ']'
    return s


classes = {}
class Class:
    def __init__(self,*args):
        self.args=args[0]
    def __call__(self,c):
        classes[c.__name__] = (self.args, c)
        return c