import os
from parser import TAG, execute

from discord import Client

client = Client()


@client.event
async def on_ready():
    print("I am ready!")


@client.event
async def on_message(message):
    if message.content.startswith(TAG):
        await message.channel.send(await execute(client, message))


client.run(os.getenv("DISCORD_TOKEN"))
