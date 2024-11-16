from enum import Enum
from typing import Protocol, runtime_checkable, TypeVar, Generic, Union

import pumlpy.rtypes as rtypes


T = TypeVar('T', bound=Union['UMLClass', 'UMLMethod', 'UMLGeneric'])


class UMLTemplate(Enum):
    r"""UMLTemplate enumeration represents the template of a UML diagram.

    Attributes:
        CLASS (str): 
            The template for a UMLClass.
        METHOD (str): 
            The template for a UMMethod.
        GENERIC (str):
            The template for a UMLGeneric. 
        PARAM (str):
            The template for a UMLParam. 
        MEMBER (str):
            The template for a UMLMember. 
        DOCS (str):
            The template for a UMLDocstrings. 
        RELATION (str):
            The template for a UMLRelation. 
        SPACE (str):
            The template for a UMLSpace. 
    """
    CLASS: str 
    METHOD: str 
    GENERIC: str 
    PARAM: str 
    MEMBER: str 
    DOCS: str 
    RELATION: str 
    SPACE: str 


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
    PUBLIC: str
    PROTECTED: str
    PRIVATE: str


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
    ASSOCIATION: str
    AGGREGATION: str
    COMPOSITION: str
    INHERITANCE: str
    IMPLEMENTATION: str
    DEPENDENCY: str
    LINK: str
    

"""Basic UML Models

Define the protocol for all items that can be added to UML Space and can be converted to UML code.
"""


@runtime_checkable
class UMLItem(Protocol):
    r"""UMLItem protocol represents an object that can be converted to UML code. 
    
    Attributes:
        template (UMLTemplate): 
            The template to use for the UML code generation.

    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    template: UMLTemplate

    def to_puml(self) -> str:
        """Return the UML code.

        Returns:
            str:
                The UML code.
        """
        pass


"""Major UML Models

Include UMLClass, UMLMethod and UMLGeneric. These define the basic object that can be added to 
UMLSpace. Basic object could be included in another basic object after wrapping it with 
UMLObjWrapeer.
"""


@runtime_checkable
class UMLObject(UMLItem, Protocol):
    r"""UMLObject protocol represents an object that can be converted to UML code. 
    This protocol should be inherited by all basic UMLObjects for the purpose of unifying the 
    generation of fully qualified name and domain. We recommend that all UML models should 
    implement `__repr__` and `__str__` methods.
    
    Attributes:
        raw (object): 
            The raw object.
        rtype (UMLType):
            The Raw Type of the raw object.
        domain (str):
            The domain of the source object. 
            For example, `pumlpy.interface.model`.
        full_qualname (str):
            The full qualified name of the source object. 
            For example, `pumlpy.interface.model.UMLItem`.
        empty (bool):
            The flag to indicate if this item is empty. If True, the item will be ignored when 
            generating UML code.
        docstring (str):
            The docstring of the source object. 

    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    raw: object
    rtype: rtypes.UMLType
    domain: str
    full_qualname: str
    empty: bool
    docstring: str


@runtime_checkable
class UMLClass(UMLObject, Protocol):
    r"""UMLClass protocol represents a UML class object that can be converted to UML code. 
    An UMLClass contains a series of attributes and methods.

    Attributes:
        is_interface (bool):
            The flag to indicate if the class is an interface.
        ancestors (list[UMLClass | UMLObjectRef]):
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
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    is_interface: bool
    ancestors: list[Union['UMLClass', 'UMLObjectRef']]
    attributes: dict[UMLMemberMode, list['UMLMember']]
    methods: dict[UMLMemberMode, list['UMLMember']]
    public_attributes: list['UMLMember']
    protected_attributes: list['UMLMember']
    private_attributes: list['UMLMember']
    public_methods: list['UMLMember']
    protected_methods: list['UMLMember']
    private_methods: list['UMLMember']


@runtime_checkable
class UMLMethod(UMLObject, Protocol):
    r"""UMLMethod protocol represents a UML method object.
    
    Attributes:
        is_bounded (bool): 
            The flag to indicate if the method is bounded. 
        params (list[UMLParam]): 
            The parameters of the method that wrapped in UMLParam.
        returns (UMLParam): 
            The returns of the method that wrapped in UMLParam.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    is_bounded: bool
    params: list['UMLParam']
    returns: 'UMLParam'


@runtime_checkable
class UMLGeneric(UMLObject, Protocol):
    """UMLGeneric protocol represents a UML type hint object. 
    Type hint objects would only be included in a parameter of a method or another type hint 
    object.

    Attributes:
        is_builtin (bool): 
            The flag to indicate if the generic type container is a built-in type.
        args (list[UMLParam]):
            The arguments of the generic type hint.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    is_builtin: bool
    args: list['UMLParam']


"""UMLObjWrapper Models

Include UMLParam, UMLMember. These define the wrapper used to override the default template and 
UML code generation for the basic UMLObject. Every UMLObject should be wrapped as a UMLMember 
before injecting it into another UMLClass, as well as a UMLParam in a UMLMethod and UMLGeneric. 
"""


@runtime_checkable
class UMLObjWrapper(UMLItem, Protocol):
    """UMLItemWrapper protocol represents an UML object that included in another UML object. 
    It could be a Parameter in a Method or a Member in a Class. This protocol should be 
    used to wrap the UMLItem object and override the default template in the UMLItem object. 

    Attributes:
        template (UMLTemplate): 
            The template to use for the UML code generation.
            This is used to override the default template in the UMLItem object. 
        hint (UMLObject | UMLObjectRef):
            This could be a UMLObject or a UMLObjectRef. 
            The UMLObjectRef refers to a UMLObject in UMLSpace. 
            The UMLObject is a UMLObject in UMLSpace that included in another UMLObject. 
            It refers to a type hinter indicating the type of the wrapped UMLObject. 
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    hint: Union[UMLObject, 'UMLObjectRef']


@runtime_checkable
class UMLParam(UMLObjWrapper, Protocol):
    r"""UMLParam protocol represents a UML object with parameter and type hints.
    
    Attributes:
        full_qualname (str):
            The full qualified name of the member. It should be designated by the host item.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    full_qualname: str


@runtime_checkable
class UMLMember(UMLParam, Protocol):
    r"""UMLMember protocol represents a UML member.

    Attributes:
        mode (str): 
            The mode of the member.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    mode: UMLMemberMode


"""UML Space Models

"""


@runtime_checkable
class UMLRelation(UMLItem, Protocol):
    r"""A UML relation Protocol.
    
    Attributes:
        source (str): 
            The source class of the relation.
        target (str):
            The target class of the relation.
        relation (UMLRelationType): 
            The type of the relation.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    source: str
    target: str
    relation: UMLRelationType


@runtime_checkable
class UMLDocstring(UMLItem, Protocol):
    r"""A UML docstring Protocol.

    Attributes:
        alias (str): 
            The alias of the docstring. 
        source (UMLObject): 
            The source UMLObject of the docstring.
        docstring (str):
            The docstring of the docstring.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    alias: str
    source: UMLObject
    docstring: str 


@runtime_checkable
class UMLObjectRef(Protocol):
    r"""UMLObjectRef protocol represents a reference to a UMLObject.
    
    Attributes:
        full_qualname (str): 
            The full qualified name of the UMLObject. 
        space (UMLSpace): 
            The UMLSpace where the UMLObject is located. 
    """
    full_qualname: str
    space: 'UMLSpace'

    def get(self) -> UMLObject:
        pass
    

@runtime_checkable
class UMLSpace(UMLItem, Protocol):
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
            A dictionary containing all references to the UML objects in the UML space.  
        objs (dict[str, UMLObject]): 
            A dictionary containing all classes in the UML space.
            
    Methods:
        to_puml() -> str:
            Return the UML code. 
    """
    template: UMLTemplate 
    name: str
    limit_fqn: str
    include_docs: bool
    refs: dict[str, UMLObjectRef]
    objs: dict[str, UMLObject]

    def register(self, full_qualname: str) -> UMLObjectRef:
        r"""Register a UMLObject Reference to the UMLSpace. This is used to register a 
        not added UMLObject to the UMLSpace. 

        Args:
            full_qualname (str): 
                The full qualified name of the UMLObject. 
                
        Returns:
            UMLObjectRef:
                The reference to the registered UMLObject. 
        """
        pass

    def add_item(self, item: UMLObject) -> UMLObjectRef:
        r"""Add a UMLObject to the UMLSpace.

        Args:
            item (UMLObject): 
                The UMLObject to add. 
        
        Returns:
            UMLObjectRef:
                The reference to the added UMLObject. 
        
        Raises:
            TypeError:
                If the input is not a UMLItem object.
        """
        pass

    def gen_relations(self) -> list[UMLRelation]:
        r"""Generate the relations for all the UMLItems in the UMLSpace.

        Returns:
            list[UMLRelation]:
                The list of relations.
        """
        pass

    def gen_docstring(self) -> list[UMLDocstring]:
        r"""Generate the docstrings for all the UMLObject in the UMLSpace. 
        This should be called before generating the UML Relations, otherwise, the docstrings 
        will be generated without relations to the UMLObject.

        Returns:
            list[UMLDocstring]:
                The list of docstrings.
        """
        pass
