import os
from os import path as p
import sys
from . import tools
bp = p.dirname(p.dirname(__file__))


def findFileHelper(fileName, path):
    for i in os.listdir(path):
        newPath = p.join(path, i)
        if p.isdir(newPath):
            res = findFileHelper(fileName, newPath)
            if res != None:
                return res
        elif i == fileName:
            return newPath


def findFile(fileName):
    res = p.abspath(findFileHelper(fileName+".py", bp))
    return res


def compilePath(path):
    newpath = path[:-3]
    newpath = '\\'.join(path.split('\\')[:-1])
    pyPath = p.relpath(path, bp)[:-3].split("\\")
    sys.path.append(newpath)
    mod = __import__(pyPath[1])
    sys.path.remove(newpath)
    return mod


importTypes = tools.dic({
    'Timport': 0,
    'TimportRename': 1,
    'Tfrom': 2,
    'TfromRename': 3,
    "Tevery": 4
})


def imph(name):
    try:
        m = __import__(name)
        return m
    except Exception as e:
        m = compilePath(findFile(name))
        return m

def objHasAttr(obj,attr):
    return not getattr(obj,attr,Exception) is Exception

def getAttrFromModel(attrArr, m):
    if len(attrArr) == 0:
        return m
    if objHasAttr(m,attrArr[0]):
        return getAttrFromModel(attrArr[1:], getattr(m,attrArr[0]))
    else:
        raise AttributeError(
            str(m)+' object has no attribute \''+attrArr[0]+'\'')


models = {}

def imp(name):
    if name in ('tools',):
        return compilePath(findFile(name))
    mname = name.split('.')
    m = compilePath(findFile(mname[0]))
    im = m.imports
    ms = {}
    for mn in im:
        t = importTypes.Timport
        arg = mn
        if ',' in mn:
            mns = mn.split(',')
            if len(mns) == 2:
                t = importTypes.TimportRename
                arg = mns
            else:
                t = importTypes.TfromRename
                arg = mns
        elif mn[-1] == '*':
            t = importTypes.Tevery
        ##print(arg if type(arg) == str else arg[0])
        if t in (importTypes.Tfrom, importTypes.TfromRename):
            ms[mn] = {'value': imodel(arg if type(
                arg) == str else arg[0]), 'type': t, 'name': arg}
        else:
            ms[mn] = {'value': imodel(arg if type(
                arg) == str else arg[0]), 'type': t, 'name': arg}
    for mn in im:
        if ms[mn]['type'] == importTypes.Timport and '.' in mn:
            ms[mn]['name']=ms[mn]['name'].split('.')[-1]

        if ms[mn]['type'] == (importTypes.Timport):
            setattr(m,ms[mn]['name'],ms[mn]['value'])
        elif ms[mn]['type'] == importTypes.TimportRename:
            setattr(m,ms[mn]['name'][1],ms[mn]['value'])
        else:
            for i in dir(ms[mn]['value']):
                setattr(m,i,getattr(ms[mn]['value'],i))
    r = tools.dic(m.initModel())
    if len(mname) != 1:
        r = getAttrFromModel(mname[1:], r)
    models[name] = r
    return r


def imodel(name):
    if name in models:
        return models[name]
    try:
        if '.' in name:
            m = getAttrFromModel(name.split('.')[1:],__import__(name))
        else:
            m = __import__(name)
        return m
    except:
        return imp(name)

def mImport(obj,name):
    n=name
    m=None
    if ',' in n:
        ns=n.split(',')
        m=imodel(ns[1])
        name=ns[0]
        n=ns[0]
    else:
        m=imodel(n)
    if n[-1]=='*':
        for i in m:
            pass
            #setattr(obj,i,getattr(m,i))
    else:
        obj[name]=m
        #setattr(obj,name,m)
# ie=None
# def Import(name):
#     mImport(ie,name)