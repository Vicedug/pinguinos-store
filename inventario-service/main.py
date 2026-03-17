from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel #valida los datos sin tantos if
                               #Convierte srt en numeros de manera automatica
                               #(BaseModel)Genera automaticamante el Json para mandar a las otras API 
from jose import jwt, JWTError
from sqlalchemy.orm import Session # Importado para manejar la sesión de DB
from database import get_db, init_db, ProductoDB # Importamos la configuración de nuestra base de datos

#Creamos la aplicacion
app = FastAPI(title="Servicio de Inventario")

# Inicializamos las tablas de SQLite al arrancar
init_db()

security = HTTPBearer()

#seguridad compartida con Auth-service
SECRET_KEY = "TU_LLAVE_SECRETA_SUPER_SEGURA_DE_LA_ANTARTIDA"
ALGORITHM = "HS256"

#Modelo de DAtos
class ActualizacionStock(BaseModel):
    cantidad : int
    
# CARGA INICIAL: Si la base de datos está vacía, insertamos los valores por defecto
@app.on_event("startup")
def cargar_inventario_inicial():
    db = next(get_db())
    # Valores iniciales que tenías en tu diccionario simulado
    productos_iniciales = {"pescado": 100, "hielo": 500, "nieve": 0}
    for nombre, cant in productos_iniciales.items():
        if not db.query(ProductoDB).filter(ProductoDB.id == nombre).first():
            db.add(ProductoDB(id=nombre, stock=cant))
    db.commit()

#DEPENDENCIA DE SEGURIDAD: Validador de los tokens
def validar_usuario(res=Depends(security)):
    try:
        token = res.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso denegado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
#EndPoints API RESTful
    #se convierte las mayusculas a minusculas con .lower()
    #en caso de error se detiene la ejecucion(raise  HttpException)

@app.get("/")
def inicio():
    return { "mensaje":"Sistema de inventario Antartico Operativo"}

@app.get("/stock/{producto_id}")
#se obtiene la cantidad disponible de un producto
def verificar_stock(producto_id: str, usuario: dict = Depends(validar_usuario), db: Session = Depends(get_db)):
        
    producto_nombre = producto_id.lower()#mayuscula a miniscula
    
    # BUSQUEDA EN BASE DE DATOS SQLITE
    producto_db = db.query(ProductoDB).filter(ProductoDB.id == producto_nombre).first()
    
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return {
        "producto" : producto_db.id,
        "cantidad" : producto_db.stock,
        "estado" : "Disponible" if producto_db.stock > 0 else "Agotado",
        "verificado_por": usuario.get("sub")
    }

@app.post("/stock/{producto_id}/update")
#Actualiza el stock
def actualizar_stock(producto_id: str, datos: ActualizacionStock, usuario: dict = Depends(validar_usuario), db: Session = Depends(get_db)):
    
    #Verificacion de autorizacion
    if usuario.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes el rol para modificar inventario"     
        )
        
    producto_nombre = producto_id.lower()
    
    # BUSQUEDA DEL PRODUCTO EN LA DB PARA ACTUALIZAR
    producto_db = db.query(ProductoDB).filter(ProductoDB.id == producto_nombre).first()
    
    if not producto_db:
        # Si el producto no existe en la DB, lo creamos
        producto_db = ProductoDB(id=producto_nombre, stock=0)
        db.add(producto_db)

    # Modificamos el stock (Sumamos la cantidad recibida)
    producto_db.stock += datos.cantidad
    
    # Verificamos que no quede stock negativo
    if producto_db.stock < 0:
        raise HTTPException(status_code=400, detail="Operación inválida: El stock no puede ser menor a cero")

    # Guardamos los cambios permanentemente en el archivo .db
    db.commit()
    db.refresh(producto_db)
    
    return {
        "mensaje": "Stock actualizado con exito",
        "producto": producto_db.id,
        "nueva_cantidad": producto_db.stock,
        "responsable": usuario.get("sub")
    }
    


