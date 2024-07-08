from datetime import datetime
import json
from typing import List, Dict, Any
from unittest import expectedFailure
from sqlmodel import Field, SQLModel, JSON, ARRAY, String, Column, UniqueConstraint, select
from pydantic import BaseModel, model_validator
from pydantic_geojson import PointModel, PolygonModel, MultiPolygonModel
from enum import Enum
from uuid import uuid4
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely import intersection, from_geojson
from geoalchemy2 import Geometry


from shapely import Point, Polygon, MultiPolygon, to_geojson, from_geojson
from pydantic_geojson import PointModel, PolygonModel, MultiPolygonModel
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from sqlalchemy.sql import func
import shapely

from utils import Utils


class ExpectedImpact(Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'


class Event(BaseModel):
    uid: str
    creation_datetime: datetime
    update_datetime: datetime | None = None
    description: str | None = None
    active: bool = True
    name: str
    venue: str
    location: PointModel | PolygonModel | MultiPolygonModel
    closures_start: datetime | str
    closures_end: datetime | str
    event_start: datetime | str
    event_end: datetime | str
    expected_impact: ExpectedImpact
    source: str
    external_urls: Dict[str, str] | None = None

    @model_validator(mode='before')
    def validate_fields(cls, fields):
        # print('fields')
        # print(fields)
        utils = Utils()
        if fields.get('uid') is None:
            fields['uid'] = str(uuid4())
        if fields.get('creation_datetime') is None:
            fields['creation_datetime'] = datetime.now()

        if fields.get('event_start') is not None:
            event_start = utils.time_str_to_obj(time_str=fields['event_start'], allow_none=False)
            # print(f"EVENT START: [{event_start}]")
            fields['event_start'] = event_start
        if fields.get('event_end') is not None:
            event_end = utils.time_str_to_obj(time_str=fields['event_end'], allow_none=False)
            # print(f"EVENT END: [{event_end}]")
            fields['event_end'] = event_end

        if 'closures_start' not in fields:
            fields['closures_start'] = event_start
        else:
            fields['closures_start'] = utils.time_str_to_obj(time_str=fields['closures_start'], allow_none=True)
        if 'closures_end' not in fields:
            fields['closures_end'] = event_end
        else:
            fields['closures_end'] = utils.time_str_to_obj(time_str=fields['closures_end'], allow_none=True)
        # print('fields')
        # print(fields)
        return fields


class EventDBBase(SQLModel):
    id: int | None = Field(primary_key=True, default=None)
    uid: str = Field(unique=True)
    creation_datetime: datetime
    update_datetime: datetime | None = None
    description: str | None = None
    active: bool
    name: str
    venue: str
    location: Any = Field(sa_column=Column(Geometry('GEOMETRY'))) # Here POINT is used but could be other geometries as well
    closures_start: datetime
    closures_end: datetime
    event_start: datetime
    event_end: datetime
    expected_impact: str
    source: str
    external_urls: Dict | None = Field(default_factory=dict, sa_column=Column(JSON))

    def cast_data_object(self, data_object_class) -> Event:
        """Return a data object based on the data_object_class"""
        content = self.model_dump()
        poly = to_shape(content['location'])
        if isinstance(poly, Point):
            location = PointModel(**json.loads(to_geojson(poly)))
        elif isinstance(poly, Polygon):
            location = PolygonModel(**json.loads(to_geojson(poly)))
        elif isinstance(poly, MultiPolygon):
            location = MultiPolygonModel(**json.loads(to_geojson(poly)))
        content['location'] = location
        data_obj = data_object_class(**content)
        return data_obj


class EventDBCreate(EventDBBase):
    @model_validator(mode='before')
    def validate_fields(cls, fields):
        polygon = fields.location
        geojson_str = polygon.model_dump_json()
        # wkt = from_geojson(geojson_str)
        fields = json.loads(fields.model_dump_json())
        fields['location'] = geojson_str
        if 'id' in fields:
            del fields['id']
        return fields


class EventDBRead(EventDBBase):
    pass


class EventDB(EventDBBase, table=True):
    __tablename__ = "event"


class EventFilter(BaseModel):
    uid: List[str] | None = None
    name: List[str] | None = None
    venue: List[str] | None = None
    # location: List[Point | Polygon] | None = None
    location: PointModel | PolygonModel | MultiPolygonModel | None = None
    active: bool | str | None = True
    # closures_start: datetime
    # closures_end: datetime
    # event_start: datetime
    # event_end: datetime
    event_after: datetime | None = None
    event_before: datetime | None = None

    expected_impact: List[ExpectedImpact] | None = None
    source: List[str] | None = None

    creation_datetime_after: datetime | None = None
    creation_datetime_before: datetime | None = None
    limit: int = 1000
    order_by: List[str] = ['creation_datetime']
    offset: int = 0

    @model_validator(mode='before')
    def validate_fields(cls, fields):
        if isinstance(fields.get('event_after'), list):
            fields['event_after'] = fields['event_after'][0]
        if isinstance(fields.get('event_before'), list):
            fields['event_before'] = fields['event_before'][0]

        if isinstance(fields.get('creation_datetime_after'), list):
            fields['creation_datetime_after'] = fields['creation_datetime_after'][0]
        if isinstance(fields.get('creation_datetime_before'), list):
            fields['creation_datetime_before'] = fields['creation_datetime_before'][0]
        if isinstance(fields.get('active'), list):
            fields['active'] = fields['active'][0]
        if isinstance(fields.get('location'), list):
            location = fields['location'][0]
            location = shapely.wkt.loads(location)
            location = PolygonModel(**json.loads(to_geojson(location)))
            fields['location'] = location
        if isinstance(fields.get('limit'), list):
            fields['limit'] = fields['limit'][0]
        if isinstance(fields.get('offset'), list):
            fields['offset'] = fields['offset'][0]
        return fields

    def apply_filters(self, database_object_class: EventDBBase, query: select) -> select:
        """Apply the filters to the query"""
        if self.uid:
            query = query.filter(database_object_class.uid.in_(self.uid))
        if self.name:
            query = query.filter(database_object_class.name.in_(self.name))
        if self.active is not None:
            if not isinstance(self.active, str):
                query = query.filter(database_object_class.active == self.active)
        if self.venue:
            query = query.filter(database_object_class.venue.in_(self.venue))
        if self.source:
            query = query.filter(database_object_class.source.in_(self.source))
        if self.location:
            location = from_geojson(self.location.model_dump_json())
            query = query.filter(
                func.ST_Intersects(database_object_class.location, from_shape(location))
            )

        if self.event_after:
            query = query.filter(database_object_class.event_start >= self.event_after)
        if self.event_before:
            query = query.filter(database_object_class.event_end <= self.event_before)

        if self.creation_datetime_after:
            query = query.filter(database_object_class.creation_datetime >= self.creation_datetime_after)
        if self.creation_datetime_before:
            query = query.filter(database_object_class.creation_datetime <= self.creation_datetime_before)
        if self.limit:
            query = query.limit(self.limit)
        for order_by in self.order_by:
            query = query.order_by(getattr(database_object_class, order_by))
        if self.offset:
            query = query.offset(self.offset)

        return query
