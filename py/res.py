import ice as ie
imgbase = '../asset/img/'
cimg = [
    {"name": "items", "path": "items.png"},
    {"name": "player", "path": "player1.png"},
    {"name": "enemy1", "path": "enemy1.png"},
    {"name": "enemy2", "path": "enemy2.png"},
    {"name": "monster1", "path": "monster1.png"},
    {"name": "monster2", "path": "monster2.png"},
    {"name": "monster3", "path": "monster3.png"},
    {"name": "sprites", "path": "sprites.png"}
]

res = []
for i in cimg:
    x = i
    x['path'] = imgbase+x['path']
    res.append(ie.tools.dic(x))

c = ie.dic()
c.playerHp = 10
c.playerFight = 3
c.playerDun = 1
c.playerSpeed = 5
c.playerHelpHp = 1

c.enemyHp = 10
c.enemyFight = 2
c.enemyDun = 1
c.enemySpeed = 5
c.enemyHelpHp = 2

c.store1price = 50
c.store2price = 100
c.store3price = 190
c.store4price = 60

c.storeNames = ('Sword', 'Dragon-Craw', 'Ice-Magic', 'Board')

