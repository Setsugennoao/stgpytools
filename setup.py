#!/usr/bin/env python3

from pathlib import Path
from typing import cast

import setuptools

package_name = 'stgpytools'

exec(Path(f'{package_name}/_metadata.py').read_text(), meta := cast(dict[str, str], {}))

readme = Path('README.md').read_text()

setuptools.setup(
    name=package_name,
    version=meta['__version__'],
    author=meta['__author_name__'],
    author_email=meta['__author_email__'],
    maintainer=meta['__maintainer_name__'],
    maintainer_email=meta['__maintainer_email__'],
    description=meta['__doc__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    project_urls={
        'Source Code': 'https://github.com/Setsugennoao/stgpytools',
    },
    python_requires='>=3.12',
    packages=[
        package_name,
        f'{package_name}.enums',
        f'{package_name}.exceptions',
        f'{package_name}.functions',
        f'{package_name}.types',
        f'{package_name}.utils'
    ],
    package_data={
        package_name: ['py.typed', 'utils/*.json']
    },
    classifiers=[
        "Natural Language :: English",

        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",

        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ]
)
