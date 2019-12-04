from setuptools import setup, find_packages

EXTRAS = {}


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='andi_matching',
    version='1.0.0',
    description='ANDi Matching Toolset and Service',
    long_description=read('README.md'),
    extras_require=EXTRAS,
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    author='Pieterjan Montens',
    author_email='pieterjan@montens.net',
)
