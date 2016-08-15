import importlib
from pipeline import msg
from PySide import QtGui

def import_module(modname,packagename=None):
    try:
        module=importlib.import_module(modname, packagename)
        msg.logMessage(("Imported", modname), msg.DEBUG)
    except ImportError as ex:
        msg.logMessage('Module could not be loaded: ' + modname)

        missingpackage = ex.message.replace('No module named ', '')

        msgBox = QtGui.QMessageBox()
        msgBox.setText("A python package is missing! Xi-cam can try to install this for you.")
        msgBox.setInformativeText("Would you like to install " + missingpackage + "?")
        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msgBox.setDefaultButton(QtGui.QMessageBox.Yes)

        response = msgBox.exec_()

        if response == QtGui.QMessageBox.Yes:
            import pip

            if not pip.main(['install', '--user', missingpackage]):
                msgBox = QtGui.QMessageBox()
                msgBox.setText('Success! The missing package, ' + missingpackage + ', has been installed!')
                msgBox.setInformativeText('Please restart Xi-cam now.')
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.exec_()
                exit(0)
            else:
                if modname == 'MOTD':
                    from xicam import debugtools
                    debugtools.frustration()
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                        'Sorry, ' + missingpackage + ' could not be installed. This is a Xi-cam critical library.')
                    msgBox.setInformativeText('Xi-cam cannot be loaded . Please install ' + modname + ' manually.')
                    msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                    msgBox.exec_()
                    exit(1)
                else:
                    from xicam import debugtools
                    debugtools.frustration()
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                        'Sorry, ' + missingpackage + ' could not be installed. Try installing this package yourself, or contact the package developer.')
                    msgBox.setInformativeText('Would you like to continue loading Xi-cam?')
                    msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    response = msgBox.exec_()
                    if response == QtGui.QMessageBox.No:
                        exit(1)

        if modname == 'MOTD':
            from xicam import debugtools
            debugtools.frustration()
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
                'Sorry, ' + missingpackage + ' could not be installed. This is a Xi-cam critical library.')
            msgBox.setInformativeText('Xi-cam cannot be loaded . Please install ' + modname + ' manually.')
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.exec_()
            exit(1)

    return module