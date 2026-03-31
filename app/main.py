from fastapi import FastAPI
from pydantic import BaseModel
from app.database import collection
from app.operations import insert_user,get_all_users,find_by_age,find_by_name,find_by_role
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    name:str
    age:int
    role:str


@app.get("/")
def home():
    return {"message": "CI/CD Pipeline Running"}

@app.get("/health")
def health():
    return {"Status": "healthy"}

@app.get("/db-check")
def db_check():
    try:
        collection.insert_one({"test":"ok"})
        return {"DB": "Connected"}
    except Exception as e:
        return {"DB": "Error", "details": str(e)}
    
@app.post("/insert")
def insert(user: User):
    return insert_user(user.name,user.age,user.role)



@app.get("/users")
def users():
    return get_all_users()

@app.get("/find/name")
def find_name(name: str):
    return find_by_name(name)

@app.get("/find/role")
def find_role(role: str):
    return find_by_role(role)

@app.get("/find/age")
def find_age(age: int):
    return find_by_age(age)