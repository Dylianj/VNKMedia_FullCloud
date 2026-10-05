from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from database import get_session
from models import Comentario, Video, Usuario

router = APIRouter(tags=["Comentarios"])

class ComentarioCreate(BaseModel):
    content: str
    user_id: int

class ComentarioConUsuario(BaseModel):
    id: int
    content: str
    user_id: int
    user_name: str

@router.post("/videos/{video_id}/comments", response_model=Comentario)
def crear_comentario(video_id: int, comment_data: ComentarioCreate, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    usuario = session.get(Usuario, comment_data.user_id)
    
    if not video or not usuario:
        raise HTTPException(status_code=404, detail="Video o Usuario no encontrado")
    
    nuevo_comentario = Comentario(content=comment_data.content, user_id=comment_data.user_id, video_id=video_id)
    session.add(nuevo_comentario)
    session.commit()
    session.refresh(nuevo_comentario)
    return nuevo_comentario

@router.get("/videos/{video_id}/comments", response_model=List[ComentarioConUsuario])
def obtener_comentarios(video_id: int, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
        
    statement = select(Comentario, Usuario).where(
        Comentario.video_id == video_id, Comentario.user_id == Usuario.id
    )
    resultados = session.exec(statement).all()
    
    return [
        ComentarioConUsuario(
            id=c.id, content=c.content, user_id=c.user_id, user_name=u.name
        ) for c, u in resultados
    ]