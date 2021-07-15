from construction_requirements_integrator import CRI, construction_required
from random import random


class Parent(CRI):
    def __init__(self, x=None, y=None, construction_permission=True):
        CRI.__init__(self, x=x, y=y, construction_permission=construction_permission)

    def __construct__(self, x, y):
        self.x = x
        self.y = y
        self.s = self.x*self.y

    @construction_required
    def get_s(self):
        return self.s

class Child(Parent):
    def __init__(self, z=None, **kwargs):
        super().__init__(construction_permission=False, **kwargs)
        self.add_to_construction_requirements(z=z)
        self.set_construction_permission(True)

    def __construct__(self, z, **kwargs):
        super().__construct__(**kwargs)
        self.z = z
        self.v = self.x*self.y*self.z

    @construction_required
    def get_v(self):
        return self.v

p = Parent(x=2, y=3)
print(p.get_s())
# >>> 6
c = Child(x=2, y=3)
print(c.is_constructed)
# >>> False
c.meet_requirement(z=4)
print(c.is_constructed)
# >>> True
print(c.get_v())
# >>> 24
c2 = Child(x=2, y=3, z=4)
print(c2.get_v())
# >>> 24