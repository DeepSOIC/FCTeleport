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
    
    from . import Job
    from . import FCProject
    
    if target_version is None:
        target_version = FreeCADVersion()
    target_revision = target_version[2]
    
    project = FCProject.load(project_filename)
    source_revision = project.program_version[2]
    job = Job.makeVersionPortJob(source_revision, target_revision)
    job.applyTo(project)
    project.setVersion(target_version, imprint_old= True)
    
    import os.path as path
    file,ext = path.splitext(project_filename)
    filename_out = file+"_ported"+str(target_revision)+ext
    project.writeFile(filename_out)

