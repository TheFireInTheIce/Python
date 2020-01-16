# from . import tools
# from . import sprite
# from . import ui
import tools
import sprite

import re
import os
import sys


def openFile(fp):
    """
    打开一个文件
    in:文件路径
    out:文件内容
    """
    text = ""
    with open(os.path.abspath(os.path.join(sys.path[0], fp))) as f:
        text = f.read()
    return text


# 正则表达式,用于解析文件
# 字符串
r_str = re.compile("^\"[^\"\n]*\"$")
# 数字
r_num = re.compile("^([\+\-]*)(\d+)(\.(\d+))?$")
# 布尔
r_bool = re.compile("^(True)|False$")
# 对象链,例:a.b,a.b.c
r_obj = re.compile("^[\w\_\$\.]+$")
# 单行列表,例:args:(a,b,c)
r_list=re.compile("\(((.*?\,)*)(.*?)\)")


# 用于删除并统计缩进
r_space = re.compile("(\t|( {4}))")
# 用于判断空行
r_nullLine=re.compile("^\s*$")


def parseValue(string,g):
    """
    解析文件中的数据
    in:string:数据的字符串
    out:解析后的字典,type对应类型,value对应值
    """

    v = {}
    if r_str.match(string):
        v['type'] = 'str'
        v['value'] = string.strip("\"")
    elif r_num.match(string):
        v['type'] = 'number'
        v['value'] = int(string) if string.find('.') != -1 else float(string)
    elif r_bool.match(string):
        v['type'] = 'bool'
        v['value'] = string == 'True'
    elif r_obj.match(string):
        v['type'] = 'obj'
        v['value'] = string.split(r".")
        # 解析
        x = getAttrFromObj(v['value'], g)
        # 设置
        v['value'] = x
    elif string == '[]':
        v['type'] = 'list'
        v['value'] = []
    elif r_list.match(string):
        v['type']=list
        strings=string[1:-1].split(',')
        values=[]
        for i in strings:
            if len(i)==0:continue
            values.append(parseValue(i,g)['value'])
        v['value']=values
    else:
        raise Exception("未知类型:"+string)

    return v


def getAttrFromObj(attrArr, obj):
    """
    获得对象链的最终值
    in:
        obj:对象链的第一个
        attrArr:对象链数组,不包含第一个
    out:
        value:对象链的结果
    例:
        getAttrFromObj(["b","c"],a)
        返回:a.b.c的值
    """

    if len(attrArr) == 0:
        return obj

    # 属性
    p = attrArr[0]

    # 判断对象拥有此属性
    if p in obj.__dict__:
        # 递归调用返回值
        return getAttrFromObj(attrArr[1:], obj[p])
    else:
        raise Exception(str(obj)+"对象没有"+attrArr[0]+"属性")


def skipSpace(string):
    """
    处理每行代码的缩进
    in:
        string:一行代码
    out:
        tuple:(缩进后的代码部分,缩进个数)

    PS:缩进为tab或4个空格

    """
    # 缩进个数
    n = 0

    # 起始位置
    sp = 0

    # 如果还有缩进
    while e:=r_space.search(string, sp):
            # 个数增加
        n += 1
        # 起始位置后移
        sp += e.span()[1]-e.span()[0]

    return string[sp:], n


def parseObj(text, game, defaultS):
    """
    解析一个对象,并转为tools.dic格式
    in:
        text:对象对应的文本
        game:游戏对象,Game()
        defaultS:默认缩进,初始时为0,意思是每行都有的无意义缩进,用于递归调用
    out:
        返回的tools.dic对象
    """
    # 将代码按行分割
    lines = text.split('\n')
    # 上一次循环的缩进个数
    ln = 0
    # 根元素,所有对象定义在他上面
    # __uuid负责处理没有名字的对象
    obj = tools.dic({'__uuid': 0})
    # 调用栈,即每次的运行环境
    stack = [obj]
    # 循环变量
    i = 0
    while i < len(lines):
        # 获取每行出去缩进剩余部分l和缩进个数n
        l, n = skipSpace(lines[i])
        #跳过空行:
        if l=='':
            continue
        # 减去默认缩进
        n -= defaultS
        # 如果比上一次的层次浅
        if (x:=ln-n) >= 1:
            # 恢复到指定层次
            for j in range(x):
                stack.pop()

        # 如果是新的代码块
        if l[-1] == ':':
            # 默认名称
            name = l[:-1]
            # 新的命名空间
            x = tools.dic({'__uuid': 0})

            # 如果是一个游戏对象声明,如Player("player"),即Type("name")
            if l[-2] == ')' and l.find('(') != -1:
                # 处理对象的类型和名称
                name = l[l.find('(')+2:-3]
                x['type'] = l[:l.find('(')]
                #设置名称
                x['name']=name
            # 如果是无名对象,如Player()
            if name == '':
                # 分配默认名称
                name = "No-name-obj-"+x['type']+"-"+str(stack[-1]['__uuid'])
                stack[-1]['__uuid'] += 1
                #设置名称
                x['name']=name
            
            # 调到新空间
            stack[-1][name] = x
            stack.append(stack[-1][name])

        # 如果是数组声明,数组中没有逗号分割,像这样:
        # children:[
            # Sprite():
            #     name:"player-halfWater"
            #     x:0
            #     y:0
            #     display:
            #         show:True
            #         asset:assets.sprites
            #         rows:1
            #         cols:8
            #         row:0
            #         col:2
            #     children:[]
            # Sword():
            #     name:"player-sword"
            #     x:16
            #     y:8
            #     display:
            #         show:True
            #         asset:assets.items
            #         rows:1
            #         cols:4
            #         row:0
            #         col:0
            #     children:[]
        # ]
        elif l[-1] == '[':
            # 中括号个数
            ks = 1
            # 数组结束行
            ek = len(lines)
            # 从下一行开始
            for j in range(i+1, len(lines)):
                # 便利每个字符
                for k in lines[j]:
                    # 括号处理
                    if k == '[':
                        ks += 1
                    elif k == ']':
                        ks -= 1
                # 如果这一行数组结束
                if ks == 0:
                    # 赋值
                    ek = j+1
                    break
            # 新的行数组数组们
            nlines = []
            # 临时行数组
            lslines = []

            for j in lines[i+1:ek-1]:
                # 如果是数组里的顶级元素
                if skipSpace(j)[1] == n+1:
                    # 并且临时行数组不为空
                    if len(lslines) != 0:
                        # 添加原先的行并清空数组
                        nlines.append(lslines[:])
                        lslines.clear()
                # 每一行添加到临时行数组中
                lslines.append(j)
            # 把最后剩下的行添加进去
            nlines.append(lslines)

            # 数组中的对象们
            objs = []
            for j in nlines:
                # 递归调用解析数组中的对象
                r = parseObj("\n".join(j), game, n+1)

                # 查找便利结果
                for k in r:
                    # 如果是数组中的无名对象
                    if k[:12] == "No-name-obj-":
                        # 添加
                        objs.append(r[k])

            # 设置属性
            property = l.split(":")[0]
            stack[-1][property] = objs
            # 更新代码行数
            i = ek
        else:
            # 获得属性和值的字符串
            property, value = l.split(":")
            # 作用域对象,包含game,obj和当前对象
            g = game+obj+stack[-n]
            # 解析值
            v = parseValue(value,g)

            # 设置属性
            stack[-1][property] = v['value']
        # 更新缩进和循环变量
        ln = n
        i += 1
    return obj

def newObj(obj,game):
    """
    根据parseObj的对象数据创建对象
    in:
        obj:parseObj的返回值,一个存储对象数据的tools.dic
        game:游戏的Game对象
    out:
        创建好的对象
    """
    #对象数据
    data=obj[i]
    #对象的显示数据
    displayData=data.display
    #对象的帧
    a=sprite.Animate(displayData.asset,displayData.rows,displayData.cols)
    a.setFrame(displayData.row,displayData.col)
    #对象的参数们
    l=[]
    for arg in game.classes[d.type][0]:
        #将每个参数解析并添加到参数列表
        l.append(parseValue(arg,data))
    #创建对象,特殊语法:f(a,b)=f(*[a,b])
    o=game.classes[d.type][1](*l)
    #递归调用创建子对象
    for j in data.children:
        o.children.append(newObj(j))
    return o

def createObj(obj, game):
    """
    根据parseObj的结果obj创建对象,并添加至game
    in:
        obj:parseObj的返回值,一个存储对象数据的tools.dic
        game:游戏的Game对象
    out:
        null
    """
    #循环遍历obj中的每个对象
    for i in obj:
        #跳过特殊属性__uuid
        if i == '__uuid':
            continue
        #创建对象
        o=newObj(i,game)
        #添加至当前场景
        game.scenes[game.scene].addSprite(o)


        



def parse(fp,game):
    text=openFile(fp)
    data=parseObj(text,game,0)
    createObj(data,game)



# print("start")
# t = openFile('../../player.iobjs')
# r = (parseObj(t, tools.dic({
#     'fps': 1/60,
#     'assets': tools.dic({
#         'player': "PlayerImg!",
#         'items': "ItemImg!",
#         'sprites': "SpriteImg!"
#     })
# }), 0))
# print(r)
# print("over")
