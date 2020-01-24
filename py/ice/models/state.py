from ..core import tools
from ..core import event
#from ..core import component


def onChange(name, oldValue, newValue):
    return event.UserEvent(name+'.change', tools.dic({
        'name': name,
        'oldValue': oldValue,
        'newValue': newValue
    }))


class State(event.EventObj):
    def __init__(self, game):
        self.states = {}
        self.game = game

    def __getattr__(self, item):
        if item == 'states':
            return super().__getattribute__(item)
        return self.states[item]

    def __setattr__(self, item, value):
        if item in ('states', 'game'):
            super().__setattr__(item, value)
            return
        ov = None
        if item in self.states:
            ov = self.states[item]
        self.states[item] = value
        if ov != None:
            self.game.addEvent(onChange(item, ov, value))

    __getitem__ = __getattr__
    __setitem__ = __setattr__
