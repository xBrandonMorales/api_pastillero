from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configura la conexión a MongoDB Atlas
MONGO_URL = "mongodb+srv://1722110607:1234@cluster0.o6f1d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URL)
db = client.pastillero  # Reemplaza "proyecto" con el nombre de tu base de datos si es diferente

# Modelo para las pastillas
class Pastilla(BaseModel):
    nombre: str
    cantidad: int
    hora_toma: str  # Formato HH:MM
    duracion_dias: int

# Configuración de CORS para permitir acceso desde todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get(
    "/pastillas/",
    response_model=List[Pastilla],
    summary="Obtener todas las pastillas",
    description="Devuelve una lista de todas las pastillas en la base de datos.",
)
async def get_pastillas():
    pastillas = await db.pastillas.find().to_list(None)
    return pastillas

@app.post(
    "/pastillas/",
    response_model=Pastilla,
    summary="Agregar una nueva pastilla",
    description="Agrega una nueva pastilla con su información.",
)
async def create_pastilla(pastilla: Pastilla):
    result = await db.pastillas.insert_one(pastilla.dict())
    if result.inserted_id:
        return pastilla
    raise HTTPException(status_code=500, detail="Error al agregar la pastilla.")

@app.put(
    "/pastillas/{nombre}",
    summary="Actualizar una pastilla",
    description="Actualiza los datos de una pastilla existente.",
)
async def update_pastilla(nombre: str, pastilla: Pastilla):
    result = await db.pastillas.update_one({"nombre": nombre}, {"$set": pastilla.dict()})
    if result.modified_count == 1:
        return {"msg": "Pastilla actualizada correctamente."}
    raise HTTPException(status_code=404, detail="Pastilla no encontrada.")

@app.delete(
    "/pastillas/{nombre}",
    summary="Eliminar una pastilla",
    description="Elimina una pastilla por su nombre.",
)
async def delete_pastilla(nombre: str):
    result = await db.pastillas.delete_one({"nombre": nombre})
    if result.deleted_count == 1:
        return {"msg": "Pastilla eliminada correctamente."}
    raise HTTPException(status_code=404, detail="Pastilla no encontrada.")
