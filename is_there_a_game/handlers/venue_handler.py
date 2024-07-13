import json
from datetime import datetime
from sqlmodel import Session, select

from .base_handler import BaseHandler
from models import Venue, VenueDBCreate, VenueDBRead, VenueDB, VenueFilter

from geoalchemy2 import Geometry
from shapely import intersection, from_geojson
from geoalchemy2.shape import to_shape, from_shape
from .exceptions import MissingRecordException, DuplicateRecordsException, DataIntegrityException


class VenueHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_venue(self, venue: Venue) -> Venue:
        self.context.logger.info(f"Creating venue: {venue.model_dump_json()}")
        with Session(self.context.database.engine) as session:
            create_obj = VenueDBCreate.model_validate(venue)
            create_obj = VenueDB.model_validate(create_obj)
            json_content = json.loads(create_obj.model_dump_json())
            geometry = json_content['geometry']
            poly = from_geojson(geometry)
            geometry = from_shape(poly)
            create_obj.geometry = geometry
            session.add(create_obj)
            session.commit()
            session.refresh(create_obj)
            read_obj = VenueDBRead.model_validate(create_obj)
            venue = read_obj.cast_data_object(Venue)
        self.context.logger.info(f"Venue Created: {venue.model_dump_json()}")
        return venue

    async def filter_venues(self, venue_filter: VenueFilter) -> list[Venue]:
        self.context.logger.info(f"Filtering venues: {venue_filter.model_dump_json()}")
        with Session(self.context.database.engine) as session:
            query = select(VenueDB)
            query = venue_filter.apply_filters(VenueDB, query)
            rows = session.exec(query).all()
            venues = []
            for row in rows:
                read_obj = VenueDBRead.model_validate(row)
                venue = read_obj.cast_data_object(Venue)
                venues.append(venue)
        self.context.logger.info(f"Venues Filtered: {len(venues)}")
        return venues

    async def find_venue(self, venue_uid: str) -> Venue:
        self.context.logger.info(f"Finding venue: {venue_uid}")
        with Session(self.context.database.engine) as session:
            query = select(VenueDB)
            query = query.where(VenueDB.uid == venue_uid)
            row = session.exec(query).first()
            if row is None:
                raise MissingRecordException(f"No records found for uid: [{venue_uid}]")
            read_obj = VenueDBRead.model_validate(row)
            venue = read_obj.cast_data_object(Venue)
        self.context.logger.info(f"Venue found: [{venue_uid}]")
        return venue

    async def update_venue(self, venue_uid: str, venue: Venue) -> Venue:
        self.context.logger.info(f"Updating venue: {venue_uid}")
        with Session(self.context.database.engine) as session:
            query = select(VenueDB)
            query = query.where(VenueDB.uid == venue_uid)
            row = session.exec(query).first()
            if row is None:
                raise MissingRecordException(f"No records found for uid: [{venue_uid}]")

            # Verify data integrity
            immutable_fields = [
                'uid',
                'creation_datetime',
            ]
            immutable_modification_detected = []
            for key in immutable_fields:
                if getattr(row, key) != getattr(venue, key):
                    immutable_modification_detected.append(key)
            if len(immutable_modification_detected) > 0:
                raise DataIntegrityException(f"Immutable fields were modified: {immutable_modification_detected}")

            # Make changes
            skip_fields = [
                'geometry',
            ]
            for key in Venue.__fields__.keys():
                if key not in skip_fields:
                    try:
                        if getattr(row, key) != getattr(venue, key):
                            setattr(row, key, getattr(venue, key))
                    except AttributeError:
                        pass
            row.update_datetime = datetime.utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            read_obj = VenueDBRead.model_validate(row)
            venue = read_obj.cast_data_object(Venue)
        self.context.logger.info(f"Venue updated: [{venue_uid}]")
        return venue

    async def set_activation(self, venue_uid: str, active_state: bool) -> Venue:
        self.context.logger.debug(f"Setting Venue activation: [{venue_uid}] to [{active_state}]")

        venue = await self.find_venue(venue_uid=venue_uid)
        venue.active = active_state
        venue = await self.update_venue(venue_uid=venue_uid, venue=venue)

        self.context.logger.info(f"Set venue activation: [{venue.uid}]")
        return venue

    async def delete_venue(self, venue_uid: str) -> None:
        self.context.logger.info(f"Deleting venue: {venue_uid}")
        with Session(self.context.database.engine) as session:
            query = select(VenueDB)
            query = query.where(VenueDB.uid == venue_uid)
            row = session.exec(query).first()
            session.delete(row)
            session.commit()
        self.context.logger.info(f"Venue deleted")
