'''
File: factory.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:20:10 pm
Modified By: koko (koko231125@gmail.com>)
'''


import pumlpy.interface as ifc
import pumlpy.impl.base as base
import pumlpy.extractor as ext


class BaseUMLFactory: 
    """The UMLFactory class is used to create UML objects.

    Attributes:
        valid_extractors (dict[str, Extractor]): 
            A dictionary mapping extractor names to their corresponding classes.
        valid_spaces (dict[str, UMLSpace]): 
            A dictionary mapping space names to their corresponding classes.
    """
    valid_extractors: dict[str, ext.Extractor]
    valid_spaces: dict[str, ifc.UMLSpace]

    def __init__(self, **kwargs) -> None:
        """Initialize the UMLFactory object.
        
        Returns: 
            None 
        """ 
        # Initialize the valid_extractors and valid_space dictionaries
        self.valid_extractors = {}
        self.valid_spaces = {}

        # Set default extractor and space
        self.valid_extractors['BaseExtractor'] = ext.BaseExtractor
        self.valid_spaces['BaseUMLSpace'] = base.BaseUMLSpace

        # Overwrite the default values with the given keyword arguments
        if 'extractor' in kwargs:
            extractor = kwargs['extractor']
            assert issubclass(extractor, ext.Extractor), "Invalid Extractor class."
            self.valid_extractors[extractor.__name__] = extractor
        if 'space' in kwargs:
            space = kwargs['space']
            assert issubclass(space, ifc.UMLSpace), "Invalid Space class."
            self.valid_spaces[space.__name__] = space

    def create_extractor(
        self, 
        domain:str, 
        limit_fqn: str = '', 
        max_depth: int = 3, 
        include_extern: bool = False, 
        extractor: str = 'BaseExtractor', 
        **kwargs
    ) -> ext.Extractor: 
        """Initialize the UMLFactory object.
        
        Args: 
            domain (str):
                The domain to be extracted. 
            limit_fqn (str): 
                The fully qualified name of the root element to be extracted.
            max_depth (int): 
                The maximum depth for the extraction process. Defaults to 10.
            include_extern (bool): 
                Whether or not to include extern definitions. Defaults to False.
            **kwargs: 
                Additional keyword arguments passed to the extractor constructor. 

        Returns:
            UMLExtractor: 
                The initialized UMLExtractor object.
        """
        extractor: ext.Extractor = self.valid_extractors[extractor]
        return extractor(domain, limit_fqn, max_depth, include_extern, **kwargs)
    
    def create_space(
        self, 
        name: str, 
        limit_fqn: str = '', 
        include_docs: bool = False, 
        space: str = "BaseUMLSpace", 
        **kwargs
        ) -> ifc.UMLSpace:
        """Create a UML space object.
        
        Args: 
            name (str): 
                The name of the space.
            limit_fqn (str): 
                The fully qualified name of the limit element to be extracted. 
            include_docs (bool): 
                Whether or not to include docstrings. 
            include_extern (bool): 
                Whether or not to include extern definitions. 
        
        Returns:
            interface.UMLSpace: 
                The UML space object. 
        """
        space: ifc.UMLSpace = self.valid_spaces[space]
        return space(name, limit_fqn, include_docs, **kwargs)
    