def msgbox(title, text):
    from PySide import QtGui
    mb = QtGui.QMessageBox()
    mb.setIcon(mb.Icon.Information)
    mb.setText(text)
    mb.setWindowTitle(title)
    mb.exec_()
    
def msgError(err):
    from PySide import QtGui
    if type(err) is CancelError: return
    mb = QtGui.QMessageBox()
    mb.setIcon(mb.Icon.Warning)
    mb.setText(err.message)
    if hasattr(err, "title"):
        mb.setWindowTitle(err.title)
    else:
        mb.setWindowTitle("Error")
    mb.exec_()
    
class CancelError(Exception):
    pass

from Show.FrozenClass import FrozenClass
class DelayedExecute(FrozenClass):
    "DelayedExecuter(func, timeout = 30): sets up a timer, executes func, and self-destructs."
    def defineAttributes(self):
        self.func = None # function to run
        self.timer = None # the timer
        self.self = None #self-reference, to keep self alive until timer fires
        self.delay = 0 # not really needed, for convenience/debug
        self.is_done = False

        self._freeze()

    def __init__(self, func, delay= 30):
        self.defineAttributes()
        self.func = func
        self.delay = delay
        from PySide import QtCore
        timer = QtCore.QTimer(); self.timer = timer
        timer.setInterval(delay)
        timer.setSingleShot(True)
        timer.connect(QtCore.SIGNAL("timeout()"), self.timeout)
        timer.start()
        self.self = self
        self.is_done = False
        
    def timeout(self):
        self.timer = None
        self.self = None
        try:
            self.func()
        finally:
            self.is_done = True