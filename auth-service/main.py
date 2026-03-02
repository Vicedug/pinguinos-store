# auth-service/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import verificar_password, crear_token_acceso, ACCESS_TOKEN_EXPIRE_MINUTES



app = FastAPI(title="Servicio de Autenticación Central")

# Base de datos de usuarios privada (Solo este servicio la ve)
db_usuarios = {
    "pinguino_admin": {
        "password_hash": "$2b$12$6pU7z0wIUqskYFVZHskrReEkjhzGah2lZdOo92Vim46mkRwC/kcvq", # pinguino123
        "rol": "admin"
    }
}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_usuarios.get(form_data.username)
    
    if not user or not verificar_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"}
            
        )
    
    #definimos el tiempo de expiracion
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generamos el token usando lógica de auth.py inyectando el rol y el tiempo
    token = crear_token_acceso(data={"sub": form_data.username, "rol": user["rol"]}, expires_delta=tiempo_expiracion)
    
    return {"access_token": token, "token_type": "bearer"}