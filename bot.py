import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

day = datetime.now().day
month = datetime.now().month
timers_active_focus = {}
timers_active_break = {}
streak_counter = {}



test_guild = discord.Object(id=1468297881130897510)

intents = discord.Intents.default()
intents.message_content = True


class BotCreate(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix="/", intents=intents)

bot = BotCreate()


message_counter = {}

@bot.event
async def on_ready():
	print(f"logged in as {bot.user}")
	try:
		synced = await bot.tree.sync()
		print(f"Synced {len(synced)} commands")
	except Exception as e:
		print(f"Failed to sync commands: {e}")
	bot.loop.create_task(streak_checker())


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	user_id = message.author.id

	print(f"{message.author}:{message.content}")

	await bot.process_commands(message)

	if user_id not in message_counter:
		message_counter[user_id] = 1
	else:
		message_counter[user_id] += 1


@bot.tree.command(name="ping", description="check bot is working")
async def ping(ctx: discord.Interaction):
	await ctx.response.send_message("pong")



@bot.tree.command(name="focus", description="start a focus timer")
async def focus(ctx: discord.Interaction, minutes: int):
	user_id = ctx.user.id
	if user_id in timers_active_focus:
		await ctx.response.send_message("you already have a timer started if you want to stop it type /stop_focus")
		return
	if minutes <= 0:
		await ctx.response.send_message("Please enter a positive value")
		return

	timers_active_focus[user_id] = True


	await ctx.response.send_message("your focus timer has started")

	await asyncio.sleep(minutes*60)

	if user_id not in timers_active_focus:
		return
	if minutes == 1:
		await ctx.followup.send(f"You have focused for {minutes} minute")
	elif minutes >= 10:
		await ctx.followup.send(f"You have focused for {minutes} minutes!")
	elif minutes >= 20:
		await ctx.followup.send(f"You have focused for {minutes} minutes! 🔥")
	else:
		await ctx.followup.send(f"You have focused for {minutes} minutes! Wow thats Exceptional 🔥🔥🔥")

	if minutes >= 10:
		if user_id not in streak_counter:
			streak_counter[user_id] = {"day": day,"month": month ,"value": 1}
			await ctx.followup.send("you have started a streak")
		else:
			if streak_counter[user_id]["day"] == day and streak_counter[user_id]["month"] == month:
				pass
			elif streak_counter[user_id]["day"] >= day+2 or streak_counter[user_id]["month"] != month:
				await ctx.followup.send("You gone for to long your streak has been reset to 1")
				streak_counter[user_id]["value"] = 1
			else:
				streak_counter[user_id]["value"] += 1
				await ctx.followup.send("You have added to you current streak!")

	timers_active_focus.pop(user_id)


@bot.tree.command(name="break", description="start a focus timer")
async def rest(ctx: discord.Interaction, minutes: int):
	user_id = ctx.user.id
	if user_id in timers_active_break:
		await ctx.response.send_message("you already have a break timer started if you want to stop it type /stop_break")
		return
	if minutes <= 0:
		await ctx.response.send_message("Please enter a positive value")
		return

	timers_active_break[user_id] = True

	await ctx.response.send_message("your break timer has started")

	await asyncio.sleep(minutes*60)

	if user_id not in timers_active_break:
		return

	await ctx.followup.send("your break timer has ended")

	timers_active_break.pop(user_id)


@bot.tree.command(name="stop_focus", description="stop focus timer")
async def stop_focus(ctx: discord.Interaction):
	user_id = ctx.user.id
	timers_active_focus.pop(user_id)
	await ctx.response.send_message("Focus timer stopped")

@bot.tree.command(name="stop_break", description="stop break timer")
async def stop_break(ctx: discord.Interaction):
	user_id = ctx.user.id
	timers_active_break.pop(user_id)
	await ctx.response.send_message("Break timer stopped")

@bot.tree.command(name="track", description="check how many messages you have sent in the server")
async def track(ctx: discord.Interaction):
	user_id = ctx.user.id
	count = message_counter.get(user_id, 0)
	await ctx.response.send_message(f"You have sent {count} messages")


@bot.tree.command(name="streak", description="check your focus streaks")
async def streak(ctx: discord.Interaction):
	if ctx.user.id not in streak_counter:
		await ctx.response.send_message("To start a streak start and finish a focus timer for 10 minutes or more.")
		return
	await ctx.response.send_message(f"Your daily focus streak is {streak_counter[ctx.user.id]['value']} 🔥")


async def streak_checker():
	await bot.wait_until_ready()
	while not bot.is_closed():
		hour_now = datetime.now().time().hour
		day_now = datetime.now().day
		month_now = datetime.now().month
		for user_id, data in list(streak_counter.items()):
			day_then = data["day"]
			month_then = data["month"]
			if (month_now == month_then and (day_now - day_then) >= 2) or (month_now != month_then and day_now >= 2):
				try:
					user = await bot.fetch_user(user_id)
					await user.send("Your streak has ended, finish a focus timer to start a new streak")
					streak_counter.pop(user_id)
				except discord.Forbidden:
					print(f"Can't DM {user_id}")
			elif day_now == day_then and month_now == month_then:
				pass
			elif hour_now == 17:
				reminders = [
					"Don’t forget your focus streak today! Start a session to keep the momentum going.",
					"Your streak is on the line! Finish a focus timer and keep it alive.",
					"Another day, another focus session! Let’s keep that streak shining.",
					"Consistency is key! Start a focus timer and maintain your streak.",
					"Time to focus! Your streak is waiting for you — don’t let it slip.",
					"Keep the streak going! A single focus session keeps the streak alive.",
					"Hit your focus target today and keep your streak strong!",
					"FlowMode ON! Start a focus timer and ride the streak wave.",
					"Your streak is valuable — don’t break it! Focus for a few minutes now.",
					"Little steps build big habits! Start a focus session to continue your streak."
				]
				user = await bot.fetch_user(user_id)
				await user.send(random.choice(reminders))
	
		await asyncio.sleep(60*60)



@bot.tree.command(name="quote", description="get a short motivational message")
async def quote(ctx: discord.Interaction):
	quotes = ["Don’t watch the clock; do what it does. Keep going.",
		   "Success is not final, failure is not fatal: It is the courage to continue that counts.",
		   "Believe you can and you’re halfway there.",
		   "The only way to do great work is to love what you do.",
		   "Dream big and dare to fail.",
		   "Your limitation—it’s only your imagination.",
		   "Push yourself, because no one else is going to do it for you.",
		   "Great things never come from comfort zones.",
		   "Don’t stop when you’re tired. Stop when you’re done.",
		   "Every day is a second chance."
		   ]
	quote = random.randint(0,len(quotes)-1)
	await ctx.response.send_message(quotes[quote])


load_dotenv()
API_KEY = os.getenv('API_KEY')

bot.run(API_KEY)






