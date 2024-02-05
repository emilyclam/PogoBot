import QuizPlayer

"""
Quiz class

attributes
- score

methods:
- random pokemon generator (sends back name, id??)
- get pokemon image? (given name, send back image? should i have this ina dif file?)
- the different types of questions (should this be its own object?)
    - given image, name the pokemon
    - given the pokemon (name? image?) select the types
    - given a pokemon (name? image?) select the weaknesses
    - t/f question on type effectiveness? 
- update score
- pick a random question to ask

questions
- question, image if applicable
- the correct answer
- how to generate the question?? is the answer multiple choice? is so, how to generate the
option choices?

question generator: given pokemon + "type" --> it'll ask what the type of the pokemon is
- or should it decide a random pokemon itself? no ishould do it here, or else i would have to
be choosing a random pokemon every time for every type of question
- so it looks up the answer and returns it

question generator: given pokemon + "weakness" --> look up answer and return it
question: given two randomly generated types (just have array of all and choice() them) --> look
up how type1 is to type2
question: weather boost (given weather, what types are boosted?) (given pokemon, what weather boosts it?)
question: what generation is it from?
question: which pokemon is bigger? (lol)

i also need to make it so i can easily ask multiple questions.. so the code is reusable

everytime you create a Question() object it decides what type of question it is (random)
solution: ""

or, each type of question is a method; eg if you ask question of type "weakness" it enters that
method. from there, it has to choose a random pokemon (input). then it searches it up

but there will be less code/repeated parts ifi just decide all the inputs at the beginning.
i just need to include all the possible info it might need for any type of question; 
the question it ends up asking might not necessarily use that info tho
nah that just feels weird

"""


class Quiz:
    def __init__(self):
        self.isActive = False
        self.hasStarted = False  # once a quiz has started it's not joinable
        self.players = {}
        self.currentQuestion = ""
        self.currentAnswer = ""

    def get_winner(self):
        """Return player with the most points."""
        winner = (0, None)  # (points, name)
        for player in self.players:
            if winner[0] < player.points:
                winner = (player.points, player.name)
        return winner[1]

    def add_player(self, name):
        """Add player to the quiz."""
        self.players[name] = QuizPlayer.QuizPlayer(name)

    def end(self):
        """Clear all the data and set quiz to inactive."""
        self.__init__()

