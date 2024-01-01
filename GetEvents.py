from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import json  # used to get info about raid bosses

events_page = requests.get("https://leekduck.com/events/")
page = BeautifulSoup(events_page.text, "html.parser")
raids_page = requests.get("https://leekduck.com/boss/")
r_page = BeautifulSoup(raids_page.text, "html.parser")


def process_date(date):
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"
    return date


# returns true if dt is before current date-time
def after_now(dt):
    date, time = dt.split('T')
    current_date = str(datetime.now().date())
    current_time = str(datetime.now().time())

    print("event date: ", date, time)
    print("current date: ", current_date, current_time)

    if current_date > date:
        if current_time > time:
            return True
    return False


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
    event = page.find('div', attrs={'class': 'pokéstop-showcase'})

    # the case where there aren't any showcases currently or upcoming
    if event is None:
        return [None, None]

    # check that event is happening right now
    event_info = event.parent.find_previous_sibling()
    event_start = event_info['data-event-start-date-check']
    event_end = event_info['data-event-end-date']

    # if event hasn't started yet
    if not after_now(event_start):
        print("not started yet")
        return [None, None]

    # if event has ended already
    if not after_now(event_end):
        print("already ended")
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


def get_five_star():
    current_boss = r_page.find('h2', attrs={'class', 'boss-tier-header tier-5'}).parent.find_next_sibling()
    current_boss = current_boss.find('p', attrs={'class', 'boss-name'}).text

    """
    TODO IN THE FUTURE
    - since i'm using the raids page instead of the event page, i don't know how it'll look like when there are
    mulitple 5 star raid bosses. my guess is that it'll only find the first one listed in the site, most likely
    buzzwole. i'll have to check next week to see
    """

    # load the pogoapi
    response = requests.get("https://pogoapi.net/api/v1/raid_bosses.json")
    bosses = json.loads(response.text)

    # check previous
    for boss in bosses["previous"]["5"]:
        if any(word == boss["name"] for word in current_boss.split()):
            return boss

    # check current (heatran)
    for boss in bosses["current"]["5"]:
        if boss["name"] == current_boss:
            return boss

    # if it hasn't been found yet, it doesn't exist in the api (just return the name)
    return current_boss


def get_mega():
    current_boss = r_page.find('h2', attrs={'class', 'boss-tier-header tier-Mega'}).parent.find_next_sibling()
    current_boss = current_boss.find('p', attrs={'class', 'boss-name'}).text

    # load the pogoapi
    response = requests.get("https://pogoapi.net/api/v1/raid_bosses.json")
    bosses = json.loads(response.text)

    # check previous
    for boss in bosses["previous"]["mega"]:
        if any(word == boss["name"] for word in current_boss.split()):
            return boss

    # check current (heatran)
    for boss in bosses["current"]["mega"]:
        if boss["name"] == current_boss:
            return boss

    # if it hasn't been found yet, it doesn't exist in the api (just return the name)
    return current_boss


s = '2023-12-30'
print(str(datetime.now()) < s)
print(datetime.now().time())
print(datetime.time(datetime.now()))

print(get_showcase())

