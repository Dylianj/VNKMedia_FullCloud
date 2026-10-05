from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from database import get_session
from models import Usuario

router = APIRouter(tags=["Autenticación"])

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/users")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    usuario_existente = session.exec(select(Usuario).where(Usuario.email == user.email)).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    db_user = Usuario(name=user.name, email=user.email, password=user.password)
    session.add(db_user)
    session.commit()
    return {"message": "Usuario registrado exitosamente"}

@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    statement = select(Usuario).where(Usuario.email == user.email, Usuario.password == user.password)
    db_user = session.exec(statement).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    return {
        "access_token": "fake-jwt-token-mvp", 
        "token_type": "bearer",
        "user_id": db_user.id,
        "name": db_user.name 
    }