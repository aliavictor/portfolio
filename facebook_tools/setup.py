from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='facebook_tools',
      version='0.0.1',
      url='#',
      packages=['facebook_tools'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)