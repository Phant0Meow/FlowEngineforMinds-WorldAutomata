from setuptools import setup

setup(
    name="fem",
    version="1.1.0",
    py_modules=["femCompiler"], 
    entry_points={
        "console_scripts": [
            "fem = femCompiler:main",
        ],
    },
)
