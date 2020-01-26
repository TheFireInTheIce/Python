from ..core import event
from ..core import component
from ..core.config import config
from ..core import tools
from . import ui
import os
import pygame
import math


@tools.Class('id color'.split(" "))
class Rect(ui.BaseUI):
    def __init__(self, id, color='black'):
        super().__init__(id)
        self.color = color
        self.display = 'inline'
        self.mode = 'fill'
        self.lineWidth = 1

    def draw(self, screen, x=0, y=0):
        if self.mode == 'fill':
            screen.fillRect(x + self.px, y + self.py,
                            self.w, self.h, self.color)
        else:
            screen.fillRect(x + self.px, y + self.py, self.w,
                            self.h, self.color, self.lineWidth)

    def onPoint(self, x, y):
        return self if x > self.px and x < self.px+self.w and y > self.py and y < self.py+self.h else None

    def step(self, time):
        super().step(time)


@tools.Class("id color".split(" "))
class Line(ui.BaseUI):
    def __init__(self, id, color):
        super().__init__(id)
        self.color = color
        self.sx = 0
        self.sy = 0
        self.ex = 0
        self.ey = 0
        self.lineWidth = 1

    def draw(self, screen, x=0, y=0):
        screen.drawLine(self.sx, self.sy, self.ex, self.ey,
                        self.color, self.lineWidth)

    def onPoint(self, x, y):
        return None
