import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='language_explorer',
    version='0.2.0',
    description='Explorer Australian aboriginal languages.',
    long_description=(read('README.md')),
    url='https://github.com/edwinsteele/language_explorer',
    license='',
    author='Edwin Steele',
    author_email='edwin@wordspeak.org',
    packages=find_packages(),
    test_suite='tests',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
