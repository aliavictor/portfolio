from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='google_tools',
      version='0.0.1',
      url='#',
      packages=['google_tools'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)