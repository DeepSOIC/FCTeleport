from .. import FCProject
from .. import Teleport

class ThisTeleport(Teleport.Teleport):
    for_revision = 9518
    brief_description = "Body ported to use extensions"
    def upgradeProject(self, project):
        bb = project.findObjects("PartDesign::Body")
        for b in bb:
            b.renameProperty('Model', 'Group')
        # extension can be omitted, FreeCAD seems to deal with it just fine

    def downgradeProject(self, project):
        bb = project.findObjects("PartDesign::Body")
        for b in bb:
            b.renameProperty('Group', 'Model')
        # extension can be omitted, FreeCAD seems to deal with it just fine

Teleport.registry.registerTeleport(ThisTeleport)