import pygame
import os
from pygame.locals import *
import IceEngine as ie
import res

game = ie.game.Game()
game.init(600, 600)
game.loadImages(res.res)

scene = ie.scene.Scene("main", game)
game.switchScene('main')
map,objects=ie.map.loadTiled('../test.json',game.assets,scene)

p=ie.sprite.Sprite('player',game.assets.player,4,2)
p.x=16
p.y=16
scene.addSprite(p)

if __name__ == "__main__":
    
    game.start()