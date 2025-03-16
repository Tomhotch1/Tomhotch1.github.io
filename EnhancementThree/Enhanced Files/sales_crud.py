import pymongo
import kagglehub
import shutil



class SalesAnalysis(object):
    """ CRUD operations for weekly_sales collection in MongoDB """

    def __init__(self, inputUser, inputPass):

        USER = inputUser
        PASS = inputPass
        HOST = 'localhost'
        PORT = 27017
        DB = 'sales'
        COL = 'weekly_sales'

        # Uncomment this line to download the dataset
        # self.download_data()

        # Initialize the MongoClient
        try: 
            self.client = pymongo.MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
            self.database = self.client['%s' % (DB)]
            self.collection = self.database['%s' % (COL)]
            print("Connected to " + DB + " as " + USER + " with port " + str(PORT))
        except Exception as e:
            print("Failed to connect to database.")
            raise e
        

    def download_data(self):
        # Download and move the latest version of the dataset
        source = kagglehub.dataset_download('mikhail1681/walmart-sales', force_download=True)

        # Move the file to the destination
        destination_path = "./SalesData"
        try:
            shutil.move(source, destination_path)
            print(f"File '{source}' cut and pasted to '{destination_path}' successfully.")
        except FileNotFoundError:
            print(f"Error: File '{source}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


    # creates a document with the given data
    # returns true if document is added, false otherwise
    def create(self, data):
        if data is not None:
            self.database.weekly_sales.insert_one(data)  # data should be dictionary      
            return True
        else:
            return False


    # finds documents matching search query
    # returns the set of matching documents
    def read(self, data=None):
        # search for matching data
        if data is not None:
            result = self.database.weekly_sales.find(data, {"_id": False})
        else:
            result = self.database.weekly_sales.find({}, {"_id": False})
        return result


    # finds and updates documents matching data with newData
    # returns the number of modified documents
    def update(self, data=None, newData=None):
        updatedDocs = self.database.weekly_sales.update_many(data, {"$set": newData})
        return updatedDocs.modified_count


    # finds and deletes documents matching documents
    # returns the number of documents removed from the collection
    def delete(self, data=None):
        deletedDocs = self.database.weekly_sales.delete_many(data)
        return deletedDocs.deleted_count