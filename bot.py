import os
from parser import TAG, execute

from discord import Client

client = Client()


@client.event
async def on_ready():
    await client.get_channel(962074652740554836).send("I hatched.")


@client.event
async def on_message(message):
    if message.content.startswith(TAG):
        await message.channel.send(await execute(client, message))
    elif message.content == "Am I right?":
        await message.channel.send("Yes you are.")


client.run(os.getenv("DISCORD_TOKEN"))
