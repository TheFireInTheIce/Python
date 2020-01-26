from ..core import tools
from ..models import Game


def getElementById(game: Game, id):
    return game.findSprite(id)


def getElements(game: Game, cmp):
    res = []
    q = game.currentScene.sprites[:]
    while len(q) != 0:
        node = q.pop(0)
        if cmp(node):
            res.append(node)
        if getattr(node, 'children', None) != None:
            q += node.children[:]
    return res


def getElementsByClass(game: Game, spriteClass):
    def byClass(node):
        return isinstance(node, spriteClass)
    return getElements(game, byClass)


def getElementsByAttr(game: Game, attr, value):
    def byAttr(node):
        if getattr(node, attr, None) != None:
            return getattr(node, attr) == value
        return False
    return getElements(game, byAttr)


def S(game: Game, string):
    if string[0] == '#':
        return getElementById(game, string[1:])
    elif string[0] == '.':
        return getElementsByClass(game, tools.classes[string[1:]][1])
    elif '=' in string:
        av = string.split('=')
        a, v = av[0], '='.join(av[1:])
        return getElementsByAttr(game, a, v)


def S_set(game: Game, string, attr, value):
    els = S(game, string)
    for i in range(len(els)):
        setattr(els[i], attr, value)
