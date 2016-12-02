from setuptools import setup, find_packages

setup(
    name='pytmpdir',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # this
    # must be the same as the name
    # above
    version='0.1.0',
    description='A class representing a file system directory, that deletes on '
                'garbage collect.',
    author='Synerty',
    author_email='support@synerty.com',
    url='https://github.com/Synerty/pydirectory',
    # use the URL to the github repo
    download_url='https://github.com/Synerty/pydirectory/tarball/0.1.0',
    # I'll explain this in a second
    keywords=['directory', 'scan', 'interrogate', 'create', 'open'],
    # arbitrary keywords
    classifiers=[],
)
