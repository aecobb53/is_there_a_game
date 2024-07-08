from calendar import month
from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, ORJSONResponse

from models import Event, EventFilter
# from handlers import EventHandler
from handlers import EventHandler, parse_query_params
# from utils import parse_query_params, parse_header, MissingRecordException, DuplicateRecordsException
from models import ContextSingleton


from html import (
    create_event_html_page,
    filter_events_html_page,
    find_event_html_page,
    # event_base_page,
    # unimplemented_page
    )

context = ContextSingleton()

router = APIRouter(
    prefix='/html/events',
    tags=['events', 'html'],
)
explicit_router = APIRouter(
    prefix='/is-there-a-fucking-game',
    tags=['is-there-a-game', 'html', 'explicit'],
)
clean_router = APIRouter(
    prefix='/is-there-a-game',
    tags=['is-there-a-game', 'html', 'clean'],
)


@router.get('/')
@explicit_router.get('/')
@clean_router.get('/')
async def html_event(request: Request):
    event_page = filter_events_html_page()
    return HTMLResponse(content=event_page, status_code=200)

@router.get('/today')
@explicit_router.get('/today')
@clean_router.get('/today')
async def html_events_today(request: Request):
    now = datetime.now()
    morning = datetime(now.year, now.month, now.day)
    evening = morning + timedelta(days=1)
    event_page = filter_events_html_page(
        datetime_start=morning,
        datetime_end=evening
    )
    return HTMLResponse(content=event_page, status_code=200)

@router.get('/this-month')
@explicit_router.get('/this-month')
@clean_router.get('/this-month')
async def html_events_today(request: Request):
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    last_day = first_day.replace(month=first_day.month + 1)
    event_page = filter_events_html_page(
        datetime_start=first_day,
        datetime_end=last_day
    )
    return HTMLResponse(content=event_page, status_code=200)

@router.get('/in-the-next-{day_number}-days')
@explicit_router.get('/in-the-next-{day_number}-days')
@clean_router.get('/in-the-next-{day_number}-days')
async def html_events_today(day_number: int, request: Request):
    now = datetime.now()
    first_day = datetime(now.year, now.month, now.day)
    last_day = first_day + timedelta(days=day_number)
    event_page = filter_events_html_page(
        datetime_start=first_day,
        datetime_end=last_day
    )
    return HTMLResponse(content=event_page, status_code=200)

# @router.get('/modify')
# async def html_modify_event(request: Request):
#     event_page = create_event_html_page()
#     return HTMLResponse(content=event_page, status_code=200)


@router.get('/{event_uid}')
async def html_event_event_uid(request: Request, event_uid: str):
    eh = EventHandler()
    try:
        event = await eh.find_event(event_uid=event_uid)
    # except MissingRecordException as err:
    #     context.logger.error(f"ERROR: {err}")
    #     raise HTTPException(status_code=404, detail=str(err))
    # except DuplicateRecordsException as err:
    #     context.logger.error(f"ERROR: {err}")
    #     raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        context.logger.error(f'ERROR: {err}')
        raise HTTPException(status_code=500, detail='Internal Server Error')
    event_page = find_event_html_page(event=event)
    return HTMLResponse(content=event_page, status_code=200)
