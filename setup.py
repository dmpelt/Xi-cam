"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
import sys
import glob
sys.setrecursionlimit(1500)
from setuptools import setup
from numpy.distutils.core import Extension
import numpy as np
import os

APP = ['main.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True,
           'resources':['gui'],
           'iconfile': 'gui/icon.icns',
           'plist': {
                'CFBundleName': 'HiPIES',
                'CFBundleShortVersionString':'0.1.0', # must be in X.X.X format
                'CFBundleVersion': '0.1.0',
                'CFBundleIdentifier':'com.lbnl.hipies', #optional
                'NSHumanReadableCopyright': '@ 2015', #optional
                'CFBundleDevelopmentRegion': 'English', #optional - English is default
                },
            'includes' : [
                'numpy', 'PySide.QtUiTools.QUiLoader', 'PySide.QtCore', 'PySide.QtGui',
                           'PySide.QtXml'
                         ],
                'packages' : [ 'pipeline', 'daemon', 'hipies' ]
            }

EXT = Extension(name = 'pipeline.cWarpImage',
                sources = ['cext/cWarpImage.cc', 'cext/remesh.cc', 'cext/kdtree2.cpp'],
                extra_compile_args = ['-fopenmp', '-O3', '-ffast-math', '-I/opt/local/include' ],
                extra_link_args  = ['-fopenmp' ]
               )

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS})
