from pymongo.mongo_client import MongoClient

from digikunkor.settings import MONGODB_URI, MONGODB_DB


def connectToMongo():
    client = MongoClient(MONGODB_URI)
    db = client.get_database(MONGODB_DB)
    return db