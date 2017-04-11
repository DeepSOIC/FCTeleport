from __future__ import print_function

import sys

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Job(list):
    direction = 0 #-1 for downgrade, +1 for upgrade
    _FreeCAD = None #FreeCAD module (to be used for printing log messages)
    change_counter = 0
    
    def __init__(self, FreeCAD = None):
        self._FreeCAD = FreeCAD
            
    def sortTeleportsByVersion(self):
        self.sort(key= lambda t: (t.for_revision if t.for_revision != -1 else 1000000000000))
        
    def applyTo(self, project):
        if self.direction not in [1, -1]:
            raise ValueError("Job direction is not set, action impossible.")
        self.log("Applying job to project '{project}'".format(project= project.Name))
        if len(self) == 0:
            self.log('Job empty, nothing to do')
            return
        self.log("{n} opeations to do".format(n= len(self)))
        self.change_counter = 0
        for teleport_class in self[::self.direction]:
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
                if teleport.change_counter > 0:
                    self.log('... {num} changes done'.format(num= teleport.change_counter))
                    self.change_counter += teleport.change_counter
                else:
                    self.log('... no changes'.format(num= teleport.change_counter))
            except Exception as err:
                self.log('...failed with an error:')
                self.err(str(err))
        return self.change_counter
        
    def analyze(self, document):
        #returns True if any of teleporters reports that it wants to fix something this FreeCAD document
        return len(self) > 0 #trivial implementation, temporary - for testing
        
    def log(self, string):
        print(string)
    def err(self, string):
        printerr(string)

def makeVersionPortJob(source_revision, target_revision):
    "makeVersionPortJob(source_revision, target_revision): returns job object filled with teleporter classes to convert between these versions"
    import Teleport
    import Teleporters
    
    job = Job()
    job.direction = +1 if target_revision > source_revision else -1
    for t in Teleport.registry.version_teleports:
        if t.for_revision > min(source_revision, target_revision) and t.for_revision <= max(source_revision, target_revision):
            if (job.direction == +1 and hasattr(t, 'upgradeProject')) or (job.direction == -1 and hasattr(t, 'downgradeProject')):
                job.append(t)
    job.sortTeleportsByVersion()
    
    return job

