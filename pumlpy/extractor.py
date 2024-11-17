'''
File: extractor.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:20:16 pm
Modified By: koko (koko231125@gmail.com>)
'''


import types
import inspect
import importlib
from typing import Protocol, runtime_checkable, ForwardRef, get_type_hints

import pumlpy.rtypes as rtypes
import pumlpy.interface as ifc
import pumlpy.impl.base as base
import pumlpy.utils as utils


@runtime_checkable
class Extractor(Protocol):
    r"""The Extractor Protocol is used to define the interface for extracting UML items from objects.
    
    Attributes:
        domain (str):
            The domain name of the base module.
        limit_fqn (str):
            The limit fully qualified name of extraction. This is used to limit the extraction to a 
            specific module, package, class, method or generic. This must be a subset of the domain.
            If empty, the domain is used.
            Example:
                domain='pandas', limit_fqn='pandas.core.frame.DataFrame' 
        max_depth (int):
            The maximum depth of extraction from domain to sub-packages. 
        include_external (bool):
            A flag to indicate whether to include classes from external packages. If True, all classes 
            imported from external packages will be included. Otherwise, only classes from the specified 
            domain are considered. 
        uml_class (UMLClass):
            A reference to the concrete implementation of the UMLClass interface. This is used to create 
            new instances of the UMLClass.
        uml_method (UMLMethod):
            A reference to the concrete implementation of the UMLMethod interface. This is used to create 
            new instances of the UMLMethod.
        uml_generic (UMLGeneric):
            A reference to the concrete implementation of the UMLGeneric interface. This is used to create 
            new instances of the UMLGeneric. 
        uml_param (UMLParam):
            A reference to the concrete implementation of the UMLParam interface. This is used to create 
            new instances of the UMLParam. 
        uml_member (UMLMember):
            A reference to the concrete implementation of the UMLMember interface. This is used to create 
            new instances of the UMLMember. 
        uml_ref (UMLObjectRef):
            A reference to the concrete implementation of the UMLObjectRef interface. This is used to create 
            new instances of the UMLObjectRef.

    Methods:
        extract(raw: any, rtype: UMLType, space: UMLSpace, next_layer: bool) -> UMLObject: 
            Extract the UML object from the given raw object.
    """
    domain: str
    limit_fqn: str
    max_depth: int
    include_extern: bool
    uml_class: ifc.UMLClass
    uml_method: ifc.UMLMethod
    uml_generic: ifc.UMLGeneric
    uml_param: ifc.UMLParam
    uml_member: ifc.UMLMember
    uml_ref: ifc.UMLObjectRef

    def extract(
        self, 
        raw: any, 
        rtype: rtypes.UMLType, 
        space: ifc.UMLSpace, 
        next_layer: bool, 
    ) -> ifc.UMLObject | ifc.UMLObjectRef | list[ifc.UMLObject]:
        pass

    def inspect_package(self, package: types.ModuleType, space: ifc.UMLSpace) -> list[ifc.UMLObject]:
        pass


class BaseExtractor(Extractor):
    r"""The BaseExtractor is the concrete implementation of the Extractor protocol."""
    domain: str
    limit_fqn: str
    max_depth: int
    include_extern: bool
    uml_class: ifc.UMLClass
    uml_method: ifc.UMLMethod
    uml_generic: ifc.UMLGeneric
    uml_param: ifc.UMLParam
    uml_member: ifc.UMLMember

    def __init__(
        self, 
        domain: str, 
        limit_fqn: str = '', 
        max_depth: int = 3, 
        include_extern: bool = False, 
        **kwargs, 
    ) -> None: 
        r"""Initialize the BaseExtractor class.
        
        Args:
            domain (str):
                The domain name of the base module.
            limit_fqn (str, optional):
                The limit fully qualified name of extraction. This is used to limit the extraction to a 
                specific module, package, class, method or generic. This must be a subset of the domain.
                If empty, the domain is used. Defaults to ''. 
                Example:
                    domain='pandas', limit_fqn='pandas.core.frame.DataFrame' 
            max_depth (int, optional):
                The maximum depth of extraction from domain to sub-packages. Defaults to 3. 
            include_extern (bool, optional):
                A flag to indicate whether to include items from external packages. If True, all items 
                imported from external packages will be included. Otherwise, only classes from the 
                specified domain are considered. Defaults to False. 
            **kwargs:
                Additional keyword arguments that can be passed to override the default values. These 
                arguments should have the same names as the attributes defined in this class.
                
                Example:
                    uml_class=MyCustomUMLClass(), 
                    uml_method=MyCustomUMLMethod(), 
                    uml_generic=MyCustomUMLGeneric(), 
                    uml_param=MyCustomUMLParam(), 
                    uml_member=MyCustomUMLMember()

        Returns:
            None 
                
        Raises:
            AssertionError:
                If the provided `uml_class`, `uml_method`, `uml_generic`, `uml_param` or `uml_member` are not 
                concrete implementations of the corresponding interfaces.
            ValueError:
                If the provided `limit_fqn` is not a subset of the `domain`. 
        """
        self.domain = domain
        self.max_depth = max_depth
        self.include_extern = include_extern

        # Set default UML Space Items Concrete Classes
        self.uml_class = base.BaseUMLClass
        self.uml_method = base.BaseUMLMethod
        self.uml_generic = base.BaseUMLGeneric
        self.uml_param = base.BaseUMLParam
        self.uml_member = base.BaseUMLMember
        self.uml_ref = base.BaseUMLObjectRef

        # Overwrite the default values with the given keyword arguments
        if 'uml_class' in kwargs:
            uml_class = kwargs['uml_class']
            assert isinstance(uml_class, ifc.UMLClass), "uml_class must be a UMLClass"
            self.uml_class = uml_class
        if 'uml_method' in kwargs:
            uml_method = kwargs['uml_method']
            assert isinstance(uml_method, ifc.UMLMethod), "uml_method must be a UMLMethod"
            self.uml_method = uml_method
        if 'uml_generic' in kwargs:
            uml_generic = kwargs['uml_generic']
            assert isinstance(uml_generic, ifc.UMLGeneric), "uml_generic must be a UMLGeneric"
            self.uml_generic = uml_generic
        if 'uml_param' in kwargs:
            uml_param = kwargs['uml_param']
            assert isinstance(uml_param, ifc.UMLParam), "uml_param must be a UMLParam"
            self.uml_param = uml_param
        if 'uml_member' in kwargs:
            uml_member = kwargs['uml_member']
            assert isinstance(uml_member, ifc.UMLMember), "uml_member must be a UMLMember"
            self.uml_member = uml_member
        if 'uml_ref' in kwargs:
            uml_ref = kwargs['uml_ref']
            assert isinstance(uml_ref, ifc.UMLObjectRef), "uml_ref must be a UMLObjectRef"
            self.uml_ref = uml_ref

        # Initialize the temporary variables for recursion
        self.layer = 0

        self.limit_fqn = limit_fqn
        if limit_fqn:
            if "::" in limit_fqn:
                self.limit_fqn = limit_fqn.split("::")[0]
        
            # Check if the limit_fqn is a subset of the domain
            if not self.limit_fqn.startswith(self.domain):
                raise ValueError(f"limit_fqn must be a subset of the domain: {self.domain}")

        # Initialize working domain
        self.working_domain = domain

    def extract(
        self, 
        raw: any, 
        rtype: rtypes.UMLType, 
        space: ifc.UMLSpace, 
        next_layer: bool = False, 
    ) -> ifc.UMLObject | ifc.UMLObjectRef | list[ifc.UMLObject]:
        r"""Extract the UML object from the given raw object.
        
        Args:
            raw (any):
                The raw object to extract the UML item from.
            rtype (UMLType):
                The type of the raw object.
            space (UMLSpace): 
                A reference to the concrete implementation of the UMLSpace interface. This is used 
                to maintain the extracted UMLItem in the space. 
            next_layer (bool, optional):
                This indicate whether the raw object is a sub-layer of another raw object. Defaults to False.

        Returns:
            UMLObject | UMLObjectRef | list[UMLObject]:
                The extracted result could be a UMLObject, UMLObjectRef or a list of UMLObjects.
        """
        # Check if the object is a class
        if rtype == rtypes.UMLType.CLASS or rtype == rtypes.UMLType.ANY:
            return self.inspect_class(raw, rtype, space, next_layer)
        
        # Check if the object is a method
        if rtype == rtypes.UMLType.METHOD:
            return self.inspect_method(raw, rtype, space, next_layer)
        
        # Check if the object is a generic
        if rtype == rtypes.UMLType.NAMED_GENERIC or rtype == rtypes.UMLType.TYPES_UNION:
            return self.inspect_generic(raw, rtype, space, next_layer)
        
        # Check if the object is a forward reference
        if rtype == rtypes.UMLType.FORWARD:
            pkg = importlib.import_module(self.working_domain)
            raw = getattr(pkg, raw.__forward_arg__)
            rtype = rtypes.check_raw_type(raw)
            return self.extract(raw, rtype, space, next_layer)
        
        # Check if the object is a NoneType
        if rtype == rtypes.UMLType.NONE:
            raw = type(raw)
            return self.uml_class(raw, rtypes.UMLType.NONE, empty=True)
        
        # Check if the object is a module
        if rtype == rtypes.UMLType.MODULE:
            return self.inspect_package(raw)
        
        # Unsupported object type
        raise ValueError(f"Unsupported object type: {rtype}")

    def inspect_package(self, package: types.ModuleType, space: ifc.UMLSpace) -> list[ifc.UMLObjectRef]:
        r"""Extract the classes and sub-packages of a package.
        
        Args:
            package (types.ModuleType):
                A Python module object representing the package to inspect. 
            space (UMLSpace): 
                A reference to the concrete implementation of the UMLSpace interface. This is used 
                to maintain the extracted UMLItem in the space. 

        Returns: 
            list[UMLObjectRef]: 
                The list of UMLObjectRefs that refer to the extracted UMLObjects. This means that all 
                the UMLObjects extracted directly from the package are independent objects in the 
                UMLSpace, not a subset of any other UMLObject.
        """
        source_domain = self.working_domain
        # Update the working domain
        self.working_domain = package.__name__

        # Extract constants
        consts = get_type_hints(package)

        for obj, raw in consts.items():
            # Get the attribute value
            rtype = rtypes.check_raw_type(raw)
            # Extract the object
            self.extract(raw, rtype, space)

        dirs = dir(package)

        # Discard the redundant object that already extracted as constants
        dirs = [d for d in dirs if d not in consts.keys()]

        objs: list[ifc.UMLObject] = []

        # Extract UMLObjects from the package
        for obj in dirs:
            # Discard all the built-in classes and attributes in the package
            if obj.startswith('__') and obj.endswith('__'):
                continue
            
            # Get the attribute value
            raw = getattr(package, obj) 

            # Discard all the built-in object in the package
            if utils.check_builtins(raw):
                continue

            # Get the raw type of the object
            rtype = rtypes.check_raw_type(raw)

            # Check if include external packages is False
            if not self.include_extern:
                if rtype == rtypes.UMLType.MODULE:
                    # Discard all the modules that imported from other packages
                    if not raw.__name__.startswith(self.domain):
                        continue
                else:
                    # Discard all the object that imported from other packages
                    if not raw.__module__.startswith(self.domain):
                        continue

            # Get the full qualified name of obj
            full_qualname = f"{self.working_domain}.{obj}"

            # Check if the full qualified name is a subset of the limit_fqn
            if self.limit_fqn and not full_qualname.startswith(self.limit_fqn):
                continue

            # Extract UMLClass object
            if rtype == rtypes.UMLType.CLASS:
                objs.append(self.inspect_class(raw, rtype, space))

            # Extract UMLMethod object
            elif rtype == rtypes.UMLType.METHOD:
                objs.append(self.inspect_method(raw, rtype, space))

            # Extract UMLGeneric object
            elif rtype == rtypes.UMLType.NAMED_GENERIC or rtype == rtypes.UMLType.TYPES_UNION:
                objs.append(self.inspect_generic(raw, rtype, space))

            # Extract a sub-package
            elif rtype == rtypes.UMLType.MODULE:
                # Increase the layer by 1
                self.layer += 1

                objs.append(self.inspect_package(raw, space))

                # Decrease the layer by 1
                self.layer -= 1

        # Recover the working domain
        self.working_domain = source_domain

        return objs
                
    def inspect_class(
        self, 
        raw: object, 
        rtype: rtypes.UMLType, 
        space: ifc.UMLSpace, 
        next_layer: bool = False, 
    ) -> ifc.UMLClass | ifc.UMLObjectRef:
        r"""Extract a UMLClass object from the given raw object and return its reference. 
        
        Args:
            raw (object): 
                The raw object to extract.
            rtype (UMLType): 
                The type of the raw object.
            space (UMLSpace): 
                The UMLSpace to add the extracted UMLClass.
            next_layer (bool, optional):
                This indicate whether the raw object is a sub-layer of another raw object. Defaults to False.
        
        Returns:
            UMLObjectRef: 
                The reference of the extracted UMLClass object. 
        """
        source_domain = self.working_domain

        # Check if the raw object should be added to the UMLSpace
        add_to_space = True
        if utils.check_builtins(raw):
            add_to_space = False
        
        # Check if the raw object is any
        if rtype == rtypes.UMLType.ANY:
            return self.uml_class(raw, rtype, empty=True)

        # Update the working domain
        self.working_domain = raw.__module__
        
        # Get the fully qualified name of the class
        full_qualname = rtypes.get_full_qualname(raw, rtype)
        
        if add_to_space:
            # Check if the class is already in the list of classes in UMLSpace
            if full_qualname in space:
                ref: ifc.UMLObjectRef = space[full_qualname]
            else:
                # Register a reference to the UMLSpace
                ref = space.register(full_qualname)

            if next_layer:
                # Recover the working domain
                self.working_domain = source_domain

                # Return a UMLObjectRef
                return ref

        # Check if the layer is greater than the max_depth
        empty = False
        if not raw.__module__.startswith(self.domain) and not self.include_extern:
            empty = True

        # Track the in-package class
        uml_class = self.__extract_class(raw, full_qualname, space, empty)

        if not uml_class.empty and add_to_space:
            # Add the class to the UMLSpace
            space.add_item(uml_class)

        # Recover the working domain
        self.working_domain = source_domain

        return ref if add_to_space else uml_class

    def __extract_class(
        self, 
        raw: object, 
        full_qualname: str, 
        space: ifc.UMLSpace, 
        empty: bool = False, 
    ) -> ifc.UMLClass:
        r"""Extract a UMLClass object from the given class.
        
        Args:
            raw (object): 
                The class object to extract. 
            full_qualname (str): 
                The fully qualified name of the class. This is used to designate the fully 
                qualified name of the member of the class. 
            space (UMLSpace): 
                The UMLSpace to add the class. 
            empty (bool, optional):
                A flag to indicate whether the class is empty or not. Defaults to False. 
        
        Returns:
            UMLClass: 
                The extracted UMLClass object.
        """
        if not empty:
            # Extract the ancestors, attributes and methods of the class
            ancestors = self.__extract_class_bases(raw, space)
            pa, pr, pv = self.__extract_class_attrs(raw, full_qualname, space)
            pam, prm, pvm = self.__extract_class_methods(raw, full_qualname, space)

            # Create kwargs for the UMLClass object
            kwargs = {
                'ancestors': ancestors,
                'public_attributes': pa,
                'protected_attributes': pr,
                'private_attributes': pv,
                'public_methods': pam,
                'protected_methods': prm,
                'private_methods': pvm
            }

            # Create a UMLClass object
            uml_class = self.uml_class(raw, rtypes.UMLType.CLASS, empty=False, **kwargs)
        else: 
            # Create a empty UMLClass object
            uml_class = self.uml_class(raw, rtypes.UMLType.CLASS, empty=True)

        return uml_class
    
    def __extract_class_bases(self, raw: object, space: ifc.UMLSpace) -> list[ifc.UMLClass, ifc.UMLObjectRef]:
        r"""Extract the ancestors of a class recursively until limitation.

        Args:
            raw (object): 
                The class object to extract ancestors from. 
            space (UMLSpace):
                The UMLSpace to add the class.

        Returns:
            list[UMLClass, UMLObjectRef]:
                The list of UMLClass or UMLObjectRefs that refer to the ancestors registered in the UMLSpace.
        """
        # Get the class bases
        bases = raw.__bases__

        # Create container for ancestors
        ancestors: list[ifc.UMLClass, ifc.UMLObjectRef] = []

        # Recursively extract ancestors
        for base in bases:
            # Discard the built-in classes
            if utils.check_builtins(base):
                continue

            # Check the raw type of the base class
            rtype = rtypes.check_raw_type(base)

            # Extract the class object
            ancestor: ifc.UMLClass | ifc.UMLObjectRef = self.inspect_class(base, rtype, space, True)
            
            # Add the ancestor to the list of ancestors
            ancestors.append(ancestor)

        return ancestors
    
    def __extract_class_attrs(
        self, 
        raw: object, 
        full_qualname: str, 
        space: ifc.UMLSpace
    ) -> tuple[list[ifc.UMLMember]]:
        r"""Extract the attributes of a class recursively until limitation.

        Args:
            raw (object): 
                The class object to extract ancestors from. 
            full_qualname (str): 
                The fully qualified name of the class. This is used to designate the fully
                qualified name of the member that maintains the attribute. 
            space (UMLSpace):
                The UMLSpace to add the class. 
                
        Returns:
            tuple[list[UMLMember]]:
                The tuple of lists of UMLMember including public, protected and private attributes.
        """
        # Get the class attributes
        attributes = raw.__annotations__

        # Create container for public attributes
        public_attributes: list[ifc.UMLParam] = []
        # Create container for protected attributes
        protected_attributes: list[ifc.UMLParam] = []
        # Create container for private attributes
        private_attributes: list[ifc.UMLParam] = []

        # Extract attributes
        for name, obj in attributes.items():
            if isinstance(obj, str):
                obj = ForwardRef(obj)
                rtype = rtypes.UMLType.FORWARD
            else:
                # Check the raw type of the attribute
                rtype = rtypes.check_raw_type(obj)

            # Extract the attribute as a UMLItem object
            item: ifc.UMLObject | ifc.UMLObjectRef = self.extract(obj, rtype, space, True)

            # Create a UMLMember object
            member: ifc.UMLMember = self.uml_member(f"{full_qualname}::{name}", item)

            # Add the member to container based on the mode
            if member.mode == base.UMLMemberMode.PUBLIC:
                public_attributes.append(member)
            elif member.mode == base.UMLMemberMode.PROTECTED:
                protected_attributes.append(member)
            elif member.mode == base.UMLMemberMode.PRIVATE:
                private_attributes.append(member)

        return public_attributes, protected_attributes, private_attributes
    
    def __extract_class_methods(
        self, 
        raw: object, 
        full_qualname: str, 
        space: ifc.UMLSpace
    ) -> tuple[list[ifc.UMLMember]]:
        r"""Extract the public methods of a class.
        
        Args:
            raw (object): 
                A callable object. 
            full_qualname (str): 
                The fully qualified name of the class. This is used to designate the fully 
                qualified name of the member that maintains the method. 
            space (UMLSpace): 
                The UMLSpace to add the class. 
        
        Returns:
            list[UMLMember]: 
                The list of public methods.
            list[UMLMember]: 
                The list of protected methods.
            list[UMLMember]: 
                The list of private methods.
        """
        # Get the class attributes
        attributes = dir(raw)

        # Create container for public methods
        public_methods: list[ifc.UMLMember] = []
        # Create container for protected methods
        protected_methods: list[ifc.UMLMember] = []
        # Create container for private methods
        private_methods: list[ifc.UMLMember] = []

        # Extract public methods
        for name in attributes:
            obj = getattr(raw, name)

            # Check if the attribute is not a method
            if not callable(obj):
                continue

            # Discard built-in methods
            if name.startswith('__') and name.endswith('__'):
                continue
            
            # Check if the class name in the attribute name
            if raw.__name__ in name:
                # If so, remove the class name from the method name
                name = name.replace(f"_{raw.__name__}", "")

            # Create a UMLMethod object
            method: ifc.UMLMethod | ifc.UMLObjectRef = self.inspect_method(
                obj, rtypes.UMLType.METHOD, space, True
            )

            # Create a UMLMember object
            member: ifc.UMLMember = self.uml_member(f"{full_qualname}::{name}", method)

            # Add the member to container based on the mode
            if member.mode == base.UMLMemberMode.PUBLIC:
                public_methods.append(member)
            elif member.mode == base.UMLMemberMode.PROTECTED:
                protected_methods.append(member)
            elif member.mode == base.UMLMemberMode.PRIVATE:
                private_methods.append(member)

        return public_methods, protected_methods, private_methods
    
    def inspect_method(
        self, 
        raw: object, 
        rtype: rtypes.UMLType, 
        space: ifc.UMLSpace, 
        next_layer: bool = False, 
    ) -> ifc.UMLMethod | ifc.UMLObjectRef:
        r"""Extract a UMLMethod object from the given callable object.
        
        Args:
            raw (object): 
                The callable object to extract. 
            rtype (UMLType):
                The UMLType of the raw object. 
            space (UMLSpace):
                The UMLSpace to add the class. 
            next_layer (bool, optional):
                This indicate whether the raw object is a sub-layer of another raw object. Defaults to False.
        
        Returns:
            UMLMethod | UMLObjectRef: 
                The extracted UMLMethod object if the raw object is a sub-layer of another raw object, otherwise, 
                a UMLObjectRef is returned. 

        Raises:
            TypeError: 
                If the raw object is not a function or method. 
            ValueError: 
                If the raw object is a built-in object. 
        """
        source_domain = self.working_domain

        # Check if the raw object is a method
        if not inspect.isfunction(raw) and not inspect.ismethod(raw):
            raise TypeError("The raw object must be a function or method.")
        
        # Check if the raw object is a built-in class
        if utils.check_builtins(raw):
            raise ValueError("Built-in Methods are not supported.")
        
        # Update the working domain
        self.working_domain = raw.__module__
        
        add_to_space = True
        # Check if there is a `.` in the qualified name, if True, it is a method
        if '.' in raw.__qualname__:
            add_to_space = False

        # Get the full qualified name of the class
        full_qualname = rtypes.get_full_qualname(raw, rtype)
        
        if add_to_space:
            # Check if the class is already in the list of classes in UMLSpace
            if full_qualname in space:
                ref: ifc.UMLObjectRef = space[full_qualname]
            else:
                # Register a reference to the UMLSpace
                ref = space.register(full_qualname)

            if next_layer:
                # Recover the working domain
                self.working_domain = source_domain

                # Return a UMLObjectRef
                return ref

        # Check if the layer is greater than the max_depth
        empty = False
        if not raw.__module__.startswith(self.domain) and not self.include_extern:
            empty = True

        # Track the in-package class with layer -1
        uml_method = self.__extract_method(raw, full_qualname, space, empty)

        if add_to_space and not uml_method.empty:
            # Add the class to the UMLSpace
            space.add_item(uml_method)
        
        # Recover the working domain
        self.working_domain = source_domain

        return ref if add_to_space else uml_method
    
    def __extract_method(
        self, 
        raw: object, 
        full_qualname: str, 
        space: ifc.UMLSpace, 
        empty: bool = False
    ) -> ifc.UMLMethod:
        r"""Extract the parameters of a method.
        
        Args:
            raw (object): 
                The callable object to extract.
            space (UMLSpace):
                The UMLSpace to add the class. 
            full_qualname (str):
                The full qualified name of the method. This is used to designate the fully 
                qualified name of the param that maintains the any kinds of UMLObject. 
            empty (bool, optional):
                A flag to indicate whether the method is empty. Defaults to False. 
        
        Returns:
            UMLMethod: 
                The extracted UMLMethod object. 
        """
        if empty:
            # Create a empty UMLMethod object
            return self.uml_method(raw, empty)

        # Get the parameters of the method
        attributes = raw.__annotations__
        
        # Create container for parameters
        params: list[ifc.UMLParam] = []
        # Create reference for returns
        returns: ifc.UMLParam = None
        
        # Extract parameters
        for name, obj in attributes.items():

            # Get the raw type of the parameter
            rtype = rtypes.check_raw_type(obj)

            if rtype == rtypes.UMLType.METHOD: 
                if utils.check_builtins(obj):
                    raise ValueError("Built-in Methods are not supported.")

            # Create a UML Object
            item: ifc.UMLObject | ifc.UMLObjectRef = self.extract(obj, rtype, space, True)

            if name != 'return':
                # Create a UMLParam object to wrap the raw parameter object
                param: ifc.UMLParam = self.uml_param(f"{full_qualname}::{name}", item)
                params.append(param)
            else:
                # Create a UMLParam object to wrap the raw parameter object
                returns = self.uml_param(f"{full_qualname}::{name}", item)
        
        # Create a UMLMethod object
        kwargs = {
            "params": params,
            "returns": returns,
        }
        return self.uml_method(raw, False, **kwargs)
    
    def inspect_generic(
        self, 
        raw: any, 
        rtype: rtypes.UMLType, 
        space: ifc.UMLSpace, 
        next_layer: bool = False, 
    ) -> ifc.UMLGeneric: 
        r"""Extract a UMLGeneric object from the given object.
        
        Args:
            raw (Any): 
                The generic object to extract. 
            rtype (UMLType): 
                The type of the generic object. 
            space (UMLSpace):
                The UMLSpace to add the class. 
            next_layer (bool, optional):
                This indicate whether the raw object is a sub-layer of another raw object. Defaults to False.

        Returns:
            UMLGeneric: 
                The extracted UMLGeneric object. 
        """
        # Check if add to space
        add_to_space = False
        if rtype == rtypes.UMLType.TYPEVAR:
            add_to_space = True

        full_qualname = rtypes.get_full_qualname(raw, rtype)
        empty = False
        
        if add_to_space:
            # Check if the class is already in the list of classes in UMLSpace
            if full_qualname in space:
                ref: ifc.UMLObjectRef = space[full_qualname]
            else:
                # Register a reference to the UMLSpace
                ref = space.register(full_qualname)

            if next_layer:
                # Return a UMLObjectRef
                return ref

            if not raw.__module__.startswith(self.domain) and not self.include_extern:
                # This is a external Generic
                empty = True

        # Track the in-package class with layer -1
        uml_generic = self.__extract_generic(raw, rtype, full_qualname, space, empty)

        if add_to_space and not uml_generic.empty:
            # Add the class to the UMLSpace
            space.add_item(uml_generic)

        return ref if add_to_space else uml_generic
    
    def __extract_generic(
        self, 
        raw: object, 
        rtype: rtypes.UMLType, 
        full_qualname: str, 
        space: ifc.UMLSpace, 
        empty: bool = False, 
    ) -> ifc.UMLGeneric:
        r"""Extract a UMLGeneric object from the given object.
        
        Args:
            raw (object): 
                The generic object to extract.
            rtype (rtypes.UMLType):
                The type of the generic object.
            full_qualname (str):
                The fully qualified name of the generic object.
            space (UMLSpace):
                The UMLSpace to store the extracted objects.
            empty (bool, optional):
                Whether the generic object should be considered as empty. Defaults to False. 
            
        Returns:
            UMLGeneric: 
                The extracted UMLGeneric object. 
        """
        # Check if the generic is empty
        if empty:
            # Create a empty UMLGeneric object
            return self.uml_generic(raw, rtype, empty)

        # Get the arguments of the object
        while True:
            if hasattr(raw, '__args__'):
                args = raw.__args__
                if args:
                    break
            if hasattr(raw, '__constraints__'):
                args = raw.__constraints__
                if args:
                    break
            if hasattr(raw, '__bound__'):
                args = raw.__bound__
                if args:
                    break
            if hasattr(raw, '__parameters__'):
                raise NotImplementedError('Not implemented yet')

            raise ValueError(f'Unsupported object type: {type(raw)}')

        # Create container for arguments
        uml_args: list[ifc.UMLItem] = []
        for idx, obj in enumerate(args):
            if isinstance(obj, str):
                obj = ForwardRef(obj)

            # Get the raw type of the argument
            raw_type = rtypes.check_raw_type(obj)

            uml_arg: ifc.UMLObject | ifc.UMLObjectRef = self.extract(
                obj, raw_type, space, next_layer=True
            )

            # Create a UMLParam object for the argument
            param = self.uml_param(f"{full_qualname}::{idx}", uml_arg)

            uml_args.append(param)

        return self.uml_generic(raw, rtype, empty, *uml_args)
    