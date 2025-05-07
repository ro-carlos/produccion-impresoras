FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorio de datos
RUN mkdir -p data

# Exponer puertos para API y Streamlit
EXPOSE 8000 8501

# Comando por defecto para iniciar la aplicación completa
CMD ["python", "main.py"]
