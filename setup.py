from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in simpliq/__init__.py
from simpliq import __version__ as version

setup(
	name="simpliq",
	version=version,
	description="ErpNext customization for simpliq v14",
	author="simpliq",
	author_email="info@simpliq.ch",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
