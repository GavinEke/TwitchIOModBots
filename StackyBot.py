import os, socket, time, re, json, datetime, requests
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env

# set up the bot
bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=['malibustacy'] # [os.environ['CHANNEL']]
)

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"StackyBot is online!")

@bot.event
async def event_message(message):
    'Runs every time a message is sent in chat.'
    if message.author.name.lower() == bot.nick or message.author.name.lower() == message.channel.name:
        return # Do nothing if the message is from bot or channel account
    elif message.author.name.lower().startswith('manofsteel'): # Checks for MoS who is a common troll in the Mario community
        print(f"{message.author.name}: {message.content}")
        mos_user = await bot.get_users(message.author.name) # Gets channel user in twitchio.dataclasses.User class format
        await message.channel.ban(message.author.name, (f"MoS Banned - account created: {mos_user[0].created_at}"))
    elif "wanna become famous" in message.content.lower() or "bigfollows" in message.content.lower(): # Checks common spam bot terms
        print(f"POSSIBLE SPAM BOT - {message.author.name}: {message.content}")
        if not message.author.badges: # Checks for any badges next to name eg. sub, mod, vip, bits etc
            channel_user = await bot.get_users(message.channel.name) # Gets channel user in twitchio.dataclasses.User class format
            follow_relationship = await bot.get_follow(message.author.id,channel_user[0].id) # Get follow relationship to channel
            if not follow_relationship: # Checks if the message.author follows the channel
                print(f"BAN SPAM BOT - {message.author.name}")
                await message.channel.ban(message.author.name, 'SPAM BOT')
    elif "bits=" in message.raw_data: # Checks if the message has bits it in
        cheerAmount = message.raw_data.split("bits=")[1].split(";")[0] # Sets bits amount to cheerAmount variable
        if int(cheerAmount) >= 1000: # Runs only if the bit donation is 1000 or more
            print(f"{message.author.display_name} cheered {cheerAmount} bits") 
            await message.channel.send(f"!hype")

@bot.event
async def event_join(ctx):
    'Runs every time when a JOIN is received from Twitch'
    if ctx.name.lower().startswith('manofsteel'): # Checks for MoS who is a common troll in the Mario community
        print(f"{ctx.name} JOINED chat")
        mos_user = await bot.get_users(ctx.name) # Gets channel user in twitchio.dataclasses.User class format
        await ctx.channel.ban(ctx.name, (f"MoS Banned - account created: {mos_user[0].created_at}"))

@bot.event
async def event_usernotice_subscription(metadata):
    'Runs every time a user subscribes or re-subscribes'
    print(f"{metadata.user.name} subbed")
    await metadata.channel.send(f"!hype")

@bot.event
async def event_raw_usernotice(channel, tags):
    'Responds to subs, resubs, raids and gifted subs'
    if tags["msg-id"] == "raid": # Checks if the usernotice is a raid
        raiderChannel = tags["display-name"] # sets raider to raiderChannel variable
        raiders = tags["msg-param-viewerCount"] # sets number of raiders to raiders variable
        if int(raiders) >= 3: # Runs only if the incoming raid had 3 or more raiders
            print(f"{raiderChannel} raided with {raiders} raiders")
            await channel.send(f"malibu8Hype WELCOME RAIDERS malibu8Hype")
            await channel.send(f"!so {raiderChannel}")

@bot.event
async def event_clearchat(notice):
    'Runs every time a user banned, timed out or a message is deleted'
    print(f'{notice.user.name} got banned, timed out or a message is deleted.')    

@bot.command(name='ping', aliases=['test'])
async def ping(ctx):
    'Runs every time !ping or !test is called'
    await ctx.send('pong!')

if __name__ == "__main__":
    bot.run()