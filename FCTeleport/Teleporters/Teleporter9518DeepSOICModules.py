from .. import FCProject
from .. import Teleport

class ThisTeleport(Teleport.Teleport):
    for_revision = 9518 # artificial number, to be applied before porting PartDesign Bodies!
    commit = None
    brief_description = "DeepSOIC's C++ Module containers removed"
    def upgradeProject(self, project):
        bb = project.findObjects("Part::BodyBase")
        for b in bb:
            b.setTypeId('PartDesign::Body')
            try:
                b.renameProperty('Model', 'Group')
                self.change_counter += 1
            except Exception as err:
                self.err("property 'Model' expected but not found")
        # extension can be omitted, FreeCAD seems to deal with it just fine

    #def downgradeProject(self, project):
        #(backwards conversion is impossible)

    def analyze(self, document, direction):
        if direction == +1:
            bodies = document.findObjects('Part::BodyBase')
            return [body.Name for body in bodies]
        else:
            return []

Teleport.registry.registerTeleport(ThisTeleport)