import pygame
from pygame import locals as l
from . import scene


class Screen:
    def __init__(self, name, wh):
        self.w, self.h = wh
        self.x = 0
        self.y = 0
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(name)

    def blit(self, img, pos):
        ix, iy = pos
        self.screen.blit(img, (ix-self.x, iy-self.y))

    def fill(self, color):
        self.screen.fill(color)

    def fillRect(self, x, y, w, h, color):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, w, h))

    def strokeRect(self, x, y, w, h, color, lineWidth):
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(x, y, w, h), lineWidth)

    def fillCircle(self, x, y, r, color):
        pygame.draw.circle(self.screen, color, (x, y), r)

    def strokeCircle(selfx, y, r, color, lineWidth=1):
        pygame.draw.circle(self.screen, color, (x, y), r, lineWidth)


class HUD(Screen):
    def __init__(self, wh, game):
        self.x = 0
        self.y = 0
        self.w, self.h = wh
        self.screen = pygame.Surface((self.w, self.h)).convert_alpha()
        self.scene = scene.Scene('HDCLayer', game)
        self.addSprite = self.scene.addSprite
        self.removeSprite = self.scene.removeSprite
        self.insertSprite = self.scene.insertSprite
        self.findSprite = self.scene.findSprite
