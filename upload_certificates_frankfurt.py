#!/usr/bin/env python3

import json
import os
from pymongo import MongoClient

username = os.environ["MONGO_USERNAME"]
password = os.environ["MONGO_PASSWORD"]
url = os.environ["MONGO_URL"]
client = MongoClient('mongodb+srv://%s:%s@%s' % (username, password, url))
db = client.DiscountCertificates
collection = db.DiscountCertificates

with open('Discount-Dax.json', 'r') as file:
    jsonfile = json.load(file)
    result = collection.insert_many(jsonfile['data'])
print('Finished Importing')
