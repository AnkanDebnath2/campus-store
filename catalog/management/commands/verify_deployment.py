"""Read-only deployment checks for Render and the configured external services."""

from importlib import import_module

import certifi
import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.urls import resolve
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from activity.mongo import MONGO_COLLECTION_NAME, MONGO_DB_NAME, MONGO_URI
from catalog.models import Book
from orders.models import Order, Review


class Command(BaseCommand):
    help = 'Run read-only deployment checks for Django and all configured services.'

    def handle(self, *args, **options):
        failures = []

        self.stdout.write(f'Django version: {django.get_version()}')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        self.stdout.write(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        self.stdout.write(f'STATIC_ROOT: {settings.STATIC_ROOT}')

        try:
            module_name, attribute = settings.WSGI_APPLICATION.rsplit('.', 1)
            application = getattr(import_module(module_name), attribute)
            if not callable(application):
                raise TypeError('WSGI application is not callable')
            self.stdout.write(self.style.SUCCESS('WSGI import: OK'))
        except Exception as exc:
            failures.append(f'WSGI import failed: {exc}')

        for alias in ('default', 'auth_db', 'orders_db'):
            try:
                from django.db import connections

                with connections[alias].cursor() as cursor:
                    cursor.execute('SELECT 1')
                    cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f'{alias} SELECT 1: OK'))
            except Exception as exc:
                failures.append(f'{alias} SELECT 1 failed: {exc}')

        try:
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                tlsCAFile=certifi.where(),
            )
            ping = client.admin.command('ping')
            if ping.get('ok') != 1:
                raise RuntimeError(f'Unexpected ping result: {ping}')
            self.stdout.write(self.style.SUCCESS('MongoDB ping: OK'))
            self.stdout.write(
                f'MongoDB target: database={MONGO_DB_NAME} collection={MONGO_COLLECTION_NAME}'
            )
        except PyMongoError as exc:
            failures.append(f'MongoDB ping failed: {exc}')

        try:
            self.stdout.write(f'Catalog books: {Book.objects.using("default").count()}')
        except Exception as exc:
            failures.append(f'Catalog count failed: {exc}')

        try:
            user_model = get_user_model()
            superusers = user_model.objects.using('auth_db').filter(
                is_superuser=True,
                is_staff=True,
                is_active=True,
            ).count()
            self.stdout.write(f'Active staff superusers: {superusers}')
        except Exception as exc:
            failures.append(f'Superuser count failed: {exc}')

        try:
            self.stdout.write(f'Orders: {Order.objects.using("orders_db").count()}')
            self.stdout.write(f'Reviews: {Review.objects.using("orders_db").count()}')
        except Exception as exc:
            failures.append(f'Order/review count failed: {exc}')

        try:
            resolve('/health/')
            self.stdout.write(self.style.SUCCESS('Health-check URL: OK'))
        except Exception as exc:
            failures.append(f'Health-check URL failed: {exc}')

        if not settings.STATIC_ROOT:
            failures.append('STATIC_ROOT is not configured.')

        if failures:
            for failure in failures:
                self.stderr.write(self.style.ERROR(failure))
            raise CommandError('Deployment verification failed.')

        self.stdout.write(self.style.SUCCESS('Deployment verification succeeded.'))
