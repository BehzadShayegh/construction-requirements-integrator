# Construction Requirements Integrator Package

Using this module, we can inherit classes configuring after their requirements are met (instead of being launched immediately after creation). You can see an example of this application below.

In this example, the `Example` class needs three arguments, `x`, `y`, and `z`, to be constructed. For example, it will calculate the volume of a cube in its constructor, so it needs all the arguments simultaneously. We want to initialize `x` and `y` for our `Example` instance using instances of `XProvider` and `YProvider` classes.
The problem is that both `XProvider` and `YProvder` need their target object to provide their values. So we need to have an uncompleted instance of `Example` till `XProvider` and `YProvider` finish their processes. Then the instance can complete its construction.

* Inherit your class that needs uncompleted construction from the `CRI` abstract class.
* Pass the construction required arguments to the `CRI.__init__` (in the `__init__` function of inherited class). We will call them "construction requirements." Don't forget to set the default value of the delayable construction requirements in the `__init__` function of the inherited class to `None`. The `None` value is what `CRI` knows as "NOT YET"!
* Override abstract `__construct__` function in the inherited class. Arguments are the same as construction requirements.
* Once you get an instance of your inherited class, you can pass to it each construction requirement value that you already know as initialization arguments. After that, you can assign values to construction requirements using the `instance.meet_requirement` function.
* The instance starts to complete the construction, As soon as the class requirements are met.
* Use `construction_required` decorator to avoid running a function before completion of the construction. In the example below, `get_construction_status` can be called before completion of construction, but `get_volume` can not.

```python
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
```

When calling the `__init__` function from the `CRI` class, you can input settings:

* `overwrite_requirement (default: False)`: If true, if one construction requirement meets multiple times, the previous values will be ignored and the new value replaced. Else, based on the `ignore_overwrite_error` setting, the new value will be ignored or cause an exception.
* `ignore_overwrite_error (default: False)`: If `overwrite_requirement` be not true and one construction requirement meets multiple times, the object raises an error. The class will not publish this error if `ignore_overwrite_error` be true.
* `auto_construct (default: True)`: If true, the class starts to complete the construction, As soon as the class requirements are met. If false, You must call the `integrate_requirements` function to complete the construction. Use `ignore_requirements_meeting_error` argument of `integrate_requirements` function to manage raising exception it.
* `purge_after_construction (default: True)`: The class does not need the construction requirements after construction (unless it stores them again during the construction process). Therefore, after completing this process, it will delete them.

```python
print(example1.__dict__)
# >>> {'_CRI__reconstruct': False, 'is_constructed': True, 'x': 6, 'y': 1, 'z': 2, 'volume': 12}
print(example2.__dict__)
# >>> {'_CRI__requirements': {'x': None, 'y': None, 'z': 2}, '_CRI__overwrite_requirement': False, '_CRI__ignore_overwrite_error': False, '_CRI__auto_construct': True, '_CRI__purge_after_construction': True, '_CRI__reconstruct': False, 'is_constructed': False}
```

You can prevent this deletion by setting `purge_after_construction` to `False`.

* `reconstruct (default: False)`: If true, allows to reconstruct the instance with new values. You can not set both `purge_after_construction` and `reconstruct` to `True` because reconstruction needs construction requirements. Also, note that if `auto_construct` is true, every `meet_requirement` call can reconstruct the object.
* `ignore_constructed_error (default: False)`: If `reconstruct` be false, and one construction requirement meets when the object is constructed, it raises an error. It will not publish this error if `ignore_constructed_error` be true.
* `construction_permission (default: True)`: While it is false, it will not be possible to construct the instance. If you want the object to auto construct, but you want to ensure it will not be constructed till some event, you can initialize this setting to `False` and, after the event, flip it to `True`. Change construction permission using `set_construction_permission` function.

**add_to_construction_requirements(self, \*\*requirements):** Use this function to add to construction requirements after initialization. Its very useful when you are using inheritance.

**requirement_value(self, requirement):** Use this function to access to value setted to a requirement. If `purge_after_construction` is `True`, this function will not be available after construction completion.

**A technique:** If `auto_construct` is true and all the requirements defined in the initialization are satisfied before calling `add_to_construction_requirements`, the object will complete the construction and not catch new requirements. To prevent this state, you can set `construction_permission` to `False`. It will prevent the object from being auto constructed until you call `instance.set_construction_permission(True)`. Use this function after calling `add_to_construction_requirements`.

```python
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
```

## Installation

```pip install construction-requirements-integrator```