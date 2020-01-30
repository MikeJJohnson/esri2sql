import json
import requests
import io
import xml.etree.ElementTree as ET
import re
import sys

def getXml(url, cookie = False, values = False, username=False, password=False):

    if (username and password and values):
        r = requests.post(url, data=values, auth=(username, password))
    elif (username and password):
        r = requests.get(url, auth=(username, password))
    elif (cookie and values):
        r = requests.post(url, data=values, cookies=cookie)
    else:
        r = requests.get(url)

    with open('working.xml', 'wb') as f: 
        f.write(r.content) 

    xml = ET.parse('working.xml')

    return xml

def yearToB2K(year):
    return 2000+(int(year)*-1)

namespaces = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'wfs':'http://www.opengis.net/wfs',
        'gml':"http://www.opengis.net/gml",
        'SIG_chronique':"SIG_chronique#",
        'skos':"http://www.w3.org/2004/02/skos/core#",
        'geo':"http://www.w3.org/2003/01/geo/wgs84_pos#",
        'acdm':"http://schemas.cloud.dcu.gr/ariadne-registry/",
        'dc':"http://purl.org/dc/elements/1.1/",
        'oai':"http://www.openarchives.org/OAI/2.0/",
        'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/",
        'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        'esri':"http://www.esri.com/schemas/ArcGIS/10.3",
        'xsi':"http://www.w3.org/2001/XMLSchema-instance",
        'xs':"http://www.w3.org/2001/XMLSchema"
        }

class sqlTable:
    name = 'noname'
    fields = []

    def __init__(self, name):
        self.name = name
        self.fields = []

    def addField(self, name, type):
        field = {
            'name':start,
            'type':end,
        }
        self.fields.append(field)

    def setName(self, name):
        # removes everything after the last "" - ""
        # name = name[:name.rfind(" - ")]
        self.name = name.title()

class esriDomain:
    name = 'noname'
    codedValues = []

    def __init__(self, name):
        self.name = name
        self.codedValues = []

    def addCodedValue(self, name, code):
        codedValue = {
            'name':name,
            'code':code,
        }
        self.codedValues.append(codedValue)

    def setName(self, name):
        # removes everything after the last "" - ""
        # name = name[:name.rfind(" - ")]
        self.name = name.title()

def convertField(field):
    sql = ''

    name = field.find('Name', namespaces).text
    fieldtype = field.find('Type', namespaces).text

    if fieldtype == 'esriFieldTypeString':
        length = field.find('Length').text
        sql = name+' VARCHAR ('+length+')'

    elif fieldtype == 'esriFieldTypeGeometry':
        geomtype = field.find('GeometryDef/GeometryType').text
        if geomtype == 'esriGeometryPolygon':
            sql = name + ' geometry(polygon,27700)'
        elif geomtype == 'esriGeometryPolyline':
            sql = name + ' geometry(path,27700)'
        elif geomtype == 'esriGeometryPoint':
            sql = name + ' geometry(point,27700)'
        else:
            print "GEOM TYPE ERROR: "+geomtype

    elif fieldtype == 'esriFieldTypeDate':
        sql = name + ' DATE'

    elif fieldtype == 'esriFieldTypeDouble':
        sql = name + ' FLOAT(8)'

    elif fieldtype == 'esriFieldTypeSmallInteger':
        length = field.find('Length').text
        sql = name + ' SMALLINT'

    else:
        #print "FIELD TYPE ERROR: "+fieldtype
        return ' '

    if field.find('IsNullable').text == 'false':
        sql += " NOT NULL"

    return sql + ","

sqlTables = {}

domains = {}

missing = []

fastisites = []

source = sys.argv[1]

with open(source) as xmlfile:
    tree = ET.parse(xmlfile) 

    root = tree.getroot()

    #print "Loading Domains "
    
    # iterate Domain items 
    for dom in root.findall('WorkspaceDefinition/Domains/Domain', namespaces):

        name = dom.findall('DomainName', namespaces)[0].text

        domains[name] = esriDomain(name)

        for value in dom.findall('CodedValues/CodedValue'):
            domains[name].addCodedValue(
                value.findall('Name', namespaces)[0].text,
                value.findall('Code', namespaces)[0].text
            )

    #print "Loading Tables "
    sql = ''
    # iterate Table items 
    for table in root.findall('WorkspaceDefinition/DatasetDefinitions/DataElement', namespaces):

        name = table.findall('Name', namespaces)[0].text.replace('ORI_CXXXX','LAR_1EW03')

        sql += "create table "+name+" (\n";

        for field in table.findall('Fields/FieldArray/Field', namespaces):
            sql += "    "+convertField(field) +"\n"

        sql =sql.strip(',\n')+"\n);\n"

        for index in table.findall('Indexes/IndexArray/Index', namespaces):

            indexfield = index.find('Fields/FieldArray/Field/Name').text
            IsUnique = ''
            if index.find('IsUnique').text != 'true':
                IsUnique = 'UNIQUE '
            sql += "create "+IsUnique+"index "+" on "+name+"("+indexfield+");\n";

    print sql





