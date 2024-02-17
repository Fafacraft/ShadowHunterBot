import asyncio
import io
import json
import os
import discord
import nest_asyncio
from discord.ext import commands

nest_asyncio.apply()


intents = discord.Intents.default() # LES DROITS

client = commands.Bot(command_prefix="$", intents = intents)

# START OF CODE



# start ship discussion
@client.command(name="ship")
async def ship_discussion(ctx):
  global ship_tree

  # if leaf, found the ship, send the right message and skip the else
  if (ship_tree.isAtLeaf()):
    await ctx.message.reply("""
# This is your ship ; 
                                     
Name : """ + ship_tree.get_current()[0] + """
Link : """ + ship_tree.get_current()[1] + """
""")


  # else, we're still in the discussion
  else:
    response = await ctx.message.reply("""
# What Star Citizen fits you the best ! 
                                  
1️⃣ : """ + ship_tree.get_current()[0] + """
2️⃣ : """ + ship_tree.get_current()[1] + """
🔄 : reset
❌ : cancel
""")
    
    # add reactions
    await response.add_reaction("1️⃣")
    await response.add_reaction("2️⃣")
    await response.add_reaction("🔄")
    await response.add_reaction("❌")
    
    # check used to listen to reaction_add
    def check(reaction, user):
      emoji_list = ['1️⃣', '2️⃣', '🔄', '❌']
      return user == ctx.message.author and str(reaction.emoji) in emoji_list
    
    try:
      # do the thing when reaction is clicked
      reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
      match reaction.emoji:
        case '1️⃣':
          # go to the True node and let's go for another round
          ship_tree.next_node(True)
          await ship_discussion(ctx)
          return
        case '2️⃣':
          # go to the False node and let's go for another round
          ship_tree.next_node(False)
          await ship_discussion(ctx)
          return
        case '🔄':
          # reset and let's go for another round
          ship_tree.current_node = ship_tree.root
          await ship_discussion(ctx)
          return
        case '❌':
          await ctx.send("Cancelled")
          pass
          
    # if it's timed out, will go out of discussion
    except asyncio.TimeoutError:
      await ctx.send("Idle for too long ; conversation stopped.")
  # end of else, out of discussion
  
  
  # reset the tree for next time, and stop the conversation
  ship_tree.current_node = ship_tree.root
  append_command(ctx)
  return


# write ochoas
@client.command(name="banu")
async def toBanu(ctx, *, msg: str):
  append_command(ctx)
  img = makeBanuTextImg(msg)
  
  # create buffer
  buffer = io.BytesIO()
  # save PNG in buffer
  img.save(buffer, format="PNG")
  # move to beginning of buffer so `send()` it will read from beginning
  buffer.seek(0)
  await ctx.send(ctx.author.mention + " : ", file=discord.File(buffer, 'banu.png'))

  # so we can't cheat, you need to know how to read banu :)
  await ctx.message.delete()


@client.event
async def on_ready():
    print("Le bot est prêt !")




# END OF CODE

with open('token.txt', 'r') as file:
  file_content = file.read()
  if file_content == "":
    print("No token")
  else:
    client.run(file_content)