from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in multi_branch_utility/__init__.py
from multi_branch_utility import __version__ as version

setup(
	name="multi_branch_utility",
	version=version,
	description="Frappe application to support Multi Branch setup in ERPNext",
	author="efeone Pvt. Ltd.",
	author_email="info@efeone.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
