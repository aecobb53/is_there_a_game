from calendar import month
from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, ORJSONResponse

from models import Venue, VenueFilter
# from handlers import VenueHandler
from handlers import VenueHandler, parse_query_params
# from utils import parse_query_params, parse_header, MissingRecordException, DuplicateRecordsException
from models import ContextSingleton


from html import (
    # create_venue_html_page,
    # filter_venues_html_page,
    # find_venue_html_page,
    # venue_base_page,
    unimplemented_page
    )

context = ContextSingleton()

router = APIRouter(
    prefix='/html/venues',
    tags=['venues', 'html'],
)


path = '/'
@router.get(path)
async def html_venue(request: Request):
    venue_page = unimplemented_page()
    return HTMLResponse(content=venue_page, status_code=200)
    # venue_page = filter_venues_html_page()
    # return HTMLResponse(content=venue_page, status_code=200)

# path = '/today'
# @router.get(path)
# async def html_venues_today(request: Request):
#     now = datetime.now()
#     morning = datetime(now.year, now.month, now.day)
#     evening = morning + timedelta(days=1)
#     venue_page = filter_venues_html_page(
#         datetime_start=morning,
#         datetime_end=evening
#     )
#     return HTMLResponse(content=venue_page, status_code=200)

# path = '/this-month'
# @router.get(path)
# async def html_venues_today(request: Request):
#     now = datetime.now()
#     first_day = datetime(now.year, now.month, 1)
#     last_day = first_day.replace(month=first_day.month + 1)
#     venue_page = filter_venues_html_page(
#         datetime_start=first_day,
#         datetime_end=last_day
#     )
#     return HTMLResponse(content=venue_page, status_code=200)

# path = '/in-the-next-{number_of_days}-days'
# @router.get(path)
# async def html_venues_today(number_of_days: int, request: Request):
#     now = datetime.now()
#     first_day = datetime(now.year, now.month, now.day)
#     last_day = first_day + timedelta(days=number_of_days)
#     venue_page = filter_venues_html_page(
#         datetime_start=first_day,
#         datetime_end=last_day
#     )
#     return HTMLResponse(content=venue_page, status_code=200)

# # @router.get('/modify')
# # async def html_modify_venue(request: Request):
# #     venue_page = create_venue_html_page()
# #     return HTMLResponse(content=venue_page, status_code=200)


# @router.get('/{venue_uid}')
# async def html_venue_venue_uid(request: Request, venue_uid: str):
#     eh = VenueHandler()
#     try:
#         venue = await eh.find_venue(venue_uid=venue_uid)
#     # except MissingRecordException as err:
#     #     context.logger.error(f"ERROR: {err}")
#     #     raise HTTPException(status_code=404, detail=str(err))
#     # except DuplicateRecordsException as err:
#     #     context.logger.error(f"ERROR: {err}")
#     #     raise HTTPException(status_code=404, detail=str(err))
#     except Exception as err:
#         context.logger.error(f'ERROR: {err}')
#         raise HTTPException(status_code=500, detail='Internal Server Error')
#     venue_page = find_venue_html_page(venue=venue)
#     return HTMLResponse(content=venue_page, status_code=200)
