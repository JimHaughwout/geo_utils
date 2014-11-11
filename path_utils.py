from datetime import datetime

class Point(object):

    def __init__(self, latitude, longitude, timestamp):
        self.lat = float(latitude)
        self.lng = float(longitude)
        self.dt = timestamp


p1 = Point(38, -77, datetime.now())
p2 = Point(38.1, -76.9, datetime.now())
path = []

path.append(p1)
path.append(p2)
for point in path:
    print point.lat, point.lng, point.dt

path.sort(key=lambda x: x.dt)
for point in path:
    print point.lat, point.lng, point.dt