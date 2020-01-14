from . import sprite
from . import component
from . import tools
from . import event
from .config import config
import pygame
import json
import os
import sys
import copy
from os import path


class TiledSet(component.ComponentObj):
    def __init__(self, mapData, img, rows, cols, imgData=None):
        """
        描述:一个游戏中的图块集对象,主要用于俯视图
        参数:
        TiledSet(mapData,img,rows,cols,imgData=None):以mapData二维数组创建地图,
        mapData[i][j]显示imgData[mapData[i][j]]
        mapData是一个int二维数组,表示地图
        img是存储帧图像的图片,rows行cols列
        imgData是一个字典,键是mapData中的整数,值是一个(row,col)的元组
        imgData可以不填,则mapData[i][j]显示img的第mapData[i][j]帧,mapData[i][j]为-1表示没有
        返回:一个TiledSet对象
        """
        super().__init__()
        self.x = 0
        self.y = 0
        self.sw = 1
        self.sh = 1
        self.mapData = mapData
        self.w = len(mapData)
        self.h = len(mapData[0])
        self.show=img != None
        if self.show:
            self.sheet = sprite.Sheet(img, rows, cols)
            self.bw, self.bh = self.sheet.get(
            0, 0).get_width(), self.sheet.get(0, 0).get_height()
            if imgData != None:
                self.imgData = imgData
            else:
                self.imgData = {}
                for i in range(rows*cols):
                    self.imgData[i] = (i//cols, i % cols)
                self.imgData[-1] = None
        else:
            self.bw=0
            self.bh=0
            self.sheet=None
            self.imgData=None

    def draw(self, screen, x=0, y=0):
        if not self.show:return
        ix = []
        self.bw, self.bh = self.sheet.get(
            0, 0).get_width(), self.sheet.get(0, 0).get_height()
        self.bw *= self.sw
        self.bh *= self.sh
        for i in self.sheet.imgs:
            line = []
            for j in i:
                line.append(pygame.transform.scale(j, (self.bw, self.bh)))
            ix.append(line)
        for i in range(len(self.mapData)):
            for j in range(len(self.mapData[i])):
                if (n := self.imgData[self.mapData[i][j]]) != None:
                    screen.blit(ix[n[0]][n[1]],
                                (self.x+j*self.bw, self.y+i*self.bh))

    def onPoint(self, x, y):
        if not self.show:return None
        bx, by = x-self.x, y-self.y
        self.bw, self.bh = self.sheet.get(
            0, 0).get_width(), self.sheet.get(0, 0).get_height()
        self.bw *= self.sw
        self.bh *= self.sh
        return (self if bx >= 0 and bx < self.bw*self.w and by >= 0 and by < self.bh*self.h else None)

    def resetSize(self, sw, sh):
        if 'sheet' in self.__dict__ and self.show:
            self.bw = sw*self.sheet.get(0, 0).get_width()
            self.bh = sh*self.sheet.get(0, 0).get_height()

    def __setattr__(self, item, value):
        self.__dict__[item] = value
        if item in "sw sh".split(" "):
            if 'sw' in self.__dict__ and 'sh' in self.__dict__:
                self.resetSize(self.sw, self.sh)


class CheckMap:
    def __init__(self, mapData, bw, bh, cData=None):
        self.mapData = mapData
        self.cData = cData or {0: False, 1: True}
        self.bw, self.bh = bw, bh

    def getPoint(self, x, y):
        return self.mapData[int((y+1)//self.bh)][int((x+1)//self.bw)]

    def checkPoint(self, x, y):
        return self.cData[self.getPoint(x, y)]

    def checkRect(self, x, y, w, h):
        sx, sy = x//self.bw, y//self.bh
        ex, ey = (x+w)//self.bw, (y+h)//self.bh
        for i in range(sx, ex+1):
            for j in range(sy, ey+1):
                if self.cData[self.mapData[j][i]]:
                    return True
        return False

    def checkSprite(self, sprite):
        return self.checkRect(sprite.x, sprite.y, sprite.w, sprite.h)


class Map(component.ComponentObj):
    def __init__(self, tiledset, checkmap):
        super().__init__()
        self.x = 0
        self.y = 0
        self.w = tiledset.w
        self.h = tiledset.h
        self.sw = 1
        self.sh = 1
        self.bw = tiledset.bw
        self.bh = tiledset.bh
        self.tiledSet = tiledset
        self.checkMap = checkmap
        self.checkMap.bw=self.bw
        self.checkMap.bh=self.bh

    def draw(self, screen, x=0, y=0):
        self.tiledSet.sw = self.sw
        self.tiledSet.sh = self.sh
        self.tiledSet.draw(screen, x+self.x, y+self.y)
        self.bw = self.tiledSet.bw
        self.bh = self.tiledSet.bh
        self.checkMap.bw,self.checkMap.bh=self.bw,self.bh

    def checkSprite(self, sprite):
        return self.checkMap.checkSprite(sprite)

    def onPoint(self, x, y):
        return self.tiledSet.onPoint(x, y)

    def getPoint(self, x, y):
        return self.tiledSet.mapData[int((y+1)//self.bh)][int((x+1)//self.bw)]



class Maps(component.ComponentObj):
    def __init__(self, tiledSets, checkData=None, cData=None):
        super().__init__()
        self.x = 0
        self.y = 0
        self.w = tiledSets[0].w
        self.h = tiledSets[0].h
        self.sw = 1
        self.sh = 1
        self.bw = tiledSets[0].bw
        self.bh = tiledSets[0].bh
        self.tiledSets = tiledSets
        if checkData:
            self.checkData = [
                [0 for i in range(self.w)] for j in range(self.h)]
        else:
            self.checkData = checkData
        self.checkMap = CheckMap

    def draw(self, screen, x=0, y=0):
        for m in reversed(self.tiledSets):
            m.sw = self.sw
            m.sh = self.sh
            m.draw(screen, x+self.x, y+self.y)
        self.bw = self.tiledSets[0].bw
        self.bh = self.tiledSets[0].bh

    def checkSprite(self, sprite):
        return self.checkMap.checkSprite(sprite)

    def onPoint(self, x, y):
        return self.tiledSets[-1].onPoint(x, y)


def loadTiledObjArgs(array):
    args = {}
    for arg in array:
        args[arg['name']] = arg['value']
    return args


def loadTiledFile(fp):
    file = None
    with open(path.join(sys.path[0], fp)) as file:
        assert file, "the file in "+fp+" is None!"
        return json.load(file)


def loadTiledTileSet(obj,assets):
    imgdatas = {}
    for i in obj['tilesets']:
        if i['name']==config.tiledCollisionTileName:
            d=tools.dic()
            d.t=i['firstgid']
            imgdatas[config.tiledCollisionTileName]=d
            continue
        d = tools.dic()
        args = loadTiledObjArgs(i['properties'])
        aname = args['source']
        assert len(aname) != 0, "the arg of source is not in tiledsets"
        d.img = assets[aname]
        d.cols = i['columns']
        d.rows = i['tilecount']//i['columns']
        d.imgdata = {}
        for gid in range(i['tilecount']):
            x = i['firstgid']+gid-1
            d.imgdata[i['firstgid']+gid] = (x//d.cols, x%d.cols)
        d.imgdata[0]=None
        imgdatas[i['name']] = d
    return imgdatas

def arrayToMapData(array,w):
    data=[]
    line=[]
    for i in range(len(array)):
        line.append(array[i])
        if (i+1) % w == 0:
            data.append(line.copy())
            line.clear()
    return data

def loadTiledMap(obj, imgdatas,classes):
    maps = []
    collision=None
    objects=[]
    for i in obj['layers']:
        if i['type'] == 'tilelayer':
            if i['name'] != config.tiledCollisionLayerName:
                w = i['width']
                h = i['height']
                data=arrayToMapData(i['data'],w)
                tileSet=None
                if i.get('properties',None) != None:
                    args = loadTiledObjArgs(i['properties'])
                    aname = args['img']
                    tileSet = imgdatas[aname]
                if not classes is None:
                    for j in range(len(data)):
                        for k in range(len(data[j])):
                            if data[j][k] in classes:
                                t=data[j][k]
                                objects.append(tools.dic({
                                    'x':k,
                                    'y':j,
                                    'w':obj['tilewidth'],
                                    'h':obj['tileheight'],
                                    'type':t,
                                    'angle':0,
                                    'name':i['name']+'-obj'
                                }))
                if tileSet !=None:
                    maps.append(
                        TiledSet(data, tileSet.img, tileSet.rows,
                                 tileSet.cols, tileSet.imgdata)
                    )
                else:
                    maps.append(
                        TiledSet(data,None,0,0,None)
                    )
            else:
                w = i['width']
                h = i['height']
                cMapData=arrayToMapData(i['data'],w)
                cData={}
                cData[0]=False
                cData[imgdatas[config.tiledCollisionTileName].t]=True
                collision=CheckMap(cMapData,0,0,cData)
        else:
            for o in i['objects']:
                s=tools.dic()
                s.x,s.y,s.w,s.h=o['x'],o['y'],o['width'],o['height']
                s.type=o['type']
                s.angle=o['rotation']
                s.name=o['name']
                s.args={}
                if o.get('properties',None)!=None:
                    args=loadTiledObjArgs(o['properties'])
                    s.args=args
                objects.append(s)
    return (maps,collision,objects)


def loadTiled(fp, assets, scene,classes:list=None):
    obj=loadTiledFile(fp)
    imgData=loadTiledTileSet(obj,assets)
    mapdatas,checkmap,objects=loadTiledMap(obj,imgData,classes)
    if not checkmap:
        checkmap=CheckMap([[0 for _ in range(mapdatas[0].w)] for _ in range(mapdatas[0].h)],mapdatas[0].bw,mapdatas[0].bh)
    maps=[]
    for m in mapdatas:
        maps.append(Map(m,copy.copy(checkmap)))
        scene.addSprite(maps[-1])
    return maps,objects

