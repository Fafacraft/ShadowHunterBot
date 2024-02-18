import asyncio
import discord
import nest_asyncio
from discord.ext import commands
from main_game.start_game import start_game

nest_asyncio.apply()


intents = discord.Intents.default() # LES DROITS
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.dm_messages = True
intents.dm_reactions = True
intents.integrations = True

client = commands.Bot(command_prefix="$", intents = intents)

# START OF CODE


#start a game
@client.command(name="start_game")
async def cmd_start_game(ctx):
  response = await ctx.message.reply("Combien de joueur ?")
  await response.add_reaction("4️⃣")
  await response.add_reaction("5️⃣")
  await response.add_reaction("6️⃣")
  await response.add_reaction("7️⃣")
  await response.add_reaction("8️⃣")
  await response.add_reaction("❌")
  
  # check used to listen to reaction_add
  def check(reaction, user):
    emoji_list = ['4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '❌']
    return user == ctx.message.author and str(reaction.emoji) in emoji_list
  
  try:
    # do the thing when reaction is clicked
    reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
    match reaction.emoji:
      case '4️⃣':
        await start_game(4, response, client)
        return
      case '5️⃣':
        await start_game(5, response, client)
        return
      case '6️⃣':
        await start_game(6, response, client)
        return
      case '7️⃣':
        await start_game(7, response, client)
        return
      case '8️⃣':
        await start_game(8, response, client)
        return
      case '❌':
        await ctx.send("Annuler.")
        pass
        
  # if it's timed out, will go out of discussion
  except asyncio.TimeoutError:
    await ctx.send("Aucune réponse ; annuler.")


@client.event
async def on_ready():
    print("Bot is up and running !")


@client.event
async def on_message(message):
  # if it's himself
  if message.author == client.user:
    return

  await client.process_commands(message)



# END OF CODE

with open('token.txt', 'r') as file:
  file_content = file.read()
  if file_content == "":
    print("No token")
  else:
    client.run(file_content)