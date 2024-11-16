import types
import inspect


def check_builtins(obj: any) -> bool:
    """Check if the class is a built-in class.

    Args:
        obj (any): 
            An object to check. 

    Returns:
        bool: 
            True if the class is a built-in class, False otherwise.
    """
    # BUG: cannot check if the class is a built-in class properly in some cases
    if inspect.ismodule(obj):
        if obj.__name__.startswith('typing'):
            return True
        if obj.__name__.startswith('types'):
            return True
        if obj.__name__.startswith('builtins'):
            return True

    if hasattr(obj, '__module__'):
        if obj.__module__ in ['builtins', 'typing', 'types']:
            return True
        
    # if obj.__module__ in ['enum']:
    #     raise NotImplementedError('Enum classes are not supported Now.')

    if obj.__name__ in [
        'int', 'float', 'bool', 'complex', 'tuple', 'range', 'bytes', 'bytearray', 'memoryview', 
        'dict', 'list', 'set', 'str', 'any', 'ANY', 'NoneType'
    ]:
        return True
    
    if isinstance(obj, (types.BuiltinFunctionType, types.BuiltinMethodType)):
        return True
    
    return False
