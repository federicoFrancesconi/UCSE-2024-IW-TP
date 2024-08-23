# exit on error
set -o errexit

pip install -r ./requirements.txt

cd $(dirname $(find . | grep manage.py$))
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --username admin --email "fedefrancesconiff@gmail.com" --noinput || true

# Create user 'fisa' with password 'Superfisa99'
echo "from django.contrib.auth.models import User; \
if not User.objects.filter(username='fisa').exists(): \
    User.objects.create_user('fisa', password='Superfisa99'); \
    print('User fisa created') \
else: \
    print('User fisa already exists')" \
| python manage.py shell