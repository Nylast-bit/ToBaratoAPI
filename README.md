# To' Barato API

Api de la aplicación de proyecto final universidad To' Barato.

## Descripción

Este proyecto es una API desarrollada como parte del proyecto final de la universidad. La API está diseñada para servir como backend para la aplicación To' Barato.

## Tecnologías

- **Lenguaje Principal:** Python (99.1%)
- **Plantillas:** Mako (0.9%)

## Instalación

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

## Configuración de la Base de Datos

Configura las siguientes variables de entorno para conectar con la base de datos:

```bash
DB_USER=myuser
DB_PASSWORD=mypass
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
```

## Uso

Para iniciar la API, ejecuta el siguiente comando:
```bash
uvicorn main:app --host 0.0.0.0 --port 8081 --reload

```
