"""
setup.py - Setup skriptu za instalaciju paketa
"""
from setuptools import setup, find_packages

setup(
    name='graph-visualization',
    version='0.1.0',
    description='Interactive graph visualization with multiple views and filters',
    author='Graph Visualization Team',
    packages=find_packages(),
    install_requires=[
        'Django==4.2.7',
        'Pillow==10.1.0',
        'requests==2.31.0',
        'xmltodict==13.0.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'graph-explorer=graph_explorer.manage:main',
        ],
    },
)