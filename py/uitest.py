import ice
from res import res
game = ice.Game()
game.init("ui-test", 600, 600)
game.loadImages(res)

s = ice.Scene("mainScene", game)
game.switchScene("mainScene")

ice.iobjs.parse("../asset/iobjs/store.iobjs", game)

# s.findSprite('sword').on(10, lambda a, b: print(a, b))
# s.findSprite('swordButton').on(ice.events.click, lambda e,
#                                this: game.addEvent(ice.UserEvent(10, ice.dic())))
game
game.start()
