from __future__ import print_function

from .Base.FrozenClass import FrozenClass
from . import FCProject

import sys

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
class Teleport(FrozenClass):
    "Teleport: base class for commit-specific converters"
    for_revision = -1 #indicates revision number of a breaking-change commit, that this object is to convert. -1 is a signal that the teleport isn't for a commit, but rather is a generic utility.
    brief_description = '' #brief description of the breaking change
    job = None #set by Job.
    change_counter = 0 # number of changes applied to project by action of the teleport. This doesn't have to be an exact number, it is usually tested to find out if teleport did something at all.
    
    def __init__(self):
        #self._freeze()
        pass
    
    # prototype functions! If not implemented -> no conversion necessary
    #def upgradeProject(self, project):
    #    "Converts project made in older version to be readable by newer version"
    #    raise NotImplementedError()
    #
    #def downgradeProject(self, project):
    #    "Converts project made in newer version to be readable by older version"
    #    raise NotImplementedError()
    
    def analyze(self, document):
        "tests if the project opened in FreeCAD should be upgraded/downgraded"
        raise NotImplementedError()
    
    def log(self, string):
        if job is None:
            print(string)
        else:
            self.job.log(string)
    
    def err(self, string):
        if job is None:
            printerr(string)
        else:
            self.job.err(string)
            
class _Registry(FrozenClass):
    'Singleton object that knows all teleports that are available'
    version_teleports = [] # list of teleport types for breaking commits in master
    other_teleports = [] #list of unrelated things that can be done to projects. E.g. file size shrinking utilities
    
    def __init__(self):
        self._freeze()
    
    def registerTeleport(self, teleport_class):
        if teleport_class.for_revision != -1:
            self.version_teleports.append(teleport_class)
        else:
            self.other_teleports.append(teleport_class)
    
    def _purge(self):
        self.version_teleports = [] # list of teleports for breaking commits in master
        self.other_teleports = [] #list of unrelated things that can be done to projects. E.g. file size shrinking utilities
    
registry = _Registry()

