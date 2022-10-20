python manage.py migrate --noinput && \
python manage.py collectstatic --no-input && \
python manage.py data_loading && \
gunicorn foodgram.wsgi:application --bind 0:8000