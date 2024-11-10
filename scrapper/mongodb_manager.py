from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .logger_config import logger

class AtlasClient:
    def __init__(self, atlas_uri, dbname):
        self.mongodb_client = MongoClient(atlas_uri)
        self.database = self.mongodb_client[dbname]

    def ping(self):
        try:
            self.mongodb_client.admin.command('ping')
            logger.info("Pinged your MongoDB deployment. Connection successful.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    def get_collection(self, collection_name):
        collection = self.database[collection_name]
        return collection

    def findOneByKey(self,collection_name,key):
        collection = self.get_collection(collection_name)
        result = collection.find_one({ key: { "$exists": True } })
        return result


    def find(self, collection_name, filter={}, limit=0, keys_only=False):
        collection = self.database[collection_name]
        if keys_only:
            logger.warning("fetching all keys")
            items = collection.find(filter=filter, limit=limit, projection={'_id': 0})
            logger.warning("fetched all keys")
            return [list(doc.keys()) for doc in items]
        else:
            items = list(collection.find(filter=filter, limit=limit))
        return items

    
    def insert(self, collection_name, documents):
        """
        Inserts one or more documents into a MongoDB collection.
        
        Parameters:
        - collection_name: str, the name of the collection
        - documents: dict or list of dicts, the document(s) to insert
        
        If `documents` is a list, it will insert multiple documents using `insert_many`.
        Otherwise, it will insert a single document using `insert_one`.
        """
        collection = self.get_collection(collection_name)
        
        if isinstance(documents, list):
            result = collection.insert_many(documents)
            return result.inserted_ids
        else:
            result = collection.insert_one(documents)
            return result.inserted_id
        
    def delete(self, collection_name, filter={}, _del_all_=False):
        """
        Deletes documents from a MongoDB collection based on the filter.
        
        Parameters:
        - collection_name: str, the name of the collection.
        - filter: dict, the filter to find documents to delete (default is {}).
        - _del_all_: bool, if True, deletes all documents matching the filter using `delete_many()`.
                      If False, deletes only one document using `delete_one()`.
        
        Returns:
        - Number of documents deleted.
        """
        collection = self.get_collection(collection_name)
        
        if _del_all_:
            result = collection.delete_many(filter)
            return result.deleted_count
        else:
            result = collection.delete_one(filter)
            if result.deleted_count == 1:
                pass
            else:
                pass
            return result.deleted_count
    
