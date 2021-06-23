import setuptools

with open("README.md") as f:
    longdesc = f.read()

setuptools.setup(
    name="nwgh",
    version="0.0.1",
    author="Nicholas Hurley",
    author_email="nwgh@nwgh.org",
    description="A package of utilities for myself",
    long_description=longdesc,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nwgh/nwgh-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Languages :: Python :: 3",
        "License :: OSI Approved :: GPLv3",
        "Operating System :: OS Independent"
    ]
)
