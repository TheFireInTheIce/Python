from IceEngine import tools
cres=[
    {"name":"items","path":"../img/items.png"},
    {"name":"player","path":"../img/player1.png"},
    {"name":"enemy1","path":"../img/enemy1.png"},
    {"name":"enemy2","path":"../img/enemy2.png"},
    {"name":"monster1","path":"../img/monster1.png"},
    {"name":"monster2","path":"../img/monster2.png"},
    {"name":"monster3","path":"../img/monster3.png"},
    {"name":"sprites","path":"../img/sprites.png"}
]

res=[]
for i in cres:
    res.append(tools.dic(i))
    