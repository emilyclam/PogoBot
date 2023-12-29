from bs4 import BeautifulSoup
import requests
import re

event_page = requests.get("https://leekduck.com/events/")
page = BeautifulSoup(event_page.text, "html.parser")


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
    raid_hour = page.find('div', attrs={'class': 'raid-hour'})
    pokemon = raid_hour.find('h2').text
    pokemon = re.search(r'(\D*) Raid Hour', pokemon).group(1)

    # find date
    raid_link = raid_hour.parent.parent.find('a', attrs={'class', 'event-item-link'})
    r_page = requests.get("https://leekduck.com" + raid_link['href'])
    r_page = BeautifulSoup(r_page.text, "html.parser")
    date = r_page.find('div', attrs={'class', 'event-time-date-wrapper'}).find('span').text
    date = re.findall(r"\w+", date)
    date = f"{date[0]}, {date[1]} {date[2]}"

    details = ""
    # if there are multiple pokemon, find the regions
    if "," in pokemon:
        details = "\n"
        details += r_page.find('div', attrs={'class', 'event-description'}).find('ul').text

    return [date, pokemon, details]
