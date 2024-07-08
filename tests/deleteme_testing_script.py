from distutils.command.clean import clean
from urllib import response
import requests
import json

from shapely import Point, Polygon, MultiPolygon, to_geojson, from_geojson
from pydantic_geojson import PointModel, PolygonModel, MultiPolygonModel
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
import shapely

base_url = 'http://localhost:8204/'

cleanup = True
if cleanup:
    resp = requests.get(base_url + '/event', params={'active': 'ALL'})
    g2 = resp.json()
    for event in resp.json()['events']:
        del_resp = requests.delete(base_url + f"/event/{event['uid']}")
# # resp = requests.get(base_url)
# coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
# polygon = Polygon(coords)
# polygon_str = to_geojson(polygon)
# geojson = json.loads(polygon_str)
# wkt = from_geojson(polygon_str)

# x=1
# a = PolygonModel(**geojson)
# b = a.model_dump_json()
# c = from_geojson(b)
# d = Geometry(b)
# e = str(c)
# # c = polygon.wkt
# # c = Polygon(geojson)
# # d = c.wkt
# # c = Geometry(geometry=a)
poly = Point(0.5, 0.5)
geojson = json.loads(to_geojson(poly))
a = from_shape(poly)
b = to_shape(a)
# print(type(b))
# c = PolygonModel(b)
c = PointModel(**json.loads(to_geojson(b)))
# c = PointModel(**geojson)
# print(type(c))
# b = to_shape(poly)
x=1

poly = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.)))
geojson = json.loads(to_geojson(poly))
a = from_shape(poly)
b = to_shape(a)
c = PolygonModel(**json.loads(to_geojson(b)))
aa = ['01030000000100000005000000000000000000000000000000000000000000000000000000000000000000f03f000000000000f03f000000000000f03f000000000000f03f000000000000000000000000000000000000000000000000']
# ab = to_shape(aa)
# ab = shapely.wkt.loads(aa[0])
x=1

create_payload = {
    "description": "A description of the event",
    "active": True,
    "name": "GAME",
    "venue": "Stadium",
    "location": geojson,
    "source": "Testing",
}
# print(f'FIRST GEOM: [{create_payload["location"]}]')
resp = requests.post(base_url + '/event', json=create_payload)
a = resp.json()
# print(a)
# print(f'SECOND GEOM: [{a["location"]}]')


query_poly = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.)))
# query_poly = Polygon(((10., 0.), (10., 1.), (11., 1.), (11., 0.), (10., 0.)))
wkt = query_poly.wkt
new_poly = shapely.wkt.loads(wkt)
new_obj = PolygonModel(**json.loads(to_geojson(new_poly)))
new_just_poly = from_geojson(new_obj.model_dump_json())
# print(type(new_just_poly))
# aaa = from_shape(query_poly)
# bbb = to_shape(aaa)
query_params = {
    'name': 'GAME',
    'location': query_poly.wkt,
}
x=1
resp = requests.get(base_url + '/event', params=query_params)
b = resp.json()
lr = len(b['events'])
# print(b)
focus_event = b['events'][0]
event_uid = focus_event['uid']
# print(f'THIRD GEOM: [{focus_event["location"]}]')


resp = requests.get(base_url + f'/event/{event_uid}')
c = resp.json()
# print(c)

focus_event['name'] = 'SHOW'
# print(f'FOURTH GEOM: [{focus_event["location"]}]')

resp = requests.put(base_url + f'/event/{event_uid}', json=focus_event)
d = resp.json()
# print(d)

resp = requests.put(base_url + f'/event/{event_uid}/activate')
e = resp.json()
# print(e)

resp = requests.put(base_url + f'/event/{event_uid}/deactivate')
f = resp.json()
# print(f)

resp = requests.get(base_url + '/event')
g = resp.json()
# lr = len(b['events'])

query_params = {
    'active': 'ALL',
}
x=1
resp = requests.get(base_url + '/event', params=query_params)
g2 = resp.json()
# lr = len(b['events'])

resp = requests.put(base_url + f'/event/{event_uid}/activate')
h = resp.json()
# print(h)

resp = requests.get(base_url + '/event')
i = resp.json()
lr = len(i['events'])

x=1
