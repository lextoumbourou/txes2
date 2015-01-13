from setuptools import setup
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements(
    'requirements/main.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='txes2',
    version='0.1.6',
    description="An Elasticsearch client for Twisted",
    keywords='twisted elasticsearch',
    author='Lex Toumbourou',
    author_email='lextoumbourou@gmail.com',
    url='https://github.com/lextoumbourou/txes2',
    license='BSD License',
    packages=['txes2'],
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ]
)
