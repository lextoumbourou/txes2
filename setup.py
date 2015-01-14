from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

install_reqs = parse_requirements(
    'requirements/main.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='txes2',
    version='0.1.7',
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
