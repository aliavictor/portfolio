from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='bleach_search',
      version='0.0.1',
      author='Alia Victor',
      author_email='alia.jo.victor@gmail.com',
      url='https://github.com/aliavictor/portfolio/tree/master/bleach_search',
      packages=['bleach_search'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)