import asyncio
import discord
from discord.ext import commands
import random
from characters.characters_functions import get_characters_by_allegiance

async def start_game(nb, message, client):
    response = await message.reply("Démarrage de la partie... Cliquez sur la réaction pour rejoindre ! Vous avez 30s")
    await response.add_reaction('✅')

    players = []
    characters = []
    
    # choose the characters randomly with some good ol' shuffles
    all_neutrals = get_characters_by_allegiance("Neutre")
    all_shadow = get_characters_by_allegiance("Hunter")
    all_hunter = get_characters_by_allegiance("Shadow")
    random.shuffle(all_neutrals)
    random.shuffle(all_shadow)
    random.shuffle(all_hunter)
    characters.append(all_shadow[0])
    characters.append(all_shadow[1])
    characters.append(all_hunter[0])
    characters.append(all_hunter[1])
    if nb in (5, 6, 7, 8):
        characters.append(all_neutrals[0])
    if nb in (6, 7, 8):
        characters.append(all_neutrals[1])
    if nb == 7:
        characters.append(all_neutrals[2])
    if nb == 8:
        characters.append(all_shadow[2])
        characters.append(all_hunter[2])
    random.shuffle(characters)


    # get the players who plays
    def check(reaction, user):
        if user not in players and not user.bot:
            players.append([user, None])  # each player is a couple of the player + their character
        return False
        
    try:
        await client.wait_for('reaction_add', timeout=5, check=check)  # DEBUG ; timeout should be how long to wait for people to ready up, for exemple, 30s
    except asyncio.TimeoutError:
        pass

    if len(players) > nb:
        await message.channel.send("Il y a trop de joueur ! Avez-vous mis le bon nombre ? (" + str(nb) + ")")
        return
    if len(players) < 1:  # DEBUG ; put that to 1 instead of nb to be able to test the bot solo
        await message.channel.send("Il n'y a pas assez de joueur pour commencer la partie.")
    else:
        await message.channel.send("La partie commence ! Votre personnage vous sera envoyé en mp.")
        for i in range(len(players)):
            players[i][1] = characters[i]
            # send character in mp
            await players[i][0].send("Votre personnage est :\n\n" + players[i][1].get_card(), file=discord.File(players[i][1].image))


