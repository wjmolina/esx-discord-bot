import os
from parser import TAG, execute

from discord import Client

client = Client()


@client.event
async def on_ready():
    await client.get_channel(962074652740554836).send("I have hatched.")


@client.event
async def on_message(message):
    if message.content.startswith(TAG):
        await message.channel.send(await execute(client, message))
    elif message.content == "Ain't that right?":
        await message.channel.send("Yes it is.")


client.run(os.getenv("DISCORD_TOKEN"))
