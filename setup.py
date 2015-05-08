from cx_Freeze import setup, Executable
import sys

sys.path.append('hipies/')

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {'packages': ['hipies'],
                'excludes': ['PyQt', 'PyQt5', 'pyqt', 'collections.sys', 'collections._weakref', 'PyQt4', 'cairo', 'tk',
                             'matplotlib'], 'optimize': 2,
                'include_files': ['hipies/gui/']}
# ,'resources':['hipies/gui/'],'iconfile':'hipies/gui/icon.icns','includes':['PIL']

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('hipies/main.py', base=base, targetName='hipies')
]

setup(name='HiPIES',
      version='0.1',
      description='High Performanc Interactive Environment for Scattering',
      options={'build_exe': buildOptions},
      executables=executables)
