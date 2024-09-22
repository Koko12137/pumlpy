import pumlpy.interface as interface
import pumlpy.impl.base as base


class UMLFactory: 
    """The UMLFactory class is used to create UML objects.
    """

    @ staticmethod
    def create_extractor(
        extractor: str, 
        max_depth: int, 
        include_extern: bool = False, 
        space: interface.UMLSpace = None, 
    ) -> interface.UMLExtractor:
        """Initialize the UMLFactory object.
        
        Args:
            extractor (str): 
                The name of the extractor to use.
            max_depth (int):
                The maximum depth to extract.
            include_extern (bool, optional):
                Whether to include external packages. Defaults to False. 
            space (interface.UMLSpace, optional):
                The space to use. Defaults to None.

        Returns:
            interface.UMLExtractor: 
                The initialized UMLExtractor object.
        
        Raises:
            ValueError: 
                If the extractor is not supported.
        """
        if extractor == 'base':
            space = base.BaseUMLSpace() if space is None else space
            extractor = base.BaseExtractor(space, max_depth, include_extern)
        else:
            raise ValueError(f'Extractor "{extractor}" is not supported.')

        return extractor
    