import pygame
import os
from pygame.locals import *
import IceEngine as ie
import res
game = ie.game.Game()
game.init("rpg game",600, 600)
game.loadImages(res.res)

sscene=ie.scene.Scene("start",game)
game.switchScene('start')

text=ie.ui.Text('孤域求存 2.0')
text.font="华文琥珀"
text.fontSize=50
text.textColor=(255,150,0,255)
text.x=300-text.w/2
text.y=100
sscene.addSprite(text)

sbutton=ie.ui.TextButton('Start',(255,255,255,255),(255,150,0,255),30,"华文琥珀")
sscene.addSprite(sbutton)
sbutton.x=300-sbutton.w/2
sbutton.y=300-sbutton.h/2
sbutton.on(ie.event.events.click,lambda event,this: game.switchScene('main'))
# switch=ie.ui.switch()
# switch.x=sbutton.x
# switch.y=sbutton.y+sbutton.h+20
# switch.addComponent(ie.component.Component(lambda this,time:print(this.state)))
# sscene.addSprite(switch)


scene = ie.scene.Scene("main", game)
maps,objects=ie.map.loadTiled('../test.json',game.assets,scene)
backMap,frontMap=maps
frontMap.sw=frontMap.sh=backMap.sw=backMap.sh=2

ways=ie.tools.dic({
    'right':(1,0,2),
    'left':(-1,0,3),
    'down':(0,1,0),
    'up':(0,-1,1)
})

tileSize=32
playerMaxScreenPos=500
playerMinScreenPos=100

class Player(ie.component.ComponentObj):
    def __init__(self,x,y):
        super().__init__()
        self.s=ie.sprite.Sprite('player',game.assets.player,4,2)
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.w='right'
        self.walking=False
        self.speed=2
        self.s.sw=2
        self.s.sh=2
        self.s.addComponent(ie.component.Component(self.walk))
        self.s.addComponent(ie.component.Component(self.input))
        self.water=ie.sprite.Sprite('halfWater',game.assets.sprites,1,8)
        self.water.frames.setFrame(0,2)
        self.water.sw=2
        self.water.sh=2
        self.s.addChild(self.water)

    def walk(self,this,time):
        if self.x-game.screen.x>=playerMaxScreenPos and game.screen.x+game.screen.w<frontMap.w*frontMap.bw:
            game.screen.x+=self.vx
        if self.x-game.screen.x<=playerMinScreenPos and game.screen.x>0:
            game.screen.x+=self.vx

        if self.y-game.screen.y>=playerMaxScreenPos and game.screen.y+game.screen.h<frontMap.h*frontMap.bh:
            game.screen.y+=self.vy
        if self.y-game.screen.y<=playerMinScreenPos and game.screen.y>0:
            game.screen.y+=self.vy
        
        if self.walking:
            if self.vx!=0:
                self.x+=self.vx
                if int(self.x)%tileSize==0:
                    self.x=int(self.x)//tileSize*tileSize
                    self.vx=0
                    self.walking=False
                self.s.frames.update()
            elif self.vy!=0:
                self.y+=self.vy
                if int(self.y)%tileSize==0:
                    self.vy=0
                    self.y=int(self.y)//tileSize*tileSize
                    self.walking=False
                self.s.frames.update()
        else:
            self.vx=self.vy=0
    
    def setWay(self,w):
        self.vx=self.speed*ways[w][0]
        self.vy=self.speed*ways[w][1]
        self.s.frames.setRow(ways[w][2])
        self.walking=True
        nx=self.x//tileSize*tileSize+ways[w][0]*tileSize+tileSize/2
        ny=self.y//tileSize*tileSize+ways[w][1]*tileSize+tileSize/2
        return int(nx),int(ny)

    def input(self,this,time):
        if self.walking:return True
        nx,ny=self.x,self.y
        if game.key(ie.event.keyCode.left):
            self.w='left'
            nx,ny=self.setWay(self.w)
        elif game.key(ie.event.keyCode.right):
            self.w='right'
            nx,ny=self.setWay(self.w)
        elif game.key(ie.event.keyCode.up):
            self.w='up'
            nx,ny=self.setWay(self.w)
        elif game.key(ie.event.keyCode.down):
            self.w='down'
            nx,ny=self.setWay(self.w)
        if frontMap.checkMap.checkPoint(nx,ny):
            self.vx=0
            self.vy=0
            self.walking=False
        self.water.show=backMap.getPoint(self.x,self.y)==1
        self.speed=1 if backMap.getPoint(self.x,self.y)==1 else 2
            
        
        

    def __setattr__(self,item,value):
        self.__dict__[item]=value
        if item =='x':
            self.s.x=self.x
        elif item=='y':
            self.s.y=self.y





p=Player(2*tileSize,5*tileSize)

scene.insertSprite(frontMap,p.s)

if __name__ == "__main__":
    
    game.start()