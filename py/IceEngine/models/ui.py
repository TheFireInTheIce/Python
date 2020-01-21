from ..core import event
from ..core import component
from ..core.config import config
from ..core import tools
import os
import pygame
import math

@tools.Class(['up','down'])
class ImgButton(component.ComponentObj):
    def __init__(self, up, down):
        super().__init__()
        self.upImg = up.convert_alpha()
        self.downImg = down.convert_alpha()
        self.img = self.upImg
        self.x = 0
        self.y = 0
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.cw = (self.downImg.get_width()-self.upImg.get_width())//2
        self.ch = (self.downImg.get_height()-self.upImg.get_height())//2

        def changeImg(eventobj, this):
            if eventobj.type == event.events.mousedown:
                self.img = self.downImg
                self.x -= self.cw
                self.y -= self.ch
            else:
                self.img = self.upImg
                self.x += self.cw
                self.y += self.ch
            self.w = self.img.get_width()
            self.h = self.img.get_height()
        self.on(event.events.mousedown, changeImg)
        self.on(event.events.mouseup, changeImg)

    def draw(self, screen, x=0, y=0):
        screen.blit(self.img, (x+self.x, y+self.y))

    def onPoint(self, x, y):
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        bx = x-self.x
        by = y-self.y
        if bx >= 0 and bx < self.w and by >= 0 and by < self.h:
            if self.img.get_at((int(bx), int(by))) != (0, 0, 0, 0):
                return self
            else:
                print(self.img.get_at((int(bx), int(by))))
        return None

@tools.Class("text textColor bgColor fontSize font".split(" "))
def TextButton(text, textColor=(255, 255, 255), bgColor=(0, 0, 0), fontSize=30, font="微软雅黑"):
    font = pygame.font.Font(os.path.join(
        config.fontPath, config[font]) if font else None, fontSize)
    w, h = font.size(text)
    up = pygame.Surface((w+20, h+20)).convert_alpha()
    down = pygame.Surface((w+30, h+30)).convert_alpha()
    ti = font.render(text, True, textColor)
    up.fill(bgColor)
    down.fill(bgColor)
    up.blit(ti, (10, 10))
    down.blit(ti, (15, 15))
    return ImgButton(up, down)

@tools.Class([])
class Switch(component.ComponentObj):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.w = 50
        self.h = 20
        self.buttonX = 0
        self.buttonVx = 0
        self.speed = 100
        self.state = False
        self.bgColor = config.closeSwitchBackgroundColor
        self.on(event.events.click, self.onclick)

    def draw(self, screen, x=0, y=0):
        buttonX = int(self.buttonX)
        halfH = int(self.h//2)
        img = pygame.Surface((self.w, self.h)).convert_alpha()
        img.fill((0, 0, 0, 0))
        pygame.draw.rect(img, self.bgColor, (halfH, 0, self.w-self.h, self.h))
        pygame.draw.circle(img, self.bgColor, (halfH, halfH), halfH)
        pygame.draw.circle(img, self.bgColor, (self.w-halfH, halfH), halfH)

        pygame.draw.circle(img, config.switchCircleColor,
                        (halfH+buttonX, halfH), halfH-3)

        screen.blit(img, (x+self.x, y+self.y))

    def update(self, time):
        super().update(time)
        self.buttonX += self.buttonVx*time
        if self.buttonX >= self.w-self.h:
            self.buttonX = self.w-self.h
            self.buttonVx = 0
            self.changeColor()
        if self.buttonX <= 0:
            self.buttonX = 0
            self.buttonVx = 0
            self.changeColor()

    def changeColor(self):
        self.bgColor = config.openSwitchBackgroundColor if self.state else config.closeSwitchBackgroundColor

    def onclick(self, event, this):
        if self.state:
            self.buttonVx = -self.speed
        else:
            self.buttonVx = self.speed
        self.state = not self.state

    def distance(self, cx, cy, px, py):
        bx = px-cx
        by = py-cy
        return int(math.sqrt(bx*bx+by*by))

    def onPoint(self, x, y):
        halfH = self.h/2
        bx = x-self.x
        by = y-self.y
        if bx >= halfH and bx <= self.w-halfH and by >= 0 and by < self.h:
            return self
        if self.distance(halfH, halfH, bx, by) <= halfH or self.distance(self.w-halfH, halfH, bx, by) <= halfH:
            return self
        return None

@tools.Class("text".split(" "))
class Text(component.ComponentObj):
    def __init__(self,text):
        super().__init__()
        self.inited=False
        self.text=text
        self.font="微软雅黑"
        self.fontSize=18
        self.bgColor=(0,0,0,0)
        self.textColor=(0,0,0,255)
        self.x=0
        self.y=0
        self.inited=True
        self.init()
    def init(self):
        if not self.inited:return
        self.fontObj = pygame.font.Font(os.path.join(
        config.fontPath, config[self.font]) if self.font else None, self.fontSize)
        self.w, self.h = self.fontObj.size(self.text)
        self.img = pygame.Surface((self.w, self.h)).convert_alpha()
        self.img.fill(self.bgColor)
        self.img.blit(self.fontObj.render(self.text, True,self.textColor),(0,0))
    def draw(self,screen,x=0,y=0):
        screen.blit(self.img,(x+self.x,y+self.y))
    def onPoint(self,x,y):
        x-=self.x
        y-=self.y
        x=int(x)
        y=int(y)
        if x>=0 and x<self.w and y>=0 and y<self.h:
            if self.img.get_at((x,y))!=(0,0,0,0):
                return self
        return None
    def __setattr__(self,item,value):
        self.__dict__[item]=value
        if 'inited' in self.__dict__ and self.inited and item in ('font','text','fontSize','textColor','bgColor'):
            self.init()

@tools.Class("text".split(" "))
class MultiLineText(Text):
    def __init__(self,text):
        super().__init__(text)
        self.init()
        self.inited=True
    def init(self):
        #if 'texts' not in self.__dict__:return
        self.texts=self.text.split('\n')
        self.fontObj = pygame.font.Font(os.path.join(
        config.fontPath, config[self.font]) if self.font else None, self.fontSize)
        self.h=len(self.texts)*self.fontObj.size('l')[1]
        self.w=0
        for i in self.texts:
            if self.fontObj.size(i)[0]>self.w:
                self.w=self.fontObj.size(i)[0]
        self.img = pygame.Surface((self.w, self.h)).convert_alpha()
        self.img.fill(self.bgColor)
        for text,y in zip(self.texts,range(0,len(self.texts)*self.fontObj.size('l')[1],self.fontObj.size('l')[1])):
            self.img.blit(self.fontObj.render(text, True,self.textColor),(0,y))

@tools.Class([])
class Div:
    def __init__(self):
        self.children=[]
    def addUi(self,ui):
        self.children.append(ui)
    def removeUi(self,ui):
        self.children.remove(ui)
    def draw(self,screen,x=0,y=0):
        for i in self.children:
            self.children.draw(screen,x,y)