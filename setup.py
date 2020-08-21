from setuptools import setup, find_packages

from citrus import __version__

setup(
    name='citrus',
    version=__version__,
    packages=find_packages(),
    url='http://github.com/mrmiguez/citrus',
    license='MIT',
    author='Matthew Miguez',
    author_email='r.m.miguez@gmail.com',
    description='Collective Information Transformation and Reconciliation Utility Service',
    long_description=open('README.rst').read() + '\n\n' +
    open('CHANGES.rst').read(),
    platforms='any',
    install_requires=[
        'pymods>=2.0.9',
        'sickle>=0.7.0', 
        'requests'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    test_suite='citrus.tests',
    keywords='oai-pmh metadata digital-libraries',
)
