from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import json  # used to get info about raid bosses


"""
TODO
- i'm not sure if the showcase works properly
    - it seems the event stays on the page even after it's ended (perhaps for time zones ??) so just checking the
    first occurance of the event is not accurate; instead i have to look at the actual start and end date of the
    event. 
    - once the next showcase actually starts, i'm not sure if the old showcase will go away?
- for the same reasons i'm also not sure if my /mega and /fivestar will work 

"""


events_page = requests.get("https://leekduck.com/events/")
page = BeautifulSoup(events_page.text, "html.parser")
raids_page = requests.get("https://leekduck.com/boss/")
r_page = BeautifulSoup(raids_page.text, "html.parser")


def process_date(date):
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"
    return date


# input: event div with the identifying class (eg "raid-battles")
# output: formatted date and time (2024-01-01 -> January 1 | 13:00:00 -> 1 pm)
# of the end date (time, month, day)
def process_dt(event):
    event_info = event.parent.find_previous_sibling()
    event_end = event_info['data-event-end-date']
    date, time = event_end.split('T')

    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    year, month, day = date.split("-")
    hour, min, sec = time.split(":")

    # formatted
    fdate = months[int(month)-1] + ' ' + str(int(day))
    ftime = str(int(hour) % 12) + ' AM' if int(hour) // 12 == 0 else ' PM'

    return [ftime, fdate]


# returns true if dt is before current date-time
def after_now(dt):
    date, time = dt.split('T')
    current_date = str(datetime.now().date())
    current_time = str(datetime.now().time())
    if current_date < date:
        return True
    if current_date == date:
        if current_time < time:
            return True
    return False


# check if event is going on currently; input: div
def is_current(event):
    # check that event is happening right now
    event_info = event.parent.find_previous_sibling()
    try:
        event_start = event_info['data-event-start-date-check']
        event_end = event_info['data-event-end-date']
    except KeyError:
        return False

    if not after_now(event_start) and after_now(event_end):
        return True
    return False


# input: tier (1/2/3/mega/5)
# output: dictionary of info or None if no info was found
def get_boss_info(boss, tier):
    # load the pogoapi
    response = requests.get("https://pogoapi.net/api/v1/raid_bosses.json")
    bosses = json.loads(response.text)

    # check previous
    for boss_info in bosses["previous"][tier]:
        if any(word == boss_info["name"] for word in boss.split()):
            return boss_info

    # check current
    for boss_info in bosses["current"][tier]:
        if boss_info["name"] == boss:
            return boss_info

    # no info was found
    return None

# finds the types that are strong against the given type (eg ice -> fighting, fire, rock, steel)
# inputs an array of types
def find_weakness(types):
    type_page = requests.get("https://pogoapi.net/api/v1/type_effectiveness.json")
    type_data = json.loads(type_page.text)
    weakness = []

    for key in type_data.keys():
        sum = 0
        for t in types:
            sum += type_data[key][t]
        if sum > len(types) + 0.5:
            weakness.append(key)

    return weakness


# this might not be necessary
def find_strength(type):
    type_page = requests.get("https://pogoapi.net/api/v1/type_effectiveness.json")
    type_data = json.loads(type_page.text)
    strength = []
    for key in type_data[type].keys():
        if type_data[type][key] > 1:  # given type is strong against this type
            strength.append(key)
    return strength


def get_spotlight_hour():
    spotlight_hour = page.find('div', attrs={'class': 'pokémon-spotlight-hour'}).parent.parent
    spotlight_link = spotlight_hour.find('a')

    # go to the spotlight hour page
    spotlight_page = requests.get("https://leekduck.com" + spotlight_link['href'])
    s_page = BeautifulSoup(spotlight_page.text, "html.parser")

    # extract the date, pokemon, and bonus
    date, pokemon, bonus = s_page.find('div', attrs={'class': 'event-description'}).findAll('strong')
    date = date.text.split()
    date = f"{date[0]} {date[1]}"
    pokemon = pokemon.text
    bonus = bonus.text

    return [date, pokemon, bonus]


def get_raid_hour():
    event = page.find('div', attrs={'class': 'raid-hour'})
    event_link = event.parent.parent.find('a', attrs={'class', 'event-item-link'})
    event_page = requests.get("https://leekduck.com" + event_link['href'])
    event_page = BeautifulSoup(event_page.text, "html.parser")

    # find pokemon
    pokemon = event.find('h2').text
    pokemon = re.search(r'\s*(\D*) Raid Hour', pokemon).group(1)

    # find date
    date = event_page.find(id='event-date-start').text
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"

    details = ""
    # if there are multiple pokemon, find the regions
    if "," in pokemon:
        details = "\n"
        details += event_page.find('div', attrs={'class', 'event-description'}).find('ul').text

    return [date, pokemon, details]


def get_comm_day():
    event = page.find('div', attrs={'class': 'community-day'})

    event_link = event.parent.parent.find('a', attrs={'class', 'event-item-link'})
    event_page = requests.get("https://leekduck.com" + event_link['href'])
    event_page = BeautifulSoup(event_page.text, "html.parser")

    # find pokemon
    pokemon = event_page.find('h1', attrs={'class', 'page-title'}).text
    pokemon = re.search(r'\s*(\D*) Community', pokemon).group(1)

    # find date
    date = event_page.find(id='event-date-start').text
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"

    # find featured attack
    attack = event_page.find('div', attrs={'class', 'features-wrapper'}).find('p').text

    return [date, pokemon, attack]


def get_showcase():
    events = page.find_all('div', attrs={'class': 'pokéstop-showcase'})
    event = None

    # the case where there aren't any showcases currently or upcoming
    if events is None:
        return [None, None]

    for e in events:
        # check that event is happening right now
        if is_current(e):
            event = e

    if event is None:
        return [None, None]

    event_link = event.parent.parent.find('a', attrs={'class', 'event-item-link'})
    event_page = requests.get("https://leekduck.com" + event_link['href'])
    event_page = BeautifulSoup(event_page.text, "html.parser")

    # find pokemon
    pokemon = event_page.find('h1', attrs={'class', 'page-title'}).text
    pokemon = re.search(r'\s*(\D*) PokéStop', pokemon).group(1)

    # find date
    end_date = event_page.find(id='event-date-end').text
    end_date = process_date(end_date)

    return [end_date, pokemon]


raid_battles = page.find_all('div', attrs={'class', 'raid-battles'})


# using the events page instead of the raid page
def get_five_star():
    events = page.find_all('div', attrs={'class': 'raid-battles'})
    event = None
    current_boss = None

    # find the first 5star boss that's currently going on
    for e in events:
        if is_current(e):
            if "5-star" in e.find('h2').text:
                event = e
                current_boss = re.search(r"(\D*) in 5-star", e.find('h2').text).group(1)

    time, date = process_dt(event)

    return [date, time, current_boss]


def get_mega():
    events = page.find_all('div', attrs={'class': 'raid-battles'})
    event = None
    current_boss = None

    # find the first 5star boss that's currently going on
    for e in events:
        if is_current(e):
            if "Mega" in e.find('h2').text:
                event = e
                current_boss = re.search(r"(\D*) in Mega", e.find('h2').text).group(1)

    time, date = process_dt(event)

    return [date, time, current_boss]


s = '2024-01-01'
print(str(datetime.now()) < s)
#print(datetime.now().time())
#print(datetime.time(datetime.now()))

