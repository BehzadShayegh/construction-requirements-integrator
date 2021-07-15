from construction_requirements_integrator import CRI, construction_required
from random import random

class XProvider:
    def __init__(self):
        self.x = int((random()*10))

    def provide_for(self, obj):
        obj.meet_requirement(x=self.x)

class YProvider:
    def __init__(self):
        self.y = int((random()*5))

    def provide_for(self, obj):
        obj.meet_requirement(y=self.y)

class Example(CRI):
    def __init__(self, x=None, y=None, z=None):
        CRI.__init__(self, x=x, y=y, z=z)

    def __construct__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.volume = x*y*z

    def get_construction_status(self):
        return self.is_constructed

    @construction_required
    def get_volume(self):
        return self.volume

example1 = Example(z=2)
XProvider().provide_for(example1)
YProvider().provide_for(example1)
print(example1.get_construction_status())
# >>> True
print(example1.x, example1.y, example1.z)
# >>> 6 2 2
print(example1.get_volume())
# >>> 24

example2 = Example(z=2)
print(example2.get_construction_status())
# >>> False
print(example2.get_volume())
# Exception: The object is not constructed yet!

print(example1.__dict__)
# >>> {'_CRI__reconstruct': False, 'is_constructed': True, 'x': 6, 'y': 1, 'z': 2, 'volume': 12}
print(example2.__dict__)
# >>> {'_CRI__requirements': {'x': None, 'y': None, 'z': 2}, '_CRI__overwrite_requirement': False, '_CRI__ignore_overwrite_error': False, '_CRI__auto_construct': True, '_CRI__purge_after_construction': True, '_CRI__reconstruct': False, 'is_constructed': False}