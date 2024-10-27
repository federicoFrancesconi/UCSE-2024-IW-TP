FROM python:3.10-slim

# Le pasa variables de entorno para Django
ENV PYTHONUNBUFFERED 1
ENV DOCKER=True
ENV DJANGO_SETTINGS_MODULE=DescuentAr.settings
# Indicamos la ubicación de la db, que ya no es la default de Django
ENV DATABASE_PATH=/data/db.sqlite3

# Creamos directorios (app_grupo4 y data) dentro del contenedor
# Lo hacemos en la misma linea para que no le agregue una layer innecesaria a la imagen
RUN mkdir /app_grupo4 /data

# Hacemos que el directorio base para todo sea /app_grupo4
WORKDIR /app_grupo4

# Copiamos el directorio del proyecto en Django al directorio base
COPY DescuentAr /app_grupo4/DescuentAr

# Movemos la base de datos a /data, que será usado para el volumen persistente
RUN mv DescuentAr/db.sqlite3 /data

# Copia el requirements.txt e instala las dependencias
COPY requirements.txt /app_grupo4
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

CMD python DescuentAr/manage.py migrate; \
    python DescuentAr/manage.py loaddata fixtures/accounts.json; \
    python DescuentAr/manage.py loaddata fixtures/sitio.json; \
    python DescuentAr/manage.py rebuild_index --noinput; \
    python DescuentAr/manage.py runserver 0.0.0.0:8000;