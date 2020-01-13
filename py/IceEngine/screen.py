import pygame
from pygame import locals as l
class Screen:
    def __init__(self,name,pos):
        self.w,self.h=pos
        self.x=0
        self.y=0
        self.screen=pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption(name)
    def blit(self,img,pos):
        ix,iy=pos
        self.screen.blit(img,(ix-self.x,iy-self.y))
    def fill(self,color):
        self.screen.fill(color)
    