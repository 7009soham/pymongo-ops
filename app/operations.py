from app.database import collection

def insert_user(name, age, role):
    collection.insert_one({
        "name": name,
        "age": age,
        "role": role
    })
    return {"message": "User inserted"}

def get_all_users():
    return list(collection.find({}, {"_id": 0}))

def find_by_name(name):
    return list(collection.find({"name": name}, {"_id": 0}))

def find_by_age(age):
    return list(collection.find({"age": {"$gt": age}}, {"_id": 0}))

def find_by_role(role):
    return list(collection.find({"role": role}, {"_id": 0}))