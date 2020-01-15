#from . import tools
import tools
import re,os,sys
def openFile(fp):
    text=""
    with open(os.path.abspath(os.path.join(sys.path[0],"../../player.iobjs"))) as f:
        text=f.read()
    return text
r_str=re.compile("^\"[^\"\n]*\"$")
r_num=re.compile("^([\+\-]*)(\d+)(\.(\d+))?$")
r_bool=re.compile("^(True)|False$")
r_obj=re.compile("^[\w\_\$\.]+$")
r_space=re.compile("^(\t|( {4}))")
class Error:
    def __init__(self,text):
        self.text=text
def parseValue(string):
    v={}
    if r_str.match(string):
        v['type']='str'
        v['value']=string
    elif r_num.match(string):
        v['type']='number'
        v['value']=int(string) if string.find('.')!=-1 else float(string)
    elif r_bool.match(string):
        v['type']='bool'
        v['value']=string=='True'
    elif r_obj.match(string):
        v['type']='obj'
        v['value']=string.split(r".")
    return v

def getAttrFromObj(attrArr,obj):
    p=attrArr[0]
    if p in obj.__dict__:
        return getAttrFromObj(attrArr[1:],obj.__dict__)
    else:
        return Error('no attr')
def skipSpace(string):
    n=0
    sp=0
    while e:=r_space.search(string,sp):
        n+=1
        string=string[e.span()[1]-e.span()[0]:]
        sp+=e.span()[1]-e.span()[0]
    
    return string,n
def parseFile(text,ctx):
    lines=text.split('\n')
    obj={}
    f=obj
    for line in lines:
        l,n=skipSpace(line)
        print(l,n)
        if l[-1]==':':
            f[l[:-1]]={}
            f=f[l[:-1]]
        else:
            property,value=l.split(":")
            v=parseValue(value)
            f[property]=v['value']
            if v['type']=='obj':
                x=getAttrFromObj(v['value'],ctx)
                if not type(x) is Error and x.text=='no attr':
                    raise Exception('no attr')
    return obj

def createObj(obj):
    pass
def parse(fp):
    pass

print("start")
t=openFile('../../player.iobjs')
print(t)
print(parseFile(t,tools.dic()))
print("over")