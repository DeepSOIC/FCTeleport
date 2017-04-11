import FreeCAD as App
from . import Utils

from FCTeleport.Base.FrozenClass import FrozenClass

class Observer(FrozenClass):
    document_status = None # dict. Key = document name, value = 'New' or 'Restoring' or 'Work'
    def reset(self):
        self.document_status = {}
    
    def __init__(self):
        self.reset()
        self._freeze()
        
    def slotCreatedDocument(self,doc): 
        docname = doc.Name
        self.document_status[docname] = 'New'
    
    def slotDeletedDocument(self,doc):
        docname = doc.Name
        self.document_status.pop(docname, None)
    
    def slotCreatedObject(self, feature):
        doc = feature.Document
        docname = doc.Name
        if len(feature.Document.Objects) == 1 and len(doc.FileName)>0 and self.document_status[docname] == 'New':
            # An object was added to a new project, yet the project already has a filename assigned. Most likely, it is restoring.
            self.document_status[docname] = 'Restoring'
            global timer
            timer.start() #polling, waiting for global purge-touched...
            # There is a small chance user had saves a project before adding any objects, and now had just added a new object. This will also trigger this code. No idea how to fix =(.
        elif self.document_status[docname] != 'Restoring':
            self.document_status[docname] = 'Work'
        
    def poll(self):
        busy = False
        for docname in self.document_status:
            if self.document_status[docname] == 'Restoring':
                busy = True
                doc = App.getDocument(docname)
                touched_found = False
                for obj in doc.Objects:
                    if 'Touched' in obj.State:
                        touched_found = True
                if not touched_found:
                    # we are using the global purge of touched to detect that a project has finished loading.
                    self.document_status[docname] = 'Work'
                    self.myslotRestoredDocument(doc)
        if not busy:
            #no projects are still restoring... why is timer still on???
            global timer
            timer.stop()
            
    
    def myslotRestoredDocument(self, doc):
        "Fires when project has finished loading"
        docname = doc.Name
        if len(doc.FileName) > 0:
            from FCTeleport import Tools as TeleTools
            dir = TeleTools.isConversionRequired(doc)
            if dir != False:
                from PySide import QtGui
                mb = QtGui.QMessageBox()
                upgraded = "upgraded" if dir>0 else "downgraded"
                older = "older" if dir>0 else "newer"
                mb.setText("Project {docname} was created in {older} version of FreeCAD, and contains features that can be {upgraded} to current version.".format(**vars()))
                mb.setWindowTitle("FCTeleport")
                btnCancel = mb.addButton(QtGui.QMessageBox.StandardButton.Cancel)
                btnConvertOpen = mb.addButton("Open converted", QtGui.QMessageBox.ButtonRole.ActionRole)
                btnConvertOpen.setToolTip("Converts the project, saves it to a temporary location and opens it in FreeCAD. You need to save the converted file yourself.")
                btnConvertWrite = mb.addButton("Create converted file", QtGui.QMessageBox.ButtonRole.ActionRole)
                btnConvertWrite.setToolTip("Converts the project, saves it next to the original file.")
                mb.setDefaultButton(btnConvertOpen)
                mb.exec_()
                if mb.clickedButton() is btnCancel:
                    return
                if mb.clickedButton() is btnConvertWrite:
                    TeleTools.convertProject(doc.FileName)
                    Utils.msgbox("File converted!")
                if mb.clickedButton() is btnConvertWrite:
                    Utils.msgbox("Not implemented =(")

            

if not "observerInstance" in globals():
    observerInstance = None
else:
    print("observerInstance already present (module reloading...)")
    if isRunning():
        stop()
        start()
        
def start():
    global observerInstance
    if observerInstance is not None:
        return
    observerInstance = Observer()
    App.addDocumentObserver(observerInstance)

    global timer
    from PySide import QtCore
    timer = QtCore.QTimer()
    timer.setInterval(300)
    timer.connect(QtCore.SIGNAL("timeout()"), observerInstance.poll)

def stop():
    global observerInstance
    if observerInstance is None:
        return
    App.removeDocumentObserver(observerInstance)
    observerInstance = None
    
    global timer
    timer.stop()
    timer = None


def isRunning():
    global observerInstance
    return observerInstance is not None
