from setuptools import setup

import os.path
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    sys.exit()


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', read('gspread/__init__.py'), re.MULTILINE).group(1)

setup(
      name="godm",
      version=version,
      description="Data Object Model for Google Sheet",
      url="https://github.com/devendrapratap02/g-odm",
      author="Devendra Pratap Singh",
      author_email="dps.manit@gmail.com",
      keywords=["spreadsheets", "google-spreadsheets", "object-data-model"],
      install_requires=[
          "gspread>=0.6.2", "oauth2client>=1.5.2"
      ],
      python_requires=">=3.4",
      license="MIT",
      packages=["godm"],
      zip_safe=False
)
