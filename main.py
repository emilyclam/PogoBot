import discord
import private
import asyncio
import GetEvents
import Quiz
import Question

# RN: quiz feature -> trying to get user response to quiz answer!

# SOURCE 1 = https://github.com/Rapptz/discord.py/blob/v2.3.2/examples/guessing_game.py
#testing git

intents = discord.Intents(1 << 9 | 1 << 10 | 1 << 11 | 1 << 12 | 1 << 13 | 1 << 14 | 1 << 15)
client = discord.Client(intents=intents)


def get_help():
    resp = f"**/spotlight** to get the current spotlight\n" + \
           f"**/raidhour** to get info about the upcoming raid hour\n" + \
           f"**/commday** to get info about the upcoming community day\n" + \
           f"**/showcase** to get info about the current showcase\n" + \
           f"**/fivestar** to get info about the current five-star raid boss\n" + \
           f"**/mega** or **/fourstar** to get info about the current mega raid boss\n" + \
           f"(not available yet) **/shadowbird** to get info about the current shadow bird raid boss\n" + \
           f"add **/next**  to the end of most commands to get the next event (eg /fivestar /next to get the next fivestar raid boss\n" + \
           f"**/help** to get the full list of commands for PogoBot\n"
    return resp


def get_spotlight_hour():
    date, pokemon, bonus = GetEvents.get_spotlight_hour()
    resp = f"The next Spotlight will be 6-7pm Tuesday, **{date}** featuring **{pokemon}**" + \
           f"! The bonus will be **{bonus}**."
    return resp


def get_raid_hour():
    date, pokemon, details = GetEvents.get_raid_hour()
    resp = f"The next Raid Hour will be 6-7pm **{date}** featuring **{pokemon}**. {details}"
    return resp


def get_comm_day():
    date, pokemon, attack = GetEvents.get_comm_day()
    if attack is None:
        resp = f"The next Community Day will be **{date}** featuring **{pokemon}**.\n\nThe special move has not been released yet."
    else:
        resp = f"The next Community Day will be **{date}** featuring **{pokemon}**.\n\n{attack}"
    return resp


def get_showcase(get_current):
    end_date, pokemon = GetEvents.get_showcase(get_current)
    resp = ""
    if end_date is None:
        resp = f"There aren't any showcases going on at the moment."
    else:
        if get_current:
            resp = f"The current showcase is for **{pokemon}**. It ends **{end_date}**."
        else:
            resp = f"The next showcase will be for **{pokemon}**. It'll end **{end_date}**."
    return resp


def get_five_star(get_current):

    date, time, bosses = GetEvents.get_five_star(get_current)
    resp = ""

    if date is None:
        return f"There aren't any 5-star raids going on right now (how rare!)."

    for i, boss in enumerate(bosses):
        try:
            boss_info = GetEvents.get_boss_info(boss, "5")
            weaknesses = Question.get_pokemon_weakness(boss_info["type"])

            if get_current:
                resp += f"5-star raids currently feature **{boss}**, until {time} {date}.\n\n"
            else:
                resp += f"The next 5-star raids will feature **{boss}**, until {time} {date}.\n\n"

            resp += f"Type: {', '.join(boss_info['type'])}\n" + \
                    f"Boosted Weather: {', '.join(boss_info['boosted_weather'])}\n" + \
                    f"Unboosted Max CP: {boss_info['min_unboosted_cp']} - {boss_info['max_unboosted_cp']}\n" + \
                    f"Boosted Max CP: {boss_info['min_boosted_cp']} - {boss_info['max_boosted_cp']}\n" + \
                    f"{boss_info['name']} is weak against: {', '.join(weaknesses)}"
        except TypeError:
            resp = f"5-star raids currently feature **{boss}**.\n\n" + \
                   f"Sorry, couldn't find any info about this raid boss."
        if i + 1 < len(bosses):
            resp += "\n\n"
    return resp


def get_mega(get_current):
    date, time, bosses = GetEvents.get_mega(get_current)
    resp = ""

    if date is None:
        return f"There aren't any mega raids going on right now (how rare!)."

    for i, boss in enumerate(bosses):
        try:
            boss_info = GetEvents.get_boss_info(boss, "mega")
            weaknesses = Question.get_pokemon_weakness(boss_info["type"])

            if get_current:
                resp += f"Mega raids currently feature **{boss}**, until {time} {date}.\n\n"
            else:
                resp += f"The next Mega raids will feature **{boss}**, until {time} {date}.\n\n"

            resp += f"Type: {', '.join(boss_info['type'])}\n" + \
                f"Boosted Weather: {', '.join(boss_info['boosted_weather'])}\n" + \
                f"Unboosted Max CP: {boss_info['min_unboosted_cp']} - {boss_info['max_unboosted_cp']}\n" + \
                f"Boosted Max CP: {boss_info['min_boosted_cp']} - {boss_info['max_boosted_cp']}\n" + \
                f"{boss_info['name']} is weak against: {', '.join(weaknesses)}"
        except TypeError:
            resp = f"5-star raids currently feature **{boss}**.\n\n" + \
                    f"Sorry, couldn't find any info about this raid boss."
        if i+1 < len(bosses):
            resp += "\n\n"
    return resp


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


quiz = Quiz.Quiz()  # always exists; only active during quiz


@client.event
async def on_message(message):
    get_current = True
    global quiz

    async def ask_question():
        quiz.q = Question.make_question()
        await message.channel.send(f"({quiz.questionCounter + 1}) {quiz.q.question}")

        # this code based off of SOURCE 1
        def is_correct(m):  # check if answer is valid or not
            return m.author.display_name in quiz.players.keys() and m.channel == message.channel and isinstance(
                m.content,
                str)

        while (not quiz.q.isOver) or len(quiz.q.answerers) < len(quiz.players):
            # try:
            guess = await client.wait_for('message', check=is_correct)  # timeout=15.0
            player = guess.author.display_name
            # except asyncio.TimeoutError:
            #    return await message.channel.send(f"Time's up! Possible answers were: {q.answer.join(',')}.")

            if player in quiz.q.answerers:
                await message.channel.send(f"You've already guessed, {player}...")
                print(f"already guessed {quiz.q.answerers}, {quiz.q.question}")
            else:
                quiz.q.answerers.append(player)
                if quiz.q.is_correct(guess.content):
                    print("correct")
                    await message.channel.send(f"**{guess.content}** is right! Nice one, {player}!\n"
                                               f"Possible answers were {', '.join(quiz.q.answer)}")
                    quiz.players[player].points += 1
                    quiz.q.isOver = True
                else:
                    await message.channel.send(f"Not quite...\nPossible answers were {', '.join(quiz.q.answer)}")

        print("question has been answered")
        quiz.questionCounter += 1

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    """
    ------------------------------- QUIZ -----------------------------------
    """
    if message.content == "/quiz":
        quiz.isActive = True
        #quiz.add_player(message.author)
        await message.channel.send(f"**Quiz will start soon!**\n" +
                                   "* Type **/join** to join the quiz.\n" +
                                   "* Type **/ready** once you're ready for questions.\n" +  # for raids is it "ready" or "ready up?"
                                   "* Quiz will start once everyone is ready!\n" +
                                   "* First person to answer correctly gets the point!\n"
                                   "* If everyone gets the question wrong, we'll move on.\n")

    # players can join the quiz
    if message.content == "/join" and quiz.isActive and not quiz.hasStarted:
        # or should i do the check for duplicates in add_player()?
        if message.author not in quiz.players.keys():  # what about duplicate usernames?
            quiz.add_player(message.author.display_name)
            await message.channel.send(f"Welcome {message.author.display_name}!\n" +
                                       f"Current players: {quiz.players_tostring()}")

    # players can ready up. all joined players need to be readied up before quiz will start
    if message.content == "/ready" and quiz.isActive and not quiz.hasStarted:
        if message.author.display_name in quiz.players.keys():
            quiz.readyPlayers.append(message.author.display_name)
            quiz.readyPlayers = list(set(quiz.readyPlayers))  # delete repeats
            await message.channel.send(f"Ready players ({len(quiz.readyPlayers)}/{len(quiz.players)}): {' '.join(quiz.readyPlayers)}")

            # start quiz when everyone is ready
            if len(quiz.readyPlayers) == len(quiz.players):
                if quiz.questionCounter == 0:
                    await message.channel.send(f"\nQuiz is starting!\n")
                else:
                    await message.channel.send(f"\nLoading next question...\n")
                quiz.hasStarted = True

    if quiz.isActive and quiz.hasStarted:
        print("make new question")
        quiz.q = Question.make_question()
        resp = ""
        await message.channel.send(f"({quiz.questionCounter + 1}) {quiz.q.question}")

        # this code based off of SOURCE 1
        def is_correct(m):  # check if answer is valid or not
            return m.author.display_name in quiz.players.keys() and m.channel == message.channel and isinstance(
                m.content, str)

        while not quiz.q.isOver:
            print("q")
            # try:
            guess = await client.wait_for('message', check=is_correct)  # timeout=15.0
            player = guess.author.display_name
            print(guess.content)
            # except asyncio.TimeoutError:
            #    return await message.channel.send(f"Time's up! Possible answers were: {q.answer.join(',')}.")

            if player in quiz.q.answerers:
                #await message.channel.send(f"You've already guessed, {player}...")
                print(f"already guessed {quiz.q.answerers}, {quiz.q.question}")
            else:
                quiz.q.answerers.append(player)
                if quiz.q.is_correct(guess.content):
                    print("correct")
                    #await message.channel.send(f"**{guess.content}** is right! Nice one, {player}!\n"
                    #                           f"Possible answers were {', '.join(quiz.q.answer)}")
                    resp += f"**{guess.content}** is right! Nice one, {player}!\n"
                    quiz.players[player].points += 1
                    quiz.q.isOver = True
                else:
                    #await message.channel.send(f"Not quite...\nPossible answers were {', '.join(quiz.q.answer)}")
                    print("note quite")
                    resp += f"Not quite...\n"

            if len(quiz.q.answerers) >= len(quiz.players):
                print(f"{len(quiz.q.answerers)} >= {len(quiz.players)}, moving on")
                quiz.q.isOver = True

        if len(quiz.q.answer) > 1:
            resp += f"Possible answers were {', '.join(quiz.q.answer)}"

        if quiz.questionCounter < quiz.totalQuestions:
            resp += "\nLet me know when you're ready for the next one"
            quiz.hasStarted = False  # players need to ready up again
            quiz.readyPlayers = []
            quiz.questionCounter += 1
            print("all done!")
        else:
            resp += f"\n\nQuiz is over! Here are the results:\n" + \
                    f"{quiz.players_tostring()}\n"
            winner = quiz.get_winner()
            if winner is None:
                resp += f"It looks like there was a tie! Let's do a tie breaker! Let me know when you're ready."
                quiz.totalQuestions += 1
            else:
                resp += f"It looks like the winner is {quiz.get_winner()}! Congrats!"
                quiz.end()

        print("reach")
        await message.channel.send(resp)

    if message.content == "/endquiz" and quiz.isActive:
        quiz.end()
        await message.channel.send('Quiz Ending')
        # insert stats
        quiz.isActive = False

    """
    ----------------------------- GET GAME INFORMATION -------------------------------------
    """
    if message.content.endswith('/next'):
        get_current = False

    if message.content == "/help":
        await message.channel.send(get_help())

    if message.content.startswith("/spotlight"):
        await message.channel.send(get_spotlight_hour())
        # await message.channel.send(get_spotlight_hour(), file=discord.File('351.png'))

    if message.content == "/raidhour":
        await message.channel.send(get_raid_hour())

    if message.content == "/commday":
        await message.channel.send(get_comm_day())

    if message.content.startswith("/showcase"):
        await message.channel.send(get_showcase(get_current))

    if message.content.startswith("/fivestar"):
        await message.channel.send(get_five_star(get_current))

    if message.content.startswith("/mega") or message.content.startswith("/fourstar"):
        await message.channel.send(get_mega(get_current))

client.run(private.TOKEN)
