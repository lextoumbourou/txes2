from setuptools import setup


setup(
    name='txes2',
    version='0.2.3',
    description="An Elasticsearch client for Twisted",
    keywords='twisted elasticsearch',
    author='Lex Toumbourou',
    author_email='lextoumbourou@gmail.com',
    url='https://github.com/lextoumbourou/txes2',
    license='BSD License',
    packages=['txes2'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Twisted', 'anyjson', 'treq'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ]
)
