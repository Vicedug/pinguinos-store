from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel #valida los datos sin tantos if
                               #Convierte srt en numeros de manera automatica
                               #(BaseModel)Genera automaticamante el Json para mandar a las otras API 
from jose import jwt, JWTError
#Creamos la aplicacion
app = FastAPI(title="Servicio de Inventario")
security = HTTPBearer()

#seguridad compartida con Auth-service
SECRET_KEY = "TU_LLAVE_SECRETA_SUPER_SEGURA_DE_LA_ANTARTIDA"
ALGORITHM = "HS256"

#Modelo de DAtos
class ActualizacionStock(BaseModel):
    cantidad : int
    
#Base de datos privada(simulada)

db_inventario = {
    "pescado" : 100,
    "hielo" : 500,
    "nieve" : 0
}
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
            headers={"www-Authenticate": "Bearer"},
        )
#EndPoints API RESTful
    #se convierte las mayusculas a minusculas con .lower()
    #en caso de error se detiene la ejecucion(raise  HttpException)

@app.get("/")

def inicio():
    return { "mensaje":"Sistema de inventario Antartico Operativo"}

@app.get("/stock/{producto_id}")

#se obtiene la cantidad disponible de un producto
def verificar_stock(producto_id: str, usuario: dict = Depends(validar_usuario)):
       
    producto = producto_id.lower()#mayuscula a miniscula
    
    if producto not in db_inventario:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "producto" : producto,
        "cantidad" : db_inventario[producto],
        "estado" : "Disponible" if db_inventario[producto] > 0 else "Agotado",
        "verificado_por": usuario.get("sub")
    }

@app.post("/stock/{producto_id}/update")

#Actualiza el stock
def actualizar_stock(producto_id: str, datos: ActualizacionStock, usuario: dict = Depends(validar_usuario)):
    
    #Verificacion de autorizacion
    if usuario.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes el rol para modificar inventario"     
        )
        
    producto = producto_id.lower()
    db_inventario[producto] = datos.cantidad
    return {
        "mensaje": "Stock actualizado con exito",
        "producto": producto,
        "nueva_cantidad": db_inventario[producto],
        "responsable": usuario.get("sub")
    }
    


