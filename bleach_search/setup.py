from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='bleach_search',
      version='0.0.1',
      url='#',
      packages=['bleach_search'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)