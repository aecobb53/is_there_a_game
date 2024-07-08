from fastapi import APIRouter, HTTPException, Request, Response, Depends

from models import Event, EventFilter
# from handlers import EventHandler
from handlers import EventHandler, parse_query_params
# from utils import parse_query_params, parse_header, MissingRecordException, DuplicateRecordsException
from models import ContextSingleton

from typing import Annotated

context = ContextSingleton()

router = APIRouter(
    prefix='/event',
    tags=['event'],
)


@router.post('/', status_code=201)
async def create_event(event: Event):
    rh = EventHandler()
    try:
        created_event = await rh.create_event(event=event)
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
    return created_event


@router.get('/', status_code=200)
async def filter_event(request: Request):
    rh = EventHandler()
    try:
        event_filter = parse_query_params(request=request, query_class=EventFilter)
        events = await rh.filter_events(event_filter=event_filter)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return {'events': events}


@router.put('/{event_id}', status_code=200)
async def update_event(event_id: str, event: Event):
    rh = EventHandler()
    try:
        updated_event = await rh.update_event(event_uid=event_id, event=event)
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
    return updated_event


@router.get('/{event_id}', status_code=200)
async def find_event(event_id: str):
    rh = EventHandler()
    try:
        event = await rh.find_event(event_uid=event_id)
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
    return event


@router.put('/{event_id}/activate', status_code=200)
async def activate_event(event_id: str):
    rh = EventHandler()
    try:
        updated_event = await rh.set_activation(event_uid=event_id, active_state=True)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_event


@router.put('/{event_id}/deactivate', status_code=200)
async def deactivate_event(event_id: str):
    rh = EventHandler()
    try:
        updated_event = await rh.set_activation(event_uid=event_id, active_state=False)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_event


@router.delete('/{event_id}', status_code=200)
async def delete_event(event_id: str):
    rh = EventHandler()
    try:
        updated_event = await rh.delete_event(event_uid=event_id)
    # except MissingRecordException as err:
    #     message = f"Record not found: [{err}]"
    #     context.logger.warning(message)
    #     raise HTTPException(status_code=404, detail=message)
    except Exception as err:
        context.logger.warning(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Service Error')
    return updated_event
