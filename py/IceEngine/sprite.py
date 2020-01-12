import pygame
from . import event
from . import component


class Sheet:
    def __init__(self, img, rows, cols):

        self.img = img
        self.rows = rows  # 行数
        self.cols = cols  # 列数

        self.fWidth = self.img.get_width()//self.cols
        self.fHeight = self.img.get_height()//self.rows

        self.imgs = []

        for i in range(self.rows):
            self.imgs.append([])
            for j in range(self.cols):
                self.imgs[i].append(self.img.subsurface(pygame.Rect(
                    j*self.fWidth, i*self.fHeight, self.fWidth, self.fHeight)))

    def get(self, row, col):
        return self.imgs[row][col]


class Animate:
    def __init__(self, img, rows, cols):

        self.row = 0
        self.col = 0

        self.frame = Sheet(img, rows, cols)

    def get(self):
        return self.frame.get(self.row, self.col)

    def setFrame(self, row, col):
        """
        注意,第一个是行,第二个是列
        """
        self.col, self.row = col, row

    def setRow(self, row):
        '''
        注意,左上角下标为 0,0
        '''
        self.row = row

    def update(self):
        self.col = (self.col+1) % 3


class Sprite(component.ComponentObj):
    def __init__(self, id, img, rows, cols):
        super().__init__()

        self.id = id

        self.x = 0
        self.y = 0
        self.sw = 1
        self.sh = 1
        self.angle = 0

        self.frames = Animate(img, rows, cols)
        self.img = self.frames.get()
        self.w, self.h = self.img.get_width(), self.img.get_height()

        self.children = []

    def draw(self, screen, x=0, y=0):
        self.img = self.frames.get()
        if self.angle != 0:
            self.img = pygame.transform.rotate(self.img, self.angle)
        if self.sw != 1 or self.sh != 1:
            self.img = pygame.transform.scale(
                self.img, (int(self.sw*self.img.get_width()), int(self.sh*self.img.get_height())))
        bx, by = int(self.x+x), int(self.y+y)
        screen.blit(self.img, (bx, by))
        for s in self.children:
            s.draw(screen, bx, by)

    def step(self, time):
        super().step(time)
        for i in self.children:
            i.step(time)

    def addChild(self, child):
        self.children.append(child)

    def delChild(self, child):
        for i in self.children:
            if i is child:
                del i

    def onPointSelf(self, x, y):
        sx = int(x-self.x)
        sy = int(y-self.y)
        if self.img != None:
            self.w, self.h = self.img.get_width()*self.sw, self.img.get_height()*self.sh
            if sx >= 0 and sx < self.w and sy >= 0 and sy < self.h:
                if self.img.get_at((sx, sy)) != (0, 0, 0, 0):
                    return True

        return False

    def onPoint(self, x, y):
        for s in self.children:
            if x:=s.onPoint(x, y) != None:
                return x
        return (self if self.onPointSelf(x, y) else None)

    def update(self, time):
        pass
