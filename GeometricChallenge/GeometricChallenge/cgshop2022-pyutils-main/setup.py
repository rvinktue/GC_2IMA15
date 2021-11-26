"""
This file is internal for creating a proper package.

Build package with `python3 setup.py sdist bdist_wheel`
Upload with `python3 -m twine upload dist/cgshop2022utils-X.X.X-py3-none-any.whl `

"""

import setuptools
from pybind11.setup_helpers import Pybind11Extension


__version__ = "0.4.6"


with open("README.md", "r") as fh:
    long_description = fh.read()

ext_modules = [
    Pybind11Extension('cgshop2022utils.verify.coloring_verifier',
                      ['cgshop2022utils/verify/coloring_verifier.cpp'],
                      define_macros = [('VERSION_INFO', __version__)],
                      include_dirs=['cgshop2022utils/verify'],
                      cxx_std=17)
]

setuptools.setup(
    name="cgshop2022utils",
    version=__version__,
    author="TU Braunschweig, IBR, Algorithms Group (Phillip Keldenich, Rouven Kniep, and Dominik Krupke)",
    author_email="keldenich@ibr.cs.tu-bs.de, krupke@ibr.cs.tu-bs.de",
    description="Utilities for the CG:SHOP 2022 Optimization Competition on Minimum Partition into Plane Subgraphs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2022/",
    packages=[p for p in setuptools.find_packages() if "cgshop2022utils" in p],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.6',
    install_requires=["networkx", "chardet"],
    ext_modules = ext_modules,
    cmdclass={},                  
    zip_safe=False,
    extras_require={'test': {'sympy'}}
)

