import IceEngine as ie
ie.Import('tools')
imgbase='../asset/img/'
cimg=[
    {"name":"items","path":"items.png"},
    {"name":"player","path":"player1.png"},
    {"name":"enemy1","path":"enemy1.png"},
    {"name":"enemy2","path":"enemy2.png"},
    {"name":"monster1","path":"monster1.png"},
    {"name":"monster2","path":"monster2.png"},
    {"name":"monster3","path":"monster3.png"},
    {"name":"sprites","path":"sprites.png"}
]

res=[]
for i in cimg:
    x=i
    x['path']=imgbase+x['path']
    res.append(ie.tools.dic(x))
    