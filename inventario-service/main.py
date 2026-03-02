from fastapi import FastAPI, HTTPException
from pydantic import BaseModel #valida los datos sin tantos if
                               #Convierte srt en numeros de manera automatica
                               #(BaseModel)Genera automaticamante el Json para mandar a las otras API 

#Creamos la aplicacion
app = FastAPI(title="Servicio de Inventario")

#Modelo de DAtos
class ActualizacionStock(BaseModel):
    cantidad : int
    
#Base de datos privada(simulada)

db_inventario = {
    "pescado" : 100,
    "hielo" : 500,
    "nieve" : 0
}

#EndPoints API RESTful
    #se convierte las mayusculas a minusculas con .lower()
    #en caso de error se detiene la ejecucion(raise  HttpException)

@app.get("/")

def inicio():
    return { "mensaje":"Sistema de inventario Antartico Operativo"}

@app.get("/stock/{producto_id}")

#se obtiene la cantidad disponible de un producto
def verificar_stock(producto_id: str):
       
    producto = producto_id.lower()#mayuscula a miniscula
    
    if producto not in db_inventario:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "producto" : producto,
        "cantidad" : db_inventario[producto],
        "estado" : "Disponible" if db_inventario[producto] > 0 else "Agotado"
    }

@app.post("/stock/{producto_id}/update")

#Actualiza el stock
def actualizar_stock(producto_id: str, datos: ActualizacionStock):
    producto = producto_id.lower()
    db_inventario[producto] = datos.cantidad
    return {
        "mensaje": "Stock actualizado con exito",
        "producto": producto,
        "nueva_cantidad": db_inventario[producto]
    }
    


