#!/usr/bin/env python
"""setup.py"""

from setuptools import setup, find_packages

setup(
    name='gweetr',
    version='0.0.1',
    packages=find_packages(),

    data_files=[
        ('var/gweetr-instance', ['instance/settings.cfg']),
    ],

    entry_points={
        'console_scripts': [
            'gweetr = gweetr:main',
        ],
    },

    install_requires=['flask', 'flask-sqlalchemy', 'pyechonest', 'rfc3987',
                      'twilio', ],

    author='John A. Barbuto',
    author_email='jbarbuto@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    description=('A Twilio voicemail greeting service '
                 'with songs optionally provided via the Echo Nest API.'),
    long_description=open('README.rst').read(),
    license='MIT',
    platforms=['POSIX'],
    keywords=['twilio', 'voicemail', 'greeting', ],
    url='https://github.com/jbarbuto/gweetr',
)
