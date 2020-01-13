import time
import os
import sys

from pygame import locals as pc
import pygame

from .sprite import *
from .component import *
from .scene import *
from . import event
from . import tools
from . import screen
from .config import config


class Game(event.EventObj):
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.scene = -1
        self.screen = None
        self.assets = tools.dic()
        self.fps = config.fps
        self.lastUpdateTime = time.time()
        self.eventCatcher = event.EventCatcher()
        self.on(event.events.quit,self.exit)
    def exit(self,event,this):
        os._exit(0)
    def init(self,title, width, height):
        assert self.screen == None, "当前屏幕对象不为空,已经进行过初始化,不能再次初始化"
        pygame.init()
        #self.screen = pygame.display.set_mode((width, height))
        self.screen=screen.Screen(title,(width,height))

    def addScene(self, scene: Scene):
        self.scenes.append(scene)

    def removeScene(self, scene: Scene):
        assert scene in self.scenes, "没有此场景"
        self.scenes.remove(scene)

    def switchScene(self, sceneId: str):
        for i in range(len(self.scenes)):
            if self.scenes[i].id == sceneId:
                self.scene = i
                return
        assert False, "没有此场景"

    def step(self, time):
        assert self.scene != -1, "没有场景对象,请先创建并设置场景"
        self.update(time)
        self.scenes[self.scene].step(time)

    def paint(self):
        assert self.scene != -1, "没有场景对象,请先创建并设置场景"
        self.screen.fill(config.bgColor)
        self.draw()
        self.scenes[self.scene].draw(self.screen)
        pygame.display.update()

    def draw(self): pass
    def update(self, time): pass

    def start(self):
        while True:
            pygame.time.delay(int(self.fps*1000))
            for e in pygame.event.get():
                eh = self.eventCatcher.classifyEvent(e)
                for i in eh:
                    el = event.Event(i, e)
                    if i <= 6:  # 鼠标事件
                        x, y = e.pos
                        obj = self.scenes[self.scene].getSpriteOnPoint(x, y)
                        if obj != None:
                            obj.event(el)
                            
                    elif i == event.events.quit:
                        self.event(el)
            mx, my = pygame.mouse.get_pos()
            self.scenes[self.scene].getSpriteOnPoint(mx, my).event(event.Event(event.events.mouseover, tools.dic({
                "pos": (mx, my)
            })))

            interval = time.time() - self.lastUpdateTime
            self.lastUpdateTime = time.time()
            self.step(interval)
            self.paint()

    def loadImages(self, assets: list):
        for i in assets:
            p = os.path.join(sys.path[0], i.path)
            if os.path.exists(p):
                img = pygame.image.load(os.path.join(sys.path[0], i.path))
                self.assets[i.name] = img.convert_alpha()
            else:
                assert False,"文件"+p+"不存在!"

    def key(self, key):
        return self.eventCatcher.keys[key]
