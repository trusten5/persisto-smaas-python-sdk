from fastapi import FastAPI
from routers import memory

app = FastAPI()

app.include_router(memory.router)