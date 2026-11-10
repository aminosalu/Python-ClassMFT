from peewee import SqliteDatabase, Model, FloatField, IntegerField, CharField, DateTimeField

db = SqliteDatabase('weather.db')


class Weather(Model):
    temp = FloatField()
    humidity = IntegerField()
    pressure = FloatField()          # فشار هوا اعشاری برمی‌گرده (مثلا 889.5)
    description = CharField(max_length=50)
    weather_code = IntegerField()    # کد WMO
    city = CharField(max_length=50)
    date = DateTimeField()

    class Meta:
        database = db
        table_name = 'weather'


Weather.create_table()
