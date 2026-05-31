from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["cricket_db"]      # Database name
matches = db["matches"]        # Collection name

print("Connected successfully")
