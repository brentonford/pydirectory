from distutils.core import setup

setup(
    name='pydirectory',
    packages=['pydirectory'],  # this must be the same as the name above
    version='0.1',
    description='A class representing a file system directory, that deletes on '
                'garbage collect.',
    author='Synerty',
    author_email='jarrod.chesney@synerty.com',
    url='https://github.com/Synerty/pydirectory',
    # use the URL to the github repo
    download_url='https://github.com/Synerty/pydirectory/tarball/0.1',
    # I'll explain this in a second
    keywords=['directory'],  # arbitrary keywords
    classifiers=[],
)
