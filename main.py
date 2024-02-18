import asyncio
import discord
import nest_asyncio
from discord.ext import commands
from main_game.start_game import start_game
from main_game.game import Game

nest_asyncio.apply()


intents = discord.Intents.default() # LES DROITS
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.dm_messages = True
intents.dm_reactions = True
intents.integrations = True
intents.members = True

client = commands.Bot(command_prefix="$", intents = intents)

game = Game([])



#start a game
@client.command(name="start_game")
async def cmd_start_game(ctx):
  global game
  global client
  response = await ctx.message.reply("Combien de joueur ?")
  await response.add_reaction("4️⃣")
  await response.add_reaction("5️⃣")
  await response.add_reaction("6️⃣")
  await response.add_reaction("7️⃣")
  await response.add_reaction("8️⃣")
  await response.add_reaction("❌")
  
  def check(reaction, user):
    emoji_list = ['4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '❌']
    return user == ctx.message.author and str(reaction.emoji) in emoji_list
  
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
    match reaction.emoji:
      case '4️⃣':
        game = await start_game(4, response, client)
        return
      case '5️⃣':
        game = await start_game(5, response, client)
        return
      case '6️⃣':
        game = await start_game(6, response, client)
        return
      case '7️⃣':
        game = await start_game(7, response, client)
        return
      case '8️⃣':
        game = await start_game(8, response, client)
        return
      case '❌':
        await ctx.send("Annuler.")
        pass
  except asyncio.TimeoutError:
    await ctx.send("Aucune réponse ; annuler.")


# draw a card, for now only vision
@client.command(name="draw")
async def draw(ctx):
  global game
  global client
  await game.draw_vision(ctx.message.author, ctx, client)



@client.event
async def on_ready():
    print("Bot is up and running !")


@client.event
async def on_message(message):
  # if it's himself
  if message.author == client.user:
    return

  await client.process_commands(message)



# get the token and start the bot
with open('token.txt', 'r') as file:
  file_content = file.read()
  if file_content == "":
    print("No token")
  else:
    client.run(file_content)