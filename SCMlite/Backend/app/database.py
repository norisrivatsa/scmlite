from pymongo import MongoClient
from datetime import datetime,date



# MongoDB connection setup
def get_user_database():
    client = MongoClient("mongodb://mongodb:27017/")
    return client["user_database"] 

def get_shipment_database():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["SCMproject"]
    return db


def del_update():
    db = get_shipment_database()
    collections = db['shipment_info']

    current_date = date.today()     
    cursor = collections.find({}, {"exp_deliver_date" : 1 ,"_id":1})    

    for document in cursor:
        expdeldatae = document.get('exp_deliver_date')
        doc_date = datetime.strptime(expdeldatae, "%Y-%m-%d").date()

        if expdeldatae:  # Checking if 'exp_deliver_date' exists
                try:
                    doc_date = datetime.strptime(expdeldatae, "%Y-%m-%d").date()  # Ensuring correct format
                    if current_date > doc_date:
                        collections.update_one(
                            {'_id': document['_id']},  # Matching the document by its ID
                            {'$set': {'status': "Delivered", 'active': False }}
                        )
                except ValueError:
                    print(f"Invalid date format for document with _id {document['_id']}: {expdeldatae}")
                    continue  # Skip this document if the date format is incorrect


