'''
File: api.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:19:15 pm
Modified By: koko (koko231125@gmail.com>)
'''


import os
from importlib import import_module
from types import ModuleType

import pumlpy.interface as ifc
import pumlpy.impl.base as base
import pumlpy.factory as fac


def plantuml(
    path: str, 
    limit_fqn: str = '', 
    include_extern: bool = False, 
    include_docs: bool = False, 
    max_depth: int = 3, 
) -> ifc.UMLSpace:
    """Inspect a package and return a UML space. 
    
    Args:
        path (str): 
            The path to the package or folder. 
        limit_fqn (str, optional): 
            The fully qualified name of the object to inspect. If empty, all objects will be 
            included. Defaults to ''. 
        include_extern (bool, optional):
            Whether to include external packages. Defaults to False. 
        include_docs (bool, optional): 
            Whether to include documentation for each object. Defaults to False. 
        max_depth (int, optional):
            The maximum depth of recursion. Defaults to 3.
    
    Returns:
        interface.UMLSpace: 
            The UML space instance.
    """
    # Check if the path is startint with `./`
    if path.startswith('./'):
        # Remove the `./` from the path
        path = path[2:]

    # Check the path is a package or a folder
    if path.endswith('.py'):
        # Remove the .py extension and replace system separators with dots
        path = path[:-3]
    path = path.replace(os.sep, '.')

    # Get the package
    package: ModuleType = import_module(path)

    # Create the UML factory
    factory = fac.BaseUMLFactory()

    # Create the UML extractor
    extractor = factory.create_extractor(path, limit_fqn, max_depth, include_extern)

    # Create the UML space
    space = factory.create_space(package.__name__, limit_fqn, include_docs)
    
    # Inspect the package
    extractor.inspect_package(package, space)
    
    return space


def space_to_file(space: ifc.UMLSpace, output: str, replace: bool = False) -> None:
    """Call the to_puml method of the UML space and write the output to a file. 
    
    Args:
        space (UMLSpace): 
            The UML space instance. 
        output (str): 
            The path to the output file. 
        replace (bool, optional):
            Whether to replace the file if it already exists. Defaults to False. 
    
    Raises:
        FileExistsError: 
            If the file already exists and replace is False. 
    """
    # Check if the file already exists
    if os.path.exists(output) and not replace:
        raise FileExistsError(f'The file {output} already exists.')

    with open(output, 'w') as f:
        f.write(space.to_puml())
