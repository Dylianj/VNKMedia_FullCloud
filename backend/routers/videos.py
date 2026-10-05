from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
import os

from database import get_session
from models import Video, Usuario
from aws_utils import subir_a_s3, borrar_de_s3

router = APIRouter(tags=["Videos"])

class VideoUpdate(BaseModel):
    title: str
    description: str

class VideoDetalleResponse(BaseModel):
    id: int
    title: str
    description: str
    video_url: str
    thumbnail_url: str
    views: int
    created_at: datetime
    user_id: int
    user_name: str

@router.get("/videos")
def obtener_catalogo(session: Session = Depends(get_session)):
    videos = session.exec(select(Video)).all()
    return videos

@router.get("/videos/{video_id}", response_model=VideoDetalleResponse)
def obtener_video_detalle(video_id: int, session: Session = Depends(get_session)):
    statement = select(Video, Usuario).where(Video.id == video_id, Video.user_id == Usuario.id)
    resultado = session.exec(statement).first()
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Video no encontrado")
        
    video, usuario = resultado
    
    return VideoDetalleResponse(
        id=video.id, title=video.title, description=video.description,
        video_url=video.video_url, thumbnail_url=video.thumbnail_url,
        views=video.views, created_at=video.created_at,
        user_id=video.user_id, user_name=usuario.name
    )

@router.post("/videos")
async def crear_video(
    title: str = Form(...),
    description: str = Form(...),
    user_id: int = Form(...),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    bucket_videos = os.getenv("S3_BUCKET_VIDEOS")
    bucket_thumbnails = os.getenv("S3_BUCKET_THUMBNAILS")
    url_video = await subir_a_s3(video_file, bucket_videos)
    url_miniatura = await subir_a_s3(thumbnail_file, bucket_thumbnails)

    try:
        nuevo_video = Video(
            title=title, description=description, user_id=user_id,
            video_url=url_video, thumbnail_url=url_miniatura
        )
        session.add(nuevo_video)
        session.commit()
        session.refresh(nuevo_video)
        return nuevo_video

    except Exception as e:
        session.rollback() 
        borrar_de_s3(url_video, bucket_videos)
        borrar_de_s3(url_miniatura, bucket_thumbnails)
        raise HTTPException(status_code=500, detail=f"Error en BD. Archivos eliminados de S3. Detalle: {str(e)}")

@router.put("/videos/{video_id}")
def actualizar_video(video_id: int, video_data: VideoUpdate, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    video.title = video_data.title
    video.description = video_data.description
    session.add(video)
    session.commit()
    session.refresh(video)
    return video

@router.delete("/videos/{video_id}")
def eliminar_video(video_id: int, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    bucket_videos = os.getenv("S3_BUCKET_VIDEOS")
    bucket_thumbnails = os.getenv("S3_BUCKET_THUMBNAILS")
    borrar_de_s3(video.video_url, bucket_videos)
    borrar_de_s3(video.thumbnail_url, bucket_thumbnails)
    session.delete(video)
    session.commit()
    return {"mensaje": "Video y archivos de S3 eliminados exitosamente"}