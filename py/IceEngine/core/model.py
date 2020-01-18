import os
from os import path as p
import sys
from . import tools
bp=p.dirname(p.dirname(__file__))
def findFileHelper(fileName,path):
    for i in os.listdir(path):
        newPath=p.join(path,i)
        if p.isdir(newPath):
            res=findFileHelper(fileName,newPath)
            if res!=None:
                return res
        elif i==fileName:
            return newPath
def findFile(fileName):
    res=p.abspath(findFileHelper(fileName+".py",bp))
    return res

def compilePath(path):
    ##print(path)
    newpath=path[:-3]
    newpath='\\'.join(path.split('\\')[:-1])
    sys.path.append(newpath)
    ##print(sys.path[-1])
    pyPath=p.relpath(path,bp)[:-3].split("\\")
    mod=__import__(pyPath[1])
    return mod
standardModels=['component','config','event','model','tools']
importTypes=tools.dic({
    'Timport':0,
    'TimportRename':1,
    'Tfrom':2,
    'TfromRename':3,
    "Tevery":4
})
def imph(name):
    if name in standardModels:
        return __import__('.'+name)
    else:
        try:
            m=__import__(name)
            return m
        except Exception as e:
            m=compilePath(findFile(name))
            return m

def imp(name,importType):
    if importType==importTypes.Timport:
        return {'name':name,'value':imph(name),'type':importTypes.Timport}
    #if importType==importTypes.TimportRename:
    #    return {'name':name[1],'value':imph(name[0]),'type':importTypes.TimportRename}
    if importType==importTypes.Tfrom:
        return {'name':name[1],'value':eval("imph(name[0])."+name[1]),'type':importTypes.Tfrom}
    if importType==importTypes.TfromRename:
        return {'name':name[2],'value':eval("imph(name[0])."+name[1]),'type':importTypes.TfromRename}
    if importType==importTypes.Tevery:
        m=imph(name)
        ns=[]
        vs=[]
        for i in dir(m):
            if i[:2]=='__' and i[-2:]=='__':
                continue
            ns.append(i)
            vs.append(eval('m.'+i))
        return {'name':ns,'value':vs}
    

def model(name):
    m=compilePath(findFile(name))
    im=m.imports
    ms={}
    for mn in im:
        t=importTypes.Timport
        arg=mn
        if ',' in mn:
            mns=mn.split(',')
            if len(mns)==2:
                t=importTypes.Tfrom
                arg=mns
            else:
                t=importTypes.TfromRename
                arg=mns
        elif mn[-1]=='*':
            t=importTypes.Tevery
        ms[mn]=imp(arg,t)
    for mn in im:
        if ms[mn]['type']in (importTypes.Timport,importTypes.TimportRename,importTypes.Tfrom,importTypes.TfromRename):
            exec('m.'+ms[mn]['name']+"="+'ms[mn]["value"]')
        else:
            for i in ms[mn]:
                exec('m.'+ms[mn]['name'][i]+"="+'ms[mn]["value"]["'+i+'"]')
    r=m.initModel()
    
    return tools.dic(r)
