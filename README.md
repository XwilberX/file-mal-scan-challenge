# File Malware Scanner

API para escanear archivos en busca de malware usando VirusTotal.

## Características

- Escaneo de archivos usando VirusTotal API
- Autenticación JWT
- Base de datos PostgreSQL
- Interfaz Swagger UI para documentación y pruebas
- Docker para despliegue

## Requisitos

- Docker y Docker Compose
- Una clave API de VirusTotal (puedes obtenerla en [VirusTotal Community](https://www.virustotal.com/gui/join-us))

## Configuración

1. Clona este repositorio:
   ```
   git clone git@github.com:XwilberX/file-mal-scan-challenge.git
   cd file-mal-scan-challenge
   ```

2. Crea un archivo `.env` basado en `.env.template`:
   ```
   cp .env.template .env
   ```

3. Edita el archivo `.env` y reemplaza:
   - `your_secret_key_here` con una clave secreta para JWT
   - `your_virustotal_api_key_here` con tu clave API de VirusTotal

## Estructura del proyecto

```
.
├── src/                    # Código fuente
│   ├── api/                # Endpoints de la API
│   │   ├── auth/           # Autenticación
│   │   ├── scans/          # Escaneo de archivos
│   │   └── users/          # Gestión de usuarios
│   ├── core/               # Configuración y utilidades
│   └── migrations/         # Migraciones de base de datos
├── scripts/                # Scripts útiles
├── alembic.ini             # Configuración de Alembic
├── docker-compose.yml      # Configuración de Docker Compose
├── Dockerfile              # Configuración de Docker
├── pyproject.toml          # Dependencias del proyecto
└── .env.template           # Plantilla de variables de entorno
```

## Ejecución con Docker

```bash
# Construir y levantar los contenedores
docker compose up -d

# Verificar logs
docker compose logs -f

# Detener los contenedores
docker compose down
```

La API estará disponible en: `http://localhost:8080`
La documentación Swagger: `http://localhost:8080/docs`


## Guía de uso de la API

A continuación se presenta un flujo completo de uso de la API utilizando curl:

### 1. Crear un usuario

```bash
curl -X 'POST' \
  'http://localhost:8080/api/v1/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User",
  "is_active": true
}'
```

Respuesta:
```json
{
  "status": {
    "code": 201,
    "message": "User created successfully"
  },
  "data": {
    "email": "test@example.com",
    "is_active": true,
    "full_name": "Test User",
    "is_superuser": false,
    "pkid": 4,
    "created_at": "2025-05-21T17:30:21.585397",
    "updated_at": "2025-05-21T17:30:21.586851"
  }
}
```

### 2. Obtener token de autenticación

```bash
curl -X 'POST' \
  'http://localhost:8080/api/v1/auth/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'email=test@example.com&password=password123'
```

Respuesta:
```json
{
  "status": {
    "code": 200,
    "message": "Authentication successful"
  },
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc4NTE3MDIuODMzMjE3LCJzdWIiOiI0In0.hs0jfW5YxnqkF4szbHfcpIMMHsKL3PkW0m7bBsVCZHA",
    "token_type": "bearer",
    "expires_at": "2025-05-21T18:01:42.833217"
  }
}
```

### 3. Subir un archivo para análisis

```bash
# Crear un archivo de ejemplo
echo "<?php echo 'Archivo de prueba PHP'; ?>" > test_file.php

# Subir el archivo
curl -X 'POST' \
  'http://localhost:8080/api/v1/scans/upload' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc4NTE3MDIuODMzMjE3LCJzdWIiOiI0In0.hs0jfW5YxnqkF4szbHfcpIMMHsKL3PkW0m7bBsVCZHA' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test_file.php'
```

Respuesta:
```json
{
  "status": {
    "code": 201,
    "message": "File uploaded and submitted for analysis"
  },
  "data": {
    "pkid": 13,
    "filename": "test_file.php",
    "original_filename": "test_file.php",
    "file_size": 39,
    "file_type": "application/octet-stream",
    "md5_hash": "5395dfafdb40067f6705797f76f24fb6",
    "sha1_hash": "1c577649c9356688f6d39bd5934df6670ba01ad8",
    "sha256_hash": "1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a",
    "status": "scanning",
    "scan_id": "NTM5NWRmYWZkYjQwMDY3ZjY3MDU3OTdmNzZmMjRmYjY6MTc0Nzg0OTk4NA==",
    "scan_date": "2025-05-21T17:53:04.308227",
    "result_date": null,
    "positives": null,
    "total_scans": null,
    "error_message": null,
    "created_at": "2025-05-21T17:53:03.753830",
    "updated_at": "2025-05-21T17:53:04.310225"
  }
}
```

### 4. Obtener resultados del análisis

```bash
curl -X 'GET' \
  'http://localhost:8080/api/v1/scans/13' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc4NTE3MDIuODMzMjE3LCJzdWIiOiI0In0.hs0jfW5YxnqkF4szbHfcpIMMHsKL3PkW0m7bBsVCZHA'
```

Respuesta (resumida):
```json
{
  "status": {
    "code": 200,
    "message": "Scan results retrieved successfully"
  },
  "data": {
    "pkid": 13,
    "filename": "test_file.php",
    "original_filename": "test_file.php",
    "file_size": 39,
    "file_type": "application/octet-stream",
    "md5_hash": "5395dfafdb40067f6705797f76f24fb6",
    "sha1_hash": "1c577649c9356688f6d39bd5934df6670ba01ad8",
    "sha256_hash": "1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a",
    "status": "completed",
    "scan_id": "NTM5NWRmYWZkYjQwMDY3ZjY3MDU3OTdmNzZmMjRmYjY6MTc0Nzg0OTk4NA==",
    "scan_date": "2025-05-21T17:53:04.308227",
    "result_date": "2025-05-21T17:53:14.982899",
    "positives": 0,
    "total_scans": 0,
    "error_message": null,
    "created_at": "2025-05-21T17:53:03.753830",
    "updated_at": "2025-05-21T17:53:14.985532",
    "detailed_report": {
      "id": "1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a",
      "type": "file",
      "links": {
        "self": "https://www.virustotal.com/api/v3/files/1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a"
      },
      "attributes": {
        "last_analysis_stats": {
          "malicious": 0,
          "suspicious": 0,
          "undetected": 0,
          "harmless": 0,
          "timeout": 0,
          "confirmed-timeout": 0,
          "failure": 0,
          "type-unsupported": 0
        },
        "md5": "5395dfafdb40067f6705797f76f24fb6",
        "sha1": "1c577649c9356688f6d39bd5934df6670ba01ad8",
        "sha256": "1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a",
        "size": 39
      }
    }
  }
}
```

### 5. Listar todos los escaneos

```bash
curl -X 'GET' \
  'http://localhost:8080/api/v1/scans/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc4NTE3MDIuODMzMjE3LCJzdWIiOiI0In0.hs0jfW5YxnqkF4szbHfcpIMMHsKL3PkW0m7bBsVCZHA'
```

Respuesta:
```json
{
  "status": {
    "code": 200,
    "message": "Scans retrieved successfully"
  },
  "data": [
    {
      "pkid": 13,
      "filename": "test_file.php",
      "original_filename": "test_file.php",
      "file_size": 39,
      "file_type": "application/octet-stream",
      "md5_hash": "5395dfafdb40067f6705797f76f24fb6",
      "sha1_hash": "1c577649c9356688f6d39bd5934df6670ba01ad8",
      "sha256_hash": "1db4a821b626790696af0a988e9c9bed5ab5fbce32475006b831cb18be774f2a",
      "status": "completed",
      "scan_id": "NTM5NWRmYWZkYjQwMDY3ZjY3MDU3OTdmNzZmMjRmYjY6MTc0Nzg0OTk4NA==",
      "scan_date": "2025-05-21T17:53:04.308227",
      "result_date": "2025-05-21T17:53:14.982899",
      "positives": 0,
      "total_scans": 0,
      "error_message": null,
      "created_at": "2025-05-21T17:53:03.753830",
      "updated_at": "2025-05-21T17:53:14.985532"
    }
  ]
}
```

## Autenticación

Para obtener un token JWT:

1. Crea un usuario con el endpoint `/api/v1/users/`
2. Obtén un token con el endpoint `/api/v1/auth/token`
3. Usa el token en el header `Authorization: Bearer {token}`

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| API_PORT | Puerto de la API | 8080 |
| SECRET_KEY | Clave secreta para JWT | - |
| ENVIRONMENT | Entorno de ejecución | local |
| DB_HOST | Host de la base de datos | postgres |
| DB_PORT | Puerto de la base de datos | 5432 |
| DB_USER | Usuario de la base de datos | postgres |
| DB_PASSWORD | Contraseña de la base de datos | postgres |
| DB_NAME | Nombre de la base de datos | file_scanner |
| VIRUSTOTAL_API_KEY | Clave API de VirusTotal | - |
| MAX_FILE_SIZE | Tamaño máximo de archivo en MB | 32 |

## Extensiones de archivo permitidas

- Ejecutables: `exe`, `dll`, `sys`
- Scripts: `js`, `py`, `php`, `sh`, `bat`
- Documentos: `pdf`, `doc`, `docx`, `xls`, `xlsx`
- Comprimidos: `zip`, `rar`, `7z`, `tar`, `gz`