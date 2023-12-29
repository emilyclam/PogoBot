import discord
import os

TOKEN = "MTE5MDE2NTgwMDk3MjE4OTY5Ng.GCtUXk.71Vpmq-y8FWD_XEGN9hgLq5LH09MLKPQGQxAbQ"

#client = discord.Client(intents=discord.Intents(68608))
intents = discord.Intents(1 << 9 | 1 << 10 | 1 << 11 | 1 << 12 | 1 << 13 | 1 << 14 | 1 << 15)
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

#client.run(os.getenv('TOKEN'))
client.run(TOKEN)
