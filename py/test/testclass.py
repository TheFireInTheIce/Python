#对类使用函数装饰器test,成功

def f(*args):
    def r(f):
        def m(name):
            print(args)
            f(name)
            print("over")
        return m
    return r

@f([1,2,3])
class t:
    def __init__(self,name):
        print("init!")
        print("my name is",name)

t('孔德玮')