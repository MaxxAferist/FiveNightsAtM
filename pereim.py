import datetime

a = datetime.datetime(2021, 12, 12, 3, 43, 2)
b = datetime.datetime.now() - a
print(b.total_seconds())