import os

print(os.listdir())
from firebase_config import db

docs = db.collection("lessons").stream()

for doc in docs:
    print(doc.to_dict())