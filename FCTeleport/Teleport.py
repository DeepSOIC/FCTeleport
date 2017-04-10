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
    
    def __init__(self):
        #self._freeze()
        pass
    
    def upgradeProject(self, project):
        "Converts project made in older version to be readable by newer version"
        raise NotImplementedError()
    
    def downgradeProject(self, project):
        "Converts project made in newer version to be readable by older version"
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

class Job(FrozenClass):
    teleport_sequence = []
    direction = 0 #-1 for downgrade, +1 for upgrade
    _FreeCAD = None #FreeCAD module (to be used for printing log messages)
    
    def __init__(self, FreeCAD = None):
        self._freeze()
        self._FreeCAD = FreeCAD
        
    def append(self, teleport_class):
        self.teleport_sequence.append(teleport_class)
    
    def sortTeleportsByVersion(self):
        self.teleport_sequence.sort(key= lambda t: (t.for_revision if t.for_revision != -1 else 1000000000000))
        
    def applyTo(self, project):
        if self.direction not in [1, -1]:
            raise ValueError("Job direction is not set, action impossible.")
        self.log("Applying job to project '{project}'".format(project= project.Name))
        self.log("{n} opeations to do".format(n= len(self.teleport_sequence)))
        for teleport_class in self.teleport_sequence[::self.direction]:
            #create instance
            teleport = teleport_class()
            teleport.job = self
            
            #apply
            self.log("  {action}: {desc}...".format(
                     action= ('upgrading' if self.direction == +1 else 'downgrading'),
                     desc= teleport.brief_description))
            try:
                if self.direction == +1:
                    teleport.upgradeProject(project)
                else:
                    teleport.downgradeProject(project)
                self.log('...done')
            except Exception as err:
                self.log('...failed with an error:')
                self.err(str(err))
                
    def log(self, string):
        print(string)
    def err(self, string):
        printerr(string)

def FreeCADVersion():
    'returns version of FreeCAD (tuple of 3 ints)'
    import FreeCAD as App
    major,minor,rev = App.Version()[0:3]
    
    #parse revision string, which looks like "10660 (Git)"
    import re
    match = re.match(r"(\d+).+",rev)
    rev = int(match.groups()[0])
    
    return (major, minor, rev)
    

def convertProject(project_filename, target_version = None):
    """convertProject(project_filename, target_version = None): upgrades or downgrades a 
    project to specified version of FreeCAD.
    
    project_filename: (string)
    target_version: tuple of three ints: (major, minor, revision). If omitted, FreeCAD is imported and its version is read out."""
    if target_version is None:
        target_version = FreeCADVersion()
    target_revision = target_version[2]
    global registry
    project = FCProject.FCProject()
    project.readFile(project_filename)
    source_revision = project.program_version[2]
    job = Job()
    for t in registry.version_teleports:
        if t.for_revision > min(source_revision, target_revision) and t.for_revision <= max(source_revision, target_revision):
            job.append(t)
    job.sortTeleportsByVersion()
    job.direction = +1 if target_revision > source_revision else -1
    job.applyTo(project)
    
    project.setVersion(target_version, imprint_old= True)
    
    import os.path as path
    file,ext = path.splitext(project_filename)
    filename_out = file+"_ported"+str(target_revision)+ext
    project.writeFile(filename_out)
