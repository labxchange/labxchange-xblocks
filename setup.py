#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package metadata for labxchange_xblocks.
"""
from __future__ import absolute_import, print_function

import os
import re
import sys

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open(path).readlines()
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment, a URL, or an included file
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


VERSION = get_version('labxchange_xblocks', '__init__.py')

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system(u"git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
CHANGELOG = open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst')).read()

setup(
    name='labxchange-xblocks',
    version=VERSION,
    description="""XBlocks for LabXchange.""",
    long_description=README + '\n\n' + CHANGELOG,
    author='OpenCraft',
    author_email='help@opencraft.com',
    url='https://github.com/open-craft/labxchange-xblocks',
    packages=[
        'labxchange_xblocks',
    ],
    package_data=package_data('labxchange_xblocks', ['static', 'public']),
    include_package_data=True,
    install_requires=load_requirements('requirements/base.in'),
    license="AGPL 3.0",
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'xblock.v1': [
            'lx_assignment = labxchange_xblocks.assignment_block:AssignmentBlock',
            'lx_case_study = labxchange_xblocks.case_study_block:CaseStudyBlock',
            'lx_document = labxchange_xblocks.document_block:DocumentBlock',
            'lx_image = labxchange_xblocks.image_block:ImageBlock',
            'lx_simulation = labxchange_xblocks.simulation_block:SimulationBlock',
            'lx_story_in_science = labxchange_xblocks.story_in_science_block:StoryInScienceBlock',
        ]
    },
)
