from .app import init_celery
from .models import User, Reservation, RepeatingReservation
from celery.schedules import crontab


app = init_celery()
app.conf.imports = app.conf.imports + ("project.tasks",)
