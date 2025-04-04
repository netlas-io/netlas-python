from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

DEPENDENCIES = open("requirements.txt", "r").read().split("\n")

setup(
    name="netlas",
    version="0.7.2",
    author="Netlas Team",
    author_email="support@netlas.io",
    description="Netlas.io API package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/netlas-io/netlas-python",
    packages=["netlas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["netlas=netlas.__main__:main"]},
    install_requires=DEPENDENCIES,
    keywords=["security", "network"],
    python_requires=">=3.6",
)
