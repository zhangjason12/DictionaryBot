import discord
import responses
import requests
import os
import json
from discord.ext import commands
from webserver import keep_alive


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTE3MzExMjU0NzIwNTk4ODM4Mg.G4LKtc.qGxOhcqpjVpf16tKeurbBzvl80iHpexe7u6ilw'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(command_prefix='!', intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('!randomquote'):
            quote = get_random_quote()
            await message.channel.send(quote)

        if message.content.startswith('!define'):
            # Split the message content into a list of words
            words = message.content.split()

            # Check if there is a word after '!define' in the message
            if len(words) > 1:
                # Extract the word following '!define'
                word_to_define = words[1]

                # Call the get_definition function
                definition = get_definition(word_to_define)

                # Send the definition to the channel
                await message.channel.send(definition)
            else:
                # If no word is provided after '!define', inform the user
                await message.channel.send("Please provide a word after `!define`.")

        username = str(message.author)
        user_message = str(message.content)
        channel = (str(message.channel))

        print(f"{username} said: '{user_message}' ({channel})")

        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    keep_alive()
    client.run(TOKEN)


def get_random_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


def get_definition(inword):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{inword}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Check for HTTP errors
        json_data = response.json()

        print(json_data)  # For debugging purposes

        if isinstance(json_data, list) and json_data:
            first_entry = json_data[0]
            if 'meanings' in first_entry:
                meanings = first_entry['meanings']

                if meanings:
                    first_meaning = meanings[0]
                    part_of_speech = first_meaning.get('partOfSpeech', '')
                    definitions = first_meaning.get('definitions', [])

                    if definitions:
                        first_definition = definitions[0]
                        meaning = first_definition.get('definition', '')
                        return f"{inword} ({part_of_speech}): {meaning}"

        return "Definition not found."

    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"




