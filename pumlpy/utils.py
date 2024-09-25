import inspect
import types
from importlib import import_module
from types import ModuleType

import pumlpy.interface as interface
import pumlpy.impl.base as base


class UMLPackageInspector(interface.UMLPackage):

    def __init__(
        self, 
        package: types.ModuleType, 
        extractor: interface.UMLExtractor = None,  
    ) -> None:
        """Get a package as input and return a UMLPackage object.

        Args:
            package (types.ModuleType): 
                The package to inspect.
            extractor (interface.UMLExtractor, optional):
                The extractor for inspecting the package. Defaults to None. 
                If None, a BaseExtractor object will be created.

        Returns:
            None
        
        Raises:
            ImportError: 
                If the package cannot be imported.
        """
        self.extractor = extractor
        self.name = package.__name__
        self.domain = package.__package__
        self.classes: list[interface.T] = self.__extract_classes(package)
        self.packages: list[interface.UMLPackage] = self.__extract_packages(package)

    def __extract_classes(self, package: types.ModuleType) -> list[interface.UMLClass]:
        """Extract the classes of a package.
        
        Args:
            package (object): 
                A package.
        
        Returns:
            list[UMLClass]: 
                The list of classes.
        """
        # Create container for classes
        uml_classes = []
        
        # Extract classes
        for attribute in dir(package):
            # Discard all the built-in classes and attributes in the package
            if attribute.startswith('__') and attribute.endswith('__'):
                continue
            # Check if the attribute is a class
            obj = getattr(package, attribute)
            if self.extractor.is_valid(obj):
                # Discard all the classes that imported from other packages
                # TODO: Add External Class/Package support that are imported in the head
                #  if include_external is True
                if not obj.__module__.startswith(self.domain):
                    continue
                
                # Refresh the max_depth of the extractor
                self.extractor.refresh()
                # Create a UMLClass object
                c = self.extractor.extract(obj, self.domain)
                uml_classes.append(c)
        
        return uml_classes
    
    def __extract_packages(self, package: types.ModuleType) -> list[interface.UMLPackage]:
        """Extract the sub-packages of a package.
        
        Args:
            package (ModuleType): 
                A package.
        
        Returns:
            list[UMLPackage]: 
                The list of sub-packages.
        """
        # Create container for packages
        uml_packages = []
        
        # Extract packages
        for attribute in dir(package):
            obj = getattr(package, attribute)
            if inspect.ismodule(obj):
                # Check if the sub-package belongs to the package
                if not obj.__package__.startswith(package.__package__):
                    continue
                uml_packages.append(UMLPackageInspector(obj, self.extractor))
        
        return uml_packages


def import_pkg(path: str) -> ModuleType:
    """Import a package or module.
    
    Args:
        path (str): 
            The path to the package or module.
    
    Returns:
        ModuleType: 
            The package or module.
    
    Raises:
        ImportError: 
            If the package or module cannot be imported.
    """
    try:
        return import_module(path)
    except ImportError:
        raise ImportError(f'Cannot import package or module "{path}".')
        

def create_package_uml(
    path: str, 
    extractor: interface.UMLExtractor = None, 
) -> interface.UMLSpace:
    """Create a UML object from a package or folder.
    
    Args:
        path (str): 
            The path to the package or folder.
    
    Returns:
        object: 
            A UML object.
    """
    # Get the package
    package: ModuleType = import_pkg(path)

    if not extractor:
        # Create a UMLSpace object
        space: interface.UMLSpace = base.BaseUMLSpace(package.__name__)

        # Create an UMLExtractor object
        extractor = base.BaseExtractor(space)
    
    # Create the UML object
    pkg: interface.UMLPackage = UMLPackageInspector(package, extractor)
    
    return space
