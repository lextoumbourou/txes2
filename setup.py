from setuptools import setup

setup(
    name='txes',
    version='0.3.7',
    description="Twisted interface to elasticsearch",
    classifiers=[],
    keywords='twisted elasticsearch',
    author='Jason K\xc3\xb6lker',
    author_email='jason@koelker.net',
    url='https://github.com/jkoelker/txes',
    license='BSD License',
    packages=['txes'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "twisted",
        "anyjson"
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
