'''
File: cli.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:31:07 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:18:59 pm
Modified By: koko (koko231125@gmail.com>)
'''


import os
import click

import pumlpy.api as api


@click.command()
@click.argument('path', type=str)
@click.option('--output', type=click.Path(), default=None, help='The path to the output file.')
@click.option('--replace', is_flag=True, help='Whether to replace the output file if it already exists.') 
@click.option('--limit-fqn', type=str, default='', help='The fully qualified name of the root element to be extracted.')
@click.option('--include-extern', is_flag=True, help='Whether or not to include extern definitions.') 
@click.option('--include-docs', is_flag=True, help='Whether to include docstring for each object.') 
@click.option('--max-depth', type=int, default=3, help='The maximum depth of the package hierarchy to be processed.')
def plantuml(
    path: str, 
    output: str = None, 
    replace: bool = False, 
    limit_fqn: str = '', 
    include_extern: bool = False, 
    include_docs: bool = False, 
    max_depth: int = 3, 
) -> None:
    """Entry point for the command-line interface. This will extract the package hierarchy from the given path and 
    generate PlantUML code that can be used to generate a diagram. 

    \b
    Args:
        path (str): 
            The path to the package or folder to be processed.
        output (str, optional): 
            The path to the output file. Defaults to None. 
        replace (bool):
            Whether to replace the output file if it already exists. Defaults to False. 
        limit_fqn (str, optional): 
            The fully qualified name of the root element to be extracted. Defaults to ''. 
        include_extern (bool, optional): 
            Whether or not to include extern definitions. Defaults to False. 
        include_docs (bool, optional): 
            Whether to include docstring for each object. Defaults to False. 
        max_depth (int): 
            The maximum depth of the package hierarchy to be processed.

    \b
    Returns:
        None
    
    \b
    Raises:
        ValueError: 
            If the output file already exists and replace is False. 
    """
    if output:
        # Check if the output file exists
        if os.path.exists(output): 
            if not replace:
                # Raise an error if the output file exists
                raise ValueError(f'The output file "{output}" already exists.')
            else:
                # Remove the output file if it exists
                os.remove(output) 
    
    uml = api.plantuml(path, limit_fqn, include_extern, include_docs, max_depth)

    if output:
        with open(output, 'w') as file:
            file.write(uml.to_puml())
    else:
        print(uml.to_puml())
