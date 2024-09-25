import types
import typing
from enum import Enum
from typing import Protocol, TypeVar, Generic, runtime_checkable


T = TypeVar('T', 'UMLClass', 'UMLMethod', 'UMLParams')


class UMLItemType(Enum):
    r"""UMLItemType enumeration represents the type of a UML item.

    Attributes:
        CLASS (str): 
            The class type.
        METHOD (str): 
            The method type.
        PARAMS (str): 
            The params type.
    """
    CLASS = 'class'
    METHOD = 'method'
    PARAMS = 'params'


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
    """
    ASSOCIATION = '--'
    AGGREGATION = '*-->'
    COMPOSITION = 'o-->'
    INHERITANCE = '--|>'
    IMPLEMENTATION = '..|>'
    DEPENDENCY = '-->'


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


class UMLParamType(Enum):
    r"""UMLParamType enumeration represents the type of a UML parameter.

    Attributes:
        TYPEVAR (typing.TypeVar): 
            The typevar type.
        TYPING_GENERIC (typing._GenericAlias): 
            The typing generic alias type.
        TYPES_GENERIC (types.GenericAlias): 
            The types generic alias type.
        UNION (types.UnionType):
            The union type.
        TYPING_UNION (typing._UnionGenericAlias):
            The typing union generic alias type.
    """
    TYPEVAR = typing.TypeVar
    TYPING_GENERIC = typing._GenericAlias       # hasattr __origin__
    TYPES_GENERIC = types.GenericAlias          # hasattr __origin__
    UNION = types.UnionType
    TYPING_UNION = typing._UnionGenericAlias    # hasattr __origin__


@runtime_checkable
class UMLItem(Protocol):
    r"""UMLItem protocol represents an object that can be converted to PlantUML code.
    
    Attributes:
        raw (object): The original object.
    """

    raw: object

    def to_puml(self) -> str:
        """Return the PlantUML code.
        """
        pass


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
    """
    source: str
    target: str
    relation: UMLRelationType


@runtime_checkable
class UMLSpaceItem(Protocol):
    r"""UMLSpaceItem protocol represents a UML item in a UML space.
    
    Attributes:
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
        independent (bool):
            The flag to indicate if the object is independent. If True, the object can not be added to the UML space.
    """
    empty: bool
    template: str
    itype: UMLItemType
    space: 'UMLSpace'
    domain: str
    full_qualname: str
    independent: bool


@runtime_checkable
class UMLMember(Generic[T], Protocol):
    r"""UMLMember protocol represents a UML member.

    Attributes:
        name (str):
            The name that excluding domain from Fully qualified name.
        mode (str): 
            The mode of the member.
        raw (UMLClass | UMLMethod | UMLParams):
            The raw object.
    """
    name: str
    mode: UMLMemberMode
    raw: T
    template: str

    def to_puml(self) -> str:
        """Return the PlantUML code.
        """
        pass


@runtime_checkable
class UMLParams(UMLItem, UMLSpaceItem, Protocol):
    r"""UMLParams protocol represents a UML object with parameters and types.
    
    Attributes:
        raw (object): 
            The original object.
        empty (bool):
            The flag to indicate if the item is empty.
        template (str): 
            The template to use for the PlantUML code generation.
        space (UMLSpace): 
            The UML space that contains this item.
        domain (str):
            The domain of the item.
        full_qualname (str):
            The full qualified name of the item.
        independent (bool):
            The flag to indicate if the object is independent. If True, the object can not be added to the UML space.
        ptype (UMLParamType):
            The type of the parameter.
        origin (str):
            The original object containing the parameters.
        member_domain (str):
            The domain of the member.
        args (list[UMLMember]): 
            The list of arguments of raw object.
    """
    ptype: UMLParamType
    origin: object  # TODO: Add the original object indicator
    args: list[UMLMember]

    def get_all_args(self) -> list[UMLMember]:
        """Return all arguments.
        """
        pass


@runtime_checkable
class UMLClass(UMLItem, UMLSpaceItem, Protocol):
    r"""UMLClass protocol represents a UML class object.

    Attributes:
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
        independent (bool):
            The flag to indicate if the object is independent. If True, the object can not be added to the UML space.
        is_interface (bool):
            The flag to indicate if the class is an interface.
        is_builtin (bool):
            The flag to indicate if the class is built-in.
        ancestors (list[UMLMember]):
            The list of ancestors of the class.
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
    docstring: str
    is_interface: bool
    is_builtin: bool

    ancestors: list[UMLMember]
    public_attributes: list[UMLMember]
    protected_attributes: list[UMLMember]
    private_attributes: list[UMLMember]
    public_methods: list[UMLMember]
    protected_methods: list[UMLMember]
    private_methods: list[UMLMember]


@runtime_checkable
class UMLMethod(UMLItem, UMLSpaceItem, Protocol):
    r"""UMLMethod protocol represents a UML method object.
    
    Attributes:
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
        independent (bool):
            The flag to indicate if the object is independent. If True, the object can not be added to the UML space.
        docstring (str):
            The docstring of the class.
        params (list[UMLClass | UMLMethod | UMLParams]): 
            The list of parameters of the method.
        returns (UMLClass | UMLMethod | UMLParams): 
            The list of return types of the method.
    """
    docstring: str
    params: list[UMLMember]
    returns: UMLMember
    

@runtime_checkable
class UMLSpace(Protocol):
    r"""UMLSpace protocol represents a UML space.

    Attributes:
        name (str): 
            The name of the UML space.
        template (str): 
            The template to use for the PlantUML code generation.
        items (dict[str, UMLItem]): 
            A dictionary containing all classes in the UML space.
        relations (list[UMLRelation]): 
            A list of relations between classes.
    """
    name: str
    template: str
    items: dict[str, UMLSpaceItem]
    relations: list[UMLRelation]

    def add_item(self, item: UMLSpaceItem) -> None:
        r"""Add a UMLClass to the UML object.

        Args:
            item (UMLItem): 
                The UMLItem object to add.
        
        Returns:
            None
        
        Raises:
            TypeError:
                If the input is not a UMLItem object.
        """
        pass

    def add_relation(self, relation: UMLRelation) -> None:
        r"""Add a relation to the UML object.

        Args:
            relation (UMLRelation): 
                The UMLRelation object to add.
        
        Returns:
            None

        Raises:
            TypeError:
                If the input is not a UMLRelation object.
        """
        pass

    def to_puml(self) -> str:
        r"""Generate the PlantUML code.

        Returns:
            str:
                The PlantUML code.
        """
        pass


@runtime_checkable
class UMLPackage(Protocol):
    r"""UMLPackage protocol represents a UML package.

    Attributes:
        space (UMLSpace): 
            The UML space of the package.
        name (str): 
            The name of the package.
        domain (str): 
            The domain of the package.
        items (list[UMLClass | UMLMethod | UMLParams]): 
            The list of items in the package.
        packages (list[UMLPackage]): 
            The list of sub-packages in the package.
    """
    space: UMLSpace
    name: str
    domain: str
    items: list[T]
    packages: list['UMLPackage']


@runtime_checkable
class UMLExtractor(Protocol):
    r"""UMLExtractor protocol represents an object that can extract UML items from other objects.
    
    Attributes:
        max_depth (int): 
            The maximum depth to traverse the object graph.
        space (UMLSpace): 
            The UML space to store the extracted items.
        include_extern (bool):
            A flag to indicate whether to include external packages in the UML diagram.
    """

    max_depth: int
    space: UMLSpace
    include_extern: bool

    def refresh(self) -> None:
        r"""Refresh the max_depth attribute."""
        pass

    def extract(self, obj: object, domain: str, fqn: str = '', next_layer: bool = True) -> T:
        r"""Extract a UML space item from the given object.

        Args:
            obj (object): 
                The object to extract.
            domain (str):
                The domain that will restrict the extraction. if the object does not belong 
                to the domain, it will be ignored.
            fqn (str): 
                The fully qualified name of the object. Default is ''.
            next_layer (bool):
                A flag to indicate whether to extract the next layer or not. Default is True.
            
        Returns:
            UMLClass | UMLMethod | UMLParams:
                The extracted UML item.
        """
        pass
