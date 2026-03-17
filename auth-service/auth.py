from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
#from passlib.context import CryptContext

#Configuracion de Seguridad
SECRET_KEY = "TU_LLAVE_SECRETA_SUPER_SEGURA_DE_LA_ANTARTIDA" #Sal o clave maestra del sistema: se usa para la firma JWT
ALGORITHM = "HS256" #Algoritmo de firma
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #vida util del token

'''#Hashing de contraseñas: #BCRYPT: Genera Hashes seguros y costosos
                         #deprecated=auto: actuliza los hashes viejos de manera automatica cuando el usuario inicia sesion
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Logica del hashing
def obtener_password_hash(password: str):
        #transforma texto plano en hash ilegible
        return pwd_context.hash(password)
def verificar_password(password_plana: str, password_hasheada: str):
    #compara la contraseña ingresada con el hash guardado.
    return pwd_context.verify(password_plana, password_hasheada)'''
    
#---GENERADOR DE TOKENS---
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    
    #crea un token firmado con un tiempo de vida definido
    to_encode = data.copy()
    
    #se usa la zona horaria explicita
    ahora = datetime.now(timezone.utc)
    
    #Calculamos el tiempo de expiracion
    if expires_delta:
        expire = ahora + expires_delta
    else:
        expire = ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 

    #Se añade el claim de expiracion al payload
    to_encode.update({"exp":expire})
    
    #Firmamos el token con nuestra SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#---VALIDADOR DE TOKENS---
def verificar_token(token: str):
     #decodifica y validad la integridad del token
     try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         username : str = payload.get("sub")
         if username is None:
             return None
         return payload #se retorna el payload si todo esta correcto
     except JWTError:
         return None