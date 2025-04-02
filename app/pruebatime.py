
from datetime import datetime
from zoneinfo import ZoneInfo
from models.models import Usuario, UnidadMedida, Producto, TipoUsuario

ahora = datetime.now(ZoneInfo("America/La_Paz"))
print(ahora)

print("Usuario Table: ", Usuario.__table__.columns.keys())
print("UnidadMedida Table: ", UnidadMedida.__table__.columns.keys())
print("Producto Table: ", Producto.__table__.columns.keys())
print("TipoUsuario Table: ", TipoUsuario.__table__.columns.keys())