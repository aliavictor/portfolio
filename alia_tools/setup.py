from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='alia_tools',
      version='0.0.2',
      author='Alia Victor',
      author_email='alia.jo.victor@gmail.com',
      url='https://github.com/aliavictor/portfolio/tree/main/alia_toolbox',
      packages=['alia_tools'],
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)