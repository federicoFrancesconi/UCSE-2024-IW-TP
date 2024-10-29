FROM python:3.10-slim

# Le pasa variables de entorno para Django
ENV PYTHONUNBUFFERED 1
ENV DOCKER=True
ENV DJANGO_SETTINGS_MODULE=DescuentAr.settings

# Indicamos la ubicación de la db, que ya no es la default de Django
ENV DATABASE_PATH=/data/db.sqlite3

# Creamos el directorio /app_grupo4 en el root de la imagen
RUN mkdir /app_grupo4

# Hacemos que el directorio base para todo sea /app_grupo4
WORKDIR /app_grupo4

# Copiamos el directorio del proyecto en Django al directorio base
COPY DescuentAr /app_grupo4/DescuentAr

# Copia el requirements.txt e instala las dependencias
COPY requirements.txt /app_grupo4
RUN pip install --no-cache-dir -r requirements.txt

# Ahora cambiamos el directorio base dentro del mismo proyecto de Django
WORKDIR /app_grupo4/DescuentAr

# Ahora sí, creamos el directorio para la base de datos
RUN mkdir /data

# Expone el puerto 8000
EXPOSE 8000

# Corremos varios comandos, para crear la db, cargarle data, reindexar la busqueda, y levantar el server
CMD python manage.py migrate; \
    python manage.py loaddata fixtures/accounts.json; \
    python manage.py loaddata fixtures/sitio.json; \
    python manage.py rebuild_index --noinput; \
    python manage.py runserver 0.0.0.0:8000; \