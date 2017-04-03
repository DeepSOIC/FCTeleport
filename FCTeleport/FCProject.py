from .Base.FrozenClass import FrozenClass

import zipfile
from xml.etree import ElementTree

class FCProject(FrozenClass):
    program_version_string = "" # version string, as extracted from main Document tag, usually like "0.17R10000 (Git)"
    program_rev_number = 0 # revision number extracted from version
    document_xml = None #ElementTree object of parsed Document.xml 
    guidocument_xml = None #ElementTree object of parsed GuiDocument.xml
    zip = None #zip file object
    filename = "" 
    
    node_objects = None
    node_objectdata = None
    
    def __init__(self):
        self._freeze()
    
    def readFile(self,filename):
        self.filename = filename
        self.zip = zipfile.ZipFile(filename)
        self.document_xml = ElementTree.parse(self.zip.open('Document.xml'))
        self.guidocument_xml = ElementTree.parse(self.zip.open('GuiDocument.xml'))
        
        self.node_objects = self.document_xml.find('Objects')
        assert(self.node_objects is not None)
        self.node_objectdata = self.document_xml.find('ObjectData')
        assert(self.node_objectdata is not None)
    
    def getObjectsList(self):
        "getObjectsList(): returns list of tuples ('ObjectName', 'Namespace::Type')"
        return [(obj.get('name'), obj.get('type')) for obj in self.node_objects]
    
    def findObjectsOfType(self, type_id):
        "getObjectsOfType(type_id): returns list of object names with type equal to type_id (string). Note that exact comparison is done, isDerivedFrom is not supported"
        objectnodes = self.node_objects.findall('*[@type="{type}"]'.format(type= type_id))
        return [obj.get('name') for obj in objectnodes]
    
    def getObjectPropertiesNodes(self, object_name):
        return self.node_objectdata.findall('Object[@name="{name}"].Properties.Property'.format(name=object_name))
        
    def getObjectPropertiesList(self, object_name):
        propsnodes = self.getObjectPropertiesNodes(object_name)
        return [prop.get('name') for prop in propsnodes]