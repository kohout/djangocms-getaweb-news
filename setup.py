import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangocms-getaweb-news',
    version='0.1',
    packages=['djangocms_news'],
    include_package_data=True,
    license='Unlicense',  # example license
    description='A news app for Django CMS 3.0',
    long_description=README,
    url='https://github.com/kohout/djangocms-getaweb-news/',
    author='Christian Kohout',
    author_email='ck@getaweb.at',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
