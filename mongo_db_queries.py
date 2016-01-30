# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 13:32:57 2015

@author: Dominik
"""
import pprint
from pymongo import MongoClient


def get_db(db_name):
    client = MongoClient()
    db = client[db_name]
    return db

db = get_db('cities_data')
db.wintert.count()

#print the documents
for doc in db.wintert.find({}):
        pprint.pprint(doc)

#Now I remove the documents with invalid postcodes (identified previously)
#['8544', '8413', '8311', '8442', '8412', '8542', '8472']

#First, I investigate some of the invalide postcode entries
cursor = db.wintert.find({"address.postcode": "8544"})
for document in cursor:
    pprint.pprint(document)
#This 8544 postcode is from the town of Attikon, which is not part of Winterthur

cursor = db.wintert.find({"address.postcode": "8412"})
for document in cursor:
    pprint.pprint(document)
#This postcode is about Ried, a town at the border to Winterthur city

#Hence, I delete these invalide entries
final_data = db.wintert.delete_many({"address.postcode": '8544'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8413'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8311'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8442'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8412'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8542'})
final_data.deleted_count
final_data = db.wintert.delete_many({"address.postcode": '8472'})
final_data.deleted_count

#Number of documents
db.wintert.find().count()   

# Number of nodes
db.wintert.find({"type":"node"}).count() 
                                           
# Number of ways
db.wintert.find({"type":"way"}).count()

#How many amenities are in the data?
db.wintert.find({"amenity": {"$exists" : 1}}).count()

# Number of cafes 
db.wintert.find({"amenity":"cafe"}).count()
cursor = db.wintert.find({"amenity":"cafe"})
for document in cursor:
    pprint.pprint(document)

#In what streets can I find cafes?    
results = db.wintert.aggregate([
        {"$match" : {"amenity":"cafe"}},
        {"$project": {"street_name": "$address.street"}},
        {"$group": {"_id" : "$street_name", "unique_streetname" : {"$addToSet" : "$street_name"}}}        
        ])
for document in results:
    pprint.pprint(document)

