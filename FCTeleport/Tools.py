def FreeCADVersion():
    'returns version of FreeCAD (tuple of 3 ints)'
    import FreeCAD as App
    major,minor,rev = App.Version()[0:3]
    
    #parse revision string, which looks like "10660 (Git)"
    import re
    match = re.match(r"(\d+).+",rev)
    rev = int(match.groups()[0])
    
    return (major, minor, rev)
    

def convertProject(project_filename, target_version = None, filename_out = None):
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
    
    if filename_out is None:
        import os.path as path
        file,ext = path.splitext(project_filename)
        filename_out = file+"_ported"+str(target_revision)+ext
    project.writeFile(filename_out)
    
    return filename_out

def isConversionRequired(document):
    '''isConversionRequired(document): tests if a conversion will yeild any change for this project 
    
    document: FreeCAD.Document, not FCProject! Its FileName must point to a real file.
    
    Returns tuple(conclusion, job). Conclusion is either False if nothing to do, +1 if upgrade 
    can be done, or -1 if downgrade can be done. Job is a Job object, which contains a list 
    of teleporters to apply, as well as list of features to be affected.'''
    try:
        from . import Job
        from . import FCProject

        project_filename = document.FileName
        target_version = FreeCADVersion()
        target_revision = target_version[2]

        project = FCProject.load(project_filename)
        source_revision = project.program_version[2]
        job = Job.makeVersionPortJob(source_revision, target_revision)
        if job.analyze(project):
            lll = len(job)
            print ("to convert from {source_revision} to {target_revision}: {lll} teleprters".format(**vars()))
            return (job.direction, job)
        else:
            return (False, job)
    except Exception as err:
        import FreeCAD as App
        App.Console.PrintError("FCTeleport: isConversionRequired: {err}\n".format(err= err))
        return (False, None)
