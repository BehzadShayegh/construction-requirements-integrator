from abc import ABC, abstractmethod

class CRI(ABC):
    def __init__(
        self,
        overwrite_requirement: bool = False,
        ignore_overwrite_error: bool = False,
        ignore_constructed_error: bool = False,
        auto_construct: bool = True,
        purge_after_construction: bool = True,
        reconstruct: bool = False,
        construction_permission: bool = True,
        **requirements
    ) -> None:
        self.__requirements = requirements
        self.__overwrite_requirement = overwrite_requirement
        self.__ignore_overwrite_error = ignore_overwrite_error
        self.__ignore_constructed_error = ignore_constructed_error
        self.__auto_construct = auto_construct
        if purge_after_construction and reconstruct:
            raise Exception("Can not reconstruct an object after purging it!")
        self.__purge_after_construction = purge_after_construction
        self.__reconstruct = reconstruct
        self.is_constructed = False
        self.__construction_permission = construction_permission
        self.__do_auto_construct()

    def add_to_construction_requirements(self, **requirements):
        if self.is_constructed:
            raise Exception("Can not add requrements to a constructed object")
        self.__requirements.update(requirements)

    def set_construction_permission(self, construction_permission):
        self.__construction_permission = construction_permission
        self.__do_auto_construct()

    def __do_auto_construct(self):
        if self.__auto_construct:
            self.integrate_requirements(ignore_requirements_meeting_error=True)
            
    @abstractmethod
    def __construct__(self, **requirements) -> None:
        pass
        
    def __are_requirements_met__(self) -> bool:
        if self.is_constructed and not self.__reconstruct:
            return False
        for requirement,value in self.__requirements.items():
            if value is None:
                return False
        return self.__construction_permission
        
    def __purge_after_construction__(self) -> None:
        if self.is_constructed:
            del self.__requirements
            del self.__overwrite_requirement
            del self.__ignore_overwrite_error
            del self.__auto_construct
            del self.__construction_permission
    
    def integrate_requirements(self, ignore_requirements_meeting_error=False) -> None:
        if self.__are_requirements_met__():
            self.__construct__(**self.__requirements)
            self.is_constructed = True
            if self.__purge_after_construction:
                self.__purge_after_construction__()
        elif not ignore_requirements_meeting_error:
            raise Exception("The requirements are not met.")
        
    def meet_requirement(self, **kwargs) -> None:
        if len(kwargs)>1:
            raise Exception("No more than one requirement can be set at a call.")
        if self.is_constructed and not self.__reconstruct:
            if self.__ignore_constructed_error:
                return
            raise Exception("The object has already been constructed.")
        requirement,value = next(iter(kwargs.items()))
        if value is None:
            raise Exception("Can not set a requirement to None.")
        if self.__requirements[requirement] is None or self.__overwrite_requirement:
            self.__requirements[requirement] = value
        elif not self.__ignore_overwrite_error:
            raise Exception("The requirement has already been met.")
        self.__do_auto_construct()


    def requirement_value(self, requirement):
        if self.is_constructed and self.__purge_after_construction:
            raise Exception("The object has already been constructed")
        return self.__requirements[requirement]


def construction_required(function):
    def wrapper(self, **kwargs):
        if not self.is_constructed:
            raise Exception("The object is not constructed yet!")
        return function(self, **kwargs)
    return wrapper