import os
import click

from pumlpy.factory import UMLFactory


@click.command()
@click.argument('path', type=click.Path(exists=True), description='The path to the package or folder to be processed.')
@click.option('--module', type=str, default=None, help='The name of the module to be processed, if None, the package will be processed.')
@click.option('--output', type=click.Path(), default=None, help='The path to the output file.')
@click.option('--max-depth', type=int, default=1, help='The maximum depth of the package hierarchy to be processed.')
def main(
    path: str, 
    module: str = None, 
    output: str = None, 
    max_depth: int = 1, 
    ) -> None:
    """Entry point for the command-line interface.

    Args:
        path (str): 
            The path to the package or folder to be processed.
        module (str):
            The name of the module to be processed, if None, the package will be processed.
        output (str): 
            The path to the output file.
        max_depth (int): 
            The maximum depth of the package hierarchy to be processed.
    
    Returns:
        None
    
    Raises:
        ValueError: 
            If the output file already exists.
    """
    if output:
        # Check if the output file exists
        if os.path.exists(output):
            # Raise an error if the output file exists
            raise ValueError(f'The output file "{output}" already exists.')
    
    uml_factory = UMLFactory()
    uml = uml_factory.create_uml(path, module, max_depth)

    if output:
        with open(output, 'w') as file:
            file.write(uml.to_puml())
    else:
        print(uml.to_puml())

    print('Processing completed.')
