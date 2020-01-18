#对类使用函数装饰器test,成功

def f(*args):
    def r(f):
        def m(*args):
            print(args)
            f(*args)
            print("over")
        return m
    return r

@f([1,2,3])
class t:
    def __init__(self,name,age):
        print("init!")
        print("my name is",name)
        print("I am",age,"years old")

t('孔德玮',13)