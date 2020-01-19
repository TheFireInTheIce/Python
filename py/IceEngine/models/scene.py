imports=['pygame','event']

def initModel():
    class Scene(event.EventObj):
        def __init__(self,id,game):
            super().__init__()
            self.id=id
            self.sprites=[]
            game.scenes.append(self)
        def addSprite(self,sprite):
            self.sprites.append(sprite)

        def removeSprite(self,sprite):
            assert sprite in self.sprites,"当前场景没有此精灵"
            self.sprites.remove(sprite)
        
        def findSprite(self,id):
            for i in self.sprites:
                if i.id==id:
                    return i
            assert False,"当前场景没有此精灵"

        def insertSprite(self,obj,sprite):
            if type(obj)==int:
                self.sprites.insert(obj,sprite)
            else:
                self.sprites.insert(self.sprites.index(obj)+1,sprite)


        def step(self,time):
            self.update(time)
            for i in self.sprites:
                i.step(time)

        def draw(self,screen):
            for i in self.sprites:
                i.draw(screen)
        
        def getSpriteOnPoint(self,x,y):
            for i in self.sprites:
                if s:=i.onPoint(x,y):
                    return s
            return self

        def update(self,time):pass
    return {
        'Scene':Scene
    }