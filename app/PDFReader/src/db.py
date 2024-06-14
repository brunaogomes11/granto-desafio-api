from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
import os


class Database:
    def __init__(self):
        load_dotenv()

        # Create a new client and connect to the server
        self.client = MongoClient(os.getenv('URI'), server_api=ServerApi('1'))
        self.db = self.client['Cluster0']
        self.col = self.db['documents']

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)


    def insert_document(self, data: dict):
        try:
            self.col.insert_one(data)
            print("You successfully inserted one element to MongoDB!")
        except Exception as e:
            print(e)
