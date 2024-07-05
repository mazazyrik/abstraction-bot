import datetime
from peewee import (
    PostgresqlDatabase, Model, CharField, BooleanField,
    DateTimeField, IntegerField
)

db = PostgresqlDatabase('postgres', user='postgres', password='1234',
                        host='localhost', port=5432)


class Guest(Model):
    username = CharField()
    user_id = IntegerField()
    made_speech = BooleanField(default=False)

    class Meta:
        database = db

    def create_guest(username, user_id):
        user = Guest(username=username, user_id=user_id,)
        user.expiry_date = datetime.datetime.now() + datetime.timedelta(days=7)
        user.save()

    def remove_expired_guests():
        expired_users = Guest.select().where(
            Guest.expiry_date < datetime.datetime.now())
        for user in expired_users:
            user.delete_instance()


class UserAuth(Model):
    username = CharField()
    premium = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    user_id = IntegerField()
    expiry_date = DateTimeField(null=True)

    class Meta:
        database = db

    def create_user(username, user_id):
        user = UserAuth(username=username, user_id=user_id,
                        premium=True, is_admin=False)
        user.expiry_date = datetime.datetime.now() + datetime.timedelta(
            days=30
        )
        user.save()

    def remove_expired_users():
        expired_users = UserAuth.select().where(
            UserAuth.expiry_date < datetime.datetime.now())
        for user in expired_users:
            user.delete_instance()


db.create_tables([UserAuth, Guest])
