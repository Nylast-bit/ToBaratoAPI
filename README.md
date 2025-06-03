# 🛒 To' Barato API

<div align="center">
  <img src="app/logo.png" alt="To' Barato Logo" width="200"/>
  <br>
  <strong>API de la aplicación de proyecto final universitario "To' Barato"</strong>
  <br>
  <em>Sistema de comparación de precios para ayudar a los consumidores a encontrar los mejores precios en productos de uso diario</em>
  <br><br>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
  [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.40-red?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
  [![Alembic](https://img.shields.io/badge/Alembic-Migrations-blue?style=for-the-badge)](https://alembic.sqlalchemy.org)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  
</div>

## 📋 Índice

- [📝 Descripción](#-descripción)
- [✨ Características](#-características)
- [🛠️ Tecnologías](#️-tecnologías)
- [🚀 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [💻 Uso](#-uso)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [📊 API Endpoints](#-api-endpoints)
- [🔄 Migraciones de Base de Datos](#-migraciones-de-base-datos)
- [🐳 Docker](#-docker)
- [🧪 Tests](#-tests)
- [👥 Contribución](#-contribución)
- [📜 Licencia](#-licencia)

## 📝 Descripción

**To' Barato API** es el backend que sustenta la aplicación "To' Barato", diseñada para permitir a los usuarios comparar precios de productos de consumo diario entre diferentes proveedores y localizar las mejores ofertas. Este servicio facilita:

- Búsqueda y comparación de precios entre múltiples proveedores
- Creación y gestión de listas de compras personalizadas
- Sistema de registro y autenticación de usuarios
- Perfiles para proveedores y usuarios regulares
- Geolocalización de sucursales y proveedores

La API está construida con FastAPI para ofrecer un servicio rápido y documentado automáticamente, utilizando PostgreSQL como base de datos.

## ✨ Características

- **Autenticación JWT**: Sistema seguro con tokens de acceso y refresco
- **Verificación OTP**: Autenticación de dos factores para mayor seguridad
- **Operaciones CRUD**: Gestión completa de usuarios, productos, proveedores y más
- **Migraciones**: Control de versiones de la base de datos con Alembic
- **Asincronía**: Operaciones asíncronas para mejor rendimiento
- **Documentación automática**: Endpoints documentados con Swagger UI
- **Validación de datos**: Esquemas Pydantic para garantizar integridad de datos
- **Geolocalización**: Integración con servicios de ubicación

## 🛠️ Tecnologías

- **Lenguaje Principal:** Python (99.1%)
- **Framework Web:** FastAPI
- **ORM:** SQLAlchemy + SQLModel
- **Base de Datos:** PostgreSQL con AsyncPG
- **Migraciones:** Alembic
- **Autenticación:** JWT + Bcrypt
- **Validación:** Pydantic
- **Comunicación:** SMTP (para envío de códigos OTP)
- **Geolocalización:** GeoPy
- **Entorno:** Docker

## 🚀 Instalación

### Prerrequisitos

- Python 3.11 o superior
- PostgreSQL 15 o superior
- Git

### Pasos de instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Nylast-bit/ToBaratoAPI.git
   ```

2. Navega al directorio del proyecto:
   ```bash
   cd ToBaratoAPI
   ```

3. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración

### Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Base de datos
DB_USER=usuario_db
DB_PASSWORD=contraseña_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tobarato_db
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# JWT
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=60

# SMTP para envío de correos
MAIL_USERNAME=tu_correo@example.com
MAIL_PASSWORD=tu_contraseña
MAIL_FROM=tu_correo@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

## 💻 Uso

### Iniciar el servidor en modo desarrollo

Para iniciar la API con recarga automática (modo desarrollo):

```bash
python -m uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8888`

### Documentación de la API

Una vez iniciado el servidor, accede a la documentación automática:

- **Swagger UI**: `http://localhost:8888/docs`
- **ReDoc**: `http://localhost:8888/redoc`

## 📁 Estructura del Proyecto

```
ToBaratoAPI/
├── alembic.ini                 # Configuración de Alembic
├── dockerfile                  # Configuración de Docker
├── main.py                     # Punto de entrada principal
├── README.md                   # Este documento
├── requirements.txt            # Dependencias del proyecto
├── app/
│   ├── __init__.py
│   ├── database.py             # Configuración de la base de datos
│   ├── dependencies.py         # Dependencias de FastAPI
│   ├── logo.png                # Logo de la aplicación
│   ├── main.py                 # Aplicación FastAPI
│   ├── utils.py                # Funciones de utilidad
│   ├── auth/                   # Módulo de autenticación
│   ├── models/                 # Modelos de base de datos
│   ├── routes/                 # Rutas de la API
│   └── schemas/                # Esquemas Pydantic
├── migrations/                 # Migraciones de Alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/               # Versiones de migraciones
└── scripts/                    # Scripts de utilidad
    └── resetbd.py              # Script para resetear la BD
```

## 📊 API Endpoints

La API ofrece múltiples endpoints organizados por categorías:

### Autenticación y Usuarios

- `POST /api/usuarios/register`: Registro de nuevo usuario
- `POST /api/usuarios/login`: Iniciar sesión
- `POST /api/usuarios/token/refresh`: Refrescar token de acceso
- `GET /api/usuarios/me`: Obtener información del usuario actual
- `PUT /api/usuarios/{id}`: Actualizar información de usuario
- `DELETE /api/usuarios/{id}`: Eliminar usuario

### Productos

- `GET /api/productos`: Listar todos los productos
- `GET /api/productos/{id}`: Obtener detalle de un producto
- `POST /api/productos`: Crear nuevo producto
- `PUT /api/productos/{id}`: Actualizar producto
- `DELETE /api/productos/{id}`: Eliminar producto

### Proveedores

- `GET /api/proveedores`: Listar todos los proveedores
- `GET /api/proveedores/{id}`: Obtener detalle de un proveedor
- `POST /api/proveedores`: Crear nuevo proveedor
- `PUT /api/proveedores/{id}`: Actualizar proveedor
- `DELETE /api/proveedores/{id}`: Eliminar proveedor

### Sucursales

- `GET /api/sucursales`: Listar todas las sucursales
- `GET /api/sucursales/cercanas`: Encontrar sucursales cercanas
- `POST /api/sucursales`: Crear nueva sucursal
- `PUT /api/sucursales/{id}`: Actualizar sucursal
- `DELETE /api/sucursales/{id}`: Eliminar sucursal

### Listas de Compras

- `GET /api/listas`: Obtener listas de un usuario
- `POST /api/listas`: Crear lista de compras
- `PUT /api/listas/{id}`: Actualizar lista
- `DELETE /api/listas/{id}`: Eliminar lista
- `POST /api/listaproductos`: Añadir producto a lista
- `DELETE /api/listaproductos/{id}`: Eliminar producto de lista

## 🔄 Migraciones de Base de Datos

### Generar nueva migración

```bash
alembic revision --autogenerate -m "descripción de cambios"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Revertir migración

```bash
alembic downgrade -1
```

## 🐳 Docker

Para construir y ejecutar la API con Docker:

```bash
# Construir la imagen
docker build -t tobarato-api .

# Ejecutar contenedor
docker run -d --name tobarato-api -p 8000:8000 tobarato-api
```

Para utilizar Docker Compose (si se requiere en el futuro):

```bash
docker-compose up -d
```

## 🧪 Tests

Para ejecutar las pruebas (cuando estén disponibles):

```bash
# Usar pytest cuando esté configurado
pytest
```

## 👥 Contribución

1. Haz fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/amazing-feature`
3. Realiza tus cambios y haz commit: `git commit -m 'feat: add amazing feature'`
4. Empuja a la rama: `git push origin feature/amazing-feature`
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

<div align="center">
  <p>Desarrollado como proyecto de grado - Universidad [Nombre de la Universidad]</p>
  <p>© 2025 To' Barato. Todos los derechos reservados.</p>
</div>
