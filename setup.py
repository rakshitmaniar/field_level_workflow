from setuptools import setup, find_packages

setup(
    name="field_level_workflow",
    version="1.0.0",
    description="Field-level conditional workflow execution for Frappe",
    author="Techseria Pvt Ltd",
    author_email="niraj@techseria.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
