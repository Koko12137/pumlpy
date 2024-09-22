import typing
import inspect
import importlib

import pumlpy.interface as interface


T = typing.TypeVar('T', interface.UMLClass, interface.UMLMethod, interface.UMLParams)


class BaseUMLRelation(interface.UMLRelation):

    template = "{source} {relation} {target}"

    def __init__(
        self, 
        source: str, 
        target: str, 
        relation: interface.UMLRelationType, 
        space: interface.UMLSpace,
    ) -> None:
        """Create a UMLRelation object.

        Args:
            source (str): 
                The full qualified name of source class.
            target (str): 
                The full qualified name of target class.
            relation (UMLRelationType): 
                The relation type.
            space (UMLSpace): 
                The UMLSpace that this relation belongs to.
        
        Returns:
            None
        """
        self.source = source
        self.target = target
        self.relation = relation
        self.space = space

    def register(self) -> None:
        """Register the relation to the UMLSpace.
        
        Raises:
            ValueError: 
                If the source or target classes are not in the UMLSpace.
        """
        self.space.add_relation(self)

    def to_puml(self) -> str:
        return self.template.format(
            source=self.source, relation=self.relation.value, target=self.target, 
        )


class BaseUMLSpaceItem(interface.UMLSpaceItem):

    templates = {
        interface.UMLItemType.CLASS: "{class_type} {name} {{\n{attributes}\n{methods}\n}}",
        interface.UMLItemType.METHOD: "Class {name} << Method >> {{\n-Params-\n{params}\n-Returns-\n{returns}\n}}",
        interface.UMLItemType.PARAMS: "Interface {name} << GenericType >> {{\n{args}\n}}",
    }

    def __init__(
        self, 
        obj: object, 
        itype: interface.UMLItemType, 
        space: interface.UMLSpace, 
        fqn: str = '', 
        empty: bool = False, 
    ) -> None:
        """Create a UMLSpaceItem object. 
        
        Args:
            obj (object): 
                The object representing the item.
            itype (UMLItemType): 
                The type of the item.
            space (UMLSpace): 
                The UMLSpace that this item belongs to.
            fqn (str): 
                The fully qualified name of the item. Defaults to an empty string.
            empty (bool): 
                A flag to indicate if the item is empty. Defaults to False.
        """
        if hasattr(obj, '__qualname__'):
            name = obj.__qualname__
        elif hasattr(obj, '__name__'):
            name = obj.__name__
        else:
            name = str(obj)
        self.raw = obj
        self.empty = empty
        self.itype = itype
        self.space = space
        self.domain = obj.__module__
        self.full_qualname = fqn if fqn else f"{self.domain}.{name}"
        self.template = self.templates[itype]


class BaseUMLMember(interface.UMLMember[T]):

    template = "\t{mode} {body}" 

    def __init__(self, name: str, raw: T) -> None:
        """Create a UMLMember object."""
        self.name = name
        self.raw = raw
        self.mode = self.__infer_mode()

    def __infer_mode(self) -> interface.UMLMemberMode:
        if self.name.startswith('_'):
            if self.name.startswith('__'):
                return interface.UMLMemberMode.PRIVATE
            else:
                return interface.UMLMemberMode.PROTECTED
        else:
            return interface.UMLMemberMode.PUBLIC


    def to_puml(self) -> str:
        # Check if the raw object is a UMLClass object
        if self.raw.itype == interface.UMLItemType.CLASS:
            body = f"{self.name}:{self.raw.full_qualname}"
            return self.template.format(mode=self.mode.value, body=body)
        elif self.raw.itype == interface.UMLItemType.METHOD:
            if not self.raw.empty:
                # All the parameters included in the method signature are UMLMember objects.
                # So, we should call the to_puml method of each parameter to override the original template 
                # and represent the parameter in the Member format.
                signature = [param.to_puml() for param in self.raw.params]
                # Remove the tab and mode indicator from the signature
                signature = [param.split(' ')[2:] for param in signature]
                # Remove the return type for all the parameters
                signature = [param.split('):')[0]+")" for param in signature]
                # Join the parameters with a comma
                signature = ', '.join(*[' '.join(sig) for sig in signature])

                # The return type of the method is a UMLMember object. So the returns of to_puml method 
                # including the return type in the Member format.
                ret = self.raw.returns.to_puml()
                # Remove the tab and mode indicator from the return type
                ret = ret.split(' ')[2:]

                # Assemble the Member format of the method with the signature and return type.
                fn_signature = f"{self.name}({signature}):{ret}"
                return self.template.format(mode=self.mode.value, body=fn_signature)
            else:
                return self.template.format(mode=self.mode.value, body=self.name)
        elif self.raw.itype == interface.UMLItemType.PARAMS:    # TODO: Format with the source type
            return self.template.format(mode=self.mode.value, body=self.name)
        else:
            raise ValueError(f'Expected UMLClass or UMLMethod but got {type(self.raw)}')


class BaseUMLParams(BaseUMLSpaceItem, interface.UMLParams):

    def __init__(
        self, 
        obj: object, 
        space: interface.UMLSpace, 
        extractor: interface.UMLExtractor = None,  
        fqn: str = '', 
        empty: bool = False, 
    ) -> None:
        """Create a UMLParams object. 
        
        Args:
            obj (object): 
                The object representing the item.
            space (UMLSpace): 
                The UMLSpace that this item belongs to.
            extractor (UMLExtractor): 
                An instance of UMLExtractor used to extract arguments from the object. Defaults to None.
            fqn (str): 
                The fully qualified name of the item. Defaults to an empty string.
            empty (bool): 
                A flag to indicate if the item is empty. Defaults to False.
        """
        super().__init__(obj, interface.UMLItemType.PARAMS, space, fqn, empty)
        self.extractor = extractor
        if not self.empty:
            self.args = self.__extract_args()
        else:
            self.args = []

    def __extract_args(self) -> list[T]:
        """Extract the arguments of a parameter type hint object.
        
        Returns:
            list[UMLClass | UMLMethod | UMLParams]: 
                The list of arguments.
        """
        # Get the arguments of the object
        if hasattr(self.raw, '__args__'):
            args = self.raw.__args__
        elif hasattr(self.raw, '__constraints__'):
            args = self.raw.__constraints__
        else:
            raise ValueError(f'Unsupported object type: {type(self.raw)}')

        # Create container for arguments
        uml_args = []
        for arg in args:
            uml_arg = self.extractor.extract(arg, self.domain)
            # Create a Generic UMLMember object for the argument depending on the item type
            name = uml_arg.full_qualname.split('.')[-1]
            if uml_arg.itype == interface.UMLItemType.PARAMS:
                member = BaseUMLMember[interface.UMLParams](name, uml_arg)
            elif uml_arg.itype == interface.UMLItemType.CLASS:
                member = BaseUMLMember[interface.UMLClass](name, uml_arg)
            elif uml_arg.itype == interface.UMLItemType.METHOD:
                member = BaseUMLMember[interface.UMLMethod](name, uml_arg)
            else:
                raise TypeError('Unsupported attribute type')
            uml_args.append(member)

            # Create a relation to the UMLSpace
            # TODO: 20240921

        return uml_args

    def get_all_args(self) -> list[T]:
        args = []
        for arg in self.args:
            if isinstance(arg, interface.UMLParams):
                args.extend(arg.get_all_args())
            else:
                args.append(arg)
        return args
    
    def to_puml(self) -> str:
        return self.template.format(
            name=self.full_qualname, 
            args='\n'.join([arg.to_puml() for arg in self.args]), 
        )


class BaseUMLClass(BaseUMLSpaceItem, interface.UMLClass):

    def __init__(
        self, 
        obj_class: object, 
        space: interface.UMLSpace, 
        extractor: interface.UMLExtractor = None,  
        fqn: str = '', 
        empty: bool = False, 
    ) -> None:
        """Get a class type as input and return a UMLClass object.

        Args:
            obj_class (object): 
                The object class to be converted to a UMLClass object.
            space (UMLSpace): 
                The UMLSpace instance to which the UMLClass object belongs.
            extractor (UMLExtractor): 
                An instance of UMLExtractor used to extract members from the class.
            fqn (str):
                The fully qualified name of the class. Defaults to an empty string.
            empty (bool):
                A flag to indicate whether the class is empty or not.

        Returns:
            None
        """
        super().__init__(obj_class, interface.UMLItemType.CLASS, space, fqn, empty)
        self.extractor = extractor
        self.docstring = obj_class.__doc__
        self.is_builtin = self.__check_builtins(obj_class)
        if not self.is_builtin:
            self.is_interface = issubclass(obj_class, typing.Protocol)
            if self.is_interface:
                self.is_interface = obj_class._is_protocol
        else:
            try: 
                self.is_interface = issubclass(obj_class, typing.Protocol)
            except:
                self.is_interface = False

        # Do not track ancestors, attributes and methods of built-in classes. 
        if not self.is_builtin and not self.empty and self.extractor:
            # Extract the ancestors, attributes and methods of the class
            self.ancestors: list[interface.UMLClass] = self.__extract_ancestors(obj_class)

            pa, pr, pv = self.__extract_attributes(obj_class)
            self.public_attributes: list[interface.UMLClass] = pa
            self.protected_attributes: list[interface.UMLClass] = pr
            self.private_attributes: list[interface.UMLClass] = pv

            pam, prm, pvm = self.__extract_methods(obj_class)
            self.public_methods: list[interface.UMLMethod] = pam
            self.protected_methods: list[interface.UMLMethod] = prm
            self.private_methods: list[interface.UMLMethod] = pvm
        else:
            # BUG: Can not extract class within a built-in container
            self.ancestors = []
            self.public_attributes = []
            self.protected_attributes = []
            self.private_attributes = []
            self.public_methods = []
            self.protected_methods = []
            self.private_methods = []

        # Add the class to the UMLSpace if it is not a built-in class
        if not self.is_builtin:
            # A new UMLClass initializing will ensure that it could be referenced in the UMLSpace.
            # If it is already registered, then an exception will be raised.
            self.space.add_item(self)

    def __check_builtins(self, obj_class: object) -> bool:
        """Check if the class is a built-in class.

        Args:
            obj_class (object): 
                A class type.

        Returns:
            bool: 
                True if the class is a built-in class, False otherwise.
        """
        # BUG: cannot check if the class is a built-in class properly in some cases
        if obj_class.__module__ in ['builtins', 'typing']:
            return True
        elif obj_class.__name__ in [
            'int', 'float', 'bool', 'complex', 'tuple', 'range', 'bytes', 'bytearray', 'memoryview', 
            'dict', 'list', 'set', 'str', 
        ]:
            return True
        else:
            return False

    def __extract_ancestors(self, obj_class: object) -> list[interface.UMLClass]:
        """Extract the ancestors of a class recursively until object.

        Args:
            obj_class (object): 
                A class type.

        Returns:
            list[UMLClass]: 
                The list of ancestors.
        """
        # Get the class bases
        bases = obj_class.__bases__

        # Create container for ancestors
        ancestors: list[interface.T] = []

        # Recursively extract ancestors
        for base in bases:
            ancestor = self.extractor.extract(base, self.domain)
            
            # Add the ancestor to the list of ancestors
            ancestors.append(ancestor)

            # Add a relation to the UMLSpace.
            # If this ancestor is a built-in class, ignore it.
            if not ancestor.is_builtin:
                # Check if the ancestor is an interface
                if ancestor.is_interface:
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        ancestor.full_qualname, 
                        interface.UMLRelationType.IMPLEMENTATION, 
                        self.space, 
                    )
                else:
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        ancestor.full_qualname, 
                        interface.UMLRelationType.INHERITANCE, 
                        self.space, 
                    )
                # Register the relation to the UMLSpace
                relation.register()

        return ancestors

    def __extract_attributes(self, obj_class: object) -> tuple[list[interface.UMLMember]]:
        """Extract the public attributes of a class.

        Args:
            obj_class (object): 
                A class type.
                
        Returns:
            list[UMLClass]: 
                The list of public attributes.
        """
        # Get the class attributes
        attributes = obj_class.__annotations__

        # Create container for public attributes
        public_attributes: list[interface.UMLClass] = []
        # Create container for protected attributes
        protected_attributes: list[interface.UMLClass] = []
        # Create container for private attributes
        private_attributes: list[interface.UMLClass] = []

        # Extract public attributes
        for name, value in attributes.items():
            attribute = self.extractor.extract(value, self.domain)

            # Inject the attribute to initialize a UMLMember object
            # Depending on the item type, the Generic UMLMember object will be created
            if attribute.itype == interface.UMLItemType.PARAMS:
                member = BaseUMLMember[interface.UMLParams](name, attribute)
            elif attribute.itype == interface.UMLItemType.CLASS:
                member = BaseUMLMember[interface.UMLClass](name, attribute)
            elif attribute.itype == interface.UMLItemType.METHOD:
                member = BaseUMLMember[interface.UMLMethod](name, attribute)
            else:
                raise TypeError('Unsupported attribute type')

            # Add the member to container based on the mode
            if member.mode == interface.UMLMemberMode.PUBLIC:
                public_attributes.append(member)
            elif member.mode == interface.UMLMemberMode.PROTECTED:
                protected_attributes.append(member)
            elif member.mode == interface.UMLMemberMode.PRIVATE:
                private_attributes.append(member)
            else:
                raise ValueError("Invalid member mode")
            
            # Check if the attribute is a class or a container
            if attribute.itype == interface.UMLItemType.PARAMS:
                # Register the relation to the UMLSpace for each member
                for member in attribute.get_all_args():
                    relation = BaseUMLRelation(
                        self.full_qualname,  
                        member.raw.full_qualname, 
                        interface.UMLRelationType.COMPOSITION, 
                        self.space, 
                    )
                    # Register the relation to the UMLSpace
                    relation.register()
            else:
                if attribute.itype == interface.UMLItemType.CLASS and not attribute.is_builtin: 
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        attribute.full_qualname, 
                        interface.UMLRelationType.DEPENDENCY, 
                        self.space, 
                    )   
                    # Register the relation to the UMLSpace
                    relation.register()
                elif attribute.itype == interface.UMLItemType.METHOD:
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        attribute.full_qualname, 
                        interface.UMLRelationType.DEPENDENCY, 
                        self.space, 
                    )
                    # Register the relation to the UMLSpace
                    relation.register()

        return public_attributes, protected_attributes, private_attributes

    def __extract_methods(self, obj_class: object) -> tuple[list[interface.UMLMethod]]:
        """Extract the public methods of a class.
        
        Args:
            obj_class (object): 
                A class type.
        
        Returns:
            list[UMLMethod]: 
                The list of public methods.
        """
        # Get the class attributes
        attributes = dir(obj_class)

        # Create container for public methods
        public_methods: list[interface.UMLMethod] = []
        # Create container for protected methods
        protected_methods: list[interface.UMLMethod] = []
        # Create container for private methods
        private_methods: list[interface.UMLMethod] = []

        # Extract public methods
        for name in attributes:
            obj = getattr(obj_class, name)
            # Check if the attribute is not a method
            if not callable(obj):
                continue
            # Discard built-in methods
            if name.startswith('__') and name.endswith('__'):
                continue
            
            # Designate the fully qualified name of the method
            fqn = f"{self.full_qualname}::{name}"
            # Create a UMLMethod object
            method = self.extractor.extract(obj, self.domain, fqn=fqn)
            # Create a UMLMember object
            member = BaseUMLMember[interface.UMLMethod](name, method)

            # Add the member to container based on the mode
            if member.mode == interface.UMLMemberMode.PUBLIC:
                public_methods.append(member)
            elif member.mode == interface.UMLMemberMode.PROTECTED:
                protected_methods.append(member)
            elif member.mode == interface.UMLMemberMode.PRIVATE:
                private_methods.append(member)
            else:
                raise ValueError("Invalid member mode")

        return public_methods, protected_methods, private_methods
        
    def to_puml(self) -> str:
        """Generate PlantUML code for the class."""
        if self.is_interface:
            class_type = 'Interface'
        else:
            class_type = 'Class'
        attrs = [attr.to_puml() for attr in self.public_attributes]
        attrs += [attr.to_puml() for attr in self.protected_attributes]
        attrs += [attr.to_puml() for attr in self.private_attributes]
        methods = [method.to_puml() for method in self.public_methods]
        methods += [method.to_puml() for method in self.protected_methods]
        methods += [method.to_puml() for method in self.private_methods]
        uml = self.template.format(
            class_type=class_type, 
            name=self.full_qualname, 
            attributes='\n'.join(attrs), 
            methods='\n'.join(methods), 
        )
        return uml


class BaseUMLMethod(BaseUMLSpaceItem, interface.UMLMethod):

    def __init__(
        self, 
        method: callable, 
        space: interface.UMLSpace, 
        extractor: interface.UMLExtractor = None, 
        fqn: str = '', 
        empty: bool = False, 
    ) -> None:
        """Get a method as input and return a UMLMethod object.
        
        Args:
            raw (object): 
                The original object.
            empty (bool):
                The flag to indicate if the item is empty.
            template (str): 
                The template to use for the PlantUML code generation.
            itype (UMLItemType):
                The type of the item.
            space (UMLSpace): 
                The UML space that contains this item.
            domain (str):
                The domain of the item.
            full_qualname (str):
                The full qualified name of the item.
            docstring (str):
                The docstring of the class.
            params (list[UMLClass | UMLMethod | UMLParams]): 
                The list of parameters of the method.
            returns (UMLClass | UMLMethod | UMLParams): 
                The list of return types of the method.
        
        Returns:
            None
        """
        super().__init__(method, interface.UMLItemType.METHOD, space, fqn, empty)
        self.extractor = extractor
        self.docstring = method.__doc__

        if not self.empty:
            params, returns = self.__extract_signatures(method)
            self.params = params
            self.returns = returns      # BUG: Cannot extract return details from tuple
        else:
            self.params = []
            self.returns = None

        # Update the method to the UMLSpace
        self.space.add_item(self)

    def __extract_signatures(self, method: callable) -> tuple[list[T]]:
        """Extract the parameters of a method.
        
        Args:
            method (callable): 
                A method.
        
        Returns:
            list[UMLClass | UMLMethod | UMLParamsContainer]: 
                The list of parameters.
        """
        # Get the parameters of the method
        attributes = method.__annotations__
        
        # Create container for parameters
        params = []
        # Create container for returns
        returns = None
        
        # Extract parameters
        for name, obj in attributes.items():
            # Create a UMLClass object
            param = self.extractor.extract(obj, self.domain)

            # Create a Generic UMLMember object depending on the item type
            if param.itype == interface.UMLItemType.PARAMS:
                member = BaseUMLMember[interface.UMLParams](name, param)
            elif param.itype == interface.UMLItemType.CLASS:
                member = BaseUMLMember[interface.UMLClass](name, param)
            elif param.itype == interface.UMLItemType.METHOD:
                member = BaseUMLMember[interface.UMLMethod](name, param)
            else:
                raise TypeError(f'Unsupported attribute type {type(param)}')
            
            if name == 'return':
                returns = member
            else:
                params.append(member)

            # Check if the parameter is a class or a container
            if param.itype == interface.UMLItemType.PARAMS:
                # Register the relation to the UMLSpace for each argument
                for arg in param.get_all_args():
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        arg.raw.full_qualname, 
                        interface.UMLRelationType.DEPENDENCY, 
                        self.space, 
                    )
                    # Register the relation to the UMLSpace
                    relation.register()
            else:
                if param.itype == interface.UMLItemType.CLASS and not param.is_builtin: 
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        param.full_qualname, 
                        interface.UMLRelationType.DEPENDENCY, 
                        self.space, 
                    )   
                    # Register the relation to the UMLSpace
                    relation.register()
                elif param.itype == interface.UMLItemType.METHOD:
                    relation = BaseUMLRelation(
                        self.full_qualname, 
                        param.full_qualname, 
                        interface.UMLRelationType.DEPENDENCY, 
                        self.space, 
                    )
                    # Register the relation to the UMLSpace
                    relation.register()
        
        return params, returns
    
    def to_puml(self) -> str:
        params = [param.to_puml() for param in self.params]
        returns = [ret.to_puml() for ret in self.returns]
        uml = self.template.format(
            name=self.full_qualname, 
            params='\n'.join([param.to_puml() for param in params]), 
            returns='\n'.join([ret.to_puml() for ret in returns]), 
        )
        return uml


class BaseUMLSpace(interface.UMLSpace):

    def __init__(self, name: str = '', template_path: str = '') -> None:
        """Create a UMLSpace object.
        """
        self.name = name
        if template_path:
            # TODO: Constraint the template_path to be a valid path, and the format to be a 
            # valid PlantUML template.
            with open(template_path, 'r') as f:
                self.template = f.read()
        else:
            self.template = '@startuml\t{name}\n\n{classes}\n\n{relations}\n\n@enduml\n'
        self.classes: dict[str, interface.UMLClass | interface.UMLMethod] = {}
        self.relations = []

    def __contains__(self, key: str) -> bool:
        return key in self.classes.keys()
    
    def __getitem__(self, key: str) -> interface.UMLClass:
        return self.classes[key]

    def add_item(self, obj_class: interface.UMLClass | interface.UMLMethod) -> None:
        """Add a class to the UML object.
        Args:
            obj_class (UMLClass): 
                A UMLClass object.

        Returns:
            None
        
        Raises:
            TypeError: 
                If the input is not a UMLClass or UMLMethod object.
        """
        if not isinstance(obj_class, (interface.UMLClass, interface.UMLMethod)):
            raise TypeError(f'Expected UMLClass or UMLMethod but got {type(obj_class)}')
        self.classes[obj_class.full_qualname] = obj_class

    def add_relation(self, relation: interface.UMLRelation) -> None:
        """Add a relation to the UML object.

        Args:
            relation (UMLRelation): 
                A UMLRelation object.
        
        Returns:
            None
        
        Raises:
            TypeError: 
                If the input is not a UMLRelation object.
        """
        if not isinstance(relation, interface.UMLRelation):
            raise TypeError(f'Expected UMLRelation but got {type(relation)}')
        self.relations.append(relation)

    def to_puml(self) -> str:
        # Clean up the Untracked classes
        classes = [c for c in self.classes.values() if not c.empty]
        # Clean up the Untracked relations
        tracked_relations = []
        for rel in self.relations:
            if rel.source in self.classes.keys() and rel.target in self.classes.keys():
                tracked_relations.append(rel)

        # Generate the PlantUML code
        uml = self.template.format(
            name=self.name,
            classes='\n'.join([c.to_puml() for c in classes]),
            relations='\n'.join([rel.to_puml() for rel in tracked_relations]),
        )
        return uml
    

class BaseExtractor(interface.UMLExtractor):
    """The BaseExtractor class is used to extract UML space items from objects using DFS search.
    
    Attributes:
        space (UMLSpace): 
            The UML space object.
        max_depth (int, optional):
            The maximum depth of recursion. Defaults to 1.
        include_external (bool, optional):
            A flag to indicate whether to include classes from external packages. Defaults to False.
    """
    space: interface.UMLSpace
    max_depth: int
    include_extern: bool 

    def __init__(self, space: interface.UMLSpace, max_depth: int = 1, include_extern: bool = False) -> None:
        self.space = space
        self.max_depth = max_depth
        self.include_extern = include_extern
        self.layer = 0

    def refresh(self) -> None:
        """Refresh the max_depth attribute."""
        self.layer = 0

    def extract(self, obj: type, domain: str, fqn: str = '', empty: bool = False) -> interface.T:
        """Extract a UML space item from the given object.
        
        Args:
            obj (object): 
                The object to extract.
            domain (str):
                The domain of the object.
            fqn (str):
                The fully qualified name of the object. Defaults to an empty string.
            empty (bool):
                A flag to indicate whether the object is empty or not. Defaults to False.
        
        Returns:
            UMLClass | UMLMethod | UMLParams: 
                The extracted UML space item.
        """
        # Update the layer
        self.layer += 1
        # Check if the max_depth is less than 0
        if self.layer > self.max_depth:
            empty = True
        elif not obj.__module__.startswith(domain) and not self.include_extern:
            empty = True
        else:
            empty = False

        # Check if the object is a class
        if inspect.isclass(obj):
            item = self.extract_class(obj, fqn, empty)
        # Check if the object is a function
        elif inspect.isfunction(obj):
            item = self.extract_method(obj, fqn, empty)
        # Check if the object is a Generic/TypeVar or any other parameter container
        elif hasattr(obj, '__args__') or hasattr(obj, '__constraints__'):
            item = self.extract_params(obj, fqn, empty)
        elif hasattr(obj, '__forward_arg__'): 
            pkg = importlib.import_module(domain)
            obj = getattr(pkg, obj.__forward_arg__)
            item = self.extract(obj, domain, fqn, empty)
        # Check if the object is a NoneType
        elif obj is None:
            obj = type(obj)
            item = self.extract(obj, domain, fqn, empty)
        # Check if the object is a string
        elif isinstance(obj, str):
            # Try to import the object from the domain
            pkg = importlib.import_module(domain)
            obj = getattr(pkg, obj)
            item = self.extract(obj, domain, fqn, empty)
        # Unsupported object type
        else:
            raise ValueError(f'Unsupported object type: {type(obj)}')
        # Update the layer
        self.layer -= 1
        return item

        
    def extract_class(self, obj: type, fqn: str = '', empty: bool = False) -> interface.UMLClass:
        """Extract a UMLClass object from the given class.
        
        Args:
            obj (type): 
                The class to extract.
            fqn (str):
                The fully qualified name of the class. Defaults to an empty string.
            empty (bool):
                A flag to indicate whether the class is empty or not. Defaults to False.
        
        Returns:
            UMLClass: 
                The extracted UMLClass object.
        """
        fqn = f"{obj.__module__}.{obj.__qualname__}"
        # Check if the class is already in the list of classes in UMLSpace
        if fqn in self.space and not self.space[fqn].empty:
            # Object Class is already in the UMLSpace and is already tracked
            uml_class = self.space[fqn]
        else:
            # Track the in-package class with max_depth -1
            uml_class = BaseUMLClass(obj, self.space, self, fqn, empty)
        return uml_class
    
    def extract_method(self, obj: type, fqn: str = '', empty: bool = False) -> interface.UMLMethod:
        """Extract a UMLMethod object from the given method.
        
        Args:
            obj (callable): 
                The method to extract.
            fqn (str):
                The fully qualified name of the method. Defaults to an empty string.
            empty (bool):
                A flag to indicate whether the method is empty or not. Defaults to False.
        
        Returns:
            UMLMethod: 
                The extracted UMLMethod object.
        """
        # Check if the method is a class method
        fqn = f"{obj.__module__}.{obj.__qualname__}" if not fqn else fqn
        if "::" in fqn:
            # Extract the class method to an empty uml item. 
            return BaseUMLMethod(obj, self.space, self, fqn, True)
        else:
            # The Method is not a class method\
            # Check if the method is already in the list of classes in UMLSpace
            if fqn in self.space and not self.space[fqn].empty:
                # Object Method is already in the UMLSpace and is already tracked
                uml_method = self.space[fqn]
            else:
                # Track the in-package method with max_depth -1
                uml_method = BaseUMLMethod(obj, self.space, self, fqn, empty)
            return uml_method

    def extract_params(self, obj: type, fqn: str = '', empty: bool = False) -> interface.UMLParams:
        fqn = f"{obj.__module__}.{obj.__name__}" if not fqn else fqn
        # Check if the object is already in the list of classes in UMLSpace
        if fqn in self.space and not self.space[fqn].empty:
            return self.space[fqn]
        else:
            return BaseUMLParams(obj, self.space, self, fqn, empty)
    