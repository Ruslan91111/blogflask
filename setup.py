from setuptools import find_packages, setup


setup (
    name='blog',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requirements=[
        'flask',
    ],
)

