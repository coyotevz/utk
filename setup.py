# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup

def find_packages(library_name):
    try:
        from setuptools import find_packages
        return find_packages()
    except ImportError:
        pass
    packages = []
    for directory, subdirectories, files in os.walk(library_name):
        if "__init__.py" in files:
            packages.append(directory.replace(os.sep, "."))
    return packages

v_file = open(os.path.join(os.path.dirname(__file__),
                           'utk', '__init__.py'))
VERSION = re.compile(r".*_version__ = '(.*?)'", r.S)\
            .match(v_file.read()).group(1)

setup(
  name = 'utk',
  version = VERSION,
  author = "Augusto Roccasalva",
  author_email = "augusto@rioplomo.com.ar",
  description = "A console toolkit with gtk api like and urwid render code",
  url = "http://github.com/coyotvz/utk",
  license = "LGPL",
  packages = find_packages('utk'),
  install_requires = ['pygtk'],
)
