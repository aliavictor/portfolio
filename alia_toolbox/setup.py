from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='alia_toolbox',
      version='0.0.1',
      url='#',
      packages=['alia_toolbox'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)