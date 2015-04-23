import os
import pymongo
import random

MONGODB_URL = os.environ["MONGODB_URL"]

db = pymongo.MongoClient(MONGODB_URL).get_default_database()

pins = db.pins

for pin in pins.find():
    pin['pin']['actions'] = [
        {
            "title": "Check-in",
            "type": "openWatchApp",
            "launchCode": random.randint(0, 2**32 - 1)
        },
        {
            "title": "Mark as seen",
            "type": "openWatchApp",
            "launchCode": random.randint(0, 2**32 - 1)
        },
    ]

    pins.replace_one(
        {'_id': pin['_id']},
        pin)
    print("updated", pin)
