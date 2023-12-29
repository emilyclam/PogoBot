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


client.run(private.TOKEN)
