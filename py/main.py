
import pygame
import os
from pygame.locals import *
import ice as ie
import res
import time
import random


game = ie.Game()
game.init("rpg game",600, 600)
game.loadImages(res.res)

sscene=ie.Scene("start",game)
game.switchScene('start')
ie.iobjs.parse('../asset/iobjs/start.iobjs', game)

sbutton = game.currentScene.findSprite('start')
sbutton.y=300-sbutton.h/2
sbutton.on(ie.event.events.click,lambda event,this: game.switchScene('main'))
scene = ie.Scene("main", game)

maps,mapObjects=ie.map.loadTiled('../asset/map/main.json',game.assets,scene,[])
backMap,frontMap=maps
frontMap.sw=frontMap.sh=backMap.sw=backMap.sh=2

board=ie.ui.MultiLineText("stateBoard","")
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
playerMinScreenPos = 100

storeScene = ie.Scene('store', game)
game.switchScene('store')
ie.iobjs.parse("../asset/iobjs/store.iobjs",game)

fightScene = ie.Scene('fight', game)
game.switchScene('fight')
ie.iobjs.parse("../asset/iobjs/fight.iobjs", game)

game.switchScene('start')

state = ie.State(game)

@ie.Class('id name value'.split(' '))
class N(ie.EventObj):
    def __init__(self, id, name, value=0):
        super().__init__()
        self.name=name
        state[name]=value
        self.s = ie.ui.Text(id, name + ": " + str(value))
        self.s.fontSize = 30
        self.s.font = '华文琥珀'
        self.s.align = 'right'
        self.s.x = -10
        self.s.y=10
        self.s.textColor=(255,255,255)
        self.s.on(name + '.change', self.onChange)
        game.hud.addSprite(self.s)
    def onChange(self, e, this):
        self.s.text = self.name+": "+str(e.data.newValue)
    

@ie.Class('name x y a'.split(" "))
class Role(ie.component.ComponentObj):
    def __init__(self,name,x,y,sdata:dict):
        super().__init__()
        self.s=ie.sprite.ISprite(name,game.assets[sdata['img']],sdata['rows'],sdata['cols'])
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
        s=game.currentScene
        if self.x-s.x>=playerMaxScreenPos and s.x+s.w<frontMap.w*frontMap.bw:
            s.x+=2*self.speed
        if self.x-s.x<=playerMinScreenPos and s.x>0:
            s.x-=2*self.speed

        if self.y-s.y>=playerMaxScreenPos and s.y+s.h<frontMap.h*frontMap.bh:
            s.y+=2*self.speed
        if self.y-s.y<=playerMinScreenPos and s.y>0:
            s.y-=2*self.speed
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


@ie.Class("name x y mode says".split(" "))
class MapNPC(Role):
    def __init__(self,name,x,y,t,says):
        super().__init__(name,x*tileSize,y*tileSize,{'img':'sprites','rows':1,'cols':9})
        self.s.frames.setFrame(0,t)
        self.says=says.split('\n')
    def walk(self,this,time):
        self.walkFunction(this,time)
    def zsq(self,text):
        def c():
            board.text=text
        return c
    def say(self,says,board):
        for i in range(len(says)):
            ie.tools.setTimeOut(self.zsq(says[i]),i*2)
        ie.tools.setTimeOut(self.zsq(""),len(says)*2)


@ie.Class('name x y mode says'.split(' '))
class Cat(MapNPC):
    def say(self,says, board):
        super().say(says,board)
        def storeInit():
            game.switchScene('store')
            s = game.currentScene
            self.setPrice(s)
            exitf=lambda a,b: game.switchScene('main')
            s.findSprite("exit").on(ie.events.click,exitf)
        ie.setTimeOut(storeInit, 2 * 0)
    def makeF(self, f, i):
        def m(event, this):
            x = i
            f(x)
        return m
    def setPrice(self, s):
        for i in range(1, 5):
            def f(x):
                price=res.c['store' + str(x) + 'price']
                if (state['gold'] >= res.c['store' + str(x) + 'price']):
                    state['gold'] -= price
                else:
                    ie.setTimeOut(lambda:self.say(['天哪，你个穷鬼！','才'+str(state['gold'])+'块钱就想买走它！'],board),0.1)
            f=self.makeF(f,i)
            s.findSprite("Buy"+str(i)).on(ie.events.click, f)
        
@ie.Class('name x y mode says'.split(' '))
class Tracer(MapNPC):
    def say(self,says, board):
        super().say(says,board)
        state['gold'] += 10

@ie.Class('name x y mode says'.split(' '))
class BadMan(MapNPC):
    def __init__(self, name, x, y, mode, says):
        super().__init__(name, x, y, mode, says)
        self.hp = res.c.enemyHp
        self.fight = res.c.enemyFight
        self.dun = res.c.enemyDun
        self.fspeed = res.c.enemySpeed
        self.helpHp=res.c.enemyHelpHp
    def say(self,says, board):
        super().say(says,board)
        game.switchScene('fight')
        s = game.currentScene
        self.sc = s
        self.p = p
        self.show()
        exitf=lambda a,b: game.switchScene('main')
        self.sc.findSprite("run").on(ie.events.click, exitf)
        self.sc.findSprite("fight").on(ie.events.click, self.onFight)
        self.sc.findSprite("help").on(ie.events.click, self.onHelp)
    def show(self):
        self.sc.findSprite('playerHP').text = "血量:" + str(self.p.hp)
        self.sc.findSprite('playerFight').text = "攻击力:" + str(self.p.fight)
        self.sc.findSprite('playerDun').text = "防御力:" + str(self.p.dun)
        self.sc.findSprite('playerSpeed').text = "灵活度:" + str(self.p.fspeed)

        self.sc.findSprite('enemyHP').text = "血量:" + str(self.hp)
        self.sc.findSprite('enemyFight').text = "攻击力:" + str(self.fight)
        self.sc.findSprite('enemyDun').text = "防御力:" + str(self.dun)
        self.sc.findSprite('enemySpeed').text = "灵活度:" + str(self.fspeed)
    
    def DoFight(self):
        jl = random.randint(1, 100)
        if jl <= self.p.speed:
            return
        else:
            self.p.hp -= self.fight - self.p.dun

    def help(self):
        self.hp += self.helpHp
    
    def JZ(self):
        if self.hp <= 4 and random.randint(1, 100) < 40:
            print("help")
            self.help()
        else:
            self.DoFight()
        self.show()
    def PD(self):
        if self.hp <= 0:
            state['gold'] += 20
            game.switchScene("main")
            npcs.remove(self)
            scene.removeSprite(self.s)
    def onFight(self, event, this):
        self.p.doFight(self)
        self.JZ()
        self.PD()
    def onHelp(self,event,this):
        self.p.help()
        self.JZ()
        self.PD()
        
@ie.Class("x y".split(" "))
class Player(Role):
    def __init__(self,x,y):
        super().__init__('player',x,y,{'img':'player','rows':4,'cols':2})
        
        self.s.addComponent(ie.component.Component(self.input))
        
        self.water=ie.sprite.ISprite('halfWater',game.assets.sprites,1,9)
        self.water.frames.setFrame(0,2)
        self.water.sw=2
        self.water.sh=2
        self.s.addChild(self.water)
        scene.on(ie.event.events.keydown,self.onSpace)

        self.hp = res.c.playerHp
        self.fight = res.c.playerFight
        self.dun = res.c.playerDun
        self.fspeed = res.c.playerSpeed
        self.helpHp = res.c.playerHelpHp

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
        self.speed=2 if backMap.getPoint(self.x,self.y)==1 else 4
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
            npc.say(npc.says,board)
    def doFight(self, e):
        jl = random.randint(1, 100)
        if jl <= e.speed:
            return
        else:
            e.hp -= self.fight - e.dun
    def help(self):
        self.hp += self.helpHp

    



p=Player(19*tileSize,16*tileSize)
scene.insertSprite(backMap,p.s)

npcs=[]

for i in mapObjects:
    l = []
    c = ie.classes[i.type]
    for a in c[0]:
        v = i[a]
        if a == 'mode':
            v-=1
        l.append(v)
    o=c[1](*l)
    #npcs.append(MapNPC(i['name'],i['x'],i['y'],int(i['type'])-1,i['args']['says']))
    npcs.append(o)
    scene.addSprite(o.s)

goldN=N('gold','gold',100)

if __name__ == "__main__":
    game.start()
