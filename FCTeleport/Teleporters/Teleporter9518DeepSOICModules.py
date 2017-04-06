from .. import FCProject
from .. import Teleport

class ThisTeleport(Teleport.Teleport):
    for_revision = 9518 # artificial number, to be applied before porting PartDesign Bodies!
    brief_description = "DeepSOIC's C++ Module containers to Bodies"
    def upgradeProject(self, project):
        bb = project.findObjects("Part::BodyBase")
        for b in bb:
            b.setTypeId('PartDesign::Body')
            try:
                b.renameProperty('Model', 'Group')
            except Exception as err:
                self.err("property 'Model' expected but not found")
        # extension can be omitted, FreeCAD seems to deal with it just fine
        

    def downgradeProject(self, project):
        pass
        #(backwards conversion is impossible)

Teleport.registry.registerTeleport(ThisTeleport)