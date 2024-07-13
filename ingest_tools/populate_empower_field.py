import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

from selenium import webdriver

from shapely import Point, Polygon, MultiPolygon, to_geojson, from_geojson

source = 'populate empower field script'
base_url = 'http://localhost:8204/'
# base_url = 'http://hamster.nax.lol:8204/'
web_url = 'https://www.empowerfieldatmilehigh.com/events'
venue = 'Empower Field at Mile High'
geometry = Point(-105.02005494353804, 39.74383936528997)

# driver = webdriver.Firefox()
# driver.get(web_url)
# html = driver.page_source

# soup = BeautifulSoup(html, "html.parser")

page = requests.get(web_url)
soup = BeautifulSoup(page.content, "html.parser")
# html = soup.prettify("utf-8")
# with open('deleteme.html', 'wb') as fl:
#     fl.write(html)

event_tags = soup.find_all("div", {"class": "info clearfix"})
# let = len(event_tags)

# Venue
x=1
venue_payload = {
    'name': venue,
    'geometry': json.loads(to_geojson(geometry)),
    'source': source,
    'external_urls': {'event_page': web_url}
}
resp = requests.post(f'{base_url}/venues', json=venue_payload)
x=1

# Events
for event_tag in event_tags:
    date = event_tag.find("div", {"class": "date"})
    date_spans = date.find_all('span')
    if not date_spans:
        continue
    print(date_spans[0].text)

    header = event_tag.find("h3")
    name = header.text.strip()

    buttons = event_tag.find_all("a", {"class": "more"})
    event_url = buttons[0]['href']
    event_details_page = requests.get(event_url)
    event_details_soup = BeautifulSoup(event_details_page.content, "html.parser")
    event_details_sidebar = event_details_soup.find_all("li", {"class": "item"})
    date = event_start_datetime = gates_open_datetime = parking_lots_open_datetime = None
    for item in event_details_sidebar:
        print('')
        print(item)
        if 'sidebar_event_date' in item['class']:
            try:
                spans = item.find_all('span')
                date = spans[0].text
                date = datetime.strptime(date, '%B %d, %Y')
                print(f"DATE: [{date}]")
            except:
                pass

        if 'sidebar_event_starts' in item['class']:
            try:
                spans = item.find_all('span')
                time = spans[0].text
                time_re_match = re.search(r'(\d+):(\d+) *(am|pm)', time.lower())
                time_details = list(time_re_match.groups())
                if time_details[2] == 'pm':
                    time_details[0] = int(time_details[0]) + 12
                time_details[1] = int(time_details[1])
                event_start_datetime = datetime(date.year, date.month, date.day, time_details[0], time_details[1])
                print(f"Event Start: [{event_start_datetime}]")
            except:
                pass

        if 'sidebar_gates_open' in item['class']:
            try:
                spans = item.find_all('span')
                time = spans[0].text
                print(f"Gates Open: [{time}]")
                time_re_match = re.search(r'(\d+):(\d+) *(am|pm)', time.lower())
                time_details = list(time_re_match.groups())
                if time_details[2] == 'pm':
                    time_details[0] = int(time_details[0]) + 12
                time_details[1] = int(time_details[1])
                gates_open_datetime = datetime(date.year, date.month, date.day, time_details[0], time_details[1])
                print(f'Gates Open: [{gates_open_datetime}]')
            except:
                pass

        if 'sidebar_parking_lots_open' in item['class']:
            try:
                spans = item.find_all('span')
                time = spans[0].text
                time_re_match = re.search(r'(\d+):(\d+) *(am|pm)', time.lower())
                time_details = list(time_re_match.groups())
                if time_details[2] == 'pm':
                    time_details[0] = int(time_details[0]) + 12
                time_details[1] = int(time_details[1])
                parking_lots_open_datetime = datetime(date.year, date.month, date.day, time_details[0], time_details[1])
                print(f'Parking Lots Open: [{parking_lots_open_datetime}]')
            except:
                pass

    if parking_lots_open_datetime:
        closures_start = parking_lots_open_datetime
    elif gates_open_datetime:
        closures_start = gates_open_datetime
    else:
        closures_start = event_start_datetime

    event_start = event_start_datetime
    duration = timedelta(hours=4)
    closures_end = event_start + duration
    event_end = event_start + duration

    event = {
        'name': name,
        'venue': venue,
        'geometry': json.loads(to_geojson(geometry)),
        'closures_start': datetime.strftime(closures_start, '%Y-%m-%dT%H:%M'),
        'closures_end': datetime.strftime(closures_end, '%Y-%m-%dT%H:%M'),
        'event_start': datetime.strftime(event_start, '%Y-%m-%dT%H:%M'),
        'event_end': datetime.strftime(event_end, '%Y-%m-%dT%H:%M'),
        'expected_impact': 'HIGH',
        'source': source,
        'external_urls': {'event_page': event_url}
    }
    x=1

    query_datetime_morning = datetime(event_start.year, event_start.month, event_start.day)
    query_datetime_evening = datetime(event_end.year, event_end.month, event_end.day + 1)
    resp = requests.get(base_url + '/event', params={
        'name': name,
        'venue': venue,
        'event_after': query_datetime_morning,
        'event_before': query_datetime_evening})
    content = resp.json()
    if resp.json()['events']:
        existing_event = resp.json()['events'][0]
        existing_event['closures_start'] = event['closures_start']
        existing_event['closures_end'] = event['closures_end']
        existing_event['event_start'] = event['event_start']
        existing_event['event_end'] = event['event_end']
        existing_event['source'] = event['source']
        existing_event['external_urls'] = event['external_urls']

        resp = requests.put(base_url + f"/event/{existing_event['uid']}", json=existing_event)
    else:
        resp = requests.post(base_url + '/event', json=event)
    print(resp)
    if not resp.ok:
        content = resp.json()
        print(content)
        break
    x=1

x=1
