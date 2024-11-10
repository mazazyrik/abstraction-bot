import datetime
from peewee import (
    SqliteDatabase, Model, CharField, BooleanField,
    BigIntegerField, DateTimeField, IntegerField
)

db = SqliteDatabase('database.db')


class Guest(Model):
    username = CharField()
    user_id = BigIntegerField()
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
            user.made_speech = False


class UserAuth(Model):
    id = IntegerField(primary_key=True)
    username = CharField()
    premium = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    user_id = BigIntegerField()
    expiry_date = DateTimeField()

    class Meta:
        database = db


class FileModel(Model):
    filename = CharField()
    uploaded_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


db.create_tables([UserAuth, Guest])
