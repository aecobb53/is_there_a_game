import json
from datetime import datetime
from sqlmodel import Session, select

from .base_handler import BaseHandler
from models import Event, EventDBCreate, EventDBRead, EventDB, EventFilter

from geoalchemy2 import Geometry
from shapely import intersection, from_geojson
from geoalchemy2.shape import to_shape, from_shape
from .exceptions import MissingRecordException, DuplicateRecordsException, DataIntegrityException


class EventHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_event(self, event: Event) -> Event:
        self.context.logger.info(f"Creating event: {event.model_dump_json()}")
        with Session(self.context.database.engine) as session:
            create_obj = EventDBCreate.model_validate(event)
            create_obj = EventDB.model_validate(create_obj)
            json_content = json.loads(create_obj.model_dump_json())
            geometry = json_content['geometry']
            poly = from_geojson(geometry)
            geometry = from_shape(poly)
            create_obj.geometry = geometry
            session.add(create_obj)
            session.commit()
            session.refresh(create_obj)
            read_obj = EventDBRead.model_validate(create_obj)
            event = read_obj.cast_data_object(Event)
        self.context.logger.info(f"Event Created: {event.model_dump_json()}")
        return event

    async def filter_events(self, event_filter: EventFilter) -> list[Event]:
        self.context.logger.info(f"Filtering events: {event_filter.model_dump_json()}")
        with Session(self.context.database.engine) as session:
            query = select(EventDB)
            query = event_filter.apply_filters(EventDB, query)
            rows = session.exec(query).all()
            events = []
            for row in rows:
                read_obj = EventDBRead.model_validate(row)
                event = read_obj.cast_data_object(Event)
                events.append(event)
        self.context.logger.info(f"Events Filtered: {len(events)}")
        return events

    async def find_event(self, event_uid: str) -> Event:
        self.context.logger.info(f"Finding event: {event_uid}")
        with Session(self.context.database.engine) as session:
            query = select(EventDB)
            query = query.where(EventDB.uid == event_uid)
            row = session.exec(query).first()
            if row is None:
                raise MissingRecordException(f"No records found for uid: [{event_uid}]")
            read_obj = EventDBRead.model_validate(row)
            event = read_obj.cast_data_object(Event)
        self.context.logger.info(f"Event found: [{event_uid}]")
        return event

    async def update_event(self, event_uid: str, event: Event) -> Event:
        self.context.logger.info(f"Updating event: {event_uid}")
        with Session(self.context.database.engine) as session:
            query = select(EventDB)
            query = query.where(EventDB.uid == event_uid)
            row = session.exec(query).first()
            if row is None:
                raise MissingRecordException(f"No records found for uid: [{event_uid}]")

            # Verify data integrity
            immutable_fields = [
                'uid',
                'creation_datetime',
            ]
            immutable_modification_detected = []
            for key in immutable_fields:
                if getattr(row, key) != getattr(event, key):
                    immutable_modification_detected.append(key)
            if len(immutable_modification_detected) > 0:
                raise DataIntegrityException(f"Immutable fields were modified: {immutable_modification_detected}")

            # Make changes
            skip_fields = [
                'geometry',
            ]
            for key in Event.__fields__.keys():
                if key not in skip_fields:
                    try:
                        if getattr(row, key) != getattr(event, key):
                            setattr(row, key, getattr(event, key))
                    except AttributeError:
                        pass
            row.update_datetime = datetime.utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            read_obj = EventDBRead.model_validate(row)
            event = read_obj.cast_data_object(Event)
        self.context.logger.info(f"Event updated: [{event_uid}]")
        return event

    async def set_activation(self, event_uid: str, active_state: bool) -> Event:
        self.context.logger.debug(f"Setting Event activation: [{event_uid}] to [{active_state}]")

        event = await self.find_event(event_uid=event_uid)
        event.active = active_state
        event = await self.update_event(event_uid=event_uid, event=event)

        self.context.logger.info(f"Set event activation: [{event.uid}]")
        return event

    async def delete_event(self, event_uid: str) -> None:
        self.context.logger.info(f"Deleting event: {event_uid}")
        with Session(self.context.database.engine) as session:
            query = select(EventDB)
            query = query.where(EventDB.uid == event_uid)
            row = session.exec(query).first()
            session.delete(row)
            session.commit()
        self.context.logger.info(f"Event deleted")
