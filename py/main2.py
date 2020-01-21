import IceEngine as ie
import res
import pretty_errors
game=ie.Game()
game.init("window-test",600,600)
game.loadImages(res.res)
scene=ie.Scene("main",game)
game.switchScene('main')
ie.iobjs.parse('../asset/iobjs/login.iobjs',game)
game.start()