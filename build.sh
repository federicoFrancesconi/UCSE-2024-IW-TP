# exit on error
set -o errexit

pip install -r ./requirements.txt

cd $(dirname $(find . | grep manage.py$))
python manage.py collectstatic --no-input
python manage.py migrate

if [ "$CREATE_SUPERUSER" == "true" ]; then
    python manage.py createsuperuser --username fisa --email "fisadev@gmail.com" --noinput || true
fi

# Carga de descuentos
python manage.py loaddata accounts.json
python manage.py loaddata sitio.json