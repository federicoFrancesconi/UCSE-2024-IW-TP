FROM python:3.10-slim

# Le pasa variables de entorno para Django
ENV PYTHONUNBUFFERED 1
ENV DOCKER=True
ENV DJANGO_SETTINGS_MODULE=DescuentAr.settings

# Creamos directorios (app_grupo4 y data) dentro del contenedor
# Lo hacemos en la misma linea para que no le agregue una layer innecesaria a la imagen
RUN mkdir /app_grupo4 /data

# Hacemos que el directorio base para todo sea /app_grupo4
WORKDIR /app_grupo4

# Copiamos todo al directorio base
COPY . /app_grupo4

# Instala las dependencias del requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

CMD python DescuentAr/manage.py migrate; \
    python DescuentAr/manage.py loaddata fixtures/accounts.json; \
    python DescuentAr/manage.py loaddata fixtures/sitio.json; \
    python DescuentAr/manage.py rebuild_index --noinput; \
    python DescuentAr/manage.py runserver 0.0.0.0:8000;