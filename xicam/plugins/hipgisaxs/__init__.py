import time
from xicam.plugins import base
from PySide import QtGui
import os
from xicam import xglobals

import json
from PySide.QtUiTools import QUiLoader
from PySide import QtGui
from PySide import QtCore
import yaml
from collectionsmod import UnsortableOrderedDict
import ui
import featuremanager
import display
import customwidgets
import numpy as np
from xicam import clientmanager as cmanager
from functools import partial
from xicam import plugins
from pipeline import msg

class plugin(base.plugin):
    name = 'HipGISAXS'

    def __init__(self, *args, **kwargs):

        self.sftp_client = dict()


        self.leftwidget, self.centerwidget, self.rightwidget = ui.load()


        # INIT FORMS
        self.computationForm = None
        self._detectorForm = None
        self._scatteringForm = None


        # SETUP FEATURES
        featuremanager.layout = ui.leftwidget.featuresList
        featuremanager.load()




        # INIT EXPERIMENT
        self.newExperiment()



        # WIREUP CONTROLS
        self.leftwidget.addFeatureButton.clicked.connect(featuremanager.addLayer)
        self.leftwidget.addSubstrateButton.clicked.connect(featuremanager.addSubstrate)
        self.leftwidget.addParticleButton.clicked.connect(featuremanager.addParticle)
        #self.leftwidget.showComputationButton.clicked.connect(self.showComputation)
        self.leftwidget.showDetectorButton.clicked.connect(self.showDetector)
        self.leftwidget.addParticleButton.setMenu(ui.particlemenu)
        self.leftwidget.runLocal.clicked.connect(self.runLocal)
        self.leftwidget.runRemote.clicked.connect(self.runRemote)
        self.leftwidget.runDask.clicked.connect(self.runDask)


        # inject loginwidget
        from xicam.plugins import login
        self.loginwidget=login.LoginDialog()
        self.leftwidget.layout().addWidget(self.loginwidget)


        # SETUP DISPLAY
        display.load()
        display.redraw()
        self.centerwidget.addWidget(display.viewWidget)

        super(plugin, self).__init__(*args, **kwargs)


    def newExperiment(self):
        pass
        # featuremanager.clearFeatures()
        # featuremanager.addSubstrate()
        # featuremanager.addLayer()

    def showFeature(self, index):
        self.showForm(index.internalPointer().form)
        print 'clicked:', index.row(), index.parent().internalPointer()


    def showComputation(self):
        if self.computationForm is None:
            self.computationForm = featuremanager.loadform('gui/guiComputation.ui')
        self.showForm(self.computationForm)

    def showScattering(self):
        self.showForm(self.scatteringForm.form)

    def showDetector(self):
        self.showForm(self.detectorForm.form)

    def showForm(self, form):
        self.rightwidget.addWidget(form)
        self.rightwidget.setCurrentWidget(form)

    @property
    def detectorForm(self):
        if self._detectorForm is None:
            self._detectorForm = customwidgets.detector()
        return self._detectorForm

    @property
    def scatteringForm(self):
        if self._scatteringForm is None:
            self._scatteringForm = customwidgets.scattering()
        return self._scatteringForm

    def genyaml(self):

        shapes = [feature.toDict() for feature in featuremanager.features if type(feature) is customwidgets.particle]
        layers = [feature.toDict() for feature in featuremanager.features if
                  type(feature) in [customwidgets.layer, customwidgets.substrate]]
        unitcells = [feature.structure.toUnitCellDict() for feature in featuremanager.features if
                     type(feature) is customwidgets.particle]
        structures = [feature.structure.toStructureDict() for feature in featuremanager.features if
                      type(feature) is customwidgets.particle]

        out = {'hipGisaxsInput': UnsortableOrderedDict([('version','0.1'),
                                                        ('shapes', shapes),
                                                        ('unitcells', unitcells),
                                                        ('layers', layers),
                                                        ('structures', structures),
                                                        ('computation', self.detectorForm.toDict())])}
        return out

    def writeyaml(self):
        out = self.genyaml()
        # with open('test.json', 'w') as outfile:
        #     json.dump(out, outfile, indent=4)

        with open(os.path.join(os.path.expanduser('~'),'test.yml'), 'w') as outfile:
            yaml.dump(out, outfile, indent=4)

        msg.logMessage(yaml.dump(out, indent=4))

    def runLocal(self):

        self.writeyaml()

        import subprocess
        p=subprocess.Popen(["hipgisaxs", os.path.join(os.path.expanduser('~'),'test.yml')], stdout=subprocess.PIPE)
        stdout,stderr=p.communicate()
        stdout=stdout.replace('\r\r','\r')        # Hack to fix double carriage returns
        out = np.array([np.fromstring(line, sep=' ') for line in stdout.splitlines()])
        #msg.logMessage(stderr.read())
        try:
           plugins.plugins['Viewer'].instance.opendata(out)
        except:
           print "Unable to load data...."
 

        # import os
        #
        # d=os.getcwd()
        # import glob
        # dirs = filter(os.path.isdir, glob.glob(os.path.join(d, "*")))
        # dirs.sort(key=lambda x: os.path.getmtime(x))
        #
        # latestdir=dirs[-1]
        # print 'latestdir',latestdir
        # import glob
        # latestout=glob.glob(os.path.join(latestdir,'*.out'))
        # from xicam import plugins
        # print 'latestout',latestout
        # plugins.plugins['Viewer'].instance.openfiles(latestout)

    def runRemote(self):

        self.writeyaml()

        if len(cmanager.ssh_clients):
            client = cmanager.ssh_clients.values()[0]
            self.loginSuccess(client)
        else:

            add_ssh_callback = lambda client: self.loginSuccess(client)
            login_callback = lambda client: cmanager.add_ssh_client(client.host,
                                                                     client,
                                                                     add_ssh_callback)
            ssh_client = cmanager.ssh_client
            self.loginwidget.loginRequest(partial(cmanager.login, login_callback, ssh_client), True)

    def runDask(self):
        import client.dask_active_executor
        import time

        if client.dask_active_executor.active_executor is None:
            #warning message
            return

        ae = client.dask_active_executor.active_executor.executor

        def hipgisaxs_func(yaml_str):
          import subprocess
          import yaml
          import time
          timestamp =time.strftime("%Y.%m.%d.%H.%M.%S")
          filename = os.path.join(os.path.expanduser('~'),"test_remote.yml")
          
          with open(filename, 'w') as outfile:
             outfile.write(yaml_str)

          a = subprocess.check_output(["srun", "--job-name=hipgisaxs", "--nodes=1", "--ntasks=1", "--ntasks-per-node=1", "--time=00:30:00", "/bin/bash", "/users/course79/rungisaxs.sh", filename])
          return a

        self.writeyaml()

        with open(os.path.join(os.path.expanduser('~'),'test.yml'), 'r') as outfile:
          fx_str = outfile.read()

        future_tag = ae.submit(hipgisaxs_func, fx_str, pure=False)

        import time
        while future_tag.status == "pending":
            print "loading..."
            time.sleep(1)

        if future_tag.status == "failure":
            print "Failed.."
            return

        print "Fetching result please wait"
        result =  future_tag.result()
        out = np.array([np.fromstring(line, sep=' ') for line in result.splitlines()])
        print "result = ", out
        #msg.logMessage(stderr.read())
        try:
          plugins.plugins['Viewer'].instance.opendata(out)
        except:
          print "caught issue.."


    def loginSuccess(self,client):
        self.loginwidget.loginSuccessful(True)
        sftp = client.open_sftp()
        timestamp =time.strftime("%Y.%m.%d.%H.%M.%S")
        sftp.put('test.yml',timestamp+'.yml')
        sftp.close()
        stdin,stdout,stderr = client.exec_command('hipgisaxs/bin/hipgisaxs '+timestamp+'.yml')
        out = np.array([np.fromstring(line,sep=',') for line in stdout.read().splitlines()])
        msg.logMessage(stderr.read())
        plugins.plugins['Viewer'].instance.opendata(out)




class mainwindow():
    def __init__(self, app):
        self.app = app






