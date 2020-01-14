import pygame
import os
from pygame.locals import *
import IceEngine as ie
import res
import time
game = ie.game.Game()
game.init("rpg game",600, 600)
game.loadImages(res.res)

sscene=ie.scene.Scene("start",game)
game.switchScene('start')

text=ie.ui.Text('RPG 2.0')
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
scene = ie.scene.Scene("main", game)

maps,mapObjects=ie.map.loadTiled('../test.json',game.assets,scene,[6,7,8])
backMap,frontMap=maps
frontMap.sw=frontMap.sh=backMap.sw=backMap.sh=2

board=ie.ui.MultiLineText("")
#board.font="华文琥珀"
board.fontSize=20
board.textColor=(255,255,255,255)
board.bgColor=(0,0,0,255)
board.x=0
board.y=0
game.hud.addSprite(board)

ways=ie.tools.dic({
    'right':(1,0,2),
    'left':(-1,0,3),
    'down':(0,1,0),
    'up':(0,-1,1)
})

tileSize=32
playerMaxScreenPos=500
playerMinScreenPos=100

class Role(ie.component.ComponentObj):
    def __init__(self,name,x,y,sdata:dict):
        super().__init__()
        self.s=ie.sprite.Sprite(name,game.assets[sdata['img']],sdata['rows'],sdata['cols'])
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
    def walk(self,this,time):
        self.walkFunction(this,time)
        if self.walking:self.s.frames.update()
    def updateScreenPos(self):
        if self.x-game.screen.x>=playerMaxScreenPos and game.screen.x+game.screen.w<frontMap.w*frontMap.bw:
            game.screen.x+=2*self.speed
        if self.x-game.screen.x<=playerMinScreenPos and game.screen.x>0:
            game.screen.x-=2*self.speed

        if self.y-game.screen.y>=playerMaxScreenPos and game.screen.y+game.screen.h<frontMap.h*frontMap.bh:
            game.screen.y+=2*self.speed
        if self.y-game.screen.y<=playerMinScreenPos and game.screen.y>0:
            game.screen.y-=2*self.speed
    def walkFunction(self,this,time):
        if self.walking:
            if self.vx!=0:
                self.x+=self.vx
                if int(self.x)%tileSize==0:
                    self.x=int(self.x)//tileSize*tileSize
                    self.vx=0
                    self.walking=False
                    self.event(ie.event.UserEvent('walkStop',{}))
            elif self.vy!=0:
                self.y+=self.vy
                if int(self.y)%tileSize==0:
                    self.vy=0
                    self.y=int(self.y)//tileSize*tileSize
                    self.walking=False
                    self.event(ie.event.UserEvent('walkStop',{}))
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

     
    def getObjInFront(self):
        return frontMap.getPoint(self.x+ways[w][0]*tileSize/2,self.y+ways[w][0]*tileSize/2)

    def __setattr__(self,item,value):
        self.__dict__[item]=value
        if item =='x':
            self.s.x=self.x
        elif item=='y':
            self.s.y=self.y

class ObjNpc(Role):
    ws=['up','right','down','left']
    def __init__(self,asset,name,x,y,t):
        super().__init__(name,x*tileSize,y*tileSize,{'img':asset,'rows':1,'cols':8})
        self.wi=0
        self.wii=0
        self.on('walkStop',self.cwalk)
        self.cwalk(None,None)
    def cwalk(self,event,this):
        if not self.wii:
            self.wii=True
        else:
            self.wii=False
            self.wi=(self.wi+1)%len(self.ws)
            self.w=self.ws[self.wi]
        self.walking=True
        self.vx=self.speed*ways[self.w][0]
        self.vy=self.speed*ways[self.w][1]
    def walk(self,this,time):
        self.walkFunction(this,time)
        if self.walking:self.s.frames.update()
        
class MapNPC(Role):
    def __init__(self,name,x,y,t,says):
        super().__init__(name,x*tileSize,y*tileSize,{'img':'sprites','rows':1,'cols':8})
        self.s.frames.setFrame(0,t)
        self.says=says.split('\n')
        self.sayIndex=0
    def walk(self,this,time):
        self.walkFunction(this,time)
    def zsq(self,text):
        def c():
            board.text=text
        return c
    def say(self,board):
        # print(self.says[self.sayIndex])
        # board.text=self.says[self.sayIndex]
        # self.sayIndex=(self.sayIndex+1)%len(self.says)
        
        for i in range(len(self.says)):
            ie.tools.setTimeOut(self.zsq(self.says[i]),i*2)
        ie.tools.setTimeOut(self.zsq(""),len(self.says)*2)

class Player(Role):
    def __init__(self,x,y):
        super().__init__('player',x,y,{'img':'player','rows':4,'cols':2})
        self.s.addComponent(ie.component.Component(self.input))
        self.water=ie.sprite.Sprite('halfWater',game.assets.sprites,1,8)
        self.water.frames.setFrame(0,2)
        self.water.sw=2
        self.water.sh=2
        self.s.addChild(self.water)
        scene.on(ie.event.events.keydown,self.onSpace)
    def walk(self,this,time):
        self.updateScreenPos()
        self.walkFunction(this,time)
        if self.walking:self.s.frames.update()
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
    def getObjInFront(self):
        dx,dy=ways[self.w][:-1]
        nx,ny=self.x//tileSize+dx,self.y//tileSize+dy
        for i in npcs:
            if i.x//tileSize==nx and i.y//tileSize==ny:
                return i
        return None
    def onSpace(self,event,this):
        if event.keyCode!=32:return
        npc=self.getObjInFront()
        if npc==None:
            pass
        else:
            print("npc!")
            npc.say(board)
            


    



p=Player(2*tileSize,5*tileSize)
scene.insertSprite(frontMap,p.s)

npcs=[]

for i in mapObjects:
    npcs.append(MapNPC(i['name'],i['x'],i['y'],int(i['type'])-1,i['args']['says']))
    scene.addSprite(npcs[-1].s)

if __name__ == "__main__":
    
    game.start()