from .. import FCProject
from .. import Teleport

class ThisTeleport(Teleport.Teleport):
    for_revision = 9518
    brief_description = "Body ported to use extensions"
    def upgradeProject(self, project):
        bb = project.findObjects("PartDesign::Body")
        for b in bb:
            try:
                b.renameProperty('Model', 'Group')
            except Exception as err:
                self.err("property 'Model' expected but not found")
        # extension can be omitted, FreeCAD seems to deal with it just fine

    def downgradeProject(self, project):
        bb = project.findObjects("PartDesign::Body")
        for b in bb:
            try:
                b.renameProperty('Group', 'Model')
            except Exception as err:
                self.err("property 'Group' expected but not found")
        # extension can be omitted, FreeCAD seems to deal with it just fine

Teleport.registry.registerTeleport(ThisTeleport)