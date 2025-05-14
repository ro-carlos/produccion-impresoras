# Guía de Despliegue
## Simulador de Producción de Impresoras 3D

Esta guía proporciona instrucciones detalladas para desplegar el Simulador de Producción de Impresoras 3D en diferentes entornos. Incluye los pasos necesarios para instalar, configurar y ejecutar tanto la aplicación completa como sus componentes individuales.

## Índice

1. [Requisitos Previos](#1-requisitos-previos)
2. [Despliegue con Docker](#2-despliegue-con-docker)
3. [Despliegue Manual](#3-despliegue-manual)
4. [Configuración del Sistema](#4-configuración-del-sistema)
5. [Inicialización de la Base de Datos](#5-inicialización-de-la-base-de-datos)
6. [Actualización del Sistema](#6-actualización-del-sistema)
7. [Monitorización y Logs](#7-monitorización-y-logs)
8. [Backup y Restore](#8-backup-y-restore)
9. [Despliegue en Producción](#9-despliegue-en-producción)
10. [Resolución de Problemas](#10-resolución-de-problemas)

## 1. Requisitos Previos

### 1.1 Requisitos Mínimos de Hardware

- **CPU**: 2 núcleos o más
- **RAM**: 2 GB mínimo, 4 GB recomendado
- **Almacenamiento**: 500 MB para la aplicación y base de datos
- **Red**: Conexión a Internet para descargar dependencias durante la instalación

### 1.2 Software Requerido

#### Para Despliegue con Docker:
- **Docker**: versión 20.10.0 o superior
- **Docker Compose**: versión 2.0.0 o superior
- **Sistema Operativo**: Cualquiera compatible con Docker (Linux, macOS, Windows)

#### Para Despliegue Manual:
- **Python**: versión 3.11 o superior
- **pip**: gestor de paquetes de Python actualizado
- **Git**: para clonar el repositorio (opcional)
- **Sistema Operativo**: Linux, macOS, Windows

## 2. Despliegue con Docker

El despliegue con Docker es la forma recomendada, ya que garantiza un entorno consistente y aislado.

### 2.1 Instalación de Docker

Siga las instrucciones oficiales para instalar Docker y Docker Compose en su sistema:
- [Instalar Docker](https://docs.docker.com/get-docker/)
- [Instalar Docker Compose](https://docs.docker.com/compose/install/)

### 2.2 Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/mrp-dgsi.git
cd mrp-dgsi
```

Si no tiene Git, puede descargar el código fuente como archivo ZIP desde el repositorio.

### 2.3 Configuración (Opcional)

Puede personalizar la configuración editando los archivos:
- `.env`: Variables de entorno para Docker
- `data/config.json`: Configuración de la simulación

### 2.4 Construir y Ejecutar con Docker Compose

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios en modo detached (background)
docker-compose up -d
```

### 2.5 Verificar Instalación

- **Interfaz Web**: Acceda a `http://localhost:8501` en su navegador
- **API REST**: Acceda a `http://localhost:8000/api/docs` para ver la documentación Swagger

### 2.6 Detener los Servicios

```bash
# Detener manteniendo los volúmenes
docker-compose down

# Detener y eliminar volúmenes (borra la base de datos)
docker-compose down -v
```

## 3. Despliegue Manual

El despliegue manual ofrece mayor control y es útil para desarrollo o entornos sin Docker.

### 3.1 Preparar el Entorno

#### En Linux/macOS:
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/mrp-dgsi.git
cd mrp-dgsi

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### En Windows:
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/mrp-dgsi.git
cd mrp-dgsi

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3.2 Inicializar la Base de Datos

```bash
# Ejecutar script de inicialización
python scripts/init_db.py
```

### 3.3 Ejecutar los Componentes

#### Iniciar API REST:
```bash
# En una terminal
uvicorn presentation.api:app --host 0.0.0.0 --port 8000
```

#### Iniciar Interfaz Web:
```bash
# En otra terminal (con el entorno virtual activado)
streamlit run presentation/streamlit_app.py
```

### 3.4 Acceder a la Aplicación

- **Interfaz Web**: Acceda a `http://localhost:8501` en su navegador
- **API REST**: Acceda a `http://localhost:8000/api/docs` para ver la documentación Swagger

## 4. Configuración del Sistema

### 4.1 Variables de Entorno

El sistema puede configurarse mediante variables de entorno:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_PATH` | Ruta a la base de datos SQLite | `./data/simulator.db` |
| `API_HOST` | Host para la API REST | `0.0.0.0` |
| `API_PORT` | Puerto para la API REST | `8000` |
| `UI_PORT` | Puerto para la interfaz Streamlit | `8501` |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `CORS_ORIGINS` | Orígenes permitidos para CORS (separados por comas) | `*` |

### 4.2 Archivo de Configuración JSON

La configuración de la simulación se almacena en `data/config.json`:

```json
{
  "production_capacity": 10,
  "demand": {
    "mean": 7,
    "variance": 2
  },
  "initial_stock": {
    "raw_materials": {
      "kit_piezas": 30,
      "pcb_v2": 20,
      "pcb_v3": 10,
      "extrusor": 25,
      "sensor_autonivel": 15,
      "cables_conexion": 50,
      "transformador_24v": 20,
      "enchufe_schuko": 30
    },
    "finished_products": {
      "P3D-Classic": 0,
      "P3D-Pro": 0
    }
  }
}
```

#### Parámetros de Configuración:

- **production_capacity**: Número máximo de impresoras que se pueden fabricar por día
- **demand.mean**: Media de la distribución normal para la generación de demanda
- **demand.variance**: Varianza de la distribución para la generación de demanda
- **initial_stock**: Inventario inicial de materiales y productos

### 4.3 Configuración de Docker Compose

El archivo `docker-compose.yml` define los servicios y su configuración:

```yaml
version: '3.8'

services:
  app:
    build: .
    command: streamlit run presentation/streamlit_app.py
    volumes:
      - ./data:/app/data
    ports:
      - "8501:8501"
    environment:
      - DB_PATH=/app/data/simulator.db
      - API_URL=http://api:8000
    depends_on:
      - api

  api:
    build: .
    command: uvicorn presentation.api:app --host 0.0.0.0 --port 8000
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    environment:
      - DB_PATH=/app/data/simulator.db
```

Puede modificar puertos, volúmenes y variables de entorno según sus necesidades.

## 5. Inicialización de la Base de Datos

### 5.1 Estructura de la Base de Datos

La base de datos SQLite se inicializa con las siguientes tablas:
- `products`: Productos y materias primas
- `bom`: Lista de materiales (Bill of Materials)
- `suppliers`: Proveedores
- `stock_current`: Inventario actual
- `manufacturing_orders`: Pedidos de fabricación
- `purchase_orders`: Órdenes de compra
- `events`: Registro de eventos
- `simulation_state`: Estado actual de la simulación

### 5.2 Inicialización Automática

#### Con Docker:
La base de datos se inicializa automáticamente la primera vez que se ejecuta el contenedor, si no existe.

#### Manual:
```bash
# Ejecutar script de inicialización
python scripts/init_db.py
```

### 5.3 Datos de Prueba (Opcional)

Para cargar datos de prueba:

```bash
# Ejecutar script con datos de prueba
python scripts/load_test_data.py
```

### 5.4 Reiniciar la Base de Datos

Si necesita reiniciar la base de datos a su estado inicial:

```bash
# Eliminar base de datos existente
rm data/simulator.db

# Volver a inicializar
python scripts/init_db.py
```

## 6. Actualización del Sistema

### 6.1 Actualización con Docker

```bash
# Detener los servicios
docker-compose down

# Obtener la última versión del código
git pull

# Reconstruir las imágenes
docker-compose build

# Iniciar los servicios actualizados
docker-compose up -d
```

### 6.2 Actualización Manual

```bash
# Obtener la última versión
git pull

# Actualizar dependencias
pip install -r requirements.txt

# Aplicar migraciones si existen (opcional)
python scripts/migrate_db.py
```

### 6.3 Migración de Datos

Si la actualización incluye cambios en el esquema de la base de datos:

```bash
# Respaldar datos actuales
python scripts/export_import.py --export --output data/backup.json

# Actualizar esquema
python scripts/migrate_db.py

# Restaurar datos (si es compatible)
python scripts/export_import.py --import --input data/backup.json
```

## 7. Monitorización y Logs

### 7.1 Logs del Sistema

#### Con Docker:
```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs api

# Seguir logs en tiempo real
docker-compose logs -f
```

#### Manual:
Los logs se almacenan en el archivo `simulator.log` en el directorio raíz del proyecto.

### 7.2 Niveles de Logging

El nivel de detalle de los logs puede configurarse mediante la variable de entorno `LOG_LEVEL`:
- `DEBUG`: Información detallada para depuración
- `INFO`: Información general sobre el funcionamiento (por defecto)
- `WARNING`: Solo advertencias y errores
- `ERROR`: Solo errores

### 7.3 Monitorización de la Base de Datos

Para examinar la base de datos directamente:

```bash
# Instalar herramienta SQLite
sqlite3 data/simulator.db

# Ejemplos de consultas útiles
sqlite> .tables
sqlite> SELECT * FROM simulation_state;
sqlite> SELECT * FROM stock_current;
```

## 8. Backup y Restore

### 8.1 Respaldo de la Base de Datos

#### Respaldo completo:
```bash
# Copiar archivo de base de datos
cp data/simulator.db data/simulator_backup_$(date +%Y%m%d).db
```

#### Exportación a JSON:
```bash
# Exportar datos en formato JSON
python scripts/export_import.py --export --output data/backup_$(date +%Y%m%d).json
```

### 8.2 Restauración de Datos

#### Restaurar desde archivo de base de datos:
```bash
# Detener la aplicación primero
cp data/simulator_backup_20240501.db data/simulator.db
```

#### Restaurar desde JSON:
```bash
# Importar datos desde JSON
python scripts/export_import.py --import --input data/backup_20240501.json
```

### 8.3 Respaldo Automatizado

Para configurar respaldos automatizados, puede utilizar un cron job (Linux/macOS) o una tarea programada (Windows):

#### Ejemplo de cron job (Linux):
```bash
# Añadir al crontab (ejecutar 'crontab -e')
0 0 * * * cd /ruta/a/mrp-dgsi && python scripts/export_import.py --export --output /backups/simulator_$(date +\%Y\%m\%d).json
```

## 9. Despliegue en Producción

### 9.1 Consideraciones de Seguridad

Para un entorno de producción, debe tener en cuenta:

1. **HTTPS**: Utilice un reverse proxy como Nginx o Traefik para habilitar HTTPS
2. **Autenticación**: Implemente un sistema de autenticación para proteger el acceso
3. **Limitación de puertos**: No exponga la aplicación directamente a Internet
4. **Regular backups**: Configure respaldos automatizados regulares

### 9.2 Ejemplo de Configuración con Nginx

#### Archivo de configuración Nginx:
```nginx
server {
    listen 80;
    server_name simulator.tudominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name simulator.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/simulator.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/simulator.tudominio.com/privkey.pem;

    # Interfaz Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API REST
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 9.3 Despliegue en la Nube

El simulador puede desplegarse en proveedores de nube como AWS, Google Cloud o Azure.

#### Ejemplo de despliegue en AWS:

1. **Crear una instancia EC2**:
   - Amazon Linux 2 o Ubuntu Server
   - Mínimo t3.small (2 vCPU, 2 GB RAM)
   - Abrir puertos 80 y 443 en el grupo de seguridad

2. **Instalar Docker y Docker Compose**:
   ```bash
   # En Amazon Linux 2
   sudo yum update -y
   sudo amazon-linux-extras install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Clonar el repositorio y configurar**:
   ```bash
   git clone https://github.com/tu-usuario/mrp-dgsi.git
   cd mrp-dgsi
   ```

4. **Configurar volumen persistente**:
   ```bash
   # Crear directorio para datos persistentes
   mkdir -p /data/mrp-simulator
   
   # Editar docker-compose.yml para usar el volumen
   # volumes:
   #   - /data/mrp-simulator:/app/data
   ```

5. **Iniciar los servicios**:
   ```bash
   docker-compose up -d
   ```

6. **Configurar Nginx y SSL**:
   ```bash
   sudo apt-get install -y nginx certbot python3-certbot-nginx
   sudo certbot --nginx -d simulator.tudominio.com
   ```

## 10. Resolución de Problemas

### 10.1 Problemas Comunes y Soluciones

#### La aplicación no inicia
**Problema**: Error al iniciar la aplicación
**Solución**:
1. Verifique los logs: `docker-compose logs` o `cat simulator.log`
2. Compruebe que la base de datos existe y tiene permisos adecuados
3. Verifique que los puertos no estén en uso por otras aplicaciones

#### Error de conexión con la API
**Problema**: La interfaz web no puede conectarse a la API
**Solución**:
1. Verifique que el servicio de API está en ejecución
2. Compruebe la configuración de `API_URL` en la interfaz
3. Verifique que no hay problemas de red o firewall

#### Problemas de rendimiento
**Problema**: La aplicación se ejecuta lentamente
**Solución**:
1. Verifique el tamaño de la base de datos (`ls -la data/simulator.db`)
2. Considere limpiar eventos antiguos: `python scripts/clean_old_events.py`
3. Aumente los recursos de hardware

### 10.2 Diagnóstico

#### Verificar estado de los servicios:
```bash
# Con Docker
docker-compose ps

# Manual
ps aux | grep uvicorn
ps aux | grep streamlit
```

#### Verificar conectividad:
```bash
# API
curl http://localhost:8000/api/simulation/current-day

# Interfaz (debe devolver HTML)
curl http://localhost:8501
```

#### Verificar base de datos:
```bash
# Comprobar archivo
ls -la data/simulator.db

# Verificar estructura
sqlite3 data/simulator.db ".tables"
```

### 10.3 Soporte y Ayuda

Si encuentra problemas que no puede resolver:

1. Consulte los [Issues del repositorio](https://github.com/tu-usuario/mrp-dgsi/issues)
2. Cree un nuevo Issue con información detallada del problema
3. Incluya logs relevantes y pasos para reproducir el problema

Para obtener soporte empresarial, contacte a support@mrp-simulator.com

## Conclusión

Esta guía proporciona las instrucciones necesarias para desplegar, configurar y mantener el Simulador de Producción de Impresoras 3D. Siguiendo estos pasos, podrá tener el sistema funcionando en poco tiempo, ya sea para desarrollo, pruebas o producción.

Para obtener información más detallada sobre el uso del sistema, consulte el [Manual de Usuario](user_guide.md) y la [Documentación de la API](api_documentation.md).