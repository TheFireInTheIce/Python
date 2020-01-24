from . import tools
from pygame import locals as l
import time

events = tools.dic({
    "mousedown": 1,
    "mousemove": 2,
    "mouseup": 3,
    "click": 4,
    "doubleclick": 5,
    "mouseover": 6,
    "keydown": 8,
    "keyup": 9,
    "quit": 10
})

keyCode = tools.dic(
    {
        "a": 97,
        "b": 98,
        "c": 99,
        "d": 100,
        "e": 101,
        "f": 102,
        "g": 103,
        "h": 104,
        "i": 105,
        "j": 106,
        "k": 107,
        "l": 108,
        "m": 109,
        "n": 110,
        "o": 111,
        "p": 112,
        "q": 113,
        "r": 114,
        "s": 115,
        "t": 116,
        "u": 117,
        "v": 118,
        "w": 119,
        "x": 120,
        "y": 121,
        "z": 122,
        "1": 49,
        "2": 50,
        "3": 51,
        "4": 52,
        "5": 53,
        "6": 54,
        "7": 55,
        "8": 56,
        "9": 57,
        "0": 48,
        "minus": 45,
        "equals": 61,
        "f1": 282,
        "f2": 283,
        "f3": 284,
        "f4": 285,
        "f5": 286,
        "f6": 287,
        "f7": 288,
        "f8": 289,
        "f9": 290,
        "f10": 291,
        "f11": 292,
        "f12": 293,
        "kp0": 256,
        "kp_period": 266,
        "kp1": 257,
        "kp2": 258,
        "kp3": 259,
        "kp4": 260,
        "kp5": 261,
        "kp6": 262,
        "kp7": 263,
        "kp8": 264,
        "kp9": 265,
        "left": 276,
        "right": 275,
        "up": 273,
        "down": 274,
        "space": 32,
        "return": 13,
        "backspace": 8
    }
)


class EventCatcher:
    def __init__(self):
        self.dbclickInterval = 0.5
        self.lastMouseDown = time.time()
        self.keys = tools.dic()
        for i in keyCode:
            self.keys[keyCode[i]] = False

    def classifyEvent(self, e):
        eventsArr = []
        if e.type == l.MOUSEBUTTONDOWN:
            eventsArr.append(events.mousedown)
        elif e.type == l.MOUSEBUTTONUP:
            eventsArr.append(events.mouseup)
            t = time.time()-self.lastMouseDown
            self.lastMouseDown = time.time()
            if t <= self.dbclickInterval:
                eventsArr.append(events.doubleclick)
            else:
                eventsArr.append(events.click)
        elif e.type == l.MOUSEMOTION:
            eventsArr.append(events.mousemove)
        elif e.type == l.KEYDOWN:
            eventsArr.append(events.keydown)
            self.keys[e.key] = True
        elif e.type == l.KEYUP:
            eventsArr.append(events.keyup)
            self.keys[e.key] = False
        elif e.type == l.QUIT:
            eventsArr.append(events.quit)
        return eventsArr


class EventObj:
    def __init__(self):
        self.events = []

    def on(self, eventName, function):
        self.events.append(tools.dic({
            "event": eventName,
            "function": function,
            "this": self
        }))

    def off(self, *args):
        """
        0-2个参数,
        0个:删除绑定的一切事件监听
        1个:删除args[0]类型的事件监听
        2个:删除args[0]类型且function为args[1]的事件监听
        """
        l = len(args)
        if l == 0:
            self.events.clear()
        elif l == 1:
            for i in range(len(self.events)):
                if self.events[i].event == args[0]:
                    del self.events[i]
        elif l == 2:
            for i in range(len(self.events)):
                if self.events[i].event == args[0] and self.events[i].function == args[1]:
                    del self.events[i]

    def event(self, e):
        for i in self.events:
            if i.event == e.type:
                i.function(e, i.this)


class Event:
    def __init__(self, type, e):
        self.type = type
        if self.type <= 6:
            self.x, self.y = e.pos
        elif self.type in (8, 9):
            self.keyCode = e.key
            self.keyChar = keyCode.find(self.keyCode)
        else:
            pass


class UserEvent:
    def __init__(self, type, data, target=None):
        self.type = type
        self.data = data
        self.target = target
