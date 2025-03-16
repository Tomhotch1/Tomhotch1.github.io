from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, inputUser, inputPass):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #
        # You must edit the connection variables below to reflect
        # your own instance of MongoDB!
        #
        # Connection Variables
        #
        USER = inputUser
        PASS = inputPass
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 30266
        DB = 'AAC'
        COL = 'animals'
        #
        # Initialize Connection
        #
        try: 
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
            self.database = self.client['%s' % (DB)]
            self.collection = self.database['%s' % (COL)]
            print("Connected to " + DB + " as " + USER + " with port " + str(PORT))
        except Exception as e:
            print("Failed to connect to database.")
            raise e

        
# creates a document with the given data
# returns true if document is added, false otherwise
    def create(self, data):
        if data is not None:
            self.database.animals.insert_one(data)  # data should be dictionary      
            return True
        else:
            return False

# finds documents matching search query
# returns the set of matching documents
    def read(self, data=None):
        # search for matching data
        if data is not None:
            result = self.database.animals.find(data, {"_id": False})
        else:
            result = self.database.animals.find({}, {"_id": False})
        return result
    
# finds and updates documents matching data with newData
# returns the number of modified documents
    def update(self, data=None, newData=None):
        updatedDocs = self.database.animals.update_many(data, {"$set": newData})
        return updatedDocs.modified_count

# finds and deletes documents matching documents
# returns the number of documents removed from the collection
    def delete(self, data=None):
        deletedDocs = self.database.animals.delete_many(data)
        return deletedDocs.deleted_count