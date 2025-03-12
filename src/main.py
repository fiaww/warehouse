from fastapi import FastAPI
from src.api.books import router


app = FastAPI()
app.include_router(router)

