import pygame
from ..core import event


class Scene(event.EventObj):
    def __init__(self, id, game):
        super().__init__()
        self.id = id
        self.sprites = []
        self.w = game.screen.w
        self.h = game.screen.h
        game.addScene(self)

    def addSprite(self, sprite):
        sprite.father = self
        self.sprites.append(sprite)

    def removeSprite(self, sprite):
        assert sprite in self.sprites, "当前场景没有此精灵"
        sprite.father = None
        self.sprites.remove(sprite)

    def findSprite(self, id):
        q = self.sprites[:]
        while len(q) != 0:
            node = q.pop(0)
            if node.id == id:
                return node
            if getattr(node, 'children', None) != None:
                q += node.children
        assert False, "当前场景没有此精灵"

    def insertSprite(self, obj, sprite):
        sprite.father = self
        if type(obj) == int:
            self.sprites.insert(obj, sprite)
        else:
            self.sprites.insert(self.sprites.index(obj)+1, sprite)

    def step(self, time):
        self.update(time)
        for i in self.sprites:
            i.step(time)

    def draw(self, screen):
        for i in self.sprites:
            i.draw(screen)

    def getSpriteOnPoint(self, x, y):
        for i in reversed(self.sprites):
            s = i.onPoint(x, y)
            if s:
                return s
        return self

    def update(self, time): pass
