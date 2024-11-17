'''
File: rtypes.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:19:56 pm
Modified By: koko (koko231125@gmail.com>)
'''


import types
import inspect
from enum import Enum


class UMLType(Enum):
    r"""UMLType enumeration represents the type of a UML item.
    
    Attributes:
        CLASS (str): 
            The class type.
        METHOD (str): 
            The method type.
        MODULE (str):
            The module type.
        FORWARD (str):
            The not imported type. This is a special indicator that needs more operations.
            For example, if you want to get the object imported, you can do it by:
            ```python
            pkg = importlib.import_module(domain)
            obj = getattr(pkg, obj.__forward_arg__)
            ```
        NONE (str):
            The none type. This is a special indicator that needs more operations. 
            For example, if you want to get the object, you can do it by:
            ```python
            obj = type(obj)
            ```
        ANY (str):
            The any type. 
        NAMED_GENERIC (str): 
            The named generic type.
    """
    # Basic types
    CLASS = 'class'
    METHOD = 'method'
    MODULE = 'module'

    # Special types
    NAMED_GENERIC = 'named_generic'
    FORWARD = 'forward'
    NONE = 'none'
    ANY = 'any'

    # Generics
    # hasattr __name__    getattr __contraints__/__bound__    a = TypeVar('T')
    TYPEVAR = 'typing.TypeVar'            
    # hasattr __name__    getattr __args__    a = typing.Generic[TypeVar('T')]        
    TYPING_GENERIC = 'typing._GenericAlias'       
    # hasattr __name__    getattr __args__    a = typing.Union[int, float]
    TYPING_UNION = 'typing._UnionGenericAlias'    
    # hasattr __name__    getattr __args__    a = list[int, float] or list[int | float]
    TYPES_GENERIC = 'types.GenericAlias'          
    #                     getattr __args__    a = int | float
    TYPES_UNION = 'types.UnionType'               


def check_raw_type(raw: any) -> UMLType:
    r"""Check the type of raw object.
    
    Args:
        raw (any): 
            The raw target to be inspected.
    
    Returns:
        UMLType: 
            The type of the object.
    """
    # Object that can be check by inspect module
    if inspect.isclass(raw):
        return UMLType.CLASS
    if inspect.isfunction(raw) or inspect.ismethod(raw):
        return UMLType.METHOD
    if inspect.ismodule(raw):
        return UMLType.MODULE
    
    # Generic object that is anomynous
    if hasattr(raw, '__args__'):
        if hasattr(raw, '__name__'):
            return UMLType.NAMED_GENERIC
        elif isinstance(raw, types.UnionType):
            return UMLType.TYPES_UNION
        
    # Generic object that is named TypeVar 
    if hasattr(raw, '__constraints__'):
        if getattr(raw, '__constraints__'):
            return UMLType.TYPEVAR
    if hasattr(raw, '__parameters__'):
        if getattr(raw, '__parameters__'):
            return UMLType.TYPEVAR
    if hasattr(raw, '__bound__'):
        if getattr(raw, '__bound__'):
            return UMLType.TYPEVAR
    
    # Object that is not imported
    if hasattr(raw, '__forward_arg__'):
        return UMLType.FORWARD
    
    # Other special cases
    if raw is None:
        return UMLType.NONE
    if hasattr(raw, '__name__'):
        if getattr(raw, '__name__') == 'Any':
            return UMLType.ANY
        elif getattr(raw, '__name__') == 'any':
            return UMLType.ANY
    
    raise ValueError(f"Unknown object type: {type(raw)}")


def get_full_qualname(raw: any, rtype: UMLType) -> str:
    r"""Get the full qualified name of an object.
    
    Args:
        raw (any): 
            The raw target to be inspected.
        rtype (UMLType): 
            The type of the object.
    
    Returns:
        str: 
            The full qualified name of the object.
    """
    match rtype:
        # Basic types
        case UMLType.MODULE:
            full_qualname = raw.__name__
        case UMLType.CLASS | UMLType.METHOD:
            domain = raw.__module__
            full_qualname = f"{domain}.{raw.__qualname__}"

        # Generics
        case UMLType.NAMED_GENERIC | UMLType.TYPEVAR:
            domain = raw.__module__
            full_qualname = f"{domain}.{raw.__name__}"
        case UMLType.TYPES_UNION:
            domain = "types"
            full_qualname = f"{domain}.Union"

        # Special types
        case UMLType.NONE:
            full_qualname = "builtins.None"
        case UMLType.ANY:
            full_qualname = "builtins.any"
        case _:
            raise NotImplementedError(
                f"Cannot handle raw type {rtype} for domain and full qualname extraction."
            )
    return full_qualname
