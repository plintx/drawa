#!/usr/bin/env python3
from setuptools.command.install import install
from setuptools import setup, find_packages
import subprocess
import os


class CustomInstallCommand(install):

  def run(self):
    install.run(self)
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    create_service_script_path = os.path.join(current_dir_path, 'systemd', 'create_service.sh')
    subprocess.check_output([create_service_script_path])

setup(name='drawa',
      description='Drawa is a Download Manager & a GUI for aria2 with built-in Chomikuj.pl support. ',
      long_description="",
      version='0.1.0',
      url='https://github.com/blackberrymamba/drawa',
      author='blackberrymamba',
      author_email='mariusz@typedef.pl',
      license='Apache License, Version 2.0',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3'
      ],
      packages=['drawa','drawa.app'],
      install_requires=[
          'flask>=0.12.2',
          'requests>=2.18.4',
          'pluggy>=0.6.0'
      ],
      entry_points={
          'console_scripts': [
              'drawa=drawa.__main__:main'
          ]
      },
      cmdclass={'install': CustomInstallCommand},
      include_package_data = True
)
