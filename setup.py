# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup

v_file = open(os.path.join(os.path.dirname(__file__),
                           'utk', '__init__.py'))
VERSION = re.compile(r".*_version__ = '(.*?)'", re.S)\
            .match(v_file.read()).group(1)

setup(
  name = 'utk',
  version = VERSION,
  author = "Augusto Roccasalva",
  author_email = "augusto@rioplomo.com.ar",
  description = "A console toolkit with gtk api like and urwid render code",
  url = "http://github.com/coyotvz/utk",
  platforms = 'unix-like',
  license = "LGPL",
  packages = ['utk'],
  install_requires = ['gulib'],
)
