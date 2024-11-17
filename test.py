'''
File: test.py
Project: pumlpy
File Created: Sunday, 17th November 2024 1:32:45 pm
Author: koko (koko231125@gmail.com)
License: GPL-3.0
-----
Last Modified: Sunday, 17th November 2024 3:19:27 pm
Modified By: koko (koko231125@gmail.com>)
'''


import pumlpy.api as api


test_example = [
    {
        'path': './pumlpy', 
        'output': './examples/pumlpy.puml', 
        'replace': True, 

    }, 
    {
        'path': './pumlpy', 
        'limit_fqn': 'pumlpy.impl', 
        'output': './examples/pumlpy-impl.puml', 
        'replace': True,
    }
]


def test(**kwargs) -> None: 
    # Create save keyword argument
    save_kwargs = {}
    for key in ['output', 'replace']:
        if key in kwargs:
            save_kwargs[key] = kwargs.pop(key)

    space = api.plantuml(**kwargs)

    # Check if the output argument is present
    if save_kwargs:
        api.space_to_file(space, **save_kwargs)
    else:
        print(space.to_puml())

    print("\n=============================================\n")


if __name__ == '__main__':
    for example in test_example:
        test(**example)
