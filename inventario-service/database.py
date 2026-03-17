from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la conexión
DATABASE_URL = "sqlite:///./inventario.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la Tabla
class ProductoDB(Base):
    __tablename__ = "productos"
    id = Column(String, primary_key=True, index=True)
    stock = Column(Integer, default=0)

# Dependencia para la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
Utilizo yield para administrar la conexión a SQLite de forma eficiente.
Esto me permite inyectar la sesión de la base de datos en cada ruta,
usarla para procesar la información y garantizar que la conexión se cierre automáticamente
al finalizar la operación, manteniendo el sistema estable y limpio.
"""
# Inicializador de la DB
def init_db():
    Base.metadata.create_all(bind=engine)