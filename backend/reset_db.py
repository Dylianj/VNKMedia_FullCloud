from database import engine
from sqlmodel import SQLModel
import models # Importamos los modelos para que SQLModel sepa qué estructura buscar

print("Conectando a AWS para borrar tablas viejas...")
# drop_all elimina las tablas definidas en models.py
SQLModel.metadata.drop_all(engine)
print("¡Limpieza exitosa! Las tablas antiguas fueron eliminadas.")