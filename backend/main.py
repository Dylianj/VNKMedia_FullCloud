from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import auth, videos, comments


app = FastAPI(title="Video Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Tablas verificadas en AWS RDS.")


app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(comments.router)

@app.get("/")
def root():
    return {"message": "¡API funcionando de manera local y conectada a AWS RDS!"}