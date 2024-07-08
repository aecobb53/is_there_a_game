import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

from selenium import webdriver

from shapely import Point, Polygon, MultiPolygon, to_geojson, from_geojson

source = 'populate ball arena script'
base_url = 'http://localhost:8204/'
web_url = 'https://www.ballarena.com/misc/all-events/'
venue = 'Ball Arena'
location = Point(-105.00762284023057, 39.74863476970756)

# driver = webdriver.Firefox()
# driver.get(web_url)
# html = driver.page_source

# soup = BeautifulSoup(html, "html.parser")

page = requests.get(web_url)
soup = BeautifulSoup(page.content, "html.parser")
# html = soup.prettify("utf-8")
# with open('deleteme.html', 'wb') as fl:
#     fl.write(html)

event_tags = soup.find_all("div", {"class": "card flex-fill"})
let = len(event_tags)
x=1

for event_tag in event_tags:
    spans = event_tag.find_all('span')
    date = event_tag.find('span').text.strip()
    if date == 'TBA':
        continue
    re_match = re.search(r'.{6}(?P<month>[A-z]+) (?P<day>\d+) (?P<year>\d+).{3}(?P<hour>\d+):(?P<minute>\d+) (?P<TOD>AM|PM)', date)
    if not re_match:
        raise ValueError(f"Could not parse date: [{date}]")
    hour = int(re_match.group('hour'))
    if re_match.group('TOD') == 'PM' and hour < 12:
        hour += 12
    event_start = datetime.strptime(f"{re_match.group('month')} {re_match.group('day')} {re_match.group('year')} {hour} {re_match.group('minute')}", '%b %d %Y %H %M')
    name = event_tag.find('h5').text.strip()
    closures_start = event_start - timedelta(hours=2)
    event_end = event_start + timedelta(hours=4)
    closures_end = event_end + timedelta(hours=2)

    event = {
        'name': name,
        'venue': venue,
        'location': json.loads(to_geojson(location)),
        'closures_start': datetime.strftime(closures_start, '%Y-%m-%dT%H:%M'),
        'closures_end': datetime.strftime(closures_end, '%Y-%m-%dT%H:%M'),
        'event_start': datetime.strftime(event_start, '%Y-%m-%dT%H:%M'),
        'event_end': datetime.strftime(event_end, '%Y-%m-%dT%H:%M'),
        'expected_impact': 'HIGH',
        'source': source,
        'external_urls': {'Events Page': "https://www.ballarena.com/misc/all-events/"}
    }
    x=1

    query_datetime_morning = datetime(event_start.year, event_start.month, event_start.day)
    query_datetime_evening = query_datetime_morning + timedelta(days=1)
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
    content = resp.json()
    # print(content)

x=1
