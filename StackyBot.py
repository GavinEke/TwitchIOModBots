import os
from datetime import datetime
import pytz
import discord
from discord.ext import commands as discord_commands
from twitchio.ext import commands
from dotenv import load_dotenv

# load secrets
load_dotenv() # take environment variables from .env

# set up the discord bot
intents = discord.Intents.default()
discord_bot = discord_commands.Bot(command_prefix='?', description='StackyBot', intents=intents)

class Twitch(discord_commands.Cog):
    def __init__(self, bot):
        self.discord_bot = bot
        self.bot = commands.Bot(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            client_secret=os.environ['CLIENT_SECRET'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']]
        )
        self.discord_bot.loop.create_task(self.bot.start())
        self.bot.listen("event_ready")(self.event_ready)
        self.bot.listen("event_message")(self.event_message)
        self.bot.listen("event_raw_usernotice")(self.event_raw_usernotice)
        self.bot.listen("event_clearchat")(self.event_clearchat)
        self.bot.command(name='ping', aliases=['test'])(self._twitchpingcmd)

    # TwitchIO event_message
    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f"Twitch bot is online!")

    # TwitchIO event_message
    async def event_message(self, message):
        'Runs every time a message is sent in chat.'
        dtnow = datetime.now(pytz.timezone('Australia/Brisbane')).strftime("%H:%M:%S")
        discord_channel = self.discord_bot.get_channel(836112934676594699)

        if message.author.name.lower() == message.channel.name:
            await discord_channel.send(f"[{dtnow}] <:twitchBroadcaster:836116626067554335> **{message.author.name}**: {message.content}")
        elif message.author.is_mod:
            await discord_channel.send(f"[{dtnow}] <:twitchMod:836116625878155285> **{message.author.name}**: {message.content}")
        elif message.author.is_subscriber:
            await discord_channel.send(f"[{dtnow}] <:wallaby:675657839582117898> **{message.author.name}**: {message.content}")
        else:
            await discord_channel.send(f"[{dtnow}] **{message.author.name}**: {message.content}")
            if "wanna become famous" in message.content.lower() or "bigfollows" in message.content.lower(): # Checks common spam bot terms
                print(f"POSSIBLE SPAM BOT - {message.author.name}: {message.content}")
                await message.channel.timeout(message.author.name, 30, '30 second timeout due to possible spam bot detection')

        if "bits=" in message.raw_data: # Checks if the message has bits it in
            cheerAmount = message.raw_data.split("bits=")[1].split(";")[0]
            embed = discord.Embed(color=0x00fffb)
            embed.add_field(name="Bits Donation", value=f"**{message.author.name}** cheered **{cheerAmount}** bits", inline=False)
            await discord_channel.send(embed=embed)
            if int(cheerAmount) >= 1000: # Runs only if the bit donation is 1000 or more
                await message.channel.send(f"!hype")

        if "stacey" in message.content.lower() and message.author.name.lower() != self.bot.nick:
            await message.channel.send(f"@{message.author.display_name} who the f is stacey? there is only Stacy here")

    # TwitchIO event_raw_usernotice
    async def event_raw_usernotice(self, channel, tags):
        'Responds to subs, resubs, raids and gifted subs'
        discord_channel = self.discord_bot.get_channel(836112934676594699)
        
        if tags["msg-id"] == "raid":
            raiderChannel = tags["display-name"]
            raiders = tags["msg-param-viewerCount"]
            embed = discord.Embed(color=0xff4000)
            embed.add_field(name="Incoming Raid", value=f"**{raiderChannel}** raided with **{raiders}** raiders", inline=False)
            await discord_channel.send(embed=embed)
            if int(raiders) >= 3: # Runs only if the incoming raid had 3 or more raiders
                print(f"{raiderChannel} raided with {raiders} raiders")
                await channel.send(f"malibu8Hype WELCOME RAIDERS malibu8Hype")
                await channel.send(f"!so {raiderChannel}")

        if tags["msg-id"] == "subgift":
            subGiver = tags["display-name"]
            subReceiver = tags["msg-param-recipient-display-name"]
            embed = discord.Embed(color=0x00ff11)
            embed.add_field(name="Gift Sub", value=f"**{subGiver}** gave sub to **{subReceiver}**", inline=False)
            await discord_channel.send(embed=embed)

        if tags["msg-id"] == "anonsubgift":
            subReceiver = tags["msg-param-recipient-display-name"]
            embed = discord.Embed(color=0xfb00ff)
            embed.add_field(name="Anonymous Gift Sub", value=f"**{subReceiver}** received an anonymous gift sub", inline=False)
            await discord_channel.send(embed=embed)

        if tags["msg-id"] == "ritual":
            newChatter = tags["display-name"]
            embed = discord.Embed(color=0xfb00ff)
            embed.add_field(name="Ritual", value=f"**{newChatter}** is new in chat", inline=False)
            await discord_channel.send(embed=embed)
            await channel.send(f"Hey @{newChatter} welcome to the channel")

        if tags["msg-id"] == "sub":
            user = tags["display-name"]
            embed = discord.Embed(color=0x00ff11)
            embed.add_field(name="New Sub", value=f"**{user}** subbed", inline=False)
            await discord_channel.send(embed=embed)
            await channel.send(f"!hype")

        if tags["msg-id"] == "resub":
            user = tags["display-name"]
            cumulativeMonths = tags['msg-param-cumulative-months']
            embed = discord.Embed(color=0x00ff11)
            embed.add_field(name="Resub", value=f"**{user}** has resubbed for **{cumulativeMonths}** months", inline=False)
            await discord_channel.send(embed=embed)
            await channel.send(f"!hype")

    # TwitchIO event_clearchat
    async def event_clearchat(self, notice):
        'Runs every time a user banned, timed out or a message is deleted'
        discord_channel = self.discord_bot.get_channel(836112934676594699)
        await discord_channel.send(f"> **{notice.user.name}** got banned, timed out or a message is deleted")

    # TwitchIO command
    async def _twitchpingcmd(self, ctx):
        'Runs the twitch command !ping'
        if ctx.author.is_mod:
            print(f"Pong!")
            await ctx.send('Pong!')

    # Discord.py event on_ready
    @discord_commands.Cog.listener()
    async def on_ready(self):
        print(f"Discord bot logged in as {self.discord_bot.user}")

    # Discord.py event on_voice_state_update
    @discord_commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        'Runs every time a member joins or leaves a voice channel'
        wp_textchat_role = discord.utils.get(member.guild.roles, id=836106960746446858) # Watch Party
        vc_textchat_role = discord.utils.get(member.guild.roles, id=836108179976093737) # Voice Channels
        if before.channel is not None:
            if before.channel.id == 786105157037326386: # Watch Party
                await member.remove_roles(wp_textchat_role) # Role removed because member left the channel
                print(f"{member} removed from WP_textchat role")
            if before.channel.id == 682162015195627530 or before.channel.id == 670215474889621508 or before.channel.id == 675919862144434216 or before.channel.id == 717379911173799971: # Voice Channels
                await member.remove_roles(vc_textchat_role) # Role removed because member left the channel
                print(f"{member} removed from VC_textchat role")
        if after.channel is not None:
            if after.channel.id == 786105157037326386: # Watch Party
                await member.add_roles(wp_textchat_role) # Role is given because member joined the channel
                print(f"{member} added to WP_textchat role")
            if after.channel.id == 682162015195627530 or after.channel.id == 670215474889621508 or after.channel.id == 675919862144434216 or after.channel.id == 717379911173799971: # Voice Channels
                await member.add_roles(vc_textchat_role) # Role is given because member joined the channel
                print(f"{member} added to VC_textchat role")

    # Discord.py command
    @discord_commands.command(name='ping', aliases=['test'])
    @discord_commands.has_any_role(675659809285996552, 675658619240448041, 742308637816520764)
    async def _discordpingcmd(self, ctx):
        'Runs the discord command ?ping'
        print(f"Pong!")
        await ctx.send('Pong!')

    # Discord.py command
    @discord_commands.command(name='setemojirole')
    @discord_commands.has_permissions(manage_emojis=True)
    @discord_commands.bot_has_permissions(manage_emojis=True)
    async def _setemojirole(self, ctx: discord_commands.Context, emoji: discord.Emoji, *roles: discord.Role):
        """
        Creates the discord command ?setemojirole to change the permissions of which roles can use an emoji

        Example 1:
        ?setemojirole :emoji: @role

        Example 2:
        ?setemojirole twitchBroadcaster 833852343484940341
        """
        if emoji.guild != ctx.guild:
            raise discord_commands.BadArgument(f"Emoji :{emoji.name}: not found.")

        await emoji.edit(name=emoji.name, roles=list(roles), reason=f"Update by {ctx.author}")

        embed = discord.Embed(color=0xff7b00)
        embed.add_field(name="Set Emoji Role", value=f"The emoji **{emoji}** may now only be used by the following roles **{roles}**", inline=False)
        await ctx.send(embed=embed)

    @_setemojirole.error
    async def _setemojirole_error(self, ctx, error):
        if isinstance(error, discord_commands.MissingPermissions):
            await self.discord_bot.send_message(ctx.message.channel, f"Sorry {ctx.message.author}, you do not have permissions to do that!")

if __name__ == "__main__":
    discord_bot.add_cog(Twitch(discord_bot))
    discord_bot.run(os.environ['DISCORD_TOKEN'])
