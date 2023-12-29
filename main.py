import discord
import private
import GetEvents

intents = discord.Intents(1 << 9 | 1 << 10 | 1 << 11 | 1 << 12 | 1 << 13 | 1 << 14 | 1 << 15)
client = discord.Client(intents=intents)


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
    live_showcase, end_date, pokemon = GetEvents.get_showcase()
    resp = ""
    if not live_showcase:
        resp = f"There aren't any showcases going on at the moment."
    else:
        resp = f"The current showcase is for **{pokemon}**. It ends **{end_date}**."
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

    if message.content == "/spotlight":
        await message.channel.send(get_spotlight_hour())
        # await message.channel.send(get_spotlight_hour(), file=discord.File('351.png'))

    if message.content == "/raidhour":
        await message.channel.send(get_raid_hour())

    if message.content == "/commday":
        await message.channel.send(get_comm_day())

    if message.content == "/showcase":
        await message.channel.send(get_showcase())


client.run(private.TOKEN)
