import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conseilpy",
    version="0.0.2",
    description="Package for blockchain indexer Conseil",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baking-bad/conseilpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
