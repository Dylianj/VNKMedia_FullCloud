import boto3
import os
import uuid
from urllib.parse import urlparse
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

async def subir_a_s3(file: UploadFile, bucket_name: str) -> str:
    file_extension = file.filename.split(".")[-1]
    file_key = f"{uuid.uuid4()}.{file_extension}"

    s3_client.upload_fileobj(
        file.file,
        bucket_name,
        file_key,
        ExtraArgs={"ContentType": file.content_type}
    )
    
    return f"https://{bucket_name}.s3.amazonaws.com/{file_key}"

def borrar_de_s3(url: str, bucket_name: str):
    try:
        parsed_url = urlparse(url)
        file_key = parsed_url.path.lstrip('/')
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"Archivo eliminado correctamente de S3: {file_key}")
    except Exception as e:
        print(f"Error al intentar borrar el archivo en S3: {e}")