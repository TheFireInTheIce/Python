# import pygame
# from pygame import locals as l
# from . import scene
imports=['pygame','pygame.locals,l','scene']
def initModel():
    class Screen:
        def __init__(self,name,wh):
            self.w,self.h=wh
            self.x=0
            self.y=0
            self.screen=pygame.display.set_mode((self.w,self.h))
            pygame.display.set_caption(name)
        def blit(self,img,pos):
            ix,iy=pos
            self.screen.blit(img,(ix-self.x,iy-self.y))
        def fill(self,color):
            self.screen.fill(color)
    class HUD:
        def __init__(self,wh,game):
            self.w,self.h=wh
            self.hud=pygame.Surface((self.w,self.h)).convert_alpha()
            self.scene=scene.Scene('HDCLayer',game)
            self.addSprite=self.scene.addSprite
            self.removeSprite=self.scene.removeSprite
            self.insertSprite=self.scene.insertSprite
            self.findSprite=self.scene.findSprite
        def blit(self,img,pos):
            self.hud.blit(img,pos)
        def fill(self,color):
            self.hud.fill(color)
    return {
        "Screen":Screen,
        "HUD":HUD
    }
    