from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from base64 import b64encode
import os

app = FastAPI(title="API Verificación QR", version="1.0.0")

# 📂 Cargar variables de entorno
load_dotenv()

# 🗄️ CONEXIÓN A LA BASE DE DATOS
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../codigos_qr.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 📋 TU TABLA — EXACTAMENTE como está en DBeaver
class CodigoQR(Base):
    __tablename__ = "qrs"
    
    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(String, unique=True, index=True)
    imagen_blob = Column(String)
    estado = Column(String)

# 📦 Modelo de respuesta
class RespuestaQR(BaseModel):
    existe: bool
    mensaje: str
    codigo: str | None = None
    imagen: str | None = None #permite None y string
    estado: str | None = None

    class Config:
        from_attributes = True

# 🔌 Conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🚀 Iniciar API
app = FastAPI(
    title="API Verificación QR",
    description="Devuelve el estado de códigos QR",
    version="1.0.0"
)
from base64 import b64encode
# 📡 Endpoint GET — por URL
@app.get("/api/verificar-qr/{codigo_qr}", response_model=RespuestaQR)
def verificar_qr_get(codigo_qr: str, db: Session = Depends(get_db)):
    try:
        resultado = db.query(CodigoQR).filter(CodigoQR.contenido == codigo_qr).first()
        if resultado:
            imagen_base64 = None
            if resultado.imagen_blob:
                if isinstance(resultado.imagen_blob, bytes):
                    imagen_base64 = b64encode(resultado.imagen_blob).decode('utf-8')        
                else:
                    imagen_base64 = str(resultado.imagen_blob)  # Convertir a string si no es bytes
            
            return RespuestaQR(
                existe=True,
                mensaje="✅ Código encontrado",
                codigo=resultado.contenido,
                imagen=imagen_base64,
                estado=resultado.estado
            )
        return RespuestaQR(
            existe=False,
            mensaje="❌ Código NO encontrado"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# 📡 Endpoint POST — más seguro para caracteres especiales
@app.post("/api/verificar-qr")
def verificar_qr_post(
    codigo_qr: str,
    db: Session = Depends(get_db)
):
    try:
    
        resultado = db.query(CodigoQR).filter(CodigoQR.contenido == codigo_qr).first()
        
        if resultado:
            imagen_base64 = None
            if resultado.imagen_blob:
                if isinstance(resultado.imagen_blob, bytes):
                    imagen_base64 = b64encode(resultado.imagen_blob).decode('utf-8')        
                else:
                    imagen_base64 = str(resultado.imagen_blob)  # Convertir a string si no es bytes
        if resultado:
            return {       
                "existe": True,
                "mensaje": "✅ Código encontrado",
                "codigo": resultado.contenido,
                "imagen": imagen_base64,
                "estado": resultado.estado
            }
        return {
            "existe": False,
            "mensaje": "❌ Código NO encontrado"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")