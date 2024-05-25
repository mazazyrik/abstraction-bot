from peewee import PostgresqlDatabase, Model, CharField, BooleanField, IntegerField

db = PostgresqlDatabase('postgres', user='postgres', password='1234',
                        host='localhost', port=5432)


class Guest(Model):
    username = CharField()
    user_id = IntegerField()
    made_speech = BooleanField(default=False)

    class Meta:
        database = db


class UserAuth(Model):
    username = CharField()
    premium = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    user_id = IntegerField()

    class Meta:
        database = db


db.create_tables([UserAuth, Guest])
