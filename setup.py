from os import path
from setuptools import setup, find_packages


this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name="pumlpy",
    version="0.0.1",
    author="koko",
    author_email="koko231125@gmail.com",
    description="A plantuml code extractor.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Koko12137/pumlpy",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.1", 
    ],
    entry_points={
        'console_scripts': [
            'pumlpy = cli:plantuml', 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent", 
    ],
    python_requires='>=3.11', 
    license="GNU General Public License v3",
    keywords=["pumlpy", "plantuml", "python", "uml"],
)
