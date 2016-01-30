# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 11:46:57 2015

@author: Dominik
"""

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


OSMFILE = "C:/Users/Dominik/Documents/DataAnalyst_Nanodegree/Project3/Project/winterthur_switzerland.osm"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        k = element.get("k")
        l = re.search(lower,k)
        lc = re.search(lower_colon,k)
        pc = re.search(problemchars,k)
        if l:
            #print l.group()
            keys['lower'] +=1
        elif lc:
            #print lc.group()
            keys['lower_colon'] +=1
        elif pc:
            #print pc.group()
            keys['problemchars'] +=1
        else:
            keys['other'] +=1
    return keys


def process_keys(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

keys = process_keys(OSMFILE)
pprint.pprint(keys)

##How many users have contributed?
def get_user(element):
    uid = []
    if element.tag == "node":
        uid = element.get('uid')
    elif element.tag == "way":
        uid = element.get('uid')
    elif element.tag == "relation":
        uid = element.get('uid')
    print uid
    return uid


def process_users(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element):
            users.add(get_user(element))
            users.discard('')
            pass

    return users

users = process_users(OSMFILE)
users_unique= list(set(users))
print(len(users_unique))

def audit_data(osmfile):
    osm_file = open(osmfile, "r")
    street_names = []    
    postcodes = []
    h_numbers = []
    amenity = []
    phone = []
    name = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    street_names.append(tag.attrib['v'])
                if tag.attrib['k'] == "addr:postcode":
                    postcodes.append(tag.attrib['v'])
                if tag.attrib['k'] == "addr:housenumber":
                    h_numbers.append(tag.attrib['v'])
                if tag.attrib['k'] == "amenity":
                    amenity.append(tag.attrib['v'])
                if tag.attrib['k'] == "phone":
                    phone.append(tag.attrib['v'])
                if tag.attrib['k'] == "name":
                    name.append(tag.attrib['v'])
    return street_names, postcodes, h_numbers, amenity, phone, name 


audit_results = audit_data(OSMFILE)
#print all street names
pprint.pprint(list(set(audit_results[0])))
#the console seems to struggle with the the German umlaut-letters
#yet, I use utf-8 encoding, so I should be fine. Spyder's variable explorer adequatly represents the umlaute!
#Generally, the street names seem to be very clean!

#print all postcodes
pprint.pprint(list(set(audit_results[1])))
#the post codes seem clean, but I will test below if they all belong to the city of Winterthur

#print all housenumbers
pprint.pprint(list(set(audit_results[2])))
#the housenumbers seem also very clean

#print all amenities
pprint.pprint(list(set(audit_results[3])))

#print all phone numbers
pprint.pprint(list(set(audit_results[4])))
#phone numbers are coded inconsistently
#For example: +41 (0)52 222 85 76, 0041443078818, 052 242 05 74
#Some are missing the country code, others have +41 or 0041
#This I will have to clean while processing the data 

#I now test whether all postcodes are in expected range
#according to Wikipedia, Winterthur should have postcodes: 8400–8411, 8310, 8352, 8482
expected_zip = ['8400', '8401', '8402', '8403', '8404', '8405', '8406', '8407', '8408', '8409', '8410', '8411',
                '8310', '8352', '8482']

postcodes = audit_results[1]

unique_codes = list(set(postcodes))

invalid_zips = list(set(unique_codes).difference(expected_zip))
print(invalid_zips)
#There are a number of entries which do not belong to the city of Winterthur
#This is a problem I will have to fix
#I will have to make sure that these entries will not go into the clean dataset
#This is done in the other python scrips, using mongodb


#I now set up a function to clean the phone numbers
#The function returns a common format: E.g., +41522420574 (+41 as country code and no spaces or indents)
def update_phone(phone):    
    phone_updated = ""
    phone_extract = re.findall(r'\d+', phone)
    phone_rejoin = ''.join(phone_extract)

    if (phone_rejoin.startswith("41") == True) & (phone_rejoin.startswith("410") == False):
        phone_updated += "+"
        phone_updated += phone_rejoin
    
    if phone_rejoin.startswith("410") == True:
        sep = '0'
        nr = phone_rejoin.split(sep, 1)[1]
        phone_updated += "+41"
        phone_updated += nr
    
    if phone_rejoin.startswith("0041") == True:
        sep = '41'
        nr = phone_rejoin.split(sep, 1)[1]
        phone_updated += "+41"
        phone_updated += nr
        
    if (phone_rejoin.startswith("0") == True) & (phone_rejoin.startswith("0041") == False):
        sep = '0'
        nr = phone_rejoin.split(sep, 1)[1]
        phone_updated += "+41"
        phone_updated += nr
        
    if len(phone_rejoin) < 7:
        return None
                
    return phone_updated



###Shape and store data
def shape_element(element):
    node = {}
    address = {}
    pos = []
    if element.tag == "node" or element.tag == "way" :
        
        node["id"] = element.attrib["id"]
        
        node["type"] =  element.tag
        
        node[ "visible"] = element.get("visible")
        created = {}
        created["version"] = element.attrib["version"]
        created["changeset"] = element.attrib["changeset"]
        created["timestamp"] = element.attrib["timestamp"]
        created["user"] = element.attrib["user"]
        created["uid"] = element.attrib["uid"]
        node["created"] = created
        if "lat" in element.keys() and "lon" in element.keys():
           pos = [element.attrib["lat"], element.attrib["lon"]]        
           node["pos"] = [float(string) for string in pos]
        else:
           node["pos"] = None
            
        for tag in element.iter('tag'):
            if re.search('addr:', tag.attrib['k']):
                if len(tag.attrib['k'].split(":")) < 3:
                    addr_add = tag.attrib['k'].split(":")[1]
                    if addr_add != 'postcode':
                        address[addr_add] = tag.attrib['v']
                    if addr_add == 'postcode':
                        if tag.attrib['v'] in expected_zip:
                            address[addr_add] = tag.attrib['v']
        if address:
            node["address"] = address     
            #pprint.pprint(node) 
        for tag in element.iter('tag'):
            if tag.attrib['k'] == "amenity":
                node["amenity"]= tag.attrib['v']
            if tag.attrib['k'] == "cuisine":
                node["cuisine"]= tag.attrib['v']
            if tag.attrib['k'] == "name":
                node["name"]= tag.attrib['v']
            if tag.attrib['k'] == "phone":
                node["phone"]= update_phone(tag.attrib['v'])
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w", encoding='utf-8') as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map(OSMFILE, False)


#check if addresses are added correctly
addresses = [s for s in data if "address" in s]
pprint.pprint(addresses[:20])

#check if amenities are added correctly
amenities = [s for s in data if "amenity" in s]
pprint.pprint(amenities[:20])

         
#The resulting .json file is stored in mongodb using mongoimport via the command prompt


