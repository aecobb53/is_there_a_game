import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import date, datetime, timedelta

from selenium import webdriver

from shapely import Point, Polygon, MultiPolygon, to_geojson, from_geojson



# Basktetball
# CrossCountry
# Football
# Skiing
# Track and Field
# Lacrosse
# Soccer
# Tennis
# Volleyball

# Mens/Womens


source = 'populate ball arena script'
base_url = 'http://localhost:8204/'


# Football
web_url = 'https://cubuffs.com/sports/football/schedule'
venue = 'Folsom Field'
location = Point(-105.26697702514522, 40.00947835921254)

page = requests.get(web_url)
soup = BeautifulSoup(page.content, "html.parser")

event_tags = soup.find_all("div", {"class": "s-game-card__header-inner-top-inner"})
let = len(event_tags)

for event_tag in event_tags:
    venue_tag = event_tag.find("a", {"class": "s-text-paragraph-small-underline"})
    if not venue_tag:
        # This is likely not a home game
        continue
    venue = venue_tag.text
    if venue != 'Folsom Field':
        continue
    details_div = event_tag.find("div", {"class": "s-game-card__header__team"})
    name_tag = details_div.find("a", {"class": "s-text-paragraph-bold"})
    name = f"Colorado Buffaloes vs {name_tag.text}"
    date_div = event_tag.find("div", {"class": "s-game-card__header__game-score-time"})

    re_match = re.search(r'(?P<month>[A-z]+) (?P<day>\d+) \([A-z]+\) ((?P<hour>\d+)(:(?P<minute>\d+))? (?P<TOD>AM|PM))?', date_div.text.strip())
    today = datetime.now()
    if re_match.group('hour'):
        hour = int(re_match.group('hour'))
        if re_match.group('TOD') == 'PM' and hour < 12:
            hour += 12
        if re_match.group('minute'):
            minute = int(re_match.group('minute'))
        else:
            minute = 0
        event_start = datetime.strptime(f"{re_match.group('month')} {re_match.group('day')} {today.year} {hour} {minute}", '%b %d %Y %H %M')
        event_end = event_start + timedelta(hours=4)
        closures_start = event_start - timedelta(hours=4)
        closures_end = event_end + timedelta(hours=2)
    else:
        # Time is TBA
        event_start = datetime.strptime(f"{re_match.group('month')} {re_match.group('day')} {today.year}", '%b %d %Y')
        event_end = event_start + timedelta(days=1)
        closures_start = event_start
        closures_end = event_end

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
        'external_urls': {'Events Page': "https://cubuffs.com/sports/football/schedule"}
    }

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



# Basketball
web_url = 'https://cubuffs.com/sports/mens-basketball/schedule'
venue = 'CU Events Center'
location = Point(-105.26062817150672, 40.00463873668913)

page = requests.get(web_url)
soup = BeautifulSoup(page.content, "html.parser")

event_tags = soup.find_all("div", {"class": "s-game-card__header-inner-top-inner"})
let = len(event_tags)

for event_tag in event_tags:
    location_tag = event_tag.find("div", {"class": "s-game-card__header__team-event-info w-auto text-left"})
    venue_tag = location_tag.find_all("span")[-1]
    if not venue_tag:
        # This is likely not a home game
        continue
    venue = venue_tag.text
    if venue != 'Boulder, Colo.':
        continue
    details_div = event_tag.find("div", {"class": "s-game-card__header__team"})
    name_tag = details_div.find("a", {"class": "s-text-paragraph-bold"})
    name = f"Colorado Buffaloes vs {name_tag.text}"
    # date_div = event_tag.find("div", {"class": "s-game-card__header__game-score-time"})
    date_div = event_tag.find("p", {"class": "text-theme-safe s-text-paragraph-small-bold"})
    """text-theme-safe s-text-paragraph-small-bold flex flex-wrap items-center justify-end"""

    print('')
    print('date_div')
    print(date_div)
    print(date_div.text.strip())

    re_match = re.search(r'(?P<month>[A-z]+) (?P<day>\d+) \([A-z]+\) ((?P<hour>\d+)(:(?P<minute>\d+))? (?P<TOD>AM|PM))?', date_div.text.strip())
    today = datetime.now()
    if re_match.group('hour'):
        hour = int(re_match.group('hour'))
        if re_match.group('TOD') == 'PM' and hour < 12:
            hour += 12
        if re_match.group('minute'):
            minute = int(re_match.group('minute'))
        else:
            minute = 0
        event_start = datetime.strptime(f"{re_match.group('month')} {re_match.group('day')} {today.year} {hour} {minute}", '%b %d %Y %H %M')
        event_end = event_start + timedelta(hours=4)
        closures_start = event_start - timedelta(hours=4)
        closures_end = event_end + timedelta(hours=2)
    else:
        # Time is TBA
        event_start = datetime.strptime(f"{re_match.group('month')} {re_match.group('day')} {today.year}", '%b %d %Y')
        event_end = event_start + timedelta(days=1)
        closures_start = event_start
        closures_end = event_end

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
        'external_urls': {'Events Page': "https://cubuffs.com/sports/football/schedule"}
    }

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
