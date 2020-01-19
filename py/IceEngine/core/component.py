# import pygame
# from . import event
imports=['pygame','event']

def initModel():
    class Component:
        def __init__(self, function, ctype="loop"):
            "init(function:执行的函数,被存储为对象的action属性,type:类型,有循环(loop),时间(int类型,秒)或次数('s'+str(int)))"
            self.action = function
            if ctype == 'loop':
                self.life = ctype
                self.type = ctype
            elif type(ctype) == int:
                self.life = ctype
                self.type = "time"
            elif ctype[0] == 's':
                self.life = int(ctype[1:])
                self.type = 'step'

        def update(self, obj, time):
            f = self.action(obj, time) is False
            if self.type == 'time':
                self.life -= time
                if self.life <= 0:
                    return False
            elif self.type == 'step':
                self.life -= 1
                if self.life <= 0:
                    return False
            return not f


    class ComponentObj(event.EventObj):
        def __init__(self):
            super().__init__()
            self.components=[]

        def addComponent(self, component):
            self.components.append(component)

        def removeComponent(self, component):
            for i in self.components:
                if i is component:
                    del i

        def step(self, time):
            self.update(time)
            for i in range(len(self.components)):
                l = self.components[i].update(self, time)
                if not l:
                    del self.components[i]

        def update(self, time): pass
    return {
        'Component':Component,
        'ComponentObj':ComponentObj
    }
