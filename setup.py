from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import coolcantonese


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = ''
# long_description = read('readme.md')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

install_requires = """
werobot>=0.6.0
beautifulsoup4>=4.3.2
lxml>=3.3.3
redis>=2.10.3
sh>=1.0.8
six>=1.10.0
requests>=2.8.1
logutils>=0.3.3
enum34==1.1.6
"""

setup(
    name='coolcantonese',
    version=coolcantonese.__version__,
    url='http://github.com/kk17/coolcantonese/',
    license='Apache Software License',
    author='Zhike Chan',
    # tests_require=['pytest', 'pytest-cov', 'webtest'],
    # cmdclass={'test': PyTest},
    tests_require=['tox'],
    cmdclass={'test': Tox},
    install_requires=install_requires,
    author_email='zk.chan007@gmail.com',
    description='A wechat robot for learning Cantonese.',
    long_description=long_description,
    packages=['coolcantonese'],
    include_package_data=True,
    platforms='any',
    # test_suite='tests.test_coolcantonese',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: Chinese',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: The MIT License (MIT)',
        'Operating System :: Linux',
        'Topic :: Software Development :: Libraries :: Python Application',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
