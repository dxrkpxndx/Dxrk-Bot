import os
import discord
from discord import Activity, ActivityType
from keep_alive import keep_alive
import random
import json
from discord.ext import tasks
from itertools import cycle
import asyncio
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown

intents = discord.Intents.all()
client = commands.Bot(command_prefix=commands.when_mentioned_or("dxrk "), intents=intents, help_command=None)

@client.event
async def on_ready():
  channel = client.get_channel(834635134409900058)
  change_status.start()
  await channel.send('>>> I Am Online\nNow Suck It Bitch')
  print('Bot is ready')


@tasks.loop(seconds=2)
async def change_status():
	await client.change_presence(activity=discord.Game(next(status)))

mainshop = [
    {
        "name": "Watch",
        "price": 100,
        "description": "Show Off Your New Watch - Sells For $70"
    },
    {
        "name": "Laptop",
        "price": 1000,
        "description": "Gotta Work Your Ass Off - Sells For $700"
    },
    {
        "name": "PC",
        "price": 10000,
        "description": "RGB = FPS - Sells For $7k"
    },
    {
        "name": "Ferrari",
        "price": 1000000,
        "description": "Show Off Your Car - Sells For $70k"
    },
    {
        "name": "DxrkCoin",
        "price": 1000000,
        "description": "You Must Be A Cat Lover To Buy This - Sells For $700k "
    },
    {
        "name": "DxrkTower",
        "price": 1234,
        "description": "Lokis Favroite Place To Play On - Sells For $833.8"
    },
    {
        "name": "DxrkyBoy",
        "price": 6969,
        "description": "Show Off Your Money - Sells For $4878"
    },
    {
        "name": "Skull",
        "price": 39862,
        "description": "Being Loved - Sells For $27,903k "
    },
    {
        "name": "Stickers ",
        "price": 5,
        "description": "You'll Be Cool - Sells For $3.5"
    },
    {
        "name": "AnimePoster",
        "price": 50,
        "description": "Show Off You Like Anime - Sells For $35  "
    },
    {
        "name": "KFC Business",
        "price": 8300000000,
        "description": "Get Free Ckicken For Life - Sells For $5600000000  "
    },
]

status = cycle(['Dxrk Network', 'Dxrk Sec'
])

coinflip_actions = ['You Got  __**Heads!!**__', '>>> You Got __**Tails!!**__']

tips = [
  '']


#Admin App https://forms.gle/HmdW6q7xqqKsGUTJ6
#Ping Command {round(client.latency *1000)} 

@client.command(aliases=['bal'])
async def balance(ctx):
	await open_account(ctx.author)
	user = ctx.author

	users = await get_bank_data()

	wallet_amt = users[str(user.id)]["wallet"]
	bank_amt = users[str(user.id)]["bank"]

	em = discord.Embed(title=f'{ctx.author.name} Balance',
	                   color=discord.Color.red())
	em.add_field(name="Wallet Balance", value=wallet_amt)
	em.add_field(name='Bank Balance', value=bank_amt)
	await ctx.send(embed=em)

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.send(
		    f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} Seconds'
		)

@client.command(aliases=['with'])
async def withdraw(ctx, amount=None):
	await open_account(ctx.author)
	if amount == None:
		await ctx.send("Please enter the amount")
		return

	bal = await update_bank(ctx.author)

	amount = int(amount)

	if amount > bal[1]:
		await ctx.send('You do not have sufficient balance')
		return
	if amount < 0:
		await ctx.send('Amount must be positive!')
		return

	await update_bank(ctx.author, amount)
	await update_bank(ctx.author, -1 * amount, 'bank')
	await ctx.send(f'{ctx.author.mention} You withdrew {amount} coins')

@client.command(aliases=['dep'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You deposited {amount} coins')

@client.command(aliases=['sd'])
async def send(ctx, member: discord.Member, amount=None):
	await open_account(ctx.author)
	await open_account(member)
	if amount == None:
		await ctx.send("Please enter the amount")
		return

	bal = await update_bank(ctx.author)
	if amount == 'all':
		amount = bal[0]

	amount = int(amount)

	if amount > bal[0]:
		await ctx.send('You do not have sufficient balance')
		return
	if amount < 0:
		await ctx.send('Amount must be positive!')
		return

	await update_bank(ctx.author, -1 * amount, 'bank')
	await update_bank(member, amount, 'bank')
	await ctx.send(f'{ctx.author.mention} You gave {member} {amount} coins')

@client.command(aliases=['rb'])
@cooldown(1, 20, BucketType.user)
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)

    if bal < 100:
        await ctx.send('It is useless to rob him :(')
        return

    if bal > 1000:
        earning = random.randrange(1,1000)
    else:
        earning = random.randrange(1,bal)

    await update_bank(ctx.author, earning)
    await update_bank(member, -1 * earning)
    await ctx.send(
        f'{ctx.author.mention} You robbed {member} and got {earning} dollars')

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.send(
		    f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} Seconds'
		)

@client.command(pass_context=True)
@cooldown(1, 15, BucketType.user)
async def slots(ctx, amount=None):

	if amount == None:
		await ctx.send("Please enter an amount")
		return

	bal = await update_bank(ctx.author)

	amount = int(amount)
	if amount > bal[0]:
		await ctx.send("You don't have that much money!")
		return
	if amount < 0:
		await ctx.send("Amount must be positive")
		return

	slots = ['bus', 'train', 'horse', 'tiger', 'monkey', 'cow']
	slot1 = slots[random.randint(0, 5)]
	slot2 = slots[random.randint(0, 5)]
	slot3 = slots[random.randint(0, 5)]

	slotOutput = '| :{}: | :{}: | :{}: |\n'.format(slot1, slot2, slot3)

	ok = discord.Embed(title="Slots Machine", color=discord.Color.red())
	ok.add_field(name="{}\nWon".format(slotOutput),
	             value=f'You won {2*amount} coins')

	won = discord.Embed(title="Slots Machine", color=discord.Color.red())
	won.add_field(name="{}\nWon".format(slotOutput),
	              value=f'You won {3*amount} coins')

	lost = discord.Embed(title="Slots Machine", color=discord.Color.red())
	lost.add_field(name="{}\nLost".format(slotOutput),
	               value=f'You lost {1*amount} coins')

	if slot1 == slot2 == slot3:
		await update_bank(ctx.author, 3 * amount)
		await ctx.send(embed=won)
		return

	if slot1 == slot2:
		await update_bank(ctx.author, 2 * amount)
		await ctx.send(embed=ok)
		return

	else:
		await update_bank(ctx.author, -1 * amount)
		await ctx.send(embed=lost)
		return


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.send(
		    f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} Seconds'
		)


@client.command()
async def shop(ctx):
	em = discord.Embed(title="Shop")

	for item in mainshop:
		name = item["name"]
		price = item["price"]
		desc = item["description"]
		em.add_field(name=name, value=f"${price} | {desc}")

	await ctx.send(embed=em)


@client.command()
async def buy(ctx, item, amount=1):
	await open_account(ctx.author)

	res = await buy_this(ctx.author, item, amount)

	if not res[0]:
		if res[1] == 1:
			await ctx.send("That Object isn't there!")
			return
		if res[1] == 2:
			await ctx.send(
			    f"You don't have enough money in your wallet to buy {amount} {item}"
			)
			return

	await ctx.send(f"You just bought {amount} {item}")


@client.command(aliases=['inv'])
async def inventory(ctx):
	await open_account(ctx.author)
	user = ctx.author
	users = await get_bank_data()

	try:
		bag = users[str(user.id)]["bag"]
	except:
		bag = []

	em = discord.Embed(title="Your Inventory")
	for item in bag:
		name = item["item"]
		amount = item["amount"]

		em.add_field(name=name, value=amount)

	await ctx.send(embed=em)


async def buy_this(user, item_name, amount):
	item_name = item_name.lower()
	name_ = None
	for item in mainshop:
		name = item["name"].lower()
		if name == item_name:
			name_ = name
			price = item["price"]
			break

	if name_ == None:
		return [False, 1]

	cost = price * amount

	users = await get_bank_data()

	bal = await update_bank(user)

	if bal[0] < cost:
		return [False, 2]

	try:
		index = 0
		t = None
		for thing in users[str(user.id)]["bag"]:
			n = thing["item"]
			if n == item_name:
				old_amt = thing["amount"]
				new_amt = old_amt + amount
				users[str(user.id)]["bag"][index]["amount"] = new_amt
				t = 1
				break
			index += 1
		if t == None:
			obj = {"item": item_name, "amount": amount}
			users[str(user.id)]["bag"].append(obj)
	except:
		obj = {"item": item_name, "amount": amount}
		users[str(user.id)]["bag"] = [obj]

	with open("mainbank.json", "w") as f:
		json.dump(users, f)

	await update_bank(user, cost * -1, "wallet")

	return [True, "Worked"]


@client.command()
async def sell(ctx, item, amount=1):
	await open_account(ctx.author)

	res = await sell_this(ctx.author, item, amount)

	if not res[0]:
		if res[1] == 1:
			await ctx.send("That Object isn't there!")
			return
		if res[1] == 2:
			await ctx.send(f"You don't have {amount} {item} in your bag.")
			return
		if res[1] == 3:
			await ctx.send(f"You don't have {item} in your bag.")
			return

	await ctx.send(f"You just sold {amount} {item}.")


async def sell_this(user, item_name, amount, price=None):
	item_name = item_name.lower()
	name_ = None
	for item in mainshop:
		name = item["name"].lower()
		if name == item_name:
			name_ = name
			if price == None:
				price = 0.7 * item["price"]
			break

	if name_ == None:
		return [False, 1]

	cost = price * amount

	users = await get_bank_data()

	bal = await update_bank(user)

	try:
		index = 0
		t = None
		for thing in users[str(user.id)]["bag"]:
			n = thing["item"]
			if n == item_name:
				old_amt = thing["amount"]
				new_amt = old_amt - amount
				if new_amt < 0:
					return [False, 2]
				users[str(user.id)]["bag"][index]["amount"] = new_amt
				t = 1
				break
			index += 1
		if t == None:
			return [False, 3]
	except:
		return [False, 3]

	with open("mainbank.json", "w") as f:
		json.dump(users, f)

	await update_bank(user, cost, "wallet")

	return [True, "Worked"]


@client.command(aliases=["lb"])
async def leaderboard(ctx, x=5):
	users = await get_bank_data()
	leader_board = {}
	total = []
	for user in users:
		name = int(user)
		total_amount = users[user]["wallet"] + users[user]["bank"]
		leader_board[total_amount] = name
		total.append(total_amount)

	total = sorted(total, reverse=True)

	em = discord.Embed(
	    title=f"Top {x} Richest Dxrk Users",
	    description=
	    "This is decided on the basis of raw money in the bank and wallet put together",
	    color=discord.Color.red())
	index = 1
	for amt in total:
		id_ = leader_board[amt]
		member = client.get_user(id_)
		name = member.name
		em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
		if index == x:
			break
		else:
			index += 1

	await ctx.send(embed=em)


async def open_account(user):

	users = await get_bank_data()

	if str(user.id) in users:
		return False
	else:
		users[str(user.id)] = {}
		users[str(user.id)]["wallet"] = 0
		users[str(user.id)]["bank"] = 0

	with open('mainbank.json', 'w') as f:
		json.dump(users, f)

	return True


async def get_bank_data():
	with open('mainbank.json', 'r') as f:
		users = json.load(f)

	return users


async def update_bank(user, change=0, mode='wallet'):
	users = await get_bank_data()

	users[str(user.id)][mode] += change

	with open('mainbank.json', 'w') as f:
		json.dump(users, f)
	bal = users[str(user.id)]['wallet'], users[str(user.id)]['bank']
	return bal

@client.command()
@cooldown(1, 900, BucketType.user)
async def work(ctx):
	await open_account(ctx.author)
	user = ctx.author
	users = await get_bank_data()

	earnings = random.randrange(500)

	await ctx.send(
	    f"__**Boss**__\nGood Job Heres {earnings} Dollars For Working So Well!!"
	)

	users[str(user.id)]["wallet"] += earnings

	with open("mainbank.json", "w") as f:
		json.dump(users, f)


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.reply(
		    f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} Seconds'
		)

@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


@client.event
async def on_message(message):
    if message.author.bot == False:
        with open('users.json', 'r') as f:
            users = json.load(f)

        await update_data(users, message.author)
        await add_experience(users, message.author, 5)
        await level_up(users, message.author, message)

        with open('users.json', 'w') as f:
            json.dump(users, f)

    await client.process_commands(message)


async def update_data(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1


async def add_experience(users, user, exp):
    users[f'{user.id}']['experience'] += exp

async def level_up(users, user, message):
    with open('levels.json', 'r') as g:
        levels = json.load(g)
    experience = users[f'{user.id}']['experience']
    lvl_start = users[f'{user.id}']['level']
    lvl_end = int(experience ** (1 / 4))
    if lvl_start < lvl_end:
        channel = client.get_channel(840323358507663360)
        await channel.send(f'{user.mention} has leveled up to level {lvl_end}! Thank You For Being Active :smiley: ')
        users[f'{user.id}']['level'] = lvl_end

@client.command()
async def level(ctx, member: discord.Member = None):
    if not member:
        id = ctx.message.author.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        lvl = users[str(id)]['level']
        xp = users[str(id)]['experience']
        await ctx.reply(f'You are at level {lvl}!')
    else:
        id = member.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        lvl = users[str(id)]['level']
        xp = users[str(id)]['experience']
        await ctx.send(f'{member} is at level {lvl}!')

@client.command()
async def help(ctx):
  embedVar = discord.Embed(title=":star2: **I Herd You Need Help** :star2:", description=f"Whats Up, Heres All My Commands\n__**Main Commands**__\nHelp - Shows This Message\nPing - Offline\nRealms\nServerinfo\n__**Economy Commands**__\nbalance\nbeg\nbuy\ndeposit\nhelp\ninventory\nleaderboard\nrob - Offline\nsell\nsend\nshop\nslots\nwithdraw\nwork\n__**Levling Commands**__\nlevel", color=discord.Color.red())
  embedVar.add_field(name="__**Our Servers**__", value="[Official Community](https://discord.gg/ctDXuN3gVT)", inline=True)
  await ctx.send(embed=embedVar)

@client.command(aliases=["si"])
async def serverinfo(ctx):
  name = str(ctx.guild.name)
  description = str(ctx.guild.description)

  owner = str(ctx.guild.owner)
  id = str(ctx.guild.id)
  region = str(ctx.guild.region)
  totalmemberCount = str(ctx.guild.member_count)
  memberCount = len([m for m in ctx.guild.members if not m.bot])

  icon = str(ctx.guild.icon_url)
   
  embed = discord.Embed(
      title=name + " Information",
      description=description,
      color=discord.Color.red()
    )
  embed.set_thumbnail(url=icon)
  embed.add_field(name="Owner", value=owner, inline=True)
  embed.add_field(name="Server ID", value=id, inline=True)
  embed.add_field(name="Region", value=region, inline=True)
  embed.add_field(name="Total Member Count", value=totalmemberCount, inline=True)
  embed.add_field(name="True Member Count", value=memberCount, inline=True)

  await ctx.send(embed=embed)

@client.command()
async def realms(ctx):

  realms = discord.Embed(title="Our Minecraft Realms", description="Dxrk's MCBE Realms ", color=discord.Color.red())
  realms.add_field(name="__**KitPvp**__", value="Status: Online\nCode: ", inline=True)
  realms.add_field(name="__**Factions**__", value="Status: Offline\nCode: ", inline=True)
  realms.add_field(name="__**Prinson**__", value="Status: Offline\nCode: ", inline=True)
  realms.add_field(name="__**SkyBlock**__", value="Status: Offline\nCode: ", inline=True)
  realms.add_field(name="__**Survival**__", value="Status: Offline\nCode: ", inline=True)

  await ctx.send(embed=realms)

@client.command()
async def apply(ctx):

  apply = discord.Embed(title="Apply For Staff", description="", color=discord.Color.red())
  apply.add_field(name="__**Apply Here**__", value="[Click Here](https://forms.gle/HmdW6q7xqqKsGUTJ6)", inline=True)
  await ctx.reply(embed=apply)

@client.command()
async def userinfo(ctx, *, user: discord.Member = None):

    if user is None:
        user = ctx.author      
    date_format = "%a, %d %b %Y %I:%M %p"
    embed = discord.Embed(color=discord.Color.red(), description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Joined At", value=user.joined_at.strftime(date_format))
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join Placment", value=str(members.index(user)+1))
    embed.add_field(name="Account Creation", value=user.created_at.strftime(date_format))
    if len(user.roles) > 1:
      role_string = ' '.join([r.mention for r in user.roles][1:])
      embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
    perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
    embed.add_field(name="Guild permissions", value=perm_string, inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed)

owner = 517020964261855232

@client.command()
@cooldown(1, 20, BucketType.user)
async def heist(ctx):

  if ctx.author.id == owner:
    await ctx.reply("")
  else:
    await ctx.reply("Your Gay : )")

@client.command()
@cooldown(1, 20, BucketType.user)
async def beg(ctx):
	await open_account(ctx.author)
	user = ctx.author

	users = await get_bank_data()

	earnings = random.randrange(250)

	await ctx.send(f'{ctx.author.mention} Got {earnings} coins!!')

	users[str(user.id)]["wallet"] += earnings

	with open("mainbank.json", 'w') as f:
		json.dump(users, f)

keep_alive()
client.run(os.getenv('TOKEN')) 
