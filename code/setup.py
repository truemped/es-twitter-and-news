# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2012 Daniel Truemper <truemped at googlemail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
from setuptools import setup

_tests_require = [
    'mock',
    'pytest',
    'pytest-cov'
]


setup(
    name='newsaggregator',
    version='1.0',

    author='Daniel Truemper',
    author_email='truemped@gmail.com',

    description='',
    packages=['newsaggregator'],

    install_requires=[
        'twython',
        'humanize',
        'delorean',
        'elasticsearch > 1.0.0',
        'Flask',
        'docopt',
    ],

    tests_require=_tests_require,
    extras_require={'test': _tests_require},

    entry_points={
        'console_scripts': [
            'streamer=newsaggregator.streamer:streamer',
            'frontend=newsaggregator.app:run',
        ]
    }
)
