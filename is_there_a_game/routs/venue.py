from fastapi import APIRouter, HTTPException, Request, Response, Depends

from models import Venue, VenueFilter
# from handlers import VenueHandler
from handlers import VenueHandler, parse_query_params
# from utils import parse_query_params, parse_header, MissingRecordException, DuplicateRecordsException
from models import ContextSingleton

from typing import Annotated

context = ContextSingleton()

router = APIRouter(
    prefix='/venue',
    tags=['venue'],
)


@router.post('/', status_code=201)
async def create_venue(venue: Venue):
    rh = VenueHandler()
    try:
        created_venue = await rh.create_venue(venue=venue)
    # except DuplicateRecordsException as err:
    #     message = f"Dupe record attempt: {err}"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=409, detail=message)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return created_venue


@router.get('/', status_code=200)
async def filter_venue(request: Request):
    rh = VenueHandler()
    try:
        venue_filter = parse_query_params(request=request, query_class=VenueFilter)
        venues = await rh.filter_venues(venue_filter=venue_filter)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return {'venues': venues}


@router.put('/{venue_id}', status_code=200)
async def update_venue(venue_id: str, venue: Venue):
    rh = VenueHandler()
    try:
        updated_venue = await rh.update_venue(venue_uid=venue_id, venue=venue)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    # except DuplicateRecordsException as err:
    #     message = f"Duplicate records found: [{err}]"
    #     context.logger.error(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_venue


@router.get('/{venue_id}', status_code=200)
async def find_venue(venue_id: str):
    rh = VenueHandler()
    try:
        venue = await rh.find_venue(venue_uid=venue_id)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    # except DuplicateRecordsException as err:
    #     message = f"Duplicate records found: [{err}]"
    #     context.logger.error(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return venue


@router.put('/{venue_id}/activate', status_code=200)
async def activate_venue(venue_id: str):
    rh = VenueHandler()
    try:
        updated_venue = await rh.set_activation(venue_uid=venue_id, active_state=True)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_venue


@router.put('/{venue_id}/deactivate', status_code=200)
async def deactivate_venue(venue_id: str):
    rh = VenueHandler()
    try:
        updated_venue = await rh.set_activation(venue_uid=venue_id, active_state=False)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_venue


@router.delete('/{venue_id}', status_code=200)
async def delete_venue(venue_id: str):
    rh = VenueHandler()
    try:
        updated_venue = await rh.delete_venue(venue_uid=venue_id)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_venue
