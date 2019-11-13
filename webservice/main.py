from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def root():
    return {"Salut le monde !"}


@app.get("/match")
def matching(q: str = None):
    return {"coucou"}
