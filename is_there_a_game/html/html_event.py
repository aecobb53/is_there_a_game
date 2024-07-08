import os

from datetime import datetime, timedelta
from phtml import *
from my_base_html_lib import MyBaseDocument, NavigationContent, SidebarContent, BodyContent, FooterContent

from models import Event, EventFilter
from handlers import EventHandler

service_url = os.environ.get('SERVICE_URL')

def create_event_html_page():
    page_content = Div().add_style({'display': 'block'})



    navigation_content = NavigationContent(webpage_name="Is There A Fucking Game")
    body_content = BodyContent(body_content=[page_content])
    new_formatted_doc = MyBaseDocument(
        navigation_content=navigation_content,
        body_content=body_content,
    )
    return new_formatted_doc.return_document

def filter_events_html_page(
        datetime_start=None,
        datetime_end=None):
    page_content = Div().add_style({'display': 'block'})

    # Form
    filter_events_form = Form(id='filter-events')

    # Name
    filter_events_form.add_element(Label('Event Name:', for_='event-name'))
    filter_events_form.add_element(Input(type="text", id='event-name', name="name"))

    filter_events_form.add_element(LineBreak())

    # # Venue
    # filter_events_form.add_element("Venue Names:")
    # filter_events_form.add_element(Label('Empower Field', for_='empower-field-checkbox'))
    # filter_events_form.add_element(Input(type="checkbox", id='empower-field-checkbox', name="empower-field-checkbox"))
    # filter_events_form.add_element(Label('Ball Arena', for_='ball-arena-checkbox'))
    # filter_events_form.add_element(Input(type="checkbox", id='ball-arena-checkbox', name="ball-arena-checkbox"))

    # filter_events_form.add_element(LineBreak())

    # # Routes
    # filter_events_form.add_element("Impacted Routs:")
    # filter_events_form.add_element(Label('I-25', for_='interstate-25'))
    # filter_events_form.add_element(Input(type="checkbox", id='interstate-25', name="interstate-25", checked=True))
    # filter_events_form.add_element(Label('36', for_='highway-36'))
    # filter_events_form.add_element(Input(type="checkbox", id='highway-36', name="highway-36", checked=True))

    # Start Date
    # TODO: Add date picker

    page_content.add_element(filter_events_form)
    page_content.add_element(Button(
        onclick='populateTable()',
        internal='Refresh',
    ))

    # Table
    events_table_div = Div(id='events-table-div').add_style({
        'width:': '100%',
        'height': '100%',
        'border': '5px solid black',
    })
    events_table = Table(id='events-table').add_style({
        'width': '100%',
        'border': '1px red double',
    })
    events_table_div.add_element(events_table)
    page_content.add_element(events_table_div)

    # JS file
    js_file = []
    find_event_html_js_path = 'html/event/filter_events_html.js'
    with open(find_event_html_js_path, 'r') as jf:
        for line in jf.readlines():
            line = line.replace('SERVICE_URL', service_url)
            if datetime_start:
                line = line.replace('DATETIME_START', datetime.strftime(datetime_start, '%Y-%m-%dT%H:%M:%S'))
            else:
                line = line.replace('DATETIME_START', 'undefined')
            if datetime_end:
                line = line.replace('DATETIME_END', datetime.strftime(datetime_end, '%Y-%m-%dT%H:%M:%S'))
            else:
                line = line.replace('DATETIME_END', 'undefined')
            js_file.append(line)

    find_event_html_script = Script(internal=js_file)
    page_content.add_element(find_event_html_script)



    navigation_content = NavigationContent(webpage_name="Is There A Fucking Game")
    body_content = BodyContent(body_content=[page_content])
    new_formatted_doc = MyBaseDocument(
        navigation_content=navigation_content,
        body_content=body_content,
    )
    return new_formatted_doc.return_document

def find_event_html_page(event):
    page_content = Div().add_style({'display': 'block'})
    # page_content.add_element(Header(level=1, internal=f"Event: {event.name} At: {event.venue}").add_style({'margin': '20px'}))
    page_content.add_element(Header(level=1, internal=f"{event.name} At: {event.venue}").add_style({'margin': '20px'}))

    details_div_style = {'padding': '20px', 'margin': '5px', 'border': '5px solid black'}
    details_div = Div().add_style(details_div_style)

    details_div.add_element(Header(level=3, internal=f"Event Name: {event.name}"))
    details_div.add_element(Header(level=3, internal=f"Event Venue: {event.venue}"))

    if event.description:
        details_div.add_element(Header(level=3, internal=f"Event description: {event.description}"))
    # details_div.add_element(Header(level=3, internal=f"Event location: {event.location}"))

    details_div.add_element(Header(level=3, internal=f"Times:"))

    details_div.add_element(Header(level=3, internal=f"Event Closures Start: {event.closures_start}"))
    details_div.add_element(Header(level=3, internal=f"Event Event Start: {event.event_start}"))
    details_div.add_element(Header(level=3, internal=f"Event Event End: {event.event_end}"))
    details_div.add_element(Header(level=3, internal=f"Event Closures End: {event.closures_end}"))
    # details_div.add_element(Header(level=3, internal=f"Event source: {event.source}"))

    if event.external_urls:
        details_div.add_element(Header(level=3, internal=f"More Info:"))
        for key, value in event.external_urls.items():
            # details_div.add_element(Header(level=3, internal=f"{key}: {value}"))
            # details_div.add_element(Link(href=value, internal=key))
            details_div.add_element(Header(level=3, internal=Link(href=value, internal=key)))
            # Header(level=3, internal=f"Event Closures End: {event.closures_end}")

    page_content.add_element(details_div)






    navigation_content = NavigationContent(webpage_name="Is There A Fucking Game")
    body_content = BodyContent(body_content=[page_content])
    new_formatted_doc = MyBaseDocument(
        navigation_content=navigation_content,
        body_content=body_content,
    )
    return new_formatted_doc.return_document
