from ..core import event
from ..core import component
from ..core.config import config
from ..core import tools
from . import sprite
import os
import pygame
import math


class BaseUI(component.ComponentObj):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.x = 0
        self.y = 0
        self.px = 0
        self.py = 0
        self.w = 0
        self.h = 0
        self.align = 'left'
        self.display = 'inline'
        self.father = None

    def setpos(self):
        if self.align == 'right':
            self.px = self.father.w -self.w+ self.x
        elif self.align == 'left':
            self.px = self.x
        elif self.align == 'center':
            self.px = self.father.w / 2 - self.w / 2
        self.py = self.y

    def step(self, time):
        super().step(time)
        self.setpos()


@tools.Class(['id', 'up', 'down'])
class ImgButton(BaseUI):
    def __init__(self, id, up, down):
        super().__init__(id)
        self.upImg = up.convert_alpha()
        self.downImg = down.convert_alpha()
        self.img = self.upImg
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
        screen.blit(self.img, (x + self.px, y + self.py))

    def onPoint(self, x, y):
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        bx = x-self.px
        by = y-self.py
        if bx >= 0 and bx < self.w and by >= 0 and by < self.h:
            if self.img.get_at((int(bx), int(by))) != (0, 0, 0, 0):
                return self
        return None


@tools.Class("id text textColor bgColor fontSize font".split(" "))
def TextButton(id, text, textColor=(255, 255, 255), bgColor=(0, 0, 0), fontSize=30, font="微软雅黑"):
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
    return ImgButton(id, up, down)


@tools.Class(['id'])
class Switch(BaseUI):
    def __init__(self, id):
        super().__init__(id)

        self.w = 50
        self.h = 20
        self.buttonX = 0
        self.buttonVx = 0
        self.speed = 100
        self._state = False
        self.bgColor = config.closeSwitchBackgroundColor
        self.on(event.events.click, self.onclick)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        if self._state:
            self.bgColor = config.openSwitchBackgroundColor
            self.buttonX = self.w - self.h
        else:
            self.bgColor = config.closeSwitchBackgroundColor
            self.buttonX = 0
        self.buttonVx = 0

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

        screen.blit(img, (x+self.px, y+self.py))

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
        self.bgColor = config.openSwitchBackgroundColor if self._state else config.closeSwitchBackgroundColor

    def onclick(self, event, this):
        if self._state:
            self.buttonVx = -self.speed
        else:
            self.buttonVx = self.speed
        self._state = not self._state

    def distance(self, cx, cy, px, py):
        bx = px-cx
        by = py-cy
        return int(math.sqrt(bx*bx+by*by))

    def onPoint(self, x, y):
        halfH = self.h/2
        bx = x-self.px
        by = y-self.py
        if bx >= halfH and bx <= self.w-halfH and by >= 0 and by < self.h:
            return self
        if self.distance(halfH, halfH, bx, by) <= halfH or self.distance(self.w-halfH, halfH, bx, by) <= halfH:
            return self
        return None


@tools.Class("id text".split(" "))
class Text(BaseUI):
    def __init__(self, id, text):
        super().__init__(id)
        self.inited = False
        self.text = text
        self.font = "微软雅黑"
        self.fontSize = 18
        self.bgColor = (0, 0, 0, 0)
        self.textColor = (0, 0, 0, 255)
        self.inited = True
        self.init()

    def init(self):
        if not self.inited:
            return
        self.fontObj = pygame.font.Font(os.path.join(
            config.fontPath, config[self.font]) if self.font else None, self.fontSize)
        self.w, self.h = self.fontObj.size(self.text)
        self.img = pygame.Surface((self.w, self.h)).convert_alpha()
        self.img.fill(self.bgColor)
        self.img.blit(self.fontObj.render(
            self.text, True, self.textColor), (0, 0))

    def draw(self, screen, x=0, y=0):
        screen.blit(self.img, (x+self.px, y+self.py))

    def onPoint(self, x, y):
        x -= self.px
        y -= self.py
        x = int(x)
        y = int(y)
        if x >= 0 and x < self.w and y >= 0 and y < self.h:
            if self.img.get_at((x, y)) != (0, 0, 0, 0):
                return self
        return None

    def __setattr__(self, item, value):
        self.__dict__[item] = value
        if 'inited' in self.__dict__ and self.inited and item in ('font', 'text', 'fontSize', 'textColor', 'bgColor'):
            self.init()


@tools.Class("id text".split(" "))
class MultiLineText(Text):
    def __init__(self, id, text):
        super().__init__(id, text)
        self.init()
        self.inited = True

    def init(self):
        self.texts = self.text.split('\n')
        self.fontObj = pygame.font.Font(os.path.join(
            config.fontPath, config[self.font]) if self.font else None, self.fontSize)
        self.h = len(self.texts)*self.fontObj.size('l')[1]
        self.w = 0
        for i in self.texts:
            if self.fontObj.size(i)[0] > self.w:
                self.w = self.fontObj.size(i)[0]
        self.img = pygame.Surface((self.w, self.h)).convert_alpha()
        self.img.fill(self.bgColor)
        for text, y in zip(self.texts, range(0, len(self.texts)*self.fontObj.size('l')[1], self.fontObj.size('l')[1])):
            self.img.blit(self.fontObj.render(
                text, True, self.textColor), (0, y))

@tools.Class(['id', 'img', 'rows', 'cols'])
class Img(BaseUI):
    def __init__(self, id, img, rows, cols):
        super().__init__(id)
        self.sheet = sprite.Sheet(img, rows, cols)
        self.row = 0
        self.col = 0
        self.sx = 0
        self.sy = 0
        self.angle = 0
        self.img = None
    def setImg(self):
        self.img = self.sheet.get(self.row, self.col)
        if self.angle != 0:
            self.img = pygame.transform.rotate(self.img, self.angle)
        if self.sw != 1 or self.sh != 1:
            self.img = pygame.transform.scale(
                self.img, (int(self.sw*self.img.get_width()), int(self.sh*self.img.get_height())))
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        
    def draw(self, screen, x=0, y=0):
        self.setImg()
        screen.blit(self.img, (x + self.px, y + self.py))
    def onPoint(self, x, y):
        self.setImg()
        x = int(x-self.px)
        y = int(y-self.py)
        if x >= 0 and x < self.img.get_width() and y >= 0 and y < self.img.get_height():
            if self.img.get_at((x, y)) != (0, 0, 0, 0):
                return self
        return None

@tools.Class(['id'])
class Div(BaseUI):
    def __init__(self, id):
        super().__init__(id)
        self.display = 'block'
        self.children = []
        self._c = self.children[:]
        self.minW = 0
        self.minH = 0

    def resetSize(self):
        self.w = self.minW
        self.h = self.minH
        for i in self.children:
            if i.py + i.h > self.h:
                self.h = i.py + self.h
        if self.display == 'block':
            self.px = 0
            self.w = self.father.w
            return
        for i in self.children:
            if i.px + i.w > self.w:
                self.w = i.px + i.w

    def addChild(self, ui):
        ui.father = self
        self.children.append(ui)
        self.w = max(self.w, ui.px+ui.w)
        self.h = max(self.h, ui.py+ui.h)

    def delChild(self, ui):
        ui.father = None
        self.children.remove(ui)
        self.resetSize()

    def draw(self, screen, x=0, y=0):
        for i in self.children:
            i.draw(screen, self.px+x, self.py+y)

    def step(self, time):
        self.resetSize()
        self.setpos()
        super().step(time)
        for i in self.children:
            i.step(time)

    def onPoint(self, x, y):
        for i in reversed(self.children):
            res = i.onPoint(x-self.px, y-self.py)
            if res != None:
                return res
        return None


@tools.Class(['id'])
class RowLayer(Div):
    def __init__(self, id):
        super().__init__(id)
        self.colWidth = 10
        self.mode = 'left'

    def step(self, time):
        super().step(time)
        if self.mode == 'left':
            bx = 0
            for i in self.children:
                i.px = i.x + bx
                bx += i.w + self.colWidth
        elif self.mode == 'dispersed':
            if len(self.children)==0:return
            if len(self.children) > 1:
                s = 0
                for i in self.children:
                    s += i.x + i.w
                sp = (self.w - s) // (len(self.children) - 1)
                bx = 0
                for i in self.children:
                    i.px = i.x + bx
                    bx += i.w + sp
            else:
                self.children[0].px = self.w/2 - \
                    self.children[0].w/2+self.children[0].x


@tools.Class(['id'])
class ColLayer(Div):
    def __init__(self, id):
        super().__init__(id)
        self.rowHeight = 10

    def step(self, time):
        super().step(time)
        by = 0
        for i in self.children:
            i.py = i.y + by
            by += i.h + self.rowHeight


@tools.Class(['id'])
class UIs(BaseUI):
    def __init__(self, id):
        super().__init__(id)
        self.children = []

    def addChild(self, ui):
        ui.father = self
        self.children.append(ui)
        self.w = max(self.w, ui.px+ui.w)
        self.h = max(self.h, ui.py+ui.h)

    def delChild(self, ui):
        ui.father = None
        self.children.remove(ui)
        self.resetSize()

    def draw(self, screen, x=0, y=0):
        for i in self.children:
            i.draw(screen, x, y)

    def onPoint(self, x, y):
        for i in reversed(self.children):
            r = i.onPoint(x, y)
            if r != None:
                return r
        return None

    def step(self, time):
        super().step(time)
        for i in self.children:
            i.step(time)
