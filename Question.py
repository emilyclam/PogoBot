import json
import requests
import random
import re

# NUM_POKEMON = 1000
NUM_POKEMON = 500  # only include first 500 pokemon
"""
QUESTIONS
- given picture of pokemon -> whats it name
- given pokemon -> whats its type
- given pokemon + "weakness" --> look up answer and return it
- given two randomly generated types (just have array of all and choice() them) --> look
up how type1 is to type2
- weather boost
    - given weather -> what types are boosted?
    - given pokemon- > what weather boosts it?
- 1 pokemon -> what generation is it from?
- 2 pokemon -> which pokemon is bigger? (lol) (weighs more AND/OR is taller)

issue with pictures
- i forgot that i'll need to download all the pictures i use
- also how would main.py know that i have a picture here? (just need to think it through)

also account for the case that the stat wasn't found (try/except; if it returns None -> try again)

i feel i should standardize the answer types.. liek for types its an array cus it's possible that theres
more than one value, but rn for the weights its just a string cus there's only ever 1 answer..
but should i return an array for continuity? when i'm comparing user answer with correct answer it'll
make it a lot easier too
"""


# static.. so could be not in this class
# returns a random pokemon. output: (int:id, str:pokemon name)
def get_random_pokemon():
    name_page = requests.get("https://pogoapi.net/api/v1/pokemon_names.json")
    name_data = json.loads(name_page.text)
    id_num = random.randrange(0, NUM_POKEMON, 1)
    return id_num, name_data[str(id_num)]["name"]


def get_pokemon_type(name):
    type_page = requests.get("https://pogoapi.net/api/v1/pokemon_types.json")
    type_data = json.loads(type_page.text)

    # poke id doesn't align with index of pokemon, since some pokemon have multiple entries
    # eg multiple forms
    types = re.findall(f"'{name}', 'type': \[(\D+)\]", str(type_data))[0]
    types = [re.findall(f"'(\D+)'", t)[0] for t in types.split()]
    return types


def get_pokemon_weight(name):
    type_page = requests.get("https://pogoapi.net/api/v1/pokemon_height_weight_scale.json")
    type_data = json.loads(type_page.text)

    try:
        weight = re.findall(f"pokedex_weight': (\d+.\d+), [a-zA-z0-9',:_ ]+'{name}'", str(type_data))[0]
    except IndexError:
        weight = None
    return weight


# given name, guess the type; output = array:type(s)
def name_guess_type():
    id_num, pokemon_name = get_random_pokemon()
    print(id_num, pokemon_name)
    return f"{pokemon_name} is of what type(s)?"
    #self.answer = type_data[id_num + 1]["type"]


"""def picture_guess_name(self):  # input_guess_output
    id_num, pokemon_name = self.get_random_pokemon()
    self.question = "What pokemon is this?"
    self.solution = pokemon_name"""


def make_question():
    question_types = ["name_guess_type", "name_guess_heaver"]  # ideally i wouldn't have to manually update this but
    choice = random.choice(question_types)
    print(choice)
    q = Question()

    if choice == "name_guess_type":
        pokemon = get_random_pokemon()[1]  # name
        q.question = f"What type is {pokemon}? If there are multiple you only need to input 1."
        q.answer = get_pokemon_type(pokemon)

    elif choice == "name_guess_heaver":
        # make sure pokemon aren't too close in weight
        while True:
            p1 = get_random_pokemon()[1]
            p2 = get_random_pokemon()[1]
            w1 = float(get_pokemon_weight(p1))
            w2 = float(get_pokemon_weight(p2))
            if w1 is None or w2 is None:
                continue  # automatically try again
            if abs(w1 - w2) > 5:
                break  # leave loop once weight difference is large enough

        q.question = f"Which pokemon is (on average) heavier: {p1} or {p2}?"
        q.answer = p1 if w1 > w2 else p2

    return q


class Question:
    def __init__(self):
        self.question = ""
        self.answer = None  # array of possible correct answers
        self.user_answer = None  # not sure about yet
        # figure out type of question it is



        # fill in the details of the question (random generators)
        # find the answer

    def __str__(self):
        return f"question: {self.question} \nanswer: {self.answer}"


print(make_question())
