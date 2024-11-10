import json
from bson import json_util
from pymongo import MongoClient

from config import cfg

# Get database configuration
db_cfg = cfg.db

def serialize_mongo_document(doc):
    """ Serialize a MongoDB document for JSON response """
    return json.loads(json_util.dumps(doc))

class MongoDB:
    def __init__(self, collection_name):
        # Initialize MongoDB connection and set the collection
        self.client = MongoClient(db_cfg.db_url)
        self.db = self.client[db_cfg.db_name]
        self.collection = self.db[collection_name]

    def add(self, data):
        """Insert a document into the collection and return its inserted ID."""
        return self.collection.insert_one(data).inserted_id

    def update(self, query, updates):
        """Update documents that match the query with the provided updates."""
        return self.collection.update_one(query, {'$set': updates})

    def delete(self, query):
        """Delete a document that matches the query."""
        return self.collection.delete_one(query)

    def find_one(self, query):
        """Find and return a single document matching the query."""
        return self.collection.find_one(query)

    def find_all(self, query={}, page=1, limit=db_cfg.default_limit, sort={}):
        """Find and return all documents matching the query."""
        return [serialize_mongo_document(doc) for doc in self.collection.find(query, limit=limit, skip=(page - 1) * limit, sort=sort)]

    def aggregate(self, query):
        """Perform an aggregation operation on the collection using the specified query."""
        return self.collection.aggregate(query)