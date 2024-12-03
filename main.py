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

# Modelo para los usuarios
class Usuario(BaseModel):
    nombre: str
    contraseña: str

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

# Rutas para usuarios
@app.post(
    "/usuarios/",
    response_model=Usuario,
    summary="Agregar un nuevo usuario",
    description="Agrega un nuevo usuario con nombre y contraseña.",
)
async def create_usuario(usuario: Usuario):
    result = await db.usuarios.insert_one(usuario.dict())
    if result.inserted_id:
        return usuario
    raise HTTPException(status_code=500, detail="Error al agregar el usuario.")

@app.get(
    "/usuarios/",
    response_model=List[Usuario],
    summary="Obtener todos los usuarios",
    description="Devuelve una lista de todos los usuarios en la base de datos.",
)
async def get_usuarios():
    usuarios = await db.usuarios.find().to_list(None)
    return usuarios

@app.post(
    "/usuarios/login/",
    summary="Autenticar usuario",
    description="Autentica un usuario con nombre y contraseña.",
)
async def autenticar_usuario(usuario: Usuario):
    usuario_encontrado = await db.usuarios.find_one({"nombre": usuario.nombre, "contraseña": usuario.contraseña})
    if usuario_encontrado:
        return {"msg": "Usuario autenticado correctamente."}
    raise HTTPException(status_code=401, detail="Nombre o contraseña incorrectos.")
