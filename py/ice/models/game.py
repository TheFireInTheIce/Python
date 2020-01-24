import time
import os
import sys
from pygame import locals as pc
import pygame
from . import sprite
from ..core import component
from . import scene
from ..core import event
from ..core import tools
from . import screen
from ..core.config import config
from . import ui


class Game(event.EventObj):
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.scene = -1
        self.screen = None
        self.hud = None
        self.assets = tools.dic()
        self.fps = config.fps
        self.lastUpdateTime = time.time()
        self.eventCatcher = event.EventCatcher()
        self.eventsQ = []
        self.on(event.events.quit, self.exit)

    def exit(self, event, this):
        os._exit(0)

    def init(self, title, width, height):
        assert self.screen == None, "当前屏幕对象不为空,已经进行过初始化,不能再次初始化"
        pygame.init()
        #self.screen = pygame.display.set_mode((width, height))
        self.screen = screen.Screen(title, (width, height))
        self.hud = screen.HUD((width, height), self)

    def addScene(self, scene: scene.Scene):
        self.scenes.append(scene)

    @property
    def currentScene(self):
        if self.scene == -1:
            return None
        return self.scenes[self.scene]

    def removeScene(self, scene: scene.Scene):
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
        self.hud.scene.step(time)
        self.scenes[self.scene].step(time)

    def paint(self):
        assert self.scene != -1, "没有场景对象,请先创建并设置场景"
        self.screen.fill(config.bgColor)
        self.hud.fill((0, 0, 0, 0))
        self.draw()
        self.scenes[self.scene].draw(self.screen)
        self.hud.scene.draw(self.hud)
        self.screen.screen.blit(self.hud.screen, (0, 0))
        pygame.display.update()

    def draw(self): pass
    def update(self, time): pass

    def addEvent(self, e):
        self.eventsQ.append(e)

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

                    elif i in (event.events.keydown, event.events.keyup):
                        self.scenes[self.scene].event(el)
            mx, my = pygame.mouse.get_pos()
            self.scenes[self.scene].getSpriteOnPoint(mx, my).event(event.Event(event.events.mouseover, tools.dic({
                "pos": (mx, my)
            })))

            while len(self.eventsQ) != 0:
                e = self.eventsQ.pop(0)
                if e.target == None:
                    q = self.currentScene.sprites[:]+self.hud.scene.sprites[:]
                    while len(q) != 0:
                        node = q.pop(0)
                        node.event(e)
                        if getattr(node, 'children', None) != None:
                            q += node.children
                else:
                    e.target.event(e)

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
                assert False, "文件"+p+"不存在!"

    def key(self, key):
        return self.eventCatcher.keys[key]
