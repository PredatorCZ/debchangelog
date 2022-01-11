from setuptools import setup

setup(
    name='dchmerge',
    version='0.1.0',
    description='Merge conflict resolver for debian changelogs',
    author='Lukas Cone',
    url='https://github.com/PredatorCZ/debchangelog',
    scripts=['dchmerge.py', 'deb.py']
)
