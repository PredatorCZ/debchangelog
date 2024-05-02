from setuptools import setup

setup(
    name='dchmerge',
    version='0.1.1',
    description='Merge conflict resolver for debian changelogs',
    author='Lukas Cone',
    url='https://github.com/PredatorCZ/debchangelog',
    scripts=['dchmerge.py', 'deb.py'],
    py_modules=[]
)
