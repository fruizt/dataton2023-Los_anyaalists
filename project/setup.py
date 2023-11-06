from setuptools import setup, find_namespace_packages

setup(
    name="nyaasolver",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    package_data={"mypkg.files": ["*.*"]},
    install_requires=[
        "numpy",
        "openpyxl",
        "pandas",
        "pulp",
    ],
)
