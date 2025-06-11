import discord
import random
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
from dotenv import load_dotenv
from fuzzywuzzy import process

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

replies = ["hey there!", "hey, how ya doin?", "hi man whassup?", "hello fine shyt"]
replies_on_whatUdoin = [
    "nothing, just thinking about you",
    "nothing specific tbh",
    "missing you",
    "contemplating life"
]
replies_on_kiKoro=["kisuna","none of your damn business","ami bangla bujhina","jibon niye bhabi"]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"I am here {bot.user}")

@bot.tree.command(name="greet", description="Send a greeting to someone")
@app_commands.describe(name="The name of the person you want to greet")
async def greet(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"KHANKIRPOLA {name}! CHOD KHAIYA MOIRA JAA")

@bot.tree.command(name="ganjaprice", description="Ask about the price of weed")
@app_commands.describe(name="The name of the person you want to greet")
async def ganjaprice(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"kire {name}, ganjar price koto ekhon ")


@bot.tree.command(name="bicepsize", description="Ask about the price of weed")
@app_commands.describe(name="The name of the person you want to greet")
async def bicepsize(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"oi hala {name} tor bicep nai ken")


@bot.tree.command(name="weather", description="Get the current weather for a city")
@app_commands.describe(city="City name to fetch weather for")
async def weather(interaction: discord.Interaction, city: str):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                description = data["weather"][0]["description"].title()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                await interaction.response.send_message(
                    f"**Weather in {city.title()}**\n"
                    f"Condition: {description}\n"
                    f"Temperature: {temp}°C\n"
                    f"Humidity: {humidity}%"
                )
            else:
                await interaction.response.send_message("City not found or API error.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    
    content = ' '.join(message.content.lower().split())

    
    responses = {
        "heybro": [f"{message.author.name}, {random.choice(replies)}"],
        "ay bro whassup": ["Hi brother, how are you?"],
        "what are you doing?": [random.choice(replies_on_whatUdoin)],
        "zakaria er dhon choto": ["ho or biceps o nai"],
        "jubayer tsnim noor pglu": ["ho oi maiya ekta magi"],
        "how are you doing guys?": ["Ei server er shob polar dhon choto"],
        "dont be so mean comeon": ["aap maa chodao hum behen chodte hain"],
        "howyadoin": ["I am fine, and you?"],
        "who is that in your pfp": ["It's Mr. Zakaria. He has no bicep."],
        "ki koro bro" :[random.choice(replies_on_kiKoro)],
        "kire hridhik ki obostha":["ganjuitta halay eine ki kore"],
        "nah oy ganja oto khayna":["ganja khaiya e height ordhek gayeb"],
        "kire shahriar": ["Eram er bhai ailo"],
        "Shahriar tell us a joke":["He himself is a joke"]

    }

    best_match, score = process.extractOne(content, responses.keys())

    if score > 80:
        response = random.choice(responses[best_match])
        await message.channel.send(response)
    else:
        await bot.process_commands(message)
    print(WEATHER_API_KEY)

@bot.tree.command(name="manualchat", description="Send a message on behalf of the bot")
async def manual_chat(interaction: discord.Interaction, message: str):
    # Send the provided message to the same channel where the slash command was invoked
    await interaction.response.defer(thinking=False)
    channel = interaction.channel  # Get the current channel
    await channel.send(message)  # Send the manual message
    try:
        # Delete the "knockoff_bot is thinking..." message (interaction reply)
        followup = await interaction.original_response()
        await followup.delete()
    except discord.NotFound:
        pass  # Already deleted or not found — ignore
@bot.tree.command(name="google", description="Search Google and get top result")
@app_commands.describe(query="Your search query or question")
async def google_search(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    # Check if credentials are set
    if not api_key or not cse_id:
        await interaction.followup.send("Google Search API credentials are not configured.")
        return

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": 1  # Get only the top result
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items")
                    if items:
                        top_result = items[0]
                        title = top_result["title"]
                        link = top_result["link"]
                        snippet = top_result.get("snippet", "No description available.")
                        
                        # Truncate snippet if too long
                        if len(snippet) > 300:
                            snippet = snippet[:300] + "..."
                        
                        # Enhanced response formatting
                        response = (
                            f"**Search Query:** {query}\n\n"
                            f"**Result Title:** {title}\n\n"
                            f"**Snippet:** {snippet}\n\n"
                            f"**Full Link:** {link}"
                        )
                        
                        await interaction.followup.send(response)
                    else:
                        await interaction.followup.send(f"No results found for: '{query}'")
                else:
                    await interaction.followup.send(f"Search failed. Status code: {resp.status}")
    except aiohttp.ClientError as e:
        await interaction.followup.send(f"Network error occurred: {str(e)}")
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {str(e)}")


bot.run("MTM2NzgwNzk4OTg3MTkzOTY1NA.Gg3q4b.x_qZO1x8-JYOf3mIT_JcnvqIJYK-D39NK01pkw")
