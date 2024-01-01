import discord
import private
import GetEvents

intents = discord.Intents(1 << 9 | 1 << 10 | 1 << 11 | 1 << 12 | 1 << 13 | 1 << 14 | 1 << 15)
client = discord.Client(intents=intents)


def get_help():
    resp = f"**/spotlight** to get the current spotlight\n" + \
           f"**/raidhour** to get info about the upcoming raid hour\n" + \
           f"**/commday** to get info about the upcoming community day\n" + \
           f"**/showcase** to get info about the current showcase\n" + \
           f"**/fivestar** to get info about the current five-star raid boss\n" + \
           f"**/mega** or **/fourstar** to get info about the current mega raid boss\n" + \
           f"**/shadowbird** to get info about the current shadow bird raid boss\n" + \
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
    resp = f"The next Community Day will be **{date}** featuring **{pokemon}**.\n\n{attack}"
    return resp


def get_showcase():
    end_date, pokemon = GetEvents.get_showcase()
    resp = ""
    if end_date is None:
        resp = f"There aren't any showcases going on at the moment."
    else:
        resp = f"The current showcase is for **{pokemon}**. It ends **{end_date}**."
    return resp


def get_five_star():
    try:
        date, time, boss = GetEvents.get_five_star()
        boss_info = GetEvents.get_boss_info(boss, "5")
        weaknesses = GetEvents.find_weakness(boss_info["type"])

        resp = f"5-star raids currently feature **{boss_info['name']}**, until {time} {date}.\n\n" + \
            f"Type: {', '.join(boss_info['type'])}\n" + \
            f"Boosted Weather: {', '.join(boss_info['boosted_weather'])}\n" + \
            f"Unboosted Max CP: {boss_info['min_unboosted_cp']} - {boss_info['max_unboosted_cp']}\n" + \
            f"Boosted Max CP: {boss_info['min_boosted_cp']} - {boss_info['max_boosted_cp']}\n" + \
            f"{boss_info['name']} is weak against: {', '.join(weaknesses)}"

    except TypeError:
        boss = GetEvents.get_five_star()
        resp = f"5-star raids currently feature **{boss}**.\n\n" + \
               f"Sorry, couldn't find any info about this raid boss."

    return resp


def get_mega():
    try:
        date, time, boss = GetEvents.get_mega()
        boss_info = GetEvents.get_boss_info(boss, "mega")
        weaknesses = GetEvents.find_weakness(boss_info["type"])

        resp = f"Mega raids currently feature **{boss_info['name']}**, until {time} {date}.\n\n" + \
               f"Type: {', '.join(boss_info['type'])}\n" + \
            f"Boosted Weather: {', '.join(boss_info['boosted_weather'])}\n" + \
            f"Unboosted Max CP: {boss_info['min_unboosted_cp']} - {boss_info['max_unboosted_cp']}\n" + \
            f"Boosted Max CP: {boss_info['min_boosted_cp']} - {boss_info['max_boosted_cp']}\n" + \
            f"{boss_info['name']} is weak against: {', '.join(weaknesses)}"
    except TypeError:
        boss = GetEvents.get_five_star()
        resp = f"5-star raids currently feature **{boss}**.\n\n" + \
               f"Sorry, couldn't find any info about this raid boss."

    return resp


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content == "/help":
        await message.channel.send(get_help())

    if message.content == "/spotlight":
        await message.channel.send(get_spotlight_hour())
        # await message.channel.send(get_spotlight_hour(), file=discord.File('351.png'))

    if message.content == "/raidhour":
        await message.channel.send(get_raid_hour())

    if message.content == "/commday":
        await message.channel.send(get_comm_day())

    if message.content == "/showcase":
        await message.channel.send(get_showcase())

    if message.content == "/fivestar":
        await message.channel.send(get_five_star())

    if message.content == "/mega" or message.content == "/fourstar":
        await message.channel.send(get_mega())

client.run(private.TOKEN)
