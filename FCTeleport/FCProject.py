from .Base.FrozenClass import FrozenClass

import zipfile
from xml.etree import ElementTree

class FCProject(FrozenClass):
    program_version_string = "" # version string, as extracted from main Document tag, usually like "0.17R10000 (Git)"
    program_version = (0,0,0) # version number extracted from version string, as tuple (major, minor, rev)
    document_xml = None #ElementTree object of parsed Document.xml 
    guidocument_xml = None #ElementTree object of parsed GuiDocument.xml
    zip = None #zip file object
    filename = "" 
    
    node_objects = None
    node_objectdata = None
    
    def __init__(self):
        self._freeze()
    
    def __getattr__(self, attr_name):
        if attr_name == 'Objects':
            return 
        FrozenClass.__getattribute__(self, attr_name)
    
    def readFile(self,filename):
        self.filename = filename
        self.zip = zipfile.ZipFile(filename)
        self.document_xml = ElementTree.parse(self.zip.open('Document.xml'))
        self.guidocument_xml = ElementTree.parse(self.zip.open('GuiDocument.xml'))
        
        self._updateFromXML()
    
    def writeFile(self, filename):
        with zipfile.ZipFile(filename, 'w') as zipout:
            filelist = self.zip.namelist()
            for file in filelist:
                if file == 'Document.xml':
                    zipout.writestr(file, ElementTree.tostring(self.document_xml.getroot(), encoding= 'utf-8'))
                elif file == 'GuiDocument.xml':
                    zipout.writestr(file, ElementTree.tostring(self.guidocument_xml.getroot(), encoding= 'utf-8'))
                else:
                    zipout.writestr(file, self.zip.open(file).read())
    
    def _updateFromXML(self):
        self.node_objects = self.document_xml.find('Objects')
        assert(self.node_objects is not None)
        self.node_objectdata = self.document_xml.find('ObjectData')
        assert(self.node_objectdata is not None)
        
        self.program_version_string = self.document_xml.getroot().get('ProgramVersion')
        
        # parse version string, which typically looks like this: "0.17R8361 (Git)"
        import re
        match = re.match(r"(\d+)\.(\d+)\R(\d+).+",self.program_version_string)
        major,minor,rev = match.groups()
        major = int(major); minor = int(minor); rev = int(rev)
        self.program_version = (major,minor,rev)
    
    def listObjects(self):
        "listObjects(): returns list of tuples ('ObjectName', 'Namespace::Type')"
        return [(obj.get('name'), obj.get('type')) for obj in self.node_objects]
    
    def listObjectsOfType(self, type_id):
        "getObjectsOfType(type_id): returns list of object names with type equal to type_id (string). Note that exact comparison is done, isDerivedFrom is not supported"
        objectnodes = self.node_objects.findall('*[@type="{type}"]'.format(type= type_id))
        return [obj.get('name') for obj in objectnodes]
    
    def findObjects(self, type_id):
        'findObjects(type_id): returns list of App objects by C++ type'
        return [self.getObject(obj_name) for obj_name in self.listObjetsOfType(type_id)]
    
    def getObject(self, object_name):
        object_node = self.node_objects.find('Object[@name="{name}"]'.format(name= object_name))
        if object_node is None:
            raise KeyError("There is no object named {name} in this project".format(name= object_name))
        data_node = self.node_objectdata.find('Object[@name="{name}"]'.format(name= object_name))
        assert(data_node is not None)
        return DocumentObject(object_node, data_node)
    
    def _Objects(self):
        # this is probably somewhat inefficient, but we'll stick with it for a while
        return [self.getObject(object_name) for (object_name, object_type) in self.getObjectsList()]
        
class DocumentObject(FrozenClass):
    datanode = None
    objectnode = None
    Name = ''
    
    def __init__(self, objectnode, datanode):
        self.objectnode = objectnode
        self.datanode = datanode
        self.Name = objectnode.get('name')
        self._freeze()
    
    def __getattr__(self, attr_name):
        if attr_name == 'PropertiesList':
            return self._PropertiesList()
        return getPropertyNode(attr_name)
        
    def getPropertyNode(self, prop_name):
        prop = self.datanode.find('Properties/Property[@name="{propname}"]'.format(propname= prop_name))
        if prop is None:
            raise AttributeError("Object {obj} has no property named '{prop}'".format(obj= self.Name, prop= attr_name))
    
    def typeId(self):
        return self.objectnode.get("type")
    
    def setTypeId(self, new_type_id):
        self.objectnode.set(type, new_type_id)
    
    def getPropertiesNodes(self):
        return self.datanode.findall('Properties/Property')

    def _PropertiesList(self):
        propsnodes = self.getObjectPropertiesNodes()
        return [prop.get('name') for prop in propsnodes]
    
    def renameProperty(self, old_name, new_name):
        node = self.getPropertyNode(old_name)
        node.set('name', new_name)

def dump(node):
    ElementTree.dump(node)