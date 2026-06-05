# setup.py
# 代码原则：所有代码不许写try静默兜底不报错，有错必须报错。

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="femwa",
    version="1.1.0",
    author="Junyue (求职大模型方向，求内推 QAQ)",
    author_email="jovielher@163.com",
    description="FlowEngineforMinds - 用写剧本的方式编排多智能体世界",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phant0Meow/FlowEngineforMinds-WorldAutomata",
    license="Apache-2.0",
    packages=find_packages(),  # 自动找到 femCompiler, femBridges 等
    py_modules=["main"],       # 根目录下的 main.py
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "fem = main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
