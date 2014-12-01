import os

from setuptools import setup
from pip.req import parse_requirements

this_dir = os.path.dirname(os.path.realpath(__file__))
install_reqs = parse_requirements('{}/requirements/main.txt'.format(this_dir))
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='txes2',
    version='0.1.2',
    description="An Elasticsearch client for Twisted",
    classifiers=[],
    keywords='twisted elasticsearch',
    author='Lex Toumbourou',
    author_email='lextoumbourou@gmail.com',
    url='https://github.com/lextoumbourou/txes2',
    license='BSD License',
    packages=['txes2'],
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs
)
