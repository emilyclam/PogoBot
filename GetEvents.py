from bs4 import BeautifulSoup
import requests
import re

events_page = requests.get("https://leekduck.com/events/")
page = BeautifulSoup(events_page.text, "html.parser")


def process_date(date):
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"
    return date


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
        return [False, None, None, None]

    event_link = event.parent.parent.find('a', attrs={'class', 'event-item-link'})
    event_page = requests.get("https://leekduck.com" + event_link['href'])
    event_page = BeautifulSoup(event_page.text, "html.parser")

    # check if there are any current showcases (if the first one found hasn't started yet)
    live_showcase = True  # means there's a showcase going on right now
    if event.find('div', attrs={'class', 'countdown-text-type'}).text == "Starts: ":
        live_showcase = False

    # find pokemon
    pokemon = event_page.find('h1', attrs={'class', 'page-title'}).text
    pokemon = re.search(r'\s*(\D*) PokéStop', pokemon).group(1)

    # find date
    end_date = event_page.find(id='event-date-end').text
    end_date = process_date(end_date)

    return [live_showcase, end_date, pokemon]


get_showcase()
