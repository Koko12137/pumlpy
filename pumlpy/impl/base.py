'''
File: base.py
Project: impl
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:19:35 pm
Modified By: koko (koko231125@gmail.com>)
'''


from enum import Enum
from abc import ABC, abstractmethod
from typing import Protocol

import pumlpy.interface as ifc 
import pumlpy.rtypes as rtypes 
import pumlpy.utils as utils 


TEMPLATES: dict[str, str] = {
    'class': "{class_type} {name} {{\n{attributes}\n{methods}\n}}", 
    'method': "Class {name} << Method >> {{\n{params}\n{returns}\n}}", 
    'generic': "Class {name} << {raw_type} >> {{\n{args}\n}}", 
    'member': "{mode} {param_uml}", 
    'param': "{hint}: {name}", 
    'relation': "{source} {relation} {target}", 
    'docstring': 'NOTE {docstring} as {alias}', 
    'space': "@startuml\t{name}\n{items}\n{relations}\n@enduml\n", 
}


class UMLTemplate(Enum):
    r"""UMLTemplate enumeration represents the templates used in the PlantUML code generation.

    Attributes:
        CLASS (str): 
            The class template.
        METHOD (str): 
            The method template.
        HINT (str): 
            The hint template.
        MEMBER (str): 
            The member template.
        PARAM (str): 
            The param template.
    """
    CLASS = TEMPLATES['class']
    METHOD = TEMPLATES['method']
    GENERIC = TEMPLATES['generic']
    MEMBER = TEMPLATES['member']
    PARAM = TEMPLATES['param']
    RELATION = TEMPLATES['relation']
    DOCSTRING = TEMPLATES['docstring']
    SPACE = TEMPLATES['space']


class UMLMemberMode(Enum):
    r"""UMLMemberMode enumeration represents the mode of a UML member.

    Attributes:
        PUBLIC (str): 
            The public mode.
        PROTECTED (str): 
            The protected mode.
        PRIVATE (str): 
            The private mode.
    """
    PUBLIC = '+'
    PROTECTED = '#'
    PRIVATE = '-'


class UMLRelationType(Enum):
    r"""UMLRelationType enumeration represents the type of a UML relation.

    Attributes:
        ASSOCIATION (str): 
            The association type.
        AGGREGATION (str): 
            The aggregation type.
        COMPOSITION (str): 
            The composition type.
        INHERITANCE (str): 
            The inheritance type.
        IMPLEMENTATION (str): 
            The implementation type.
        DEPENDENCY (str):
            The dependency type.
        LINK (str):
            The link type.
    """
    ASSOCIATION = '--'
    AGGREGATION = '*-->'
    COMPOSITION = 'o-->'
    INHERITANCE = '--|>'
    IMPLEMENTATION = '..|>'
    DEPENDENCY = '-->'
    LINK = '..'


"""Basic UML Models

Define the basic attributes and methods for UML models.
"""

class BaseUMLItem(ABC, ifc.UMLItem):
    r"""BaseUMLItem protocol concrete implementation represents a UML object that can be converted 
    to PlantUML code. This class is abstract and should not be instantiated directly. 
    
    Attributes:
        template (UMLTemplate): 
            The template to use for the PlantUML code generation.

    Methods:
        to_puml() -> str:
            Return the PlantUML code. 
    """
    template: UMLTemplate

    def __init__(self, template: UMLTemplate) -> None:
        """Create a UMLSpaceItem object. 
        
        Args:
            template (str): 
                The template to use for the PlantUML code generation.

        Returns:
            None. 
        
        Raises: 
            TypeError: 
                If the template is not an instance of UMLTemplate.
        """
        assert isinstance(template, UMLTemplate), TypeError(f"{template} is not a UMLTemplate")
        self.template = template

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError("The `__repr__` method is not implemented")
    
    @abstractmethod
    def to_puml(self) -> str:
        raise NotImplementedError("The `to_puml` method is not implemented")


"""Major UML Models

Include UMLClass, UMLMethod and UMLGeneric. These define the basic object that can be added to 
UMLSpace. Basic object could be included in another basic object after wrapping it with 
UMLObjWrapeer.
"""


class BaseUMLObject(BaseUMLItem, ifc.UMLObject):
    r"""

    Attributes:
        raw (object): 
            The original object. 
        rtype (UMLType): 
            The raw type of the source object.
        domain (str):
            The domain of the source object. For example, `pumlpy.impl.base.model`.
        full_qualname (str):
            The full qualified name of the source object. 
            For example, `pumlpy.impl.base.model.BaseUMLItem`.
        empty (bool):
            The flag to indicate if this item is empty. If True, the item will be ignored when 
            generating PlantUML code.
        docstring (str):
            The docstring of the source object. 
        template_maps (dict[UMLType, UMLTemplate]):
            The mapping between raw types and templates. 

    Methods:
        to_puml() -> str:
            Return the PlantUML code. 
    """
    raw: object
    rtype: rtypes.UMLType
    domain: str
    full_qualname: str
    empty: bool
    docstring: str
    template_maps: dict[rtypes.UMLType, UMLTemplate] = {
        rtypes.UMLType.CLASS: UMLTemplate.CLASS, 
        rtypes.UMLType.ANY: UMLTemplate.CLASS, 
        rtypes.UMLType.NONE: UMLTemplate.CLASS, 
        rtypes.UMLType.METHOD: UMLTemplate.METHOD, 
        rtypes.UMLType.NAMED_GENERIC: UMLTemplate.GENERIC, 
        rtypes.UMLType.TYPES_UNION: UMLTemplate.GENERIC, 
    }

    def __init__(
        self, 
        raw: object, 
        rtype: rtypes.UMLType, 
        empty: bool = False, 
    ) -> None: 
        r"""Create a UMLObject object. 
        
        Args:
            raw (object): 
                The original object.
            rtype (UMLType): 
                The raw type of the source object.
            empty (bool):
                The flag to indicate if this item is empty. If True, the item will be ignored when 
                generating PlantUML code. Defaults to False. 
        
        Returns:
            None.

        Raises:
            NotImplementedError: 
                If the raw type is not supported. 
            TypeError: 
                If the raw type is not an instance of UMLType. 
                If the domain or full qualified name are not strings. 
                If the empty flag is not a boolean. 
            ValueError: 
                If the full qualified name does not start with the domain. 
        """
        super().__init__(template=self.template_maps[rtype])
        self.raw = raw

        # Check if the raw type is UMLType
        assert isinstance(rtype, rtypes.UMLType), TypeError(f"{rtype} is not a UMLType")
        self.rtype = rtype

        # Get the domain and full qualified name of the raw object depending on the raw type
        self.full_qualname = rtypes.get_full_qualname(raw, rtype)
        self.domain = self.full_qualname.split('.')[-1]

        assert isinstance(empty, bool), TypeError(f"{empty} is not a boolean")
        self.empty = empty

        self.docstring = raw.__doc__ if hasattr(raw, '__doc__') else ""


class BaseUMLClass(BaseUMLObject, ifc.UMLClass):
    r"""UMLClass protocol concrete implementation represents a class object that can be converted 
    to PlantUML code.
    
    Attributes:
        is_interface (bool):
            The flag to indicate if the class is an interface.
        ancestors (list[UMLClass, UMLObjectRef]):
            The list of UMLClass or UMLObjectRefs that refer to ancestors of the class. 
        attributes (dict[UMLMemberMode, list[UMLMember]]):
            The dictionary of attributes grouped by their modes.
        methods (dict[UMLMemberMode, list[UMLMember]]):
            The dictionary of methods grouped by their modes. 
        public_attributes (list[UMLMember]):
            The list of public attributes of the class.
        protected_attributes (list[UMLMember]):
            The list of protected attributes of the class.
        private_attributes (list[UMLMember]):
            The list of private attributes of the class.
        public_methods (list[UMLMember]):
            The list of public methods of the class.
        protected_methods (list[UMLMember]):
            The list of protected methods of the class.
        private_methods (list[UMLMember]):
            The list of private methods of the class.
    """
    is_interface: bool
    ancestors: list[ifc.UMLClass, ifc.UMLObjectRef]
    attributes: dict[UMLMemberMode, list[ifc.UMLMember]]
    methods: dict[UMLMemberMode, list[ifc.UMLMember]]
    public_attributes: list[ifc.UMLMember]
    protected_attributes: list[ifc.UMLMember]
    private_attributes: list[ifc.UMLMember]
    public_methods: list[ifc.UMLMember]
    protected_methods: list[ifc.UMLMember]
    private_methods: list[ifc.UMLMember]

    def __init__(
        self, 
        raw: object, 
        rtype: rtypes.UMLType, 
        empty: bool = False, 
        **kwargs,  
    ) -> None:
        r"""Get a class type as input and return a UMLClass object.

        Args:
            raw (object): 
                The original object.
            rtype (UMLType): 
                The raw type of the source object. 
            empty (bool, optional):
                The flag to indicate if this item is empty. If True, the item will be ignored when 
                generating PlantUML code.
            **kwargs (dict[str, list[UMLMember | UMLClass]]):
                The list of ancestors, public attributes, protected attributes, private attributes, 
                public methods, protected methods, and private methods of the class. 

        Returns:
            None 

        Raises:
            TypeError:
                If any of the arguments is not of the correct type. 
        """
        is_builtin = utils.check_builtins(raw)
        # Check if the raw object is a built-in class
        if is_builtin:
            empty = True

        super().__init__(raw=raw, rtype=rtype, empty=empty)
        
        self.is_interface = False
        if rtype != rtypes.UMLType.ANY:
            if not is_builtin:
                # Check if the source object is a protocol.
                self.is_interface = issubclass(raw, Protocol)
                if self.is_interface:
                    self.is_interface = raw._is_protocol
        
        if not self.empty and not is_builtin:
            ancestors = kwargs.get('ancestors', [])
            for ancestor in ancestors:
                if not isinstance(ancestor, ifc.UMLObjectRef) and not isinstance(ancestor, ifc.UMLClass):
                    raise TypeError(f"{ancestor} is not a UMLObjectRef or UMLClass")
            self.ancestors = ancestors

            public_attributes = kwargs.get('public_attributes', [])
            for attribute in public_attributes:
                assert isinstance(attribute, ifc.UMLMember), TypeError(f"{attribute} is not a UMLMember")
                assert attribute.mode == UMLMemberMode.PUBLIC, ValueError(f"{attribute} mode must be PUBLIC")
            self.public_attributes = public_attributes

            protected_attributes = kwargs.get('protected_attributes', [])
            for attribute in protected_attributes:
                assert isinstance(attribute, ifc.UMLMember), TypeError(f"{attribute} is not a UMLMember")
                assert attribute.mode == UMLMemberMode.PROTECTED, ValueError(f"{attribute} mode must be PROTECTED")
            self.protected_attributes = protected_attributes

            private_attributes = kwargs.get('private_attributes', [])
            for attribute in private_attributes:
                assert isinstance(attribute, ifc.UMLMember), TypeError(f"{attribute} is not a UMLMember")
                assert attribute.mode == UMLMemberMode.PRIVATE, ValueError(f"{attribute} mode must be PRIVATE")
            self.private_attributes = private_attributes

            public_methods = kwargs.get('public_methods', [])
            for method in public_methods:
                assert isinstance(method, ifc.UMLMember), TypeError(f"{method} is not a UMLMember")
                assert method.mode == UMLMemberMode.PUBLIC, ValueError(f"{method} mode must be PUBLIC")
            self.public_methods = public_methods

            protected_methods = kwargs.get('protected_methods', [])
            for method in protected_methods:
                assert isinstance(method, ifc.UMLMember), TypeError(f"{method} is not a UMLMember")
                assert method.mode == UMLMemberMode.PROTECTED, ValueError(f"{method} mode must be PROTECTED")
            self.protected_methods = protected_methods

            private_methods = kwargs.get('private_methods', [])
            for method in private_methods:
                assert isinstance(method, ifc.UMLMember), TypeError(f"{method} is not a UMLMember")
                assert method.mode == UMLMemberMode.PRIVATE, ValueError(f"{method} mode must be PRIVATE")
            self.private_methods = private_methods
        else:
            self.ancestors = []
            self.public_attributes = []
            self.protected_attributes = []
            self.private_attributes = []
            self.public_methods = []
            self.protected_methods = []
            self.private_methods = []

        self.attributes = {
            UMLMemberMode.PUBLIC: self.public_attributes, 
            UMLMemberMode.PROTECTED: self.protected_attributes, 
            UMLMemberMode.PRIVATE: self.private_attributes, 
        }
        self.methods = {
            UMLMemberMode.PUBLIC: self.public_methods, 
            UMLMemberMode.PROTECTED: self.protected_methods, 
            UMLMemberMode.PRIVATE: self.private_methods, 
        }

    def __repr__(self):
        return f"BaseUMLClass({self.full_qualname})"
        
    def to_puml(self) -> str:
        r"""Generate PlantUML code for UMLClass instance.
            
        Returns:
            str: 
                The PlantUML code for the class. Example:
                Class pumlpy.impl.base.BaseUMLClass {
                    + str: full_qualname
                    + str: to_puml()
                }
        """
        if self.is_interface:
            class_type = 'Interface'
        else:
            class_type = 'Class'
        
        # Generate attributes PlantUML code
        attrs = []
        for _, attributes in self.attributes.items():
            for attribute in attributes:
                attrs.append(f"\t{attribute.to_puml()}")

        # Generate methods PlantUML code 
        mds = []
        for _, methods in self.methods.items():
            for method in methods:
                mds.append(f"\t{method.to_puml()}")

        uml = self.template.value.format(
            class_type=class_type, 
            name=self.full_qualname, 
            attributes='\n'.join(attrs), 
            methods='\n'.join(mds), 
        )
        return uml


class BaseUMLMethod(BaseUMLObject, ifc.UMLMethod):
    r"""UMLMethod protocol represents a UML method object.
    
    Attributes:
        is_bounded (bool): 
            The flag to indicate if the method is bounded. 
        params (list[UMLParam]): 
            The parameters of the method that wrapped in UMLParam.
        returns (UMLParam): 
            The returns of the method that wrapped in UMLParam.
    """
    is_bounded: bool 
    params: list[ifc.UMLParam]
    returns: ifc.UMLParam

    def __init__(self, raw: callable, empty: bool = False, **kwargs) -> None:
        """Get a method as input and return a UMLMethod object.
        
        Args:
            raw (object): 
                The original object.
            domain (str):
                The domain of the source object. For example, `pumlpy.impl.base.model`.
            full_qualname (str):
                The full qualified name of the source object. 
                For example, `pumlpy.impl.base.model.BaseUMLItem`.
            empty (bool):
                The flag to indicate if this item is empty. If True, the item will be ignored when 
                generating PlantUML code.
            **kwargs (dict[str, UMLParam | list[UMLParam] | tuple[UMLParam]]):
                The parameters and returns of the method. Keyword `params` is a list of UMLParam, 
                and keyword `returns` is a UMLParam object or a tuple of UMLParam objects. Both 
                of them are optional. 
        
        Returns:
            None 

        Raises:
            TypeError:
                If any of the arguments is not of the correct type. 
        """
        super().__init__(raw, rtypes.UMLType.METHOD, empty)

        # Check if the method is bounded
        if '.' in raw.__qualname__:
            self.is_bounded = True
        else:
            self.is_bounded = False
        
        if not self.empty:
            params = kwargs.get('params', [])
            for param in params:
                assert isinstance(param, ifc.UMLParam), TypeError(f"{param} is not a UMLParam")
            self.params = params

            returns = kwargs.get('returns', None)
            if returns is not None:
                assert isinstance(returns, ifc.UMLParam), TypeError(f"{returns} is not a UMLParam")
            self.returns = returns
        else:
            self.params = []
            self.returns = None

    def __repr__(self) -> str:
        return f'BaseUMLMethod({self.full_qualname})'
    
    def to_puml(self) -> str:
        """Generate PlantUML code for UMLMethod instance.
            
        Returns:
            str: 
                The PlantUML code for the method. Example:
                Class pumlpy.utils.check_builtins << Method >> {
                    + object | callable: obj
                    + bool: returns
                }
        """
        params = [f"\t{param.to_puml()}" for param in self.params]
        returns = f"\t{self.returns.to_puml()}"
        uml = self.template.value.format(
            name=self.full_qualname, 
            params='\n'.join([param for param in params]), 
            returns=returns, 
        )
        return uml
    

class BaseUMLGeneric(BaseUMLObject, ifc.UMLGeneric):
    """UMLGeneric protocol concrete implementation represents a type hint object that can be
    converted to PlantUML code. Type hint objects would only be included in a parameter of a 
    method or another type hint object.

    Attributes:
        is_builtin (bool): 
            The flag to indicate if this item is a built-in type. 
        args (list[UMLParam]):
            The arguments of the generic type.
    """
    is_builtin: bool
    args: list[ifc.UMLParam]

    def __init__(self, raw: object, rtype: rtypes.UMLType, empty: bool = False, *args) -> None:
        """Create a UMLGenericType object. 
        
        Args:
            raw (object): 
                The original object.
            rtype (UMLType): 
                The raw type of the source object. 
            empty (bool):
                The flag to indicate if this item is empty. If True, the item will be ignored when 
                generating PlantUML code.
            *args (list[UMLItem]):
                The arguments of the generic type.

        Returns:
            None
        
        Raises:
            TypeError:
                If any of the arguments is not of the correct type. 
        """
        super().__init__(raw, rtype, empty)

        # Check if the generic container is built-in type
        self.is_builtin = utils.check_builtins(raw)
        
        if not self.empty:
            for arg in args:
                assert isinstance(arg, ifc.UMLParam), TypeError(f"{arg} is not a UMLParam")
            self.args = args
        else:
            self.args = []

    def __repr__(self) -> str:
        return f'BaseUMLGeneric({self.full_qualname})'
    
    def to_puml(self) -> str:
        """Generate PlantUML code for UMLGeneric instance.
            
        Returns:
            str: 
                The PlantUML code for the generic. Example:
                Class pumlpy.impl.base.TEMPLATE << dict >> {
                    str: 0 
                    str: 1 
                }
        """
        raw_type = self.full_qualname.split('.')[-1]

        # Generate PlantUML code for the generic arguments
        args = []
        for arg in self.args:
            # arg must be a UMLObject wrapped in a UMLParam, so we need to discard the name
            arg_uml = arg.to_puml()
            arg_uml = ': '.join(arg_uml.split(': ')[:-1])
            args.append(f"\t{arg_uml}")

        uml = self.template.value.format(
            name=self.full_qualname, 
            raw_type=raw_type, 
            args='\n'.join(args), 
        )
        return uml


"""UMLObjWrapper Models

Include UMLParam, UMLMember. These define the wrapper used to override the default template and 
UML code generation for the basic UMLObject. Every UMLObject should be wrapped as a UMLMember 
before injecting it into another UMLClass, as well as a UMLParam in a UMLMethod and UMLGeneric. 
"""


class BaseUMLObjWrapper(BaseUMLItem, ifc.UMLObjWrapper):
    """BaseUMLItemWrapper protocol concrete implementation represents an UML object that included in 
    another UML object. It could be a Parameter in a Method or a Member in a Class. This implementation 
    could be used to override the default template in the UMLItem object, generate PlantUML code and
    can be used to specify the refined UML relations. 

    Attributes:
        template (UMLTemplate): 
            The template to use for the UML code generation. 
            This is used to override the default template in the UMLItem object. 
        hint (UMLObjectRef):
            This could be a UMLObject or a UMLObjectRef. 
            The UMLObjectRef refers to a UMLObject in UMLSpace. 
            The UMLObject is a UMLObject in UMLSpace that included in another UMLObject. 
            It refers to a type hinter indicating the type of the wrapped UMLObject. 
    """
    hint: ifc.UMLObject | ifc.UMLObjectRef

    def __init__(self, hint: ifc.UMLObjectRef, template: UMLTemplate) -> None:
        """Create a UMLDependentItem object."""
        super().__init__(template)
        if not isinstance(hint, ifc.UMLObjectRef) and not isinstance(hint, ifc.UMLObject):
            raise TypeError("hint must be an instance of UMLObject or an instance of UMLObjectRef")
        self.hint = hint

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError("The `__repr__` method is not implemented")

    @abstractmethod
    def to_puml(self) -> str:
        """Generate PlantUML code for Wrapper UMLObject instance.
            
        Returns:
            str: 
                The PlantUML code for the Wrapper UMLObject.
        """
        raise NotImplementedError("The `to_puml` method is not implemented")


class BaseUMLParam(BaseUMLObjWrapper, ifc.UMLParam):
    r"""UMLParam protocol concrete implementation represents a UML object with parameter and type hints 
    that can be converted to PlantUML code. 
    
    Attributes:
        full_qualname (str):
            The full qualified name of the parameter.
    """
    full_qualname: str

    def __init__(self, full_qualname: str, hint: ifc.UMLObject) -> None:
        """Create a UMLParams object. 
        
        Args:   
            full_qualname (str):
                The full qualified name of the member.
            hint (UMLObject):
                The UMLObject that included in the host item. 
                It could be a type hinter indicating the type of the wrapped item.

        Returns:
            None

        Raises:
            TypeError:
                If any of the arguments is not of the correct type.
        """
        super().__init__(hint, UMLTemplate.PARAM)
        assert isinstance(full_qualname, str), TypeError("full_qualname must be a string")
        self.full_qualname = full_qualname
        
    def __repr__(self) -> str:
        return f'BaseUMLParam({self.full_qualname})'
    
    def to_puml(self) -> str:
        """Generate PlantUML code for the UMLObject that wrapped as a UMLParam instance. 
            
        Returns:
            str: 
                The PlantUML code for the UMLParam. Example:
                # UMLClass wrapped in UMLParam
                '    SomeClass: param_name'
                # UMLMethod wrapped in UMLParam
                '    some_func(a: int, b: float): return_type'
                # UMLGeneric wrapped in UMLParam
                '    generic_type[args]: param_name'
        """
        name = self.full_qualname.split('.')[-1]
        name = name.split('::')[-1] 

        # Check if the hint is UMLObject or UMLObjectRef
        hint_obj = None
        if isinstance(self.hint, ifc.UMLObjectRef):
            try: 
                hint_obj = self.hint.get()
            except KeyError:
                return self.template.value.format(hint=self.hint.full_qualname, name=name)
        else:
            hint_obj = self.hint

        # Check the type of the wrapped UMLObject
        if isinstance(hint_obj, ifc.UMLClass):
            hint = self.hint.full_qualname.split('.')[-1]

        elif isinstance(hint_obj, ifc.UMLMethod):
            # Get the signatures of the method
            signatures = []

            # Traverse the signatures of the method
            for sig in hint_obj.params:
                sig_uml = sig.to_puml()
                
                # Revert the order of name and hint in sig_uml
                tmp = sig_uml.split(': ')
                sig_name = tmp.pop(-1)
                sig_hint = ': '.join(tmp) 
                sig_uml = f"{sig_name}: {sig_hint}"
                signatures.append(sig_uml)

            # Get the returns of the method
            ret = hint_obj.returns.to_puml()

            # Compose hint
            if signatures:
                hint = f"{name}({', '.join(signatures)})" 
            else:
                hint = f"{name}()"

            # In case of UMLMethod wrapped in UMLParam, `   func_name(a: int, b: float): ret`
            # Overwrite the name with the return type
            name = ret
            if ": " in name:
                name = ': '.join(name.split(': ')[:-1])
            
        elif isinstance(hint_obj, ifc.UMLGeneric):
            # Get the generic name
            hint_name = hint_obj.full_qualname.split('.')[-1]

            # Get the generic arguments
            args = []
            for arg in hint_obj.args:
                arg_uml = arg.to_puml()

                # Discard the name of the UMLParam
                arg_uml = ': '.join(arg_uml.split(': ')[:-1])

                args.append(f"{arg_uml}")

            if args:
                hint = f"{hint_name}[{', '.join(args)}]"

        return self.template.value.format(hint=hint, name=name)
    

class BaseUMLMember(BaseUMLParam, ifc.UMLMember):
    r"""UMLMember protocol represents a UML member.

    Attributes:
        mode (str): 
            The mode of the member.
    """
    mode: ifc.UMLMemberMode

    def __init__(self, full_qualname: str, hint: ifc.UMLItem) -> None:
        """Create a UMLMember object."""
        super().__init__(full_qualname, hint)

        # Overwrite the template
        self.template = UMLTemplate.MEMBER

        # Infer the mode of the member
        self.mode = self.__infer_mode()

    def __repr__(self) -> str:
        return f'BaseUMLMember({self.full_qualname})'

    def __infer_mode(self) -> ifc.UMLMemberMode:
        # Infer the mode of the member by checking the underlines
        name = self.full_qualname.split('::')[-1]
        if name.startswith('_'):
            if name.startswith('__'):
                return UMLMemberMode.PRIVATE
            else:
                return UMLMemberMode.PROTECTED
        else:
            return UMLMemberMode.PUBLIC

    def to_puml(self) -> str:
        """Generate PlantUML code for the UMLObject that wrapped as a UMLMember instance.
            
        Returns:
            str: 
                The PlantUML code for the UMLMember. Example:
                # UMLClass wrapped in UMLMember
                '    + SomeClass: param_name'
                # UMLMethod wrapped in UMLMember
                '    + return_type: some_func(a: int, b: float)'
                # UMLGeneric wrapped in UMLMember
                '    + generic_type[args]: param_name'
        """
        # Overwrite the template temporarily
        self.template = UMLTemplate.PARAM

        # Get the param uml
        param_uml = super().to_puml()

        # Recover the template
        self.template = UMLTemplate.MEMBER

        return self.template.value.format(mode=self.mode.value, param_uml=param_uml)


"""Base UML Space and Relation Models

"""


class BaseUMLRelation(BaseUMLItem, ifc.UMLRelation):
    r"""UMLRelation protocol represents a UML relation."""
    source: str
    target: str
    relation: ifc.UMLRelationType

    def __init__(
        self, 
        source: str, 
        target: str, 
        relation: ifc.UMLRelationType, 
    ) -> None:
        """Create a UMLRelation object.

        Args:
            source (str): 
                The full qualified name of source class.
            target (str): 
                The full qualified name of target class.
            relation (UMLRelationType): 
                The relation type.
        
        Returns:
            None
        """
        super().__init__(UMLTemplate.RELATION)
        assert isinstance(source, str), TypeError("source must be a string")
        self.source = source
        assert isinstance(target, str), TypeError("target must be a string")
        self.target = target
        self.relation = relation
    
    def __repr__(self) -> str:
        return f'BaseUMLRelation(source={self.source}, target={self.target}, relation={self.relation})'

    def to_puml(self) -> str:
        return self.template.value.format(
            source=self.source, relation=self.relation.value, target=self.target, 
        )


class BaseUMLDocstring(BaseUMLItem, ifc.UMLDocstring):
    r"""UMLDocstring protocol represents a UML docstring."""
    alias: str
    source: ifc.UMLObject
    docstring: str

    def __init__(self, source: ifc.UMLObject, docstring: str, alias: str) -> None:
        """Create a UMLDocString object.

        Args:
            alias (str): 
                The alias of the docstring. 
            source (UMLObject): 
                The source UMLObject of the docstring.
            docstring (str):
                The docstring of the docstring.
        
        Returns:
            None
        """
        super().__init__(UMLTemplate.DOCSTRING)
        self.alias = alias
        self.docstring = docstring
    
    def __repr__(self) -> str:
        return f'BaseUMLDocString({self.alias})'
    
    def __str__(self):
        return self.to_puml()

    def to_puml(self) -> str:
        return self.template.value.format(docstring=self.docstring, alias=self.alias)


class BaseUMLObjectRef(ifc.UMLObjectRef):
    r"""UMLObjectRef protocol represents a reference to a UMLObject.
    
    Attributes:
        full_qualname (str): 
            The full qualified name of the UMLObject. 
        space (UMLSpace): 
            The UMLSpace where the UMLObject is located. 
    """
    full_qualname: str
    space: ifc.UMLSpace

    def __init__(self, full_qualname: str, space: ifc.UMLSpace) -> None:
        r"""Create a UMLObjectRef object.

        Args:
            full_qualname (str): 
                The full qualified name of the UMLObject.
            space (UMLSpace): 
                The UMLSpace where the UMLObject is located. 
        
        Returns:
            None
        """
        assert isinstance(full_qualname, str), TypeError("full_qualname must be a string")
        self.full_qualname = full_qualname
        assert isinstance(space, ifc.UMLSpace), TypeError("space must be a UMLSpace") 
        self.space = space

    def get(self) -> ifc.UMLObject:
        r"""Get the UMLObject from the UMLSpace.

        Returns:
            UMLObject: 
                The UMLObject referenced by this UMLObjectRef. 
        
        Raises:
            KeyError: 
                If the UMLObject is not found in the UMLSpace. 
        """
        if not self.full_qualname in self.space.objs:
            raise KeyError(f"{self.full_qualname} is not found in {self.space}")
        return self.space.objs[self.full_qualname]


class BaseUMLSpace(BaseUMLItem, ifc.UMLSpace):
    r"""UMLSpace protocol represents a UML space.
    
    Attributes:
        name (str): 
            The name of the UML space. 
        limit_fqn (str): 
            The limitation of fully qualified name of the UML space. If provided, the UML space 
            will only contain the items whose fully qualified name starts with the given string 
            and items that are linked directly to the specific items. The relations will not be 
            simplified by the UML space if the limitation is provided. 
        include_docs (bool):
            The flag to indicate if the docstrings should be included in the UML code.
        refs (dict[str, UMLObjectRef]): 
            A dictionary containing all UMLObjectRef in the UML space. 
        objs (dict[str, UMLItem]): 
            A dictionary containing all UMLObject in the UML space.
    """
    name: str
    limit_fqn: str
    include_docs: bool
    refs: dict[str, ifc.UMLObjectRef]
    objs: dict[str, ifc.UMLObject]

    def __init__(
        self, 
        name: str = '', 
        limit_fqn: str = '', 
        include_docs: bool = False, 
        **kwargs, 
    ) -> None:
        """Create a UMLSpace object.

        Args:
            name (str): 
                The name of the UML space. Default is empty string. 
            limit_fqn (str): 
                The limitation of fully qualified name of the UML space. If provided, the UML space 
                will only contain the items whose fully qualified name starts with the given string 
                and items that are linked directly to the specific items. The relations will not be 
                simplified by the UML space if the limitation is provided. Default is empty string. 
            include_docs (bool):
                The flag to indicate if the docstrings should be included in the UML code. Default is False.
        
        Returns:
            None
        """
        super().__init__(UMLTemplate.SPACE)
        self.name = name
        self.limit_fqn = limit_fqn
        self.include_docs = include_docs
        self.refs = {}
        self.objs = {}
    
    def __repr__(self) -> str:
        return f'BaseUMLSpace({self.name})'

    def __contains__(self, key: str) -> bool:
        return key in self.refs.keys()
    
    def __getitem__(self, key: str) -> ifc.UMLObjectRef:
        return self.refs[key]

    def register(self, full_qualname: str) -> ifc.UMLObjectRef:
        """Register an item before adding it to the UML space.

        This is used for avoiding infinite recursion when extracting UMLObjects.

        In UMLSpace, the items are stored in a dictionary with the full qualified name as the key. And 
        there are three states of the items:
            1. Not registered: The item has not been registered yet. 
            2. Registered: The item has been registered but not added to the UML space. 
            3. Added: The item has been added to the UML space. 

        Args:
            full_qualname (str): 
                The full qualified name of the item will be added to the UML space. 

        Returns:
            UMLObjectRef: 
                A UMLObjectRef object referring to the item in the UMLSpace.  
        """
        if full_qualname in self.objs.keys():
            raise KeyError(f'{full_qualname} is already added to the UML space')
        
        # Create a new UMLObjectRef object
        ref = BaseUMLObjectRef(full_qualname, self)
        self.refs[full_qualname] = ref
        return ref

    def add_item(self, item: ifc.UMLObject) -> ifc.UMLObjectRef:
        """Add a class to the UML object.

        Args:
            item (UMLObject): 
                The UMLObject to be added to the UML space. 

        Returns:
            None
        
        Raises:
            TypeError: 
                If the input is not a UMLObject. 
        """
        if not isinstance(item, ifc.UMLObject):
            raise TypeError(f'Expected UMLObject but got {type(item)}') 

        self.objs[item.full_qualname] = item
        
        # Check if the item is already registered
        if item.full_qualname not in self.refs.keys():
            ref = self.register(item.full_qualname)
        else:
            ref = self.refs[item.full_qualname]
        return ref

    def __gen_class_rels(self, obj: ifc.UMLClass) -> list[ifc.UMLRelation]:
        relations: list[ifc.UMLRelation] = []

        # Generate relations for the ancestors
        for ancestor_ref in obj.ancestors:
            # Get the registered instance
            ancestor = None
            if isinstance(ancestor_ref, ifc.UMLObjectRef):
                try:
                    ancestor = ancestor_ref.get()
                except KeyError:
                    continue
            else:
                ancestor = ancestor_ref

            if ancestor.is_interface: 
                rel_type = UMLRelationType.IMPLEMENTATION
            else:
                rel_type = UMLRelationType.INHERITANCE

            relations.append(BaseUMLRelation(
                source=obj.full_qualname, 
                target=ancestor.full_qualname, 
                relation=rel_type,
            ))

        # Generate relations for the attributes
        for attributes in obj.attributes.values():
            for attr in attributes:
                rels = self.__gen_wrapped_rels(attr)
                relations.extend(rels)

        # Generate relations for the methods
        for methods in obj.methods.values():
            for method in methods:
                rels = self.__gen_wrapped_rels(method)
                relations.extend(rels)

        # Converge relations that target was linked to more than twice
        targets: dict[str, list[ifc.UMLRelation]] = {}

        # Traverse the relations
        for rel in relations:
            if rel.target in targets.keys():
                targets[rel.target].append(rel)
            else:
                targets[rel.target] = [rel]

        # Converge relations
        new_rels = []

        for target, rels in targets.items():
            if len(rels) > 1:
                new_rel = BaseUMLRelation(
                    source=obj.full_qualname, 
                    target=target, 
                    relation=UMLRelationType.DEPENDENCY,
                )
                new_rels.append(new_rel)
            else:
                new_rels.extend(rels)

        return relations

    def __gen_method_rels(self, obj: ifc.UMLMethod, source: str = '') -> list[ifc.UMLRelation]:
        relations: list[ifc.UMLRelation] = []

        # Check if source is provided
        if not source: 
            source = obj.full_qualname

        # Check if the method is bounded to a class
        if not obj.is_bounded:
            # Generate relations of the method parameters
            for param in obj.params:
                rels = self.__gen_wrapped_rels(param)
                relations.extend(rels)

            # Generate relations of the method return type
            if obj.returns:
                rels = self.__gen_wrapped_rels(obj.returns)
                relations.extend(rels)
        else:
            if not source:
                raise ValueError("Cannot extract bounded method's UMLRelation without designated source")
            # Generate relations of the method parameters
            for param in obj.params:
                rels = self.__gen_wrapped_rels(param, source)
                relations.extend(rels)

            # Generate relations of the method return type
            if obj.returns:
                rels = self.__gen_wrapped_rels(obj.returns, source)
                relations.extend(rels)

        return relations

    def __gen_generic_rels(self, obj: ifc.UMLGeneric, source: str = '') -> list[ifc.UMLRelation]:
        relations: list[ifc.UMLRelation] = []

        # Check if the generic is a built-in type
        if not obj.is_builtin:
            if not source:
                # Generate relations for the generic arguments
                for arg in obj.args:
                    rels = self.__gen_wrapped_rels(arg, obj.full_qualname)
                    relations.extend(rels)
            else:
                rel = BaseUMLRelation(
                    source=source, 
                    target=obj.full_qualname, 
                    relation=UMLRelationType.DEPENDENCY,
                )
                relations.append(rel)
        else:
            if not source:
                raise ValueError(
                    "Cannot extract built-in type generic's UMLRelation without designated source"
                )
            # Generate relations for the generic arguments
            for arg in obj.args:
                rels = self.__gen_wrapped_rels(arg, source)
                relations.extend(rels)

        return relations

    def __gen_wrapped_rels(
        self, 
        obj: ifc.UMLParam | ifc.UMLMember, 
        source: str = '', 
    ) -> list[ifc.UMLRelation]:
        relations: list[ifc.UMLRelation] = []

        # Check if source is provided
        if not source:
            source = obj.full_qualname

        # Check if the hint is a UMLObject or a UMLObjectRef
        hint_obj = None
        if isinstance(obj.hint, ifc.UMLObjectRef):
            try:
                hint_obj = obj.hint.get()
            except KeyError:
                return relations
        else:
            hint_obj = obj.hint

        # Check the type of the UMLParam hint
        if isinstance(hint_obj, ifc.UMLClass):
            relations.append(BaseUMLRelation(
                source=source, 
                target=obj.hint.full_qualname, 
                relation=UMLRelationType.DEPENDENCY,
            ))

        elif isinstance(hint_obj, ifc.UMLMethod):
            # Check if the method is bounded
            if not hint_obj.is_bounded: 
                # As for the not bounded method, there is a independent instance in the UMLSpace, 
                # and this instance will maintain all the relations that the method has.
                rel = BaseUMLRelation(
                    source=source, 
                    target=obj.hint.full_qualname, 
                    relation=UMLRelationType.DEPENDENCY,
                )
                relations.append(rel)
            else: 
                rels = self.__gen_method_rels(obj.hint, source)
                relations.extend(rels)

        elif isinstance(hint_obj, ifc.UMLGeneric): 
            # Check if the generic is a built-in type
            if hint_obj.is_builtin:
                if not source: 
                    raise ValueError(
                        "Cannot extract built-in type generic's UMLRelation without designated source"
                    ) 

                rels = self.__gen_generic_rels(obj.hint, source)
                relations.extend(rels)
            else: 
                rel = BaseUMLRelation(
                    source=source, 
                    target=obj.hint.full_qualname, 
                    relation=UMLRelationType.DEPENDENCY,
                )
                relations.append(rel)

        return relations

    def gen_relations(self) -> list[ifc.UMLRelation]:
        """Generate relations between UMLObjects in the UMLSpace. 

        Returns: 
            list[UMLRelation]: 
                The list of UMLRelations. 
        
        Raises:
            TypeError: 
                If the traversed object is not a UMLObject.
        """
        relations: list[ifc.UMLRelation] = []
        
        # Traverse the UMLSpace and generate relations
        for obj in self.objs.values():
            # Check the type of the object
            if isinstance(obj, ifc.UMLClass):
                rels = self.__gen_class_rels(obj)
            elif isinstance(obj, ifc.UMLMethod):
                rels = self.__gen_method_rels(obj)
            elif isinstance(obj, ifc.UMLGeneric):
                rels = self.__gen_generic_rels(obj)
            else:
                raise TypeError(f'Unknown object type: {type(obj)}')
                
            relations.extend(rels)
        
        return relations

    def gen_docstring(self) -> list[ifc.UMLDocstring]:
        raise NotImplementedError("The `gen_docstring` method is not implemented")

    def to_puml(self) -> str:
        # Discard empty objects
        self.objs = {k: v for k, v in self.objs.items() if not v.empty}

        # Generate the relations
        relations = self.gen_relations()

        # Discard the relations that are not between UMLObjects in the UMLSpace
        relations = [r for r in relations if r.source in self.objs and r.target in self.objs]

        # Generate the PlantUML code
        uml = self.template.value.format(
            name=self.name,
            items='\n'.join([obj.to_puml() for obj in self.objs.values()]),
            relations='\n'.join([rel.to_puml() for rel in relations]),
        )
        return uml
    