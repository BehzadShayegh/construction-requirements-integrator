# Construction Requirements Integrator Package

With the help of this module, classes can be inherited that are built and configured after their needs are met (instead of being launched immediately after creation).
You can see an example of this application below.

In this example, the `Example` class needs 3 arguments `x`,`y` and `z` to be constructed. For example, it will calculate volume of a cube in its constructor, so it needs all the arguments at the same time.
We want to initialize `x` and `y` for our `Example` instanse using instances of `XProvider` and `YProvider` classes.
The problem is there both `XProvider` and `YProvder` need their target object to provide their values.
So we neet to have an uncompleted instance of `Example` till `XProvider` and `YProvider` finish their processes. Then the instance can complete its construction.

* Inherit your class, that needs uncomleted construction, from `CRI` abstract class.
* Pass the construction reqired arguments to the `CRI.__init__` (in the `__init__` function of inherited class) as below. We will call them "construction requirements". Don't forget to set default value of the delayable construction requirements in the `__init__` function of inherited class to `None`. The `None` value is what `CRI` knows as "NOT YET"!
* Override abstract `__construct__` function in the inherited class. Arguments are the same as construction requirements.
* Once you get an instance of your inherited class, you can pass it each construction requirement value that you already know, as initialization arguments. After that, you can assign values to construction requirements using `instance.meet_requirement` function as in the example below.
* The instance starts to complete the construction, As soon as the class requirements are met.
* Use `construction_required` decorator to avoid running a function before completion of the construction.
In the example below, `get_construction_status` can be called before completion of construction but `get_volume` cann't.

```python
from construction_requirements_integrator import CRI, construction_required
from random import random

class XProvider:
    def __init__(self):
        self.x = int((random()*10))

    def provide_for(self, obj):
        obj.meet_requirement('x', self.x)

class YProvider:
    def __init__(self):
        self.y = int((random()*5))

    def provide_for(self, obj):
        obj.meet_requirement('y', self.y)

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
# >>> Exception: The object is not constructed yet!
```

When calling the `__init__` function from the `CRI` class, you can input settings:

* `overwrite_requirement (default: False)`: If true, if one construction requirement meets multiple times, the previous values will be ignored and the new value replaced. Else, based on `ignore_overwrite_error` setting, new value will be ignored or cause an exception.
* `ignore_overwrite_error (default: False)`: If `overwrite_requirement` be not true and one construction requirement meets multiple times, the object raises an error. This error will not be published if `ignore_overwrite_error` is true.
* `auto_construct (default: True)`: If true, the class starts to complete the construction, As soon as the class requirements are met. If false, You must call `integrate_requirements` function to complete the construction.
Use `ignore_requirements_meeting_error` argument of `integrate_requirements` function to manage raising exception it.
* `purge_after_construction (default: True)`: The class does not need the construction requirements after completion of cunstruction (unless it is stored again during the construction process).
Therefore, after completing this process, it will delete them.

```python
print(example1.__dict__)
# >>> {'_CRI__reconstruct': False, 'is_constructed': True, 'x': 6, 'y': 1, 'z': 2, 'volume': 12}
print(example2.__dict__)
# >>> {'_CRI__requirements': {'x': None, 'y': None, 'z': 2}, '_CRI__overwrite_requirement': False, '_CRI__ignore_overwrite_error': False, '_CRI__auto_construct': True, '_CRI__purge_after_construction': True, '_CRI__reconstruct': False, 'is_constructed': False}
```

You can prevent this deletion by setting `purge_after_construction` to `False`.
* `reconstruct (default: False)`: If true, allows the class to be reconstructed with new values. Note that you can not set both `purge_after_construction` and `reconstruct` to `True` because reconstruction needs construction requirements. Also note that if `auto_construct` be true, every `meet_requirement` call has the potential to reconstruct the object.

**add_to_construction_requirements(self, \*\*requirements):** Use this function to add to construction requirements after initialization. Its very useful when you are using inheritance.

**A technique:** If `auto_construct` be true and all the requirements defined in the initialization satisfied befor calling `add_to_construction_requirements`, the object will be completly constructed and will not catch new requirements. To prevent this state, you can simply add an unreal requirement in initialization and set it to `None`. It will prevent the object to be auto constructed untill you give a value to it. After calling `add_to_construction_requirements`, you can simply satisfy this virtual requirement using `meet_requirement` function and ignore it in `__construct__`.

## Installation

```pip install construction-requirements-integrator```