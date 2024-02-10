from setuptools import setup, find_packages

setup(
    name="sesaCanvas",
    version="0.1.9",
    author="Mark Mba Wright",
    author_email="markmw@iastate.edu",
    packages=["sesaCanvas"],
    package_dir={"sesaCanvas": "src"},
    package_data={"sesaCanvas": []},
    install_requires=["igraph", "PyQt6", "biosteam"],
)
