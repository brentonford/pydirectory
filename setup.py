from setuptools import setup, find_packages

package_name = "pytmpdir"
package_version = '0.1.1'

setup(
    name=package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=["sphinx_rtd_theme"],
    version=package_version,
    description='A class representing a file system directory, that deletes on '
                'garbage collect.',
    author='Synerty',
    author_email='support@synerty.com',
    url='https://github.com/Synerty/%s' % package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        package_name, package_version),
    keywords=['directory', 'scan', 'interrogate', 'create', 'open', 'Python', 'Synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
