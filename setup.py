# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tokhna_peru/__init__.py
from tokhna_peru import __version__ as version

setup(
	name='tokhna_peru',
	version=version,
	description='Peru localization for ERPNext',
	author='Tokhna',
	author_email='info@tokhna.dev',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
