from setuptools import setup, find_packages

setup(
    name='pytmpdir',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    version='0.1.0',
    description='A class representing a file system directory, that deletes on '
                'garbage collect.',
    author='Synerty',
    author_email='support@synerty.com',
    url='https://github.com/Synerty/pytmpdir',
    download_url='https://github.com/Synerty/pytmpdir/tarball/0.1.0',
    keywords=['directory', 'scan', 'interrogate', 'create', 'open'],
    classifiers=[],
)
