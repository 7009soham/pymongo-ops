from fastapi import FastAPI
from app.database import collection
from app.operations import run_cli_app

app = FastAPI()
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
    
@app.get("/db-ops")
def operations():
    run_cli_app()
    
