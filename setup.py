from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="suave_deletes",
    version="0.1.4",
    packages=find_packages(),
    author="Stefan Framework",
    description="A simple soft delete implementation for sqlalchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefanFramework/suave_deletes",
    install_requires=[
        'SQLAlchemy>=2.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)