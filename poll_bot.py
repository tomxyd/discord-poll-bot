import discord
from discord.ext import commands, tasks
import datetime
import logging
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True #required to read messages

bot = commands.Bot(command_prefix="!",  intents=intents)

#replace with your target channel ID
CHANNEL_ID = 1357507233063112825

#set your scheduled time (24-hour format)
SCHEDULED_HOUR = 18 # 2 PM
SCHEDULED_MINUTE = 30

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduled_poll.start()

# ...existing code...

poll_active = False
poll_message_id = None
poll_options = {
    "🟩": "South side",
    "🟦": "North side",
    "🟨": "West side"
}
poll_votes = {}  # user_id: option

CHANNEL_IDS = [1324143756701597736, 1357507233063112825]  # Add your second channel ID here

poll_message_ids = {}  # channel_id: message_id

@tasks.loop(minutes=1)
async def scheduled_poll():
    global poll_active, poll_message_ids, poll_votes
    now = datetime.datetime.now()
    if now.weekday() == 5 and now.hour == SCHEDULED_HOUR and now.minute == SCHEDULED_MINUTE:
        poll_active = True
        poll_votes = {}
        poll_message_ids = {}
        for channel_id in CHANNEL_IDS:
            channel = bot.get_channel(channel_id)
            if channel:
                msg = await channel.send(
                    "📊 **Poll:** I need a ride to church and I stay on the:\n\n"
                    "🟩 South side\n\n"
                    "🟦 North side\n\n"
                    "🟨 West side\n\n"
                    "Vote by reacting below!"
                )
                poll_message_ids[channel_id] = msg.id
                for emoji in poll_options.keys():
                    await msg.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    global poll_votes
    channel_id = reaction.message.channel.id
    if (
        poll_active
        and channel_id in poll_message_ids
        and reaction.message.id == poll_message_ids[channel_id]
        and not user.bot
    ):
        option = poll_options.get(str(reaction.emoji))
        if option:
            poll_votes[user.display_name] = option
            await reaction.message.channel.send(f"{user.display_name} voted on the {option.lower()}")

@bot.command()
async def pollresults(ctx):
    if not poll_active or not poll_message_ids:
        await ctx.send("No active poll.")
        return
    if not poll_votes:
        await ctx.send("No votes yet.")
        return
    results = {}
    for voter, option in poll_votes.items():
        results.setdefault(option, []).append(voter)
    msg = "**Poll Results:**\n"
    for option, voters in results.items():
        msg += f"{option}: {len(voters)} votes\n"
        msg += "Voters: " + ", ".join(voters) + "\n"
    await ctx.send(msg)


token = os.getenv("DISCORD_TOKEN")
bot.run(token)
